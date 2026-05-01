// Lanczos2 with antiringing - compute shader version
// Adapted from Magpie effect by funnyplanter (CC0-1.0)
// Optimised: thread-group shared memory for texel reuse,
//            fallback to original path when source region too large.

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
    float blur;             // kernel width (1.0 = standard Lanczos2)
    float antiringStrength; // 0 = off, 1 = full hard clamp
    bool linearLight;       // true = process in linear light
};

// ==================================================================
//  Kernel helpers
// ==================================================================

float lanczos(float x)
{
    float s = 1.0 / blur;
    float kx = 3.1415926535897932 * s * x;
    float wx = 0.5 * kx;
    return x < 1e-5 ? 1.0 : sin(kx) * sin(wx) / (x * x);
}

float catmullRom(float x)
{
    float ax = abs(x);
    if (ax < 1.0)
        return 1.5 * ax * ax * ax - 2.5 * ax * ax + 1.0;
    else if (ax < 2.0)
        return -0.5 * ax * ax * ax + 2.5 * ax * ax - 4.0 * ax + 2.0;
    return 0.0;
}

#define K(x) lanczos(x)
#define C(x) catmullRom(x)

// ------------------------------------------------------------------
// Helper: return the integer base pixel (p0) for a given output pixel
// ------------------------------------------------------------------
int2 getSampleBase(int ox, int oy)
{
    if (ox < dstX || ox >= dstX + dstW || oy < dstY || oy >= dstY + dstH)
        return int2(-1000000, -1000000);
    float2 uv = (float2(ox - dstX, oy - dstY) + 0.5) / float2(dstW, dstH);
    float2 inputPos = uv * float2(srcWidth, srcHeight);
    return int2(floor(inputPos - 0.5));
}

// ==================================================================
//  Shared‑memory cache
// ==================================================================
#define CACHE_DIM 19
groupshared float3 g_cache[CACHE_DIM][CACHE_DIM];

[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 outPos = dtid.xy;

    // ------------------------------------------------------------------
    //  Determine whether shared‑memory path is usable
    // ------------------------------------------------------------------
    uint2 groupBase = (outPos / 16) * 16;
    uint2 groupEnd  = min(groupBase + 15, uint2(dstTotalWidth - 1, dstTotalHeight - 1));

    int2 outMin = max(groupBase, int2(dstX, dstY));
    int2 outMax = min(groupEnd, int2(dstX + dstW - 1, dstY + dstH - 1));
    bool anyValid = (outMin.x <= outMax.x && outMin.y <= outMax.y);

    int2 srcMin, srcMax;
    int  srcW = 0, srcH = 0;
    bool useCache = false;

    if (anyValid)
    {
        int2 p00 = getSampleBase(outMin.x, outMin.y);
        int2 p10 = getSampleBase(outMax.x, outMin.y);
        int2 p01 = getSampleBase(outMin.x, outMax.y);
        int2 p11 = getSampleBase(outMax.x, outMax.y);

        int2 pMin = min(min(p00, p10), min(p01, p11));
        int2 pMax = max(max(p00, p10), max(p01, p11));
        srcMin = max(pMin - int2(1, 1), int2(0, 0));
        srcMax = min(pMax + int2(2, 2), int2(srcWidth - 1, srcHeight - 1));
        srcW = srcMax.x - srcMin.x + 1;
        srcH = srcMax.y - srcMin.y + 1;
        useCache = (srcW <= CACHE_DIM && srcH <= CACHE_DIM);
    }

    // ==================================================================
    //  SHARED‑MEMORY PATH
    // ==================================================================
    if (useCache)
    {
        // Load texels into groupshared memory
        uint2 localId = dtid.xy % 16;
        uint localIndex = localId.y * 16 + localId.x;
        uint totalTexels = uint(srcW * srcH);

        for (uint i = localIndex; i < totalTexels; i += 256)
        {
            int lx = srcMin.x + int(i % uint(srcW));
            int ly = srcMin.y + int(i / uint(srcW));
            g_cache[ly - srcMin.y][lx - srcMin.x] = InputTex.Load(int3(lx, ly, 0)).rgb;
        }
        GroupMemoryBarrierWithGroupSync();

        // ---- Per‑pixel processing ------------------------------------
        if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight)
            return;
        int x = int(outPos.x);
        int y = int(outPos.y);
        if (x < dstX || x >= dstX + dstW || y < dstY || y >= dstY + dstH)
        {
            OutputTex[outPos] = bgColor;
            return;
        }

        // Convert output coordinates back to source pixel base + fractional offset
        float2 uv = (float2(outPos.x - dstX, outPos.y - dstY) + 0.5) / float2(dstW, dstH);
        float2 inputPos = uv * float2(srcWidth, srcHeight);
        int2 p0 = int2(floor(inputPos - 0.5));
        float2 f = float2(inputPos - 0.5 - float2(p0));

        // Gather 4×4 neighbourhood
        float3 l[4][4];
        float3 vmin = 1e6, vmax = -1e6;
        [unroll] for (int dy = 0; dy < 4; ++dy)
        {
            [unroll] for (int dx = 0; dx < 4; ++dx)
            {
                int sx = p0.x + dx - 1;
                int sy = p0.y + dy - 1;
                float3 raw = g_cache[sy - srcMin.y][sx - srcMin.x];
                float3 val = linearLight ? raw * raw : raw;
                vmin = min(vmin, val);
                vmax = max(vmax, val);
                l[dy][dx] = val;
            }
        }

        // Choose kernel
        float scaleX = float(dstW) / float(srcWidth);
        float scaleY = float(dstH) / float(srcHeight);
        bool useLanczos = (blur != 1.0) || (scaleX >= 1.6 && scaleY >= 1.6);

        float4 wx, wy;
        if (useLanczos)
        {
            wx = float4(K(1 + f.x), K(0 + f.x), K(1 - f.x), K(2 - f.x));
            wy = float4(K(1 + f.y), K(0 + f.y), K(1 - f.y), K(2 - f.y));
        }
        else
        {
            wx = float4(C(1 + f.x), C(0 + f.x), C(1 - f.x), C(2 - f.x));
            wy = float4(C(1 + f.y), C(0 + f.y), C(1 - f.y), C(2 - f.y));
        }
        wx /= dot(wx, 1.0);
        wy /= dot(wy, 1.0);

        // Weighted sum
        float3 v = mul(wy, float4x3(
            mul(wx, float4x3(l[0][0], l[0][1], l[0][2], l[0][3])),
            mul(wx, float4x3(l[1][0], l[1][1], l[1][2], l[1][3])),
            mul(wx, float4x3(l[2][0], l[2][1], l[2][2], l[2][3])),
            mul(wx, float4x3(l[3][0], l[3][1], l[3][2], l[3][3]))
        ));

        // Soft anti‑ringing
        float3 vclamped = clamp(v, lerp(v, vmin, antiringStrength),
                                   lerp(v, vmax, antiringStrength));
        if (linearLight)
            vclamped = sqrt(vclamped);

        OutputTex[outPos] = float4(vclamped, 1.0);
        return;
    }

    // ==================================================================
    //  FALLBACK PATH
    // ==================================================================
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
    float2 s = p0 * pt;                                           // normalized coordinate of top-left of 4x4 neighborhood

    // Choose kernel
    float scaleX = float(dstW) / float(srcWidth);
    float scaleY = float(dstH) / float(srcHeight);
    bool useLanczos = (blur != 1.0) || (scaleX >= 1.6 && scaleY >= 1.6);

    float4 wx, wy;
    if (useLanczos)
    {
        wx = float4(K(1 + f.x), K(0 + f.x), K(1 - f.x), K(2 - f.x));
        wy = float4(K(1 + f.y), K(0 + f.y), K(1 - f.y), K(2 - f.y));
    }
    else
    {
        wx = float4(C(1 + f.x), C(0 + f.x), C(1 - f.x), C(2 - f.x));
        wy = float4(C(1 + f.y), C(0 + f.y), C(1 - f.y), C(2 - f.y));
    }
    wx /= dot(wx, 1.0);
    wy /= dot(wy, 1.0);

    float3 l[4][4];
    float3 vmin = 1e6, vmax = -1e6;
    float3 q3;

    #define L(x) (q3 = (x), vmin = min(vmin, q3), vmax = max(vmax, q3), q3)

    for (int iy = 0; iy < 4; iy += 2)
    {
        for (int ix = 0; ix < 4; ix += 2)
        {
            float2 t = s + float2(ix, iy) * pt;

            float4 r_raw = InputTex.GatherRed(PointSampler, t);
            float4 g_raw = InputTex.GatherGreen(PointSampler, t);
            float4 b_raw = InputTex.GatherBlue(PointSampler, t);

            float4 r = linearLight ? r_raw * r_raw : r_raw;
            float4 g = linearLight ? g_raw * g_raw : g_raw;
            float4 b = linearLight ? b_raw * b_raw : b_raw;

            l[iy + 0][ix + 0] = L(float3(r.w, g.w, b.w));
            l[iy + 0][ix + 1] = L(float3(r.z, g.z, b.z));
            l[iy + 1][ix + 0] = L(float3(r.x, g.x, b.x));
            l[iy + 1][ix + 1] = L(float3(r.y, g.y, b.y));
        }
    }

    // Apply Lanczos weights in y then x direction
    float3 v = mul(wy, float4x3(
        mul(wx, float4x3(l[0][0], l[0][1], l[0][2], l[0][3])),
        mul(wx, float4x3(l[1][0], l[1][1], l[1][2], l[1][3])),
        mul(wx, float4x3(l[2][0], l[2][1], l[2][2], l[2][3])),
        mul(wx, float4x3(l[3][0], l[3][1], l[3][2], l[3][3]))
    ));

    // Soft anti‑ringing
    float3 vclamped = clamp(v, lerp(v, vmin, antiringStrength),
                               lerp(v, vmax, antiringStrength));
    if (linearLight)
        vclamped = sqrt(vclamped);

    OutputTex[outPos] = float4(vclamped, 1.0);
}