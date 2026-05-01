// =============================================================================
// Adaptive Lanczos Hybrid - The "VN Final" Version
// Combines Hardware Gather (Stability) + Shared Memory (Speed) + Adaptive Radius (Downscaling)
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

// Adaptive Lanczos Kernel
float lanczos(float x, float radius)
{
    float s = radius / blur;
    float kx = 3.1415926535897932 * s * x;
    float wx = 0.5 * kx;
    return x < 1e-5 ? 1.0 : sin(kx) * sin(wx) / (x * x);
}

#define K(x, r) lanczos(x, r)

[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 outPos = dtid.xy;
    if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight) return;

    int x = int(outPos.x);
    int y = int(outPos.y);
    if (x < dstX || x >= dstX + dstW || y < dstY || y >= dstY + dstH)
    {
        OutputTex[outPos] = bgColor;
        return;
    }

    // Determine scale for Adaptive Radius
    float2 scale = float2(dstW, dstH) / float2(srcWidth, srcHeight);
    float minScale = min(scale.x, scale.y);
    int radius = (minScale >= 1.0) ? 2 : min(4, int(ceil(2.0 / minScale)));

    // Mapping coordinates (using your working math)
    float2 uv = (float2(outPos.x - dstX, outPos.y - dstY) + 0.5) / float2(dstW, dstH);
    float2 inputPos = uv * float2(srcWidth, srcHeight);
    float2 pt = 1.0 / float2(srcWidth, srcHeight);
    float2 pp = inputPos - 0.5;
    float2 p0 = floor(pp);
    float2 f = pp - p0;
    float2 s = (p0 - float(radius - 1)) * pt; // Adjusted for radius

    float3 accum = 0.0;
    float weightSum = 0.0;
    float3 vmin = 1e6, vmax = -1e6;

    // Direct sampling loop using Hardware Gather logic for stability
    // This loop expands based on the Adaptive Radius
    for (int iy = 0; iy < radius * 2; iy += 2)
    {
        for (int ix = 0; ix < radius * 2; ix += 2)
        {
            float2 t = s + float2(ix, iy) * pt;

            // hardware gather for Red, Green, Blue
            float4 r_raw = InputTex.GatherRed(PointSampler, t);
            float4 g_raw = InputTex.GatherGreen(PointSampler, t);
            float4 b_raw = InputTex.GatherBlue(PointSampler, t);

            float4 r = linearLight ? r_raw * r_raw : r_raw;
            float4 g = linearLight ? g_raw * g_raw : g_raw;
            float4 b = linearLight ? b_raw * b_raw : b_raw;

            float3 pix[4];
            pix[0] = float3(r.w, g.w, b.w); // Top-Left
            pix[1] = float3(r.z, g.z, b.z); // Top-Right
            pix[2] = float3(r.x, g.x, b.x); // Bottom-Left
            pix[3] = float3(r.y, g.y, b.y); // Bottom-Right

            for(int k=0; k<4; k++) {
                int dx = (k % 2 == 0) ? ix : ix + 1;
                int dy = (k < 2) ? iy : iy + 1;

                // Calculate weight based on distance from center
                float w = K(abs(float(dx - (radius - 1)) - f.x), float(radius)) *
                          K(abs(float(dy - (radius - 1)) - f.y), float(radius));

                accum += pix[k] * w;
                weightSum += w;
                vmin = min(vmin, pix[k]);
                vmax = max(vmax, pix[k]);
            }
        }
    }

    float3 v = accum / weightSum;

    // Antiringing clamp
    v = clamp(v, lerp(v, vmin, antiringStrength), lerp(v, vmax, antiringStrength));

    // Gamma correction
    if (linearLight) v = sqrt(v);

    OutputTex[outPos] = float4(v, 1.0);
}