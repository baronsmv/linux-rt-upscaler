// =============================================================================
//  Adaptive Lanczos Resampler - single-pass, high-quality 2D convolution
//  Based on Magpie Lanczos2 (CC0-1.0), extended with:
//    - Adaptive kernel radius for perfect anti-aliasing when downscaling
//    - Thread-group shared-memory cache for the common upscaling case (radius 2)
//    - Direct-load path for larger (downscaling) radii
//    - Soft anti-ringing clamp (user-adjustable)
//    - Linear-light processing toggle (on by default)
//
//  Radius adaptation:
//    upscaling   (scale ≥ 1.0)   -> radius 2  (sharp Lanczos2)
//    downscaling (scale < 1.0)   -> radius = ceil(2.0 / min(scale)), capped at 6
//
//    Examples:
//      1440p -> 4K   (1.5x)   -> radius 2
//      4K -> 1440p    (0.75x)  -> radius 3  (proper anti-aliasing)
//      8K -> 1080p    (0.5x)   -> radius 4
//
//  Dispatch dimensions:
//    groupsX = ceil(dstTotalWidth  / 16)
//    groupsY = ceil(dstTotalHeight / 16)
//
//  Textures:
//    t0 - InputTex   (source, SRV)
//    u0 - OutputTex  (destination, UAV)
//
//  Constant buffer (must match Python-side packing):
//    float4 bgColor;           // background colour (RGBA)
//    uint   srcWidth, srcHeight;     // source texture dimensions
//    uint   dstTotalWidth, dstTotalHeight;   // full output dimensions
//    int    dstX, dstY, dstW, dstH;          // destination rectangle
//    float  blur;                          // kernel softness (1.0 = standard)
//    float  antiringStrength;             // 0 = off, 1 = full hard clamp
//    bool   linearLight;                  // true = process in linear light
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
    float  antiringStrength;
    bool   linearLight;
}

// ==================================================================
//  Kernel functions
// ==================================================================

// Windowed sinc (Lanczos) kernel.  `radius` controls the support width.
float lanczos(float x, float radius)
{
    float s = radius / blur;               // scale factor
    float kx = 3.1415926535897932 * s * x;
    float wx = 0.5 * kx;
    return x < 1e-5 ? 1.0 : sin(kx) * sin(wx) / (x * x);
}

// ==================================================================
//  Helper functions
// ==================================================================

// Map an output pixel (in screen coordinates) to continuous source coordinates.
float2 getSourceCoord(int ox, int oy)
{
    float2 uv = (float2(ox - dstX, oy - dstY) + 0.5) / float2(dstW, dstH);
    return uv * float2(srcWidth, srcHeight);
}

// Determine the filter radius from the scale factor.
int getRadius(float scale)
{
    if (scale >= 1.0)
        return 2;                              // sharp upscaling
    return min(6, int(ceil(2.0 / scale)));     // wider kernel for downscaling
}

// ==================================================================
//  Thread-group shared memory (used only for radius 2, the common case)
//
//  We cache a 20x20 source region because:
//    - thread group is 16x16
//    - max filter radius is 2 on each side
//    - 16 + 2*2 = 20
// ==================================================================
#define GROUP_X 16
#define GROUP_Y 16
#define CACHE_DIM 20
groupshared float3 g_cache[CACHE_DIM][CACHE_DIM];

// ==================================================================
//  Main entry point
// ==================================================================
[numthreads(GROUP_X, GROUP_Y, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 outPos = dtid.xy;

    // ---- Bounds check --------------------------------------------
    if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight)
        return;
    int x = int(outPos.x);
    int y = int(outPos.y);
    if (x < dstX || x >= dstX + dstW || y < dstY || y >= dstY + dstH)
    {
        OutputTex[outPos] = bgColor;
        return;
    }

    // ---- Compute source coordinates and determine filter radius ----
    float2 srcCoord = getSourceCoord(x, y);
    float2 scale    = float2(dstW, dstH) / float2(srcWidth, srcHeight);
    float  minScale = min(scale.x, scale.y);
    int    radius   = getRadius(minScale);

    // ==================================================================
    //  PATH A - fast shared-memory path for upscaling (radius == 2)
    // ==================================================================
    if (radius == 2)
    {
        // ----------------------------------------------------------------
        //  1. Determine the source rectangle needed by the whole thread group
        // ----------------------------------------------------------------
        // The group covers a 16x16 block of output pixels.  We take the
        // four corners of that block, map them to source coordinates,
        // and build the axis-aligned bounding box enlarged by the radius.
        uint2 groupBase = (outPos / uint2(GROUP_X, GROUP_Y)) * uint2(GROUP_X, GROUP_Y);
        uint2 groupEnd  = min(groupBase + uint2(GROUP_X - 1, GROUP_Y - 1),
                              uint2(dstTotalWidth - 1, dstTotalHeight - 1));

        // We only consider pixels inside the destination rectangle.
        int2 outMin = max(int2(groupBase), int2(dstX, dstY));
        int2 outMax = min(int2(groupEnd),  int2(dstX + dstW - 1, dstY + dstH - 1));

        if (outMin.x <= outMax.x && outMin.y <= outMax.y)
        {
            // Map the four corners to source space, then expand by radius.
            float2 srcTL = getSourceCoord(outMin.x, outMin.y);
            float2 srcTR = getSourceCoord(outMax.x, outMin.y);
            float2 srcBL = getSourceCoord(outMin.x, outMax.y);
            float2 srcBR = getSourceCoord(outMax.x, outMax.y);

            float2 srcMinF = min(min(srcTL, srcTR), min(srcBL, srcBR)) - 0.5f - float(radius);
            float2 srcMaxF = max(max(srcTL, srcTR), max(srcBL, srcBR)) - 0.5f + float(radius);

            int2 srcMin = int2(floor(srcMinF));
            int2 srcMax = int2(floor(srcMaxF));
            srcMin = max(srcMin, int2(0, 0));
            srcMax = min(srcMax, int2(srcWidth - 1, srcHeight - 1));
            int2 srcExtent = srcMax - srcMin + 1;

            // ----------------------------------------------------------------
            //  2. Load the required source texels into shared memory
            // ----------------------------------------------------------------
            uint2 localId = dtid.xy % uint2(GROUP_X, GROUP_Y);
            uint  localIdx = localId.y * GROUP_X + localId.x;
            uint  totalTexels = uint(srcExtent.x * srcExtent.y);

            // Each thread loads one or more texels in a strided loop.
            for (uint i = localIdx; i < totalTexels; i += GROUP_X * GROUP_Y)
            {
                int lx = srcMin.x + int(i % uint(srcExtent.x));
                int ly = srcMin.y + int(i / uint(srcExtent.x));
                g_cache[ly - srcMin.y][lx - srcMin.x] = InputTex.Load(int3(lx, ly, 0)).rgb;
            }
            GroupMemoryBarrierWithGroupSync();

            // ----------------------------------------------------------------
            //  3. Convolve this thread’s output pixel using the cache
            // ----------------------------------------------------------------
            float3 accum = 0.0;
            float  weightSum = 0.0;
            float3 vmin = 1e6, vmax = -1e6;
            float2 center = srcCoord - 0.5;
            int2   base   = int2(floor(center));

            for (int dy = -radius; dy <= radius; ++dy)
            {
                for (int dx = -radius; dx <= radius; ++dx)
                {
                    int2 sp = base + int2(dx, dy);
                    sp = clamp(sp, srcMin, srcMax);   // stay inside the cache bounds
                    float3 color = g_cache[sp.y - srcMin.y][sp.x - srcMin.x];

                    // Apply linear light if enabled
                    float3 val = linearLight ? color * color : color;

                    // 2D separable weight = wx * wy
                    float w = lanczos(float(dx) - (center.x - float(base.x)), float(radius))
                            * lanczos(float(dy) - (center.y - float(base.y)), float(radius));

                    accum     += val * w;
                    weightSum += w;
                    vmin = min(vmin, val);
                    vmax = max(vmax, val);
                }
            }

            float3 v = accum / weightSum;

            // Soft anti-ringing clamp
            v = clamp(v, lerp(v, vmin, antiringStrength), lerp(v, vmax, antiringStrength));

            // Convert back from linear light if necessary
            if (linearLight)
                v = sqrt(v);

            OutputTex[outPos] = float4(v, 1.0);
            return;
        }
        // If no valid destination pixels inside the group (shouldn't happen),
        // fall through to the direct path.
    }

    // ==================================================================
    //  PATH B - direct per-pixel convolution for downscaling (radius > 2)
    // ==================================================================
    float3 accum     = 0.0;
    float  weightSum = 0.0;
    float3 vmin      = 1e6, vmax = -1e6;
    float2 center    = srcCoord - 0.5;
    int2   base      = int2(floor(center));

    for (int dy = -radius; dy <= radius; ++dy)
    {
        for (int dx = -radius; dx <= radius; ++dx)
        {
            int2 sp = base + int2(dx, dy);
            sp = clamp(sp, int2(0, 0), int2(srcWidth - 1, srcHeight - 1));
            float3 color = InputTex.Load(int3(sp.x, sp.y, 0)).rgb;

            float3 val = linearLight ? color * color : color;
            float w = lanczos(float(dx) - (center.x - float(base.x)), float(radius))
                    * lanczos(float(dy) - (center.y - float(base.y)), float(radius));

            accum     += val * w;
            weightSum += w;
            vmin = min(vmin, val);
            vmax = max(vmax, val);
        }
    }

    float3 v = accum / weightSum;

    // Soft anti-ringing clamp
    v = clamp(v, lerp(v, vmin, antiringStrength), lerp(v, vmax, antiringStrength));

    // Convert back from linear light if necessary
    if (linearLight)
        v = sqrt(v);

    OutputTex[outPos] = float4(v, 1.0);
}