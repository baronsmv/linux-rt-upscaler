// =============================================================================
// Anisotropic Adaptive Lanczos - The Final Refinement
//  - Independent X/Y scaling for perfect aspect-ratio preservation
//  - Clamped integer-precision mapping (No pixelation)
//  - Enhanced Anti-Ringing for Visual Novel text boxes
// =============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

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

// Optimized Lanczos math with pre-calculated PI
#define PI 3.14159265358979
float lanczos(float x, float r)
{
    if (x < 1e-4) return 1.0;
    if (x >= r) return 0.0;
    float pi_x = PI * x;
    return (r * sin(pi_x) * sin(pi_x / r)) / (pi_x * pi_x);
}

[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 outPos = dtid.xy;
    if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight) return;

    // Scissor test
    if (int(outPos.x) < dstX || int(outPos.x) >= dstX + dstW ||
        int(outPos.y) < dstY || int(outPos.y) >= dstY + dstH) {
        OutputTex[outPos] = bgColor;
        return;
    }

    // 1. Calculate Anisotropic Scale Factors
    float scaleX = float(dstW) / float(srcWidth);
    float scaleY = float(dstH) / float(srcHeight);

    // Adaptive radius per axis: prevents blur on one axis and jaggies on the other
    float rx = (scaleX >= 1.0) ? 2.0 : ceil(2.0 / scaleX);
    float ry = (scaleY >= 1.0) ? 2.0 : ceil(2.0 / scaleY);

    int irx = int(rx);
    int iry = int(ry);

    // 2. Map coordinates with half-pixel offset correction
    float2 uv = (float2(outPos.x - dstX, outPos.y - dstY) + 0.5) / float2(dstW, dstH);
    float2 inputPos = uv * float2(srcWidth, srcHeight);
    float2 pp = inputPos - 0.5;
    int2 p0 = int2(floor(pp));
    float2 f = pp - float2(p0);

    float3 accum = 0.0;
    float weightSum = 0.0;

    // Anti-ringing bounds (initialize to very high/low)
    float3 vmin = 1e6, vmax = -1e6;

    // 3. Anisotropic Sampling Loop
    for (int iy = -iry + 1; iy <= iry; iy++)
    {
        float wy = lanczos(abs(float(iy) - f.y), ry);

        for (int ix = -irx + 1; ix <= irx; ix++)
        {
            int2 sc = clamp(p0 + int2(ix, iy), int2(0, 0), int2(srcWidth - 1, srcHeight - 1));
            float3 color = InputTex.Load(int3(sc, 0)).rgb;

            float3 val = linearLight ? color * color : color;
            float wx = lanczos(abs(float(ix) - f.x), rx);
            float w = wx * wy;

            accum += val * w;
            weightSum += w;

            // Only use the core 2x2 for ringing constraints (Keeps text sharper)
            if (abs(ix) <= 1 && abs(iy) <= 1) {
                vmin = min(vmin, val);
                vmax = max(vmax, val);
            }
        }
    }

    // 4. Final Assembly
    float3 v = accum / (weightSum + 1e-7);

    // Soft Anti-Ringing (Magpie Style)
    v = clamp(v, lerp(v, vmin, antiringStrength), lerp(v, vmax, antiringStrength));

    if (linearLight) v = sqrt(max(v, 0.0));

    OutputTex[outPos] = float4(v, 1.0);
}