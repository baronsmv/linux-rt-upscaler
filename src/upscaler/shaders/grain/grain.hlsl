// =============================================================================
//  Master Aesthetic Grain - Compute Shader
//  ---------------------------------------
//  Adds film-like texture to the final image, enhancing the visual-novel
//  atmosphere without degrading text or line art.
//
//  Features :
//    - Luminance-masked application - grain is strongest at midtones,
//      invisible at pure black/white (preserves text and shadows).
//    - Soft-light blending - organic tonal variation, not harsh additive noise.
//    - Organic pseudo-random noise with configurable grain size.
//    - Temporal jitter via `frameIndex` - simulates 24fps film movement,
//      preventing a static overlay look.
//    - Operates in place (reads and writes the same RGBA8 texture).
//
//  Workgroup size : 16x16 threads.
//  Dispatch :
//    groupsX = ceil(dstWidth  / 16)
//    groupsY = ceil(dstHeight / 16)
//
//  Tuning :
//      strength   = 0.0   -> off (default)
//                   0.01  -> ultra-fine photochemical texture
//                   0.05  -> moderate grain (cinematic)
//                   0.10  -> gritty / vintage feel
//      grainSize  = 1.0   -> fine grain (default)
//                   2.0   -> coarser, more visible grain
//      frameIndex = increasing integer each frame for temporal variation
//
//  Integration :
//    - Place after all other post-effects (CAS, Bloom) and before OSD blending.
//    - Use the screen texture as both input and output (safe in-place).
//    - Call `update_constants` every frame with an incremented `frame_index`.
//
//  Adapted from Adobe Lightroom and DaVinci Resolve for linux-rt-upscaler.
// =============================================================================

Texture2D<float4> InputTex  : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

cbuffer Constants : register(b0)
{
    float grainStrength;        // 0.0 - 0.10 (0 = off)
    uint  dstWidth;
    uint  dstHeight;
    uint  frameIndex;           // frame counter for temporal noise
    float grainSize;            // 1.0 = fine, >1.0 = coarser
}

// -----------------------------------------------------------------------------
//  Organic noise generator - creates film-like grain clumps
//  using the pixel position, frame counter, and grain size.
// -----------------------------------------------------------------------------
float OrganicNoise(uint2 p, uint frame, float grainSz)
{
    float2 s = float2(p) / max(grainSz, 1.0);
    float  seed = dot(s + float(frame % 60), float2(12.9898, 78.233));
    return frac(sin(seed) * 43758.5453);
}

[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 pos = dtid.xy;
    if (pos.x >= dstWidth || pos.y >= dstHeight)
        return;

    float4 source = InputTex.Load(int3(pos, 0));
    float3 color  = source.rgb;

    // ---- 1. Perceptual luminance (Rec.709) ----------------------------------
    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));

    // ---- 2. Luminance masking - Adobe-style parabolic curve -----------------
    //  Peaks at 0.5, falls to 0 at both 0.0 and 1.0.
    //  Saturate prevents overshoot (mask > 1.0) in extreme values.
    float lumaMask = saturate(4.0 * luma * (1.0 - luma));

    // ---- 3. Generate organic noise (varies with frame and grain size) -------
    float noise = OrganicNoise(pos, frameIndex, grainSize);

    // ---- 4. Soft-light blending --------------------------------------------
    //  Darkens when noise < 0.5, lightens when noise > 0.5.
    //  This mimics real film emulsion, not digital additive noise.
    float3 grainResult;
    if (noise < 0.5)
        grainResult = color * (1.0 - (0.5 - noise) * grainStrength * lumaMask);
    else
        grainResult = color +       (noise - 0.5) * grainStrength * lumaMask;

    // ---- 5. Safe output (alpha preserved) ----------------------------------
    OutputTex[pos] = float4(saturate(grainResult), source.a);
}