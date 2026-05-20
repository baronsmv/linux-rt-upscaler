// ============================================================================
//  Radial Vignette
//  ---------------
//  Darkens the screen corners.
//
//  Components:
//    - Distance-based darkening with no hard edges.
//
//  Tuning:
//    - strength = 0.0   -> off
//                 0.2   -> barely visible
//                 0.5   -> moderate
//                 1.0   -> black corners
//    - radius   = 0.0   -> darkening starts at center
//                 0.7   -> keeps center bright
//                 1.2   -> only extreme corners
//    - falloff  = 1.0   -> gentle, wide transition
//                 3.0   -> sharp vignette ring
//
//  Written for linux-rt-upscaler. Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

cbuffer Constants : register(b0) {
  float vignetteStrength; // 0.0 - 1.0
  uint dstWidth;
  uint dstHeight;
  float vignetteRadius;  // distance where darkening starts (0.0 - 1.5)
  float vignetteFalloff; // soft edge sharpness (higher = sharper)
};

[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  uint2 pos = dtid.xy;
  if (pos.x >= dstWidth || pos.y >= dstHeight)
    return;

  // ---- 1. Load original color --------------------------------------------
  float4 color = InputTex.Load(int3(pos, 0));

  // ---- 2. Distance from center (norm. to [0, ~0.707] for square image) ---
  float2 uv = (float2(pos) + 0.5) / float2(dstWidth, dstHeight) - 0.5;
  float dist = length(uv);

  // ---- 3. Darkening factor -----------------------------------------------
  //  factor = smoothstep-like blend: 0.0 where dist <= radius,
  //  rising linearly (or faster with falloff exponent) beyond it.
  float factor = saturate((dist - vignetteRadius) * vignetteFalloff);
  float darken = 1.0 - vignetteStrength * factor;

  // ---- 4. Apply and preserve alpha ---------------------------------------
  color.rgb *= darken;

  OutputTex[pos] = float4(color.rgb, color.a);
}