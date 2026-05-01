// =============================================================================
//  3D LUT Colour Grading - Compute Shader
//  --------------------------------------
//  Applies a cinematic colour-lookup table to the image. Uses a 2D-array
//  texture with trilinear interpolation for smooth, banding-free results.
//
//  Features:
//    - Correct UV-to-texel-centre mapping - input 0.0 lands on the centre of
//      the first LUT texel, 1.0 on the centre of the last, eliminating
//      half-texel offsets that cause colour inaccuracies at extremes.
//    - Trilinear interpolation - bilinear in R/G within each Blue slice,
//      plus manual linear blend between two adjacent Blue slices for full
//      three-dimensional smoothing.
//    - Intensity slider (0-1) - blend between original and graded image.
//    - Alpha-preserving - RGB is transformed, alpha passed through unchanged.
//    - Operates in-place (reads and writes the same RGBA8 texture).
//    - LUT size configurable via constant buffer (typical: 32).
//    - Sampler-based bilinear filtering for R/G - efficient single-tap
//      per slice, no manual bilinear math required.
//
//  LUT texture layout:
//    - Type : 2D array of (lutSize x lutSize) pixels, with lutSize slices.
//    - Each slice corresponds to a fixed Blue coordinate; the Red coordinate
//      maps to the horizontal axis, Green to vertical.
//    - Format : RGBA8 (sRGB or linear, depending on pipeline; this shader
//      stays in sRGB space - no extra conversions needed).
//    - Sampler : linear (provides bilinear filtering within a slice).
//
//  Workgroup size: 16x16 threads.
//  Dispatch:
//    groupsX = ceil(dstWidth  / 16)
//    groupsY = ceil(dstHeight / 16)
//
//  Tuning:
//      intensity = 0.0   -> original image (passthrough, zero cost)
//                  0.5   -> half blend
//                  1.0   -> full colour grade
//      lutSize   = common values: 16, 32 (default), 64
//                  larger -> smoother gradients, but more GPU memory
//
//  Integration:
//    - Place near the end of the post-processing chain (after bloom/vignette,
//      before film grain or as the final step).
//    - Requires a pre-populated LUT texture (2D array) bound to t1 and a
//      linear sampler at s1. An identity LUT (R,G,B -> R,G,B) should be
//      loaded by default so that the effect can be toggled without missing
//      resources.
//    • The Python handler (`LUTPass`) automatically creates an identity LUT
//      and exposes methods to upload custom LUT data.
//
//  Based on Resolve 3D LUTs colour grading for linux‑rt‑upscaler.
// =============================================================================

Texture2D<float4>         InputTex   : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4>       OutputTex  : register(u0);
Texture2DArray<float4>     LUTTex     : register(t1);
SamplerState               LUTSampler : register(s1);

cbuffer Constants : register(b0)
{
    float intensity;        // 0.0 – 1.0
    uint  lutSize;          // e.g., 32
    uint  dstWidth;
    uint  dstHeight;
};

// =============================================================================
//  Main kernel
// =============================================================================
[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 pos = dtid.xy;
    if (pos.x >= dstWidth || pos.y >= dstHeight)
        return;

    // ---- 1. Load original colour --------------------------------------------
    float4 color = InputTex.Load(int3(pos, 0));

    // Early exit – no grading applied. This skips all remaining work.
    if (intensity <= 0.0f)
    {
        OutputTex[pos] = color;
        return;
    }

    // ---- 2. Prepare RGB values (clamped to [0,1]) -----------------------------
    float3 rgb = saturate(color.rgb);
    float  fSize = float(lutSize);

    // ---- 3. Compute LUT UV coordinates with texel‑centre alignment -----------
    //  The LUT texture is indexed so that input 0.0 lands on the centre of
    //  texel 0 and input 1.0 lands on the centre of texel (lutSize-1).
    //  Formula:   (r * (fSize - 1) + 0.5) / fSize
    //  =  r * ((fSize - 1.0) / fSize) + (0.5 / fSize)
    float3 lutUV = rgb * ((fSize - 1.0f) / fSize) + (0.5f / fSize);

    // ---- 4. Compute the Blue index and fractional Z blend --------------------
    //  Blue axis spans the array slices. We find the two adjacent slices
    //  and the interpolation weight between them.
    float  blueIdx = rgb.b * (fSize - 1.0f);
    uint   slice0  = uint(floor(blueIdx));
    uint   slice1  = min(slice0 + 1u, lutSize - 1u);
    float  zLerp   = frac(blueIdx);

    // ---- 5. Sample the two Blue slices ---------------------------------------
    //  The linear sampler handles the 2D bilinear interpolation inside each
    //  slice automatically. We pass lutUV.x and lutUV.y as the 2D coordinate,
    //  and the slice index as the third component.
    float3 col0 = LUTTex.SampleLevel(LUTSampler, float3(lutUV.xy, float(slice0)), 0.0f).rgb;
    float3 col1 = LUTTex.SampleLevel(LUTSampler, float3(lutUV.xy, float(slice1)), 0.0f).rgb;

    // ---- 6. Trilinear blend --------------------------------------------------
    //  Interpolate between the two sampled colours based on zLerp.
    float3 graded = lerp(col0, col1, zLerp);

    // ---- 7. Apply intensity and preserve alpha -------------------------------
    color.rgb = lerp(color.rgb, graded, intensity);
    OutputTex[pos] = float4(color.rgb, color.a);
}