// ============================================================================
//  Linear -> sRGB Converter (Gamma Compression)
//  --------------------------------------------
//  Inverse of the linearize pass.
//
//  Converts a linear-light texture back to sRGB while injecting
//  blue-noise dither to hide banding.
//
//  Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

// Blue-noise texture (64x64 RGBA8, tiled)
Texture2D<float4> NoiseTex : register(t1);
SamplerState PointSampler : register(s0);

// Constant buffer
cbuffer Constants : register(b0) {
  uint outputWidth;
  uint outputHeight;
  float ditherStrength; // recommended: 1.0/255.0 (one 8-bit step)
}

// ----------------------------------------------------------------------------
//  IEC 61966-2-1 linear -> sRGB
//  https://entropymine.com/imageworsener/srgbformula/
// ----------------------------------------------------------------------------
float3 LinearToSRGB(float3 lin) {
  float3 low = lin * 12.92;
  float3 high = 1.055 * pow(abs(lin), 1.0 / 2.4) - 0.055;
  return lerp(high, low, step(lin, 0.0031308));
}

// ============================================================================
//  Main kernel
// ============================================================================
[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  uint2 pos = dtid.xy;
  if (pos.x >= outputWidth || pos.y >= outputHeight)
    return;

  float3 lin = InputTex.Load(int3(pos, 0)).rgb;

  // Base UV for a 64x64 noise texture tile
  float2 uv = (float2(pos) + 0.5) / 64.0;

  // Fetch three independent noise values
  float r = NoiseTex.SampleLevel(PointSampler, uv, 0).r;
  float g = NoiseTex.SampleLevel(PointSampler, uv + float2(0.33, 0.33), 0).g;
  float b = NoiseTex.SampleLevel(PointSampler, uv + float2(0.67, 0.67), 0).b;

  // Dither
  float3 dither = (float3(r, g, b) - 0.5) * ditherStrength;
  float3 ditheredLinear = max(0.0, lin + dither);
  float3 srgb = LinearToSRGB(ditheredLinear);

  // Write to the 8-bit UAV
  OutputTex[pos] = float4(srgb, 1.0);
}