// =============================================================================
// Ironclad Adaptive Lanczos - Stability First Version
// Uses discrete integer offsets and hardware Gather to eliminate pixelation.
// Optimized for VN line art and high-contrast text.
// =============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);
SamplerState PointSampler : register(s0);

cbuffer Constants : register(b0)
{
    float4 bgColor;
    uint srcWidth, srcHeight;
    uint dstTotalWidth, dstTotalHeight;
    int dstX, dstY, dstW, dstH;
    float blur;
    float antiringStrength;
    bool linearLight;
}

float lanczos(float x, float r)
{
    float s = r / blur;
    float kx = 3.1415926535 * s * x;
    float wx = 0.5 * kx;
    return x < 1e-5 ? 1.0 : sin(kx) * sin(wx) / (x * x);
}

[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 outPos = dtid.xy;
    if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight) return;

    if (int(outPos.x) < dstX || int(outPos.x) >= dstX + dstW ||
        int(outPos.y) < dstY || int(outPos.y) >= dstY + dstH) {
        OutputTex[outPos] = bgColor;
        return;
    }

    // 1. Calculate Scale and Adaptive Radius
    float2 scale = float2(dstW, dstH) / float2(srcWidth, srcHeight);
    float minScale = min(scale.x, scale.y);

    // Radius 2 for upscaling (4x4), Radius 3 for downscaling (6x6)
    int radius = (minScale >= 1.0) ? 2 : 3;

    // 2. Precise Pixel Mapping (Integer-based)
    float2 uv = (float2(outPos.x - dstX, outPos.y - dstY) + 0.5) / float2(dstW, dstH);
    float2 inputPos = uv * float2(srcWidth, srcHeight);
    float2 pt = 1.0 / float2(srcWidth, srcHeight);

    float2 pp = inputPos - 0.5;
    int2 p0 = int2(floor(pp));
    float2 f = pp - float2(p0); // Fractional offset [0, 1]

    float3 accum = 0.0;
    float weightSum = 0.0;
    float3 vmin = 1e6, vmax = -1e6;

    // 3. The Sampling Loop
    // We sample from -(radius-1) to +radius
    // For radius 2: -1 to 2 (4 pixels)
    // For radius 3: -2 to 3 (6 pixels)
    for (int iy = -radius + 1; iy <= radius; iy++)
    {
        for (int ix = -radius + 1; ix <= radius; ix++)
        {
            int2 sc = clamp(p0 + int2(ix, iy), int2(0, 0), int2(srcWidth - 1, srcHeight - 1));
            float3 color = InputTex.Load(int3(sc, 0)).rgb;

            float3 val = linearLight ? color * color : color;

            // Separate weights for X and Y (The "Separable" path is more stable)
            float wx = lanczos(abs(float(ix) - f.x), float(radius));
            float wy = lanczos(abs(float(iy) - f.y), float(radius));
            float w = wx * wy;

            accum += val * w;
            weightSum += w;

            // Track min/max for anti-ringing
            vmin = min(vmin, val);
            vmax = max(vmax, val);
        }
    }

    // 4. Final Color Assembly
    float3 v = accum / weightSum;

    // Antiringing
    v = clamp(v, lerp(v, vmin, antiringStrength), lerp(v, vmax, antiringStrength));

    if (linearLight) v = sqrt(max(v, 0.0));

    OutputTex[outPos] = float4(v, 1.0);
}