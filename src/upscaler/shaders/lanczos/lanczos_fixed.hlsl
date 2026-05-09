// =============================================================================
//  Lanczos2 (Fixed Radius 2) - Compute Shader
//  ------------------------------------------
//  High-performance 4x4 Lanczos-2 resampling for upscaling.
//  Exact replica of the original working Lanczos-2 upscaler, with optional
//  blur/softness. Uses hardware Gather for optimal memory throughput.
//  Anti-ringing clamps to the full 4x4 pixel window - the only configuration
//  that proved artifact-free in practice. Linear-light processing (square ->
//  process -> sqrt) is always applied; this matches the original behaviour.
//
//  This shader is used automatically when radiusX = radiusY = 2 (upscaling).
//  For downscaling or non-uniform scaling, lanczos_adaptive.hlsl is used.
//
//  Features:
//    - Lanczos-2 kernel (fixed radius 2)
//    - Hardware Gather (4 Gather calls per color channel)
//    - Separable, normalised weights - zero sum drift
//    - Full 4x4 anti-ringing clamp (proven, block-free)
//    - Implicit linear-light processing (squaring / sqrt)
//    - Integer-pixel alignment - no jitter
//    - Optional blur parameter (1.0 = standard Lanczos-2)
//
//  Observations:
//    - Every deviation we tested (variable anti-ringing neighborhood, soft
//      clamp, togglable linear light, different gather offset) introduced
//      visible or subtle blockiness.
//    - The adaptive shader (lanczos_adaptive.hlsl) handles the advanced
//      features (tight/soft anti-ringing, linear-light toggle) correctly
//      because its explicit pixel-offset loop makes the center region trivial
//      to define. For radius 2 upscaling, these features are not needed and
//      the fixed shader is kept simple and safe.
//
//  Constant buffer layout (must match CB_FORMAT_FIXED):
//    float4 bgColor;               // color outside the destination rect
//    uint   srcWidth, srcHeight;
//    uint   dstTotalWidth, dstTotalHeight;
//    int    dstX, dstY, dstW, dstH;
//    float  blur;                  // kernel softness (1.0 = standard)
//
//  Workgroup size: 16x16.
//  Dispatch:
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
    float4 bgColor;
    uint   srcWidth, srcHeight;
    uint   dstTotalWidth, dstTotalHeight;
    int    dstX, dstY, dstW, dstH;
    float  blur;
}

// -------------------------------------------------------------------------
//  Lanczos-2 kernel
//  L(x) = sinc(x) · sinc(x/2)   for |x| < 2,  1 at x=0.
//  blur > 1.0 softens the kernel (x -> x / blur).
// -------------------------------------------------------------------------
#define PI 3.1415926535897932

float lanczos(float x)
{
    float s = 1.0 / blur;
    float kx = PI * s * x;
    float wx = 0.5 * kx;
    return x < 1e-5 ? 1.0 : sin(kx) * sin(wx) / (x * x);
}

#define K(x) lanczos(x)
#define E(x) sqrt(x)

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

    // Map destination pixel to continuous source coordinate
    float2 uv       = (float2(outPos.x - dstX, outPos.y - dstY) + 0.5)
                      / float2(dstW, dstH);
    float2 inputPos = uv * float2(srcWidth, srcHeight);

    float2 pt = 1.0 / float2(srcWidth, srcHeight);
    float2 pp = inputPos - 0.5;
    float2 p0 = floor(pp);
    float2 f  = pp - p0;

    // Top-left of the 4x4 sampling window (indices p0 ... p0+3)
    float2 s = p0 * pt;

    // Separable Lanczos-2 weights for offsets -1, 0, +1, +2
    float4 wx = float4(K(1 + f.x), K(f.x), K(1 - f.x), K(2 - f.x));
    float4 wy = float4(K(1 + f.y), K(f.y), K(1 - f.y), K(2 - f.y));
    wx /= dot(wx, 1.0);
    wy /= dot(wy, 1.0);

    float3 l[4][4];
    float3 vmin = 1e6, vmax = -1e6;
    float3 q3;

    #define L(x) (q3 = (x), vmin = min(vmin, q3), vmax = max(vmax, q3), q3)

    // 4x4 Gather convolution
    for (int y = 0; y < 4; y += 2)
    {
        for (int x = 0; x < 4; x += 2)
        {
            float2 t = s + float2(x, y) * pt;

            float4 r_raw = InputTex.GatherRed  (PointSampler, t);
            float4 g_raw = InputTex.GatherGreen(PointSampler, t);
            float4 b_raw = InputTex.GatherBlue (PointSampler, t);

            // Implicit linear-light: square during gather
            float4 r = r_raw * r_raw;
            float4 g = g_raw * g_raw;
            float4 b = b_raw * b_raw;

            // Gather return order: .w = top-left, .z = top-right,
            //                      .x = bottom-left, .y = bottom-right
            l[y + 0][x + 0] = L(float3(r.w, g.w, b.w));
            l[y + 0][x + 1] = L(float3(r.z, g.z, b.z));
            l[y + 1][x + 0] = L(float3(r.x, g.x, b.x));
            l[y + 1][x + 1] = L(float3(r.y, g.y, b.y));
        }
    }

    // Apply Lanczos weights in y, then x
    float3 v = mul(wy, float4x3(
        mul(wx, float4x3(l[0][0], l[0][1], l[0][2], l[0][3])),
        mul(wx, float4x3(l[1][0], l[1][1], l[1][2], l[1][3])),
        mul(wx, float4x3(l[2][0], l[2][1], l[2][2], l[2][3])),
        mul(wx, float4x3(l[3][0], l[3][1], l[3][2], l[3][3]))
    ));

    // Hard anti-ringing clamp (full 4x4 neighborhood)
    v = clamp(v, vmin, vmax);

    // Linear-light output: sqrt to return to sRGB
    OutputTex[outPos] = float4(E(v), 1.0);
}