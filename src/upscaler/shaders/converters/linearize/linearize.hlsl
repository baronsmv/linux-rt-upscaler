// ============================================================================
//  sRGB -> Linear Converter (Gamma Expansion)
//  ------------------------------------------
//  Transforms an sRGB-encoded color texture to linear light.
//
//  Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

float3 Linearize(float3 srgb) {
  // Gamma-2.2 approximation (faster)
  // return pow(srgb, 2.2);

  // IEC 61966-2-1 sRGB -> linear (slower)
  // https://entropymine.com/imageworsener/srgbformula/
  float3 low = srgb / 12.92;
  float3 high = pow((srgb + 0.055) / 1.055, 2.4);
  return lerp(high, low, step(srgb, 0.04045));
}

// ============================================================================
//  Main kernel
// ============================================================================
[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  float4 c = InputTex.Load(int3(dtid.xy, 0));
  OutputTex[dtid.xy] = float4(Linearize(c.rgb), c.a);
}