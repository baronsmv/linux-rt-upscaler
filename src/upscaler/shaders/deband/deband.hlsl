// =============================================================================
//  Anisotropic Stochastic Debanding - Compute Shader
//  -------------------------------------------------
//  Removes colour banding artefacts that occasionally survive AI upscaling,
//  particularly visible in smooth gradients (skies, fog, flat backgrounds).
//
//  How it works:
//    - Four pseudo-random sample points are chosen per pixel, varying in angle
//      and distance up to a strength-controlled radius (max 16 pixels).
//    - Each sample is compared to the centre pixel - if the difference is small
//      (band-like), it contributes to a weighted average; large differences
//      (real edges) are ignored.
//    - A small amount of high-frequency dither (0.5/255) is injected per frame,
//      breaking any remaining spatial correlation and preventing the GPU’s
//      output pipeline from re-banding during the final 8-bit conversion.
//    - The result is clamped to the local min/max of all the samples,
//      guaranteeing no overshoot or haloing.
//
//  Features:
//    - Linear-light processing - samples squared before filtering, sqrt after,
//      for perceptually uniform smoothing.
//    - Dynamic 4-tap sampling - breaks band structures statistically.
//    - Edge-preserving threshold - line art and text remain sharp.
//    - Grain / dither injection - eliminates “shimmer” or static patterns
//      when strength is high.
//    - Frame-index parameter - to avoid static noise, pass an increasing
//      integer each frame (e.g., frame count).
//
//  Workgroup size: 16x16 threads.
//  Dispatch:
//    groupsX = ceil(dstWidth  / 16)
//    groupsY = ceil(dstHeight / 16)
//
//  Tuning:
//      strength = 0.0   ->  pass-through (original image)
//      strength = 0.3   ->  subtle debanding
//      strength = 0.6   ->  strong, use with grain for best results
//      strength = 1.0   ->  maximum (may soften very fine textures)
//
//  Constant buffer layout (must match Python struct packing):
//      float debandStrength;    // 0.0 - 1.0
//      uint  dstWidth;
//      uint  dstHeight;
//      uint  frameIndex;        // optional frame counter (0-based)
//
//  Integration:
//    - Place between CuNNy AI upscale and Lanczos scaling.
//    - Input and output textures must be separate (avoid read-after-write
//      hazards when using an intermediate texture).
//    - Pass an incrementing `frameIndex` from the pipeline to get
//      temporally varying dither.
//
//  Adapted from libplacebo / f3kdb for linux-rt-upscaler.
// =============================================================================

Texture2D<float4> InputTex  : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

cbuffer Constants : register(b0)
{
    float debandStrength;       // 0.0 - 1.0
    uint  dstWidth;
    uint  dstHeight;
    uint  frameIndex;           // increment every frame for dynamic dither
}

// -----------------------------------------------------------------------------
//  High-quality pseudo-random number generator (PCG-ish)
// -----------------------------------------------------------------------------
float Hash(uint2 seed)
{
    return frac(sin(dot(float2(seed), float2(12.9898, 78.233))) * 43758.5453);
}

// -----------------------------------------------------------------------------
//  Load a pixel and convert to approximate linear light (sRGB -> linear)
// -----------------------------------------------------------------------------
float3 LoadPixelLinear(int2 coord)
{
    coord = clamp(coord, int2(0, 0), int2(dstWidth - 1, dstHeight - 1));
    float3 col = InputTex.Load(int3(coord, 0)).rgb;
    return col * col;
}

// =============================================================================
//  Main kernel
// =============================================================================
[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 pos = dtid.xy;
    if (pos.x >= dstWidth || pos.y >= dstHeight)
        return;

    // ---- 1. Centre pixel (linear light) --------------------------------------
    float3 center = LoadPixelLinear(pos);

    // ---- 2. Pseudo-random parameters from hash --------------------------------
    //  seed unique per pixel and frame -> no temporal correlation of artefacts.
    float seed = Hash(pos + frameIndex);

    // ---- 3. Dynamic search radius -------------------------------------------
    //  Strength 0.0 -> radius 0, no debanding.
    //  Strength 1.0 -> radius up to 16 pixels (handles wide bands).
    float radius = debandStrength * 16.0;

    // ---- 4. Random angle and distance for first sample direction ------------
    float angle = seed * 6.283185f;               // [0, 2π)
    float2 dir  = float2(cos(angle), sin(angle));
    float  dist = seed * radius;

    // ---- 5. Four samples at orthogonal positions, at distance `dist` --------
    //  Two along the random direction, two perpendicular.
    float3 tap1 = LoadPixelLinear(pos + int2(dir * dist));
    float3 tap2 = LoadPixelLinear(pos - int2(dir * dist));
    float3 tap3 = LoadPixelLinear(pos + int2(float2(-dir.y, dir.x) * dist));
    float3 tap4 = LoadPixelLinear(pos - int2(float2(-dir.y, dir.x) * dist));

    // ---- 6. Edge-aware blend weights -----------------------------------------
    //  The threshold separates “banding” (small difference) from “real edge”
    //  (large difference).  The formula is scaled by strength, with a
    //  minimum safety margin of 2/255 (≈0.0078 in linear).
    float3 diff1 = abs(center - tap1);
    float3 diff2 = abs(center - tap2);
    float3 diff3 = abs(center - tap3);
    float3 diff4 = abs(center - tap4);

    float3 threshold = (debandStrength * 0.1f) + (2.0f / 255.0f);

    float3 w1 = saturate(1.0f - diff1 / threshold);
    float3 w2 = saturate(1.0f - diff2 / threshold);
    float3 w3 = saturate(1.0f - diff3 / threshold);
    float3 w4 = saturate(1.0f - diff4 / threshold);

    // ---- 7. Weighted average (centre gets a small fixed weight) --------------
    //  This pulls the pixel towards the sampled neighbours when they are
    //  band-like, while preserving centre value when weights are zero.
    float3 avg = (tap1 * w1 + tap2 * w2 + tap3 * w3 + tap4 * w4) + (center * 0.1f);
    float3 weightSum = (w1 + w2 + w3 + w4) + 0.1f;
    float3 debanded = avg / weightSum;

    // ---- 8. Dither injection (0.5/255) ---------------------------------------
    //  Adds a tiny, temporally varying noise that masks any residual
    //  quantisation steps after the final 8-bit output.
    float grain = (seed - 0.5f) * (1.0f / 255.0f);
    debanded += grain * debandStrength;

    // ---- 9. Clamp to the local neighbourhood’s min/max -----------------------
    //  Prevents any overshoot that could create false edges or colour shifts.
    float3 minN = min(center, min(min(tap1, tap2), min(tap3, tap4)));
    float3 maxN = max(center, max(max(tap1, tap2), max(tap3, tap4)));
    debanded = clamp(debanded, minN, maxN);

    // ---- 10. Convert back to gamma space and write ---------------------------
    OutputTex[pos] = float4(sqrt(max(debanded, 0.0f)), 1.0f);
}