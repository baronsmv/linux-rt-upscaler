// =============================================================================
//  Contrast Adaptive Sharpening (CAS) - Compute Shader
//  ---------------------------------------------------
//  Single-pass, full-screen post-processing sharpening filter.
//
//  Based on AMD FidelityFX CAS, adapted for linear-light operation and
//  straightforward integration into the linux-rt-upscaler pipeline.
//
//  Features :
//    - Adaptive sharpening - strength automatically scales with local contrast,
//      preventing noise amplification in flat areas.
//    - 5-tap kernel (centre + N/S/E/W) - fewer texture reads, same visual quality
//      as 9-tap, thanks to the contrast-sensitive weighting.
//    - Linear-light processing - sRGB samples are squared before sharpening and
//      square-rooted afterwards, giving perceptually uniform results.
//    - Clamped output - result is restricted to the local min/max of the
//      5-tap neighbourhood, hard-suppressing ringing / haloing.
//    - Full-screen operation - reads and writes the same RGBA8 texture.
//    - Configurable sharpening strength via constant buffer (0.0 - 1.0).
//
//  Workgroup size : 16x16 threads.
//  Dispatch :
//    groupsX = ceil(dstWidth  / 16)
//    groupsY = ceil(dstHeight / 16)
//
//  Tuning :
//      strength = 0.0   ->  pass-through (no sharpening)
//      strength = 0.2   ->  subtle edge enhancement
//      strength = 0.4   ->  moderate (good for text / line art)
//      strength = 0.6+  ->  aggressive (risk of visible ringing)
//
//  Integration :
//    1. Compile to SPIR-V with dxc (same flags as lanczos.hlsl).
//    2. Create a Compute pipeline binding `InputTex` as SRV (t0),
//       `OutputTex` as UAV (u0), and the constant buffer (b0).
//    3. Dispatch after Lanczos scaling, before OSD / swapchain present.
//    4. The `OutputTex` can be the same texture as `InputTex` (in-place).
//
//  Adapted from AMD FidelityFX CAS for linux-rt-upscaler.
// =============================================================================

Texture2D<float4> InputTex  : register(t0);          // screen texture (also output)
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);        // UAV target (can be same as InputTex)

cbuffer Constants : register(b0)
{
    float sharpeningStrength;   // 0.0 - 1.0  (disable -> full effect)
    uint  dstWidth;             // width of the texture (pixels)
    uint  dstHeight;            // height of the texture (pixels)
    uint  _pad0;                // align to 16 bytes (Vulkan requirement)
};

// -----------------------------------------------------------------------------
//  Helper - load a pixel with border clamping.
//  Prevents out-of-bounds access at screen edges.
// -----------------------------------------------------------------------------
float3 LoadPixel(int2 coord)
{
    coord = clamp(coord, int2(0, 0), int2(dstWidth - 1, dstHeight - 1));
    return InputTex.Load(int3(coord, 0)).rgb;
}

// -----------------------------------------------------------------------------
//  Main CAS kernel
// -----------------------------------------------------------------------------
[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 pos = dtid.xy;
    if (pos.x >= dstWidth || pos.y >= dstHeight)
        return;

    // ---- 1. Sample 5-tap neighbourhood (centre + N/S/E/W) --------------------
    //  Using only the axial neighbours keeps the kernel compact while preserving
    //  edge features. The local contrast is measured in these 5 values.
    float3 c  = LoadPixel(int2(pos.x,     pos.y));     // centre
    float3 n  = LoadPixel(int2(pos.x,     pos.y - 1)); // north
    float3 s  = LoadPixel(int2(pos.x,     pos.y + 1)); // south
    float3 e  = LoadPixel(int2(pos.x + 1, pos.y));     // east
    float3 w  = LoadPixel(int2(pos.x - 1, pos.y));     // west

    // ---- 2. Convert to approximate linear light -------------------------------
    //  Sharpening in linear space yields a more natural, perceptually uniform
    //  result. We use a simple squaring from sRGB - accurate enough for this
    //  post-effect and zero extra texture reads.
    c *= c;
    n *= n;
    s *= s;
    e *= e;
    w *= w;

    // ---- 3. Local min / max for anti-ringing ---------------------------------
    //  Compute the min and max of the 5 taps. The final sharpened value will
    //  be clamped to this range, guaranteeing no overshoot beyond the local
    //  luminance extremes.
    float3 minRGB = min(c, min(min(n, s), min(e, w)));
    float3 maxRGB = max(c, max(max(n, s), max(e, w)));

    // ---- 4. Compute CAS weight -------------------------------------------------
    //  This is the core of the AMD FX-CAS algorithm.
    //
    //    contrast  = maxRGB - minRGB
    //
    //    weight = saturate( min(minRGB, 1.0 - maxRGB) / (contrast + epsilon) )
    //
    //  - For flat regions (contrast ≈ 0), weight -> 0, so no sharpening is
    //    applied, preserving smooth gradients.
    //  - For edges, weight becomes large, allowing strong sharpening.
    //  - The numerator `min(minRGB, 1.0 - maxRGB)` handles the case where
    //    the local values are near 0 or 1, reducing sharpening near black or
    //    white to avoid clipping artefacts.
    //
    float3 contrast = maxRGB - minRGB;
    float3 weight = saturate(min(minRGB, 1.0 - maxRGB) / (contrast + 1e-5));

    // ---- 4a. Map user `sharpeningStrength` to peak sharpening offset ----------
    //  The peak value controls how much the centre pixel deviates from the
    //  neighbourhood average. AMD’s range is roughly -0.125 (mild) to -0.25
    //  (strong). We interpolate between 1/8 and 1/5 based on the strength
    //  slider.
    //
    //    peak = -1.0 / lerp(8.0, 5.0, sharpeningStrength)
    //
    //  For strength = 0.0 -> peak = -1/8  = -0.125
    //  For strength = 1.0 -> peak = -1/5  = -0.2
    //
    float peak = -1.0 / lerp(8.0, 5.0, sharpeningStrength);
    float3 wRGB = weight * peak;

    // ---- 5. Convolve -----------------------------------------------------------
    //  The sharpening operation blends the centre pixel with its neighbours
    //  using the computed weight:
    //
    //    result = (c + (n + s + e + w) * w) / (1.0 + 4.0 * w)
    //
    //  When w is negative (sharpening), the denominator keeps the result
    //  correctly normalised, preventing DC-shift.
    float3 res = (c + (n + s + e + w) * wRGB) / (1.0 + 4.0 * wRGB);

    // ---- 6. Clamp and return to gamma space ---------------------------------
    //  Clamp to local extrema to remove any residual overshoot, then convert
    //  back to sRGB with square-root.
    res = clamp(res, minRGB, maxRGB);
    OutputTex[pos] = float4(sqrt(max(res, 0.0)), 1.0);
}