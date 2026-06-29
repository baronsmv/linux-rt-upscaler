// ============================================================================
//  sRGB-to-sRGB with Blue-Noise Dither
//  -----------------------------------
//  Reads a 16-bit float sRGB image, adds dither, and writes to 8-bit sRGB.
//
//  Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

Texture2D<float4> NoiseTex : register(t1);
SamplerState PointSampler : register(s0);

cbuffer Constants : register(b0) {
  uint outputWidth;
  uint outputHeight;
  float ditherStrength; // recommended: 1.0/255.0
}

[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  uint2 pos = dtid.xy;
  if (pos.x >= outputWidth || pos.y >= outputHeight)
    return;

  float3 srgb = InputTex.Load(int3(pos, 0)).rgb;

  float2 uv = (float2(pos) + 0.5) / 64.0;
  float r = NoiseTex.SampleLevel(PointSampler, uv, 0).r;
  float g = NoiseTex.SampleLevel(PointSampler, uv + float2(0.33, 0.33), 0).g;
  float b = NoiseTex.SampleLevel(PointSampler, uv + float2(0.67, 0.67), 0).b;

  float3 dither = (float3(r, g, b) - 0.5) * ditherStrength;
  OutputTex[pos] = float4(srgb + dither, 1.0);
}