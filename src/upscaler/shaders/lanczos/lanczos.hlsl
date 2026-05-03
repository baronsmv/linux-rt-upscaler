// =============================================================================
//  Anisotropic Adaptive Lanczos 3.0
//  --------------------------------
//  Single-pass, high-quality 2D resampler for upscaling and downscaling.
//
//  Features :
//    - Correct variable-radius Lanczos kernel (no frequency-domain shortcuts)
//    - Independent X/Y radii (pre‑computed by the Python handler)
//    - Automatic anti-aliasing when downscaling (radii grow with the inverse scale)
//    - Hardware Gather fast path for radius-2 (4x4) upscaling
//    - Optional linear-light processing (gamma-correct resampling)
//    - Soft anti-ringing with configurable neighbourhood
//    - Integer-pixel alignment - zero jitter or sub-pixel discrepancies
//
//  Use case example :
//    1440p -> 4K     (scale 1.5x)   radius = 2  -> sharp upscale
//    4K    -> 1440p  (scale 0.75x)  radius = 3  -> properly filtered downscale
//
//  Dispatch :
//    groupsX = ceil(dstTotalWidth  / 16)
//    groupsY = ceil(dstTotalHeight / 16)
//
//  Adapted from Magpie effect by funnyplanter for linux-rt-upscaler.
// =============================================================================

Texture2D<float4>   InputTex    : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex   : register(u0);
SamplerState        PointSampler: register(s0);   // needed for Gather()

cbuffer Constants : register(b0)
{
    float4 bgColor;                  // color used outside the destination rectangle
    uint   srcWidth, srcHeight;
    uint   dstTotalWidth, dstTotalHeight;
    int    dstX, dstY, dstW, dstH;   // destination rectangle
    uint   radiusX;                  // pre‑computed filter radius in X
    uint   radiusY;                  // pre‑computed filter radius in Y
    float  blur;                     // kernel softness (1.0 = standard Lanczos)
    float  antiringStrength;         // 0 = off, 1 = full clamp
    bool   linearLight;              // process in linear light (recommended)
    bool   tightAntiring;            // true = only central 2x2 for ringing bounds
}

// =============================================================================
//  Correct Lanczos kernel
//  L(x) = sinc(x) · sinc(x / r)    for |x| < r
//       = 1                        for x = 0
//       = 0                        for |x| ≥ r
//
//  Standard formula : r * sin(πx) * sin(πx / r) / (π² x²)
// =============================================================================
#define PI 3.1415926535897932f

float lanczos(float x, float r)
{
    if (x < 1e-4f) return 1.0f;                 // removable singularity at 0
    if (x >= r)    return 0.0f;                 // compact support

    float pi_x = PI * x;
    return (r * sin(pi_x) * sin(pi_x / r)) / (pi_x * pi_x);
}


// =============================================================================
//  Hardware Gather path for the 4x4 (radius-2) case.
//  Used when both axes are radius 2 (upscaling or very mild downscale).
//  Identical mathematics to the generic loop, but faster.
// =============================================================================
float3 ConvolveRadius2(
    float2 srcCoord,        // continuous source coordinate (in pixels)
    float2 pt,              // texel size (1/width, 1/height)
    float  blur,
    bool   linearLight,
    bool   tightAntiring,
    float  antiringStrength)
{
    // Centre alignment (see main() comments)
    float2 pp = srcCoord - 0.5f;
    int2   p0 = int2(floor(pp));
    float2 f  = pp - float2(p0);           // fractional offset [0,1)

    // Pre-compute separable weights for the 4x4 neighbourhood.
    // For ix = -1,0,1,2 the distances are: 1+f.x, f.x, 1-f.x, 2-f.x
    float4 wx = float4(
        lanczos(1.0f + f.x, 2.0f),
        lanczos(    0.0f + f.x, 2.0f),
        lanczos(1.0f - f.x, 2.0f),
        lanczos(2.0f - f.x, 2.0f));
    float4 wy = float4(
        lanczos(1.0f + f.y, 2.0f),
        lanczos(    0.0f + f.y, 2.0f),
        lanczos(1.0f - f.y, 2.0f),
        lanczos(2.0f - f.y, 2.0f));

    wx /= dot(wx, 1.0f);   // normalise so weights sum to 1
    wy /= dot(wy, 1.0f);

    // Source texel coordinate of the top-left sample (p0 - 1, p0 - 1)
    float2 s = (float2(p0) - 1.0f) * pt;

    float3 accum = 0.0f;
    float  weightSum = 0.0f;
    float3 vmin = 1e6f, vmax = -1e6f;

    // We walk the 4x4 neighbourhood using two Gather calls per color channel.
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

            // Convert to linear light if requested
            float4 r = linearLight ? r_raw * r_raw : r_raw;
            float4 g = linearLight ? g_raw * g_raw : g_raw;
            float4 b = linearLight ? b_raw * b_raw : b_raw;

            // The four samples and their integer offsets:
            //   pix[0] at (xBlock+0, yBlock+0)  -> r.w, g.w, b.w
            //   pix[1] at (xBlock+1, yBlock+0)  -> r.z, g.z, b.z
            //   pix[2] at (xBlock+0, yBlock+1)  -> r.x, g.x, b.x
            //   pix[3] at (xBlock+1, yBlock+1)  -> r.y, g.y, b.y
            float3 pix[4] = {
                float3(r.w, g.w, b.w),
                float3(r.z, g.z, b.z),
                float3(r.x, g.x, b.x),
                float3(r.y, g.y, b.y)
            };

            // Corresponding kernel offsets relative to the centre p0
            // (ix, iy) in [-1, 2] range
            int ix_base = xBlock;   // 0 or 2
            int iy_base = yBlock;

            for (int k = 0; k < 4; ++k)
            {
                int dx = (k % 2 == 0) ? 0 : 1;
                int dy = (k < 2) ? 0 : 1;
                int ix = ix_base + dx;
                int iy = iy_base + dy;

                // The weight array is indexed directly by (iy) and (ix)
                // because we stored wx/wy in order [-1,0,1,2].
                float w = wx[ix] * wy[iy];

                accum     += pix[k] * w;
                weightSum += w;

                // Anti-ringing bounds - only consider central 2x2 if tight
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
    return v;
}


// =============================================================================
//  Main entry point
// =============================================================================
[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 outPos = dtid.xy;

    // ---- Bounds / scissor check --------------------------------------------
    if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight)
        return;

    int x = int(outPos.x);
    int y = int(outPos.y);
    if (x < dstX || x >= dstX + dstW || y < dstY || y >= dstY + dstH)
    {
        OutputTex[outPos] = bgColor;
        return;
    }

    // ---- 1. Radii already computed by the host ----------------------------
    int irx = int(radiusX);
    int iry = int(radiusY);

    // ---- 2. Map destination pixel to continuous source coordinate --------
    // We want the centre of the destination pixel to align with the source
    // pixel grid such that integer positions correspond to exact pixel centres.
    // Standard formula:
    //   uv = (destCoord + 0.5) / destSize
    //   srcCoord = uv * srcSize
    //   pp = srcCoord - 0.5   (centre on integer positions)
    //   p0 = floor(pp)        -> integer pixel index of the nearest texel
    //   f  = pp - p0          -> fractional offset [0,1)
    float2 uv       = (float2(outPos.x - dstX, outPos.y - dstY) + 0.5f) / float2(dstW, dstH);
    float2 srcCoord = uv * float2(srcWidth, srcHeight);
    float2 pt       = 1.0f / float2(srcWidth, srcHeight);   // texel size

    // ---- 3. Fast path for the common radius-2 case (upscaling) ------------
    if (irx == 2 && iry == 2)
    {
        float3 linearResult = ConvolveRadius2(srcCoord, pt, blur,
                                              linearLight, tightAntiring, antiringStrength);

        // Convert back from linear light if needed
        float3 finalColor = linearLight ? sqrt(max(linearResult, 0.0f)) : linearResult;
        OutputTex[outPos] = float4(finalColor, 1.0f);
        return;
    }

    // ---- 4. Generic variable-radius path (for any other scale factors) ----
    float2 pp = srcCoord - 0.5f;
    int2   p0 = int2(floor(pp));
    float2 f  = pp - float2(p0);

    float3 accum     = 0.0f;
    float  weightSum = 0.0f;
    float3 vmin      = 1e6f, vmax = -1e6f;

    // Walk the sampling window:
    //   iy from -iry+1 to iry   (e.g. for radius 3: -2, -1, 0, 1, 2, 3)
    //   ix from -irx+1 to irx
    for (int iy = -iry + 1; iy <= iry; ++iy)
    {
        float wy = lanczos(abs(float(iy) - f.y), float(iry));

        for (int ix = -irx + 1; ix <= irx; ++ix)
        {
            // Clamp to source texture area
            int2 sc = clamp(p0 + int2(ix, iy),
                            int2(0, 0),
                            int2(srcWidth - 1, srcHeight - 1));

            float3 color = InputTex.Load(int3(sc, 0)).rgb;
            float3 val   = linearLight ? color * color : color;

            float wx = lanczos(abs(float(ix) - f.x), float(irx));
            float w  = wx * wy;

            accum     += val * w;
            weightSum += w;

            // Anti-ringing bounds
            bool isCentral = (abs(ix) <= 1 && abs(iy) <= 1);
            if (!tightAntiring || isCentral)
            {
                vmin = min(vmin, val);
                vmax = max(vmax, val);
            }
        }
    }

    // Normalise (avoid division by zero in pathological cases)
    float3 v = accum / (weightSum + 1e-7f);

    // Soft anti-ringing clamp (Magpie style)
    v = clamp(v, lerp(v, vmin, antiringStrength), lerp(v, vmax, antiringStrength));

    // Convert from linear light to sRGB / gamma space
    float3 finalColor = linearLight ? sqrt(max(v, 0.0f)) : v;

    OutputTex[outPos] = float4(finalColor, 1.0f);
}