// =============================================================================
//  Lanczos2 (Fixed Radius 2) - Compute Shader
//  ------------------------------------------
//  High-performance 4x4 Lanczos-2 resampling for upscaling.
//  Uses hardware Gather for the 4x4 neighborhood, with optional linear-light
//  processing and soft anti-ringing.  No adaptive radius - always radius 2.
//
//  This is the optimal shader for the common 1440p -> 4K (1.5x) upscaling case.
//  For downscaling or non-uniform scaling the adaptive shader
//  (lanczos_adaptive.hlsl) is used automatically by the Python host.
//
//  Features :
//    - Lanczos-2 kernel (fixed radius 2)
//    - Hardware Gather (4 Gather calls per color channel)
//    - Optional linear-light processing (sRGB -> linear -> sRGB)
//    - Soft anti-ringing with configurable neighborhood
//    - Integer-pixel alignment - no jitter
//
//  Constant buffer layout (must match LanczosScaler.CB_FORMAT_LANCZOS2) :
//    float4 bgColor;           // color outside the destination rect
//    uint   srcWidth, srcHeight;
//    uint   dstTotalWidth, dstTotalHeight;
//    int    dstX, dstY, dstW, dstH;
//    float  blur;              // kernel softness (1.0 = standard)
//    float  antiringStrength;  // 0.0 - 1.0
//    bool   linearLight;
//    bool   tightAntiring;     // true = central 2x2 only for ringing bounds
//
//  Workgroup size : 16x16.
//  Dispatch :
//    groupsX = ceil(dstTotalWidth  / 16)
//    groupsY = ceil(dstTotalHeight / 16)
//
//  Adapted from Magpie effect by funnyplanter for linux-rt-upscaler.
// =============================================================================

Texture2D<float4>   InputTex    : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex   : register(u0);
SamplerState        PointSampler: register(s0);

cbuffer Constants : register(b0)
{
    float4 bgColor;              // color outside the destination rectangle
    uint   srcWidth, srcHeight;
    uint   dstTotalWidth, dstTotalHeight;
    int    dstX, dstY, dstW, dstH;
    float  blur;                 // kernel softness (1.0 = standard Lanczos-2)
    float  antiringStrength;     // 0 = off, 1 = full hard clamp
    bool   linearLight;          // process in linear light (recommended)
    bool   tightAntiring;        // true = only central 2x2 for ringing bounds
}

// =============================================================================
//  Lanczos-2 kernel (fixed radius = 2)
// =============================================================================
#define PI 3.1415926535897932f

float lanczos2(float x)
{
    float s = 1.0f / blur;
    x *= s;                           // apply blur stretch
    if (x < 1e-4f) return 1.0f;
    if (x >= 2.0f)  return 0.0f;

    float pi_x = PI * x;
    return (2.0f * sin(pi_x) * sin(pi_x * 0.5f)) / (pi_x * pi_x);
}

// =============================================================================
//  Main entry point
// =============================================================================
[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 outPos = dtid.xy;
    if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight)
        return;

    int x = int(outPos.x);
    int y = int(outPos.y);
    if (x < dstX || x >= dstX + dstW || y < dstY || y >= dstY + dstH)
    {
        OutputTex[outPos] = bgColor;
        return;
    }

    // ---- Map destination pixel to continuous source coordinate ------------
    float2 uv       = (float2(outPos.x - dstX, outPos.y - dstY) + 0.5f) / float2(dstW, dstH);
    float2 srcCoord = uv * float2(srcWidth, srcHeight);
    float2 pt       = 1.0f / float2(srcWidth, srcHeight);

    float2 pp = srcCoord - 0.5f;                 // center on integer positions
    int2   p0 = int2(floor(pp));
    float2 f  = pp - float2(p0);                 // fractional offset [0,1)

    // ---- Pre-compute separable Lanczos-2 weights for the 4x4 neighborhood -
    // For ix = -1,0,1,2 the distances are: 1+f.x, f.x, 1-f.x, 2-f.x
    float4 wx = float4(
        lanczos2(1.0f + f.x),
        lanczos2(      f.x),
        lanczos2(1.0f - f.x),
        lanczos2(2.0f - f.x));
    float4 wy = float4(
        lanczos2(1.0f + f.y),
        lanczos2(      f.y),
        lanczos2(1.0f - f.y),
        lanczos2(2.0f - f.y));

    wx /= dot(wx, 1.0f);   // normalise so weights sum to 1
    wy /= dot(wy, 1.0f);

    // Source texel coordinate of the top-left sample (p0 - 1, p0 - 1)
    float2 s = (float2(p0) - 1.0f) * pt;

    float3 accum     = 0.0f;
    float  weightSum = 0.0f;
    float3 vmin      = 1e6f, vmax = -1e6f;

    // ---- 4x4 Gather convolution (identical to original, proven code) ------
    // GatherRed/Green/Blue return a 2x2 quad:
    //   r.w = top-left,  r.z = top-right,  r.x = bottom-left, r.y = bottom-right
    for (int yBlock = 0; yBlock < 2; ++yBlock)   // 0, 2
    {
        for (int xBlock = 0; xBlock < 2; ++xBlock) // 0, 2
        {
            float2 t = s + float2(xBlock, yBlock) * pt;

            float4 r_raw = InputTex.GatherRed  (PointSampler, t);
            float4 g_raw = InputTex.GatherGreen(PointSampler, t);
            float4 b_raw = InputTex.GatherBlue (PointSampler, t);

            // Optional linear-light conversion (squaring)
            float4 r = linearLight ? r_raw * r_raw : r_raw;
            float4 g = linearLight ? g_raw * g_raw : g_raw;
            float4 b = linearLight ? b_raw * b_raw : b_raw;

            float3 pix[4] = {
                float3(r.w, g.w, b.w),   // (xBlock+0, yBlock+0)
                float3(r.z, g.z, b.z),   // (xBlock+1, yBlock+0)
                float3(r.x, g.x, b.x),   // (xBlock+0, yBlock+1)
                float3(r.y, g.y, b.y)    // (xBlock+1, yBlock+1)
            };

            int ix_base = xBlock;
            int iy_base = yBlock;

            for (int k = 0; k < 4; ++k)
            {
                int dx = (k % 2 == 0) ? 0 : 1;
                int dy = (k < 2) ? 0 : 1;
                int ix = ix_base + dx;
                int iy = iy_base + dy;

                float w = wx[ix] * wy[iy];
                accum     += pix[k] * w;
                weightSum += w;

                // Anti-ringing bounds - use full or central 2x2 depending on tightAntiring
                bool isCentral = (ix >= 0 && ix <= 1 && iy >= 0 && iy <= 1);
                if (!tightAntiring || isCentral)
                {
                    vmin = min(vmin, pix[k]);
                    vmax = max(vmax, pix[k]);
                }
            }
        }
    }

    float3 v = accum / weightSum;

    // Soft anti-ringing clamp
    v = clamp(v, lerp(v, vmin, antiringStrength), lerp(v, vmax, antiringStrength));

    // Convert back from linear light if necessary
    float3 finalColor = linearLight ? sqrt(max(v, 0.0f)) : v;

    OutputTex[outPos] = float4(finalColor, 1.0f);
}