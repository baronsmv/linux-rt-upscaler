// =============================================================================
//  Master Aesthetic Grain - Compute Shader
//  ---------------------------------------
//  Adds a realistic, film-emulsion texture to the final image.  The grain is
//  isotropic, temporally jittered, and blended via soft-light, producing a
//  natural organic look without directional bias or flicker.
//
//  Based on Adobe Lightroom and DaVinci Resolve emulsion models, refined for
//  visual-novel and 2D art.
//
//  Features :
//    - Static 2D bilinear noise - produces a smooth, uniform grain pattern
//      with no visible grid or directional streaks.
//    - Temporal micro-jitter - the entire noise field shifts by a fraction of
//      a pixel each frame (< 0.3 px), giving a subtle "swimming" motion that
//      mimics real film-grain Brownian movement without blinking.
//    - Luminance-masked application - grain is strongest at midtones and
//      fades to zero at pure black and pure white, preserving text clarity
//      and preventing dirty shadows.
//    - Soft-light blending - darkens and lightens the image naturally in a
//      way that mimics real film emulsion, avoiding the harsh digital look
//      of additive noise.
//    - Configurable strength and particle size - from ultra-fine photochemical
//      texture to gritty vintage grain.
//    - Operates in-place (reads and writes the same RGBA8 texture).
//
//  Workgroup size : 16-x16 threads.
//  Dispatch :
//    groupsX = ceil(dstWidth  / 16)
//    groupsY = ceil(dstHeight / 16)
//
//  Tuning :
//      strength   = 0.0   -> off
//                   0.005 -> barely visible, adds subtle film texture
//                   0.02  -> moderate grain (cinematic)
//                   0.05  -> noticeable vintage look
//                   0.10  -> gritty, maximum intensity
//      grainSize  = 1.0   -> fine grain
//                   2.0   -> coarser, more visible grain clumps
//      frameIndex = increasing integer each frame for temporal variation
//
//  Integration :
//    - Place after all other post-effects (CAS, Bloom, Vignette, LUT) and
//      before OSD blending.
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
//  High-quality 2D integer hash - uniform, no visible grid
// -----------------------------------------------------------------------------
float Hash2D(uint2 p)
{
    uint n = p.x * 314159 + p.y * 112589;
    n = (n ^ (n << 13)) * 15731u;
    n = n * (n * n * 60493u + 19990303u) + 1376312589u;
    return float(n & 0x7fffffff) / 2147483648.0;
}

// -----------------------------------------------------------------------------
//  Static, isotropic 2D bilinear noise - completely free of directional bias
// -----------------------------------------------------------------------------
float StaticNoise(float2 uv)
{
    float2 i = floor(uv);
    float2 f = frac(uv);
    // Smooth Hermite spline
    f = f * f * (3.0 - 2.0 * f);

    float a = Hash2D(uint2(i));
    float b = Hash2D(uint2(i + float2(1.0, 0.0)));
    float c = Hash2D(uint2(i + float2(0.0, 1.0)));
    float d = Hash2D(uint2(i + float2(1.0, 1.0)));

    return lerp(lerp(a, b, f.x), lerp(c, d, f.x), f.y);
}

// -----------------------------------------------------------------------------
//  Temporal micro-jitter - shifts the noise coordinates by < 0.3 pixel
// -----------------------------------------------------------------------------
float2 FrameJitter(uint frame)
{
    float jx = float((frame * 1453u) & 0x7FFF) / 32768.0 - 0.5;
    float jy = float((frame * 8539u) & 0x7FFF) / 32768.0 - 0.5;
    return float2(jx, jy) * 0.3;
}

// -----------------------------------------------------------------------------
//  Master noise generator - combines static pattern and temporal jitter
// -----------------------------------------------------------------------------
float OrganicNoise(uint2 p, uint frame, float grainSz)
{
    float2 uv = float2(p) / max(grainSz, 1.0);
    uv += FrameJitter(frame);
    return StaticNoise(uv);
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

    float4 source = InputTex.Load(int3(pos, 0));
    float3 color  = source.rgb;

    // ---- 1. Perceptual luminance (Rec.709) ----------------------------------
    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));

    // ---- 2. Luminance masking - peaks at 0.5, falls off to 0 at 0.0 and 1.0
    float lumaMask = saturate(4.0 * luma * (1.0 - luma));

    // ---- 3. Generate organic noise (varies with frame and grain size) -------
    float noise = OrganicNoise(pos, frameIndex, grainSize);

    // ---- 4. Soft-light blending --------------------------------------------
    float3 grainResult;
    if (noise < 0.5)
        grainResult = color * (1.0 - (0.5 - noise) * grainStrength * lumaMask);
    else
        grainResult = color +       (noise - 0.5) * grainStrength * lumaMask;

    // ---- 5. Safe output (alpha preserved) ----------------------------------
    OutputTex[pos] = float4(saturate(grainResult), source.a);
}