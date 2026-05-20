// ============================================================================
//  Contrast Adaptive Sharpening (CAS)
//  ----------------------------------
//  Single-pass sharpening filter with local contrast.
//
//  Components:
//    - 5-tap kernel (center + N/S/E/W).
//    - Linear-light processing.
//    - Clamp to min/max of the 5-tap neighborhood.
//
//  Tuning (strength examples):
//    - strength = 0.0   ->  pass-through (no sharpening)
//    - strength = 0.2   ->  subtle edge enhancement
//    - strength = 0.4   ->  moderate (good for text / line art)
//    - strength = 0.6+  ->  aggressive (risk of visible ringing)
//
//  Written for linux-rt-upscaler. Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

cbuffer Constants : register(b0) {
  float sharpeningStrength; // 0.0 - 1.0  (disable -> full effect)
  uint dstWidth;            // width of the texture (pixels)
  uint dstHeight;           // height of the texture (pixels)
  uint _pad0;               // align to 16 bytes (Vulkan requirement)
};

// ----------------------------------------------------------------------------
//  Clamp to prevent out-of-bounds access
// ----------------------------------------------------------------------------
float3 LoadPixel(int2 coord) {
  coord = clamp(coord, int2(0, 0), int2(dstWidth - 1, dstHeight - 1));
  return InputTex.Load(int3(coord, 0)).rgb;
}

// ----------------------------------------------------------------------------
//  Main CAS kernel
// ----------------------------------------------------------------------------
[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  uint2 pos = dtid.xy;
  if (pos.x >= dstWidth || pos.y >= dstHeight)
    return;

  // ---- 1. Sample 5-tap neighborhood (center + N/S/E/W) -------------------
  //  Using only the axial neighbours keeps the kernel compact while
  //  preserving edge features.
  //  The local contrast is measured in these 5 values.
  float3 c = LoadPixel(int2(pos.x, pos.y));     // center
  float3 n = LoadPixel(int2(pos.x, pos.y - 1)); // north
  float3 s = LoadPixel(int2(pos.x, pos.y + 1)); // south
  float3 e = LoadPixel(int2(pos.x + 1, pos.y)); // east
  float3 w = LoadPixel(int2(pos.x - 1, pos.y)); // west

  // ---- 2. Convert to approximate linear light ----------------------------
  //  Sharpening in linear space yields a more natural, perceptually uniform
  //  result. We use a simple squaring from sRGB, accurate enough for this
  //  post-effect and zero extra texture reads.
  c *= c;
  n *= n;
  s *= s;
  e *= e;
  w *= w;

  // ---- 3. Local min / max for anti-ringing -------------------------------
  //  Compute the min and max of the 5 taps. The final sharpened value will
  //  be clamped to this range, guaranteeing no overshoot beyond the local
  //  luminance extremes.
  float3 minRGB = min(c, min(min(n, s), min(e, w)));
  float3 maxRGB = max(c, max(max(n, s), max(e, w)));

  // ---- 4. Compute CAS weight ---------------------------------------------
  //  - For flat regions (contrast ≈ 0), weight -> 0, so no sharpening is
  //    applied, preserving smooth gradients.
  //  - For edges, weight becomes large, allowing strong sharpening.
  //  - The numerator `min(minRGB, 1.0 - maxRGB)` handles the case where
  //    the local values are near 0 or 1, reducing sharpening near black or
  //    white to avoid clipping artifacts.
  // -  For 2D art we add a small minimum weight to keep the sharpening
  //    visible on high-contrast lines.
  float3 contrast = maxRGB - minRGB;
  float3 weight =
      max(0.15, saturate(min(minRGB, 1.0 - maxRGB) / (contrast + 1e-5)));

  // ---- 5. Map user `sharpeningStrength` to peak sharpening offset --------
  //  The peak value controls how much the center pixel deviates from the
  //  neighborhood average.
  float peak = -1.0 / lerp(8.0, 4.0, sharpeningStrength);
  float3 wRGB = weight * peak;

  // ---- 6. Convolve -------------------------------------------------------
  //  The sharpening operation blends the center pixel with its neighbours.
  float3 res = (c + (n + s + e + w) * wRGB) / (1.0 + 4.0 * wRGB);

  // ---- 7. Clamp and return to gamma space --------------------------------
  //  Clamp to local extrema to remove any residual overshoot, then convert
  //  back to sRGB with square-root.
  res = clamp(res, minRGB, maxRGB);
  OutputTex[pos] = float4(sqrt(max(res, 0.0)), 1.0);
}