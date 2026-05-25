// ============================================================================
//  Linear -> sRGB Converter (Gamma Compression)
//  --------------------------------------------
//  Inverse of the linearize pass.
//
//  Written for linux-rt-upscaler. Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

float3 Delinearize(float3 lin) {
  // Gamma-2.2 approximation (faster)
  // return pow(linear, 1.0 / 2.2);

  // IEC 61966-2-1 linear -> sRGB (slower)
  // https://entropymine.com/imageworsener/srgbformula/
  float3 low = lin * 12.92;
  float3 high = 1.055 * pow(lin, 1.0 / 2.4) - 0.055;
  return lerp(high, low, step(lin, 0.0031308));
}

// ============================================================================
//  Main kernel
// ============================================================================
[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  float4 c = InputTex.Load(int3(dtid.xy, 0));
  OutputTex[dtid.xy] = float4(Delinearize(c.rgb), c.a);
}