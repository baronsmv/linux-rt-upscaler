// Lanczos2 with antiringing – compute shader version
// Adapted from Magpie effect by funnyplanter (CC0‑1.0)

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);
SamplerState PointSampler : register(s0);

cbuffer Constants : register(b0)
{
    float4 bgColor;         // background color
    uint srcWidth;          // upscaled source width
    uint srcHeight;         // upscaled source height
    uint dstTotalWidth;     // physical window width
    uint dstTotalHeight;    // physical window height
    int dstX;               // rectangle top‑left X
    int dstY;               // rectangle top‑left Y
    int dstW;               // rectangle width
    int dstH;               // rectangle height
    float blur;
};

float lanczos(float x)
{
    float s = 1.0 / blur;
    float kx = 3.1415926535897932 * s * x;
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

    // Check if output pixel lies inside the destination rectangle
    int x = int(outPos.x);
    int y = int(outPos.y);
    if (x < dstX || x >= dstX + dstW || y < dstY || y >= dstY + dstH)
    {
        OutputTex[outPos] = bgColor;
        return;
    }

    // ----- map to input texture coordinates -----
    float2 uv = (float2(outPos.x - dstX, outPos.y - dstY) + 0.5) / float2(dstW, dstH);
    float2 inputPos = uv * float2(srcWidth, srcHeight);

    float2 pt = 1.0 / float2(srcWidth, srcHeight);               // texel size in normalized space
    float2 pp = inputPos - 0.5;                                   // align so integer positions are pixel centers
    float2 p0 = floor(pp);
    float2 f = pp - p0;                                           // fractional offset from that pixel center
    float2 s = p0 * pt;                                           // normalized coordinate of top‑left of 4x4 neighborhood

    // Lanczos weights for the 4x4 neighbourhood (x and y directions)
    float4 wx = float4(K(1 + f.x), K(0 + f.x), K(1 - f.x), K(2 - f.x));
    float4 wy = float4(K(1 + f.y), K(0 + f.y), K(1 - f.y), K(2 - f.y));
    wx /= dot(wx, 1.0);
    wy /= dot(wy, 1.0);

    float3 l[4][4];
    float3 vmin = 1e6, vmax = -1e6;
    float3 q3;
    float4 q4;   // used by the D() macro

    #define L(x) (q3 = (x), vmin = min(vmin, q3), vmax = max(vmax, q3), q3)

    // Sample the 4x4 region using four Gather calls (each returns a 2x2 block)
    for (int y = 0; y < 4; y += 2)
    {
        for (int x = 0; x < 4; x += 2)
        {
            float2 t = s + float2(x, y) * pt;

            float4 r_raw = InputTex.GatherRed(PointSampler, t);
            float4 g_raw = InputTex.GatherGreen(PointSampler, t);
            float4 b_raw = InputTex.GatherBlue(PointSampler, t);

            float4 r = r_raw * r_raw;
            float4 g = g_raw * g_raw;
            float4 b = b_raw * b_raw;

            l[y + 0][x + 0] = L(float3(r.w, g.w, b.w));
            l[y + 0][x + 1] = L(float3(r.z, g.z, b.z));
            l[y + 1][x + 0] = L(float3(r.x, g.x, b.x));
            l[y + 1][x + 1] = L(float3(r.y, g.y, b.y));
        }
    }

    // Apply Lanczos weights in y then x direction
    float3 v = mul(wy, float4x3(
        mul(wx, float4x3(l[0][0], l[0][1], l[0][2], l[0][3])),
        mul(wx, float4x3(l[1][0], l[1][1], l[1][2], l[1][3])),
        mul(wx, float4x3(l[2][0], l[2][1], l[2][2], l[2][3])),
        mul(wx, float4x3(l[3][0], l[3][1], l[3][2], l[3][3]))
    ));

    v = clamp(v, vmin, vmax);      // antiring clamping
    OutputTex[outPos] = float4(E(v), 1.0);
}