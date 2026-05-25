// ============================================================================
//  3D LUT Color Grading
//  --------------------
//  Applies a color-lookup table to the image.
//
//  Components:
//    - UV-to-texel-center mapping.
//    - Trilinear interpolation.
//    - Configurable LUT size.
//    - Sampler-based bilinear filtering for R/G.
//
//  LUT texture layout:
//    - Type: 2D array of (lutSize x lutSize) pixels, with lutSize slices.
//    - Each slice corresponds to a fixed Blue coordinate. The Red coordinate
//      maps to the horizontal axis, and the Green to the vertical one.
//    - Format: RGBA8 (sRGB or linear, depending on pipeline).
//    - Sampler: linear (provides bilinear filtering within a slice).
//
//  Tuning:
//    - intensity = 0.0   -> original image (passthrough, zero cost)
//                  0.5   -> half blend
//                  1.0   -> full color grade
//    - lutSize   = common values: 16, 32 (default), 64
//                  larger -> smoother gradients, but more GPU memory
//
//  Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);
Texture2DArray<float4> LUTTex : register(t1);
SamplerState LUTSampler : register(s0);

cbuffer Constants : register(b0) {
  float intensity; // 0.0 - 1.0
  uint lutSize;    // e.g., 32
  uint dstWidth;
  uint dstHeight;
};

// ============================================================================
//  Main kernel
// ============================================================================
[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  uint2 pos = dtid.xy;
  if (pos.x >= dstWidth || pos.y >= dstHeight)
    return;

  // ---- 1. Load original color ----------------------------------------------
  float4 color = InputTex.Load(int3(pos, 0));
  color.rgb = color.bgr;

  // Early exit if no grading applied.
  if (intensity <= 0.0f) {
    OutputTex[pos] = color;
    return;
  }

  // ---- 2. Prepare RGB values (clamped to [0,1]) ----------------------------
  float3 rgb = saturate(color.rgb);
  float fSize = float(lutSize);

  // ---- 3. Compute LUT UV coordinates with texel-center alignment -----------
  //  The LUT texture is indexed so that input 0.0 lands on the center of
  //  texel 0 and input 1.0 lands on the center of texel (lutSize-1).
  //  Formula:   (r * (fSize - 1) + 0.5) / fSize
  //  =  r * ((fSize - 1.0) / fSize) + (0.5 / fSize)
  float3 lutUV = rgb * ((fSize - 1.0f) / fSize) + (0.5f / fSize);

  // ---- 4. Compute the Blue index and fractional Z blend --------------------
  //  Blue axis spans the array slices. We find the two adjacent slices
  //  and the interpolation weight between them.
  float blueIdx = rgb.b * (fSize - 1.0f);
  uint slice0 = uint(floor(blueIdx));
  uint slice1 = min(slice0 + 1u, lutSize - 1u);
  float zLerp = frac(blueIdx);

  // ---- 5. Sample the two Blue slices ---------------------------------------
  //  The linear sampler handles the 2D bilinear interpolation inside each
  //  slice automatically. We pass lutUV.x and lutUV.y as the 2D coordinate,
  //  and the slice index as the third component.
  float3 col0 =
      LUTTex.SampleLevel(LUTSampler, float3(lutUV.xy, float(slice0)), 0.0f).rgb;
  float3 col1 =
      LUTTex.SampleLevel(LUTSampler, float3(lutUV.xy, float(slice1)), 0.0f).rgb;

  // ---- 6. Trilinear blend --------------------------------------------------
  //  Interpolate between the two sampled colors based on zLerp.
  float3 graded = lerp(col0, col1, zLerp);
  graded.rgb = graded.bgr;

  // ---- 7. Apply intensity and preserve alpha -------------------------------
  color.rgb = lerp(color.rgb, graded, intensity);
  OutputTex[pos] = float4(color.rgb, color.a);
}