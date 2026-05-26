// ============================================================================
//  Catmull-Rom Resampler
//  ---------------------
//  Cubic downscaling using 9 taps.
//  Based on MJP's sample:
//  https://gist.github.com/TheRealMJP/bc503b0b87b643d3505d41eab8b332ae
//
//  Parameters:
//    blur              - kernel stretch (1.0 = standard Catmull-Rom)
//    antiringStrength  - 0.0 = off, 1.0 = full clamp to local bounds
//
//  Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);
SamplerState LinearSampler : register(s0);

cbuffer Constants : register(b0) {
  float4 bgColor;
  uint srcWidth, srcHeight;
  uint dstTotalWidth, dstTotalHeight;
  int dstX, dstY, dstW, dstH;
  float blur;
  float antiringStrength;
}

// ============================================================================
//  Catmull-Rom sampling function (9 taps)
// ============================================================================
float4 SampleTextureCatmullRom(Texture2D<float4> tex, SamplerState samp,
                               float2 uv, float2 texSize, float b) {
  float2 samplePos = uv * texSize;
  float2 texPos1 = floor(samplePos - 0.5f) + 0.5f;
  float2 f = (samplePos - texPos1) / max(b, 0.001f);

  float2 w0 = f * (-0.5f + f * (1.0f - 0.5f * f));
  float2 w1 = 1.0f + f * f * (-2.5f + 1.5f * f);
  float2 w2 = f * (0.5f + f * (2.0f - 1.5f * f));
  float2 w3 = f * f * (-0.5f + 0.5f * f);

  float2 w12 = w1 + w2;
  float2 offset12 = w2 / max(w12, 0.001f);

  float2 texPos0 = texPos1 - 1;
  float2 texPos3 = texPos1 + 2;
  float2 texPos12 = texPos1 + offset12;

  texPos0 /= texSize;
  texPos3 /= texSize;
  texPos12 /= texSize;

  float4 result = 0.0f;
  result +=
      tex.SampleLevel(samp, float2(texPos0.x, texPos0.y), 0) * w0.x * w0.y;
  result +=
      tex.SampleLevel(samp, float2(texPos12.x, texPos0.y), 0) * w12.x * w0.y;
  result +=
      tex.SampleLevel(samp, float2(texPos3.x, texPos0.y), 0) * w3.x * w0.y;

  result +=
      tex.SampleLevel(samp, float2(texPos0.x, texPos12.y), 0) * w0.x * w12.y;
  result +=
      tex.SampleLevel(samp, float2(texPos12.x, texPos12.y), 0) * w12.x * w12.y;
  result +=
      tex.SampleLevel(samp, float2(texPos3.x, texPos12.y), 0) * w3.x * w12.y;

  result +=
      tex.SampleLevel(samp, float2(texPos0.x, texPos3.y), 0) * w0.x * w3.y;
  result +=
      tex.SampleLevel(samp, float2(texPos12.x, texPos3.y), 0) * w12.x * w3.y;
  result +=
      tex.SampleLevel(samp, float2(texPos3.x, texPos3.y), 0) * w3.x * w3.y;

  return result;
}

// ============================================================================
//  Main entry point
// ============================================================================
[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  uint2 outPos = dtid.xy;
  if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight)
    return;

  int x = int(outPos.x);
  int y = int(outPos.y);

  // Background fill
  if (x < dstX || x >= dstX + dstW || y < dstY || y >= dstY + dstH) {
    OutputTex[outPos] = bgColor;
    return;
  }

  // Map destination pixel to continuous source coordinate
  float2 uv = (float2(x - dstX, y - dstY) + 0.5f) / float2(dstW, dstH);
  float4 color = SampleTextureCatmullRom(InputTex, LinearSampler, uv,
                                         float2(srcWidth, srcHeight), blur);

  // ---- Anti-ringing clamp --------------------------------------------
  if (antiringStrength > 0.0f) {
    // Compute integer source coordinate of the nearest pixel
    float2 srcCoord = uv * float2(srcWidth, srcHeight);
    int2 iSrc = int2(floor(srcCoord));

    // Load 2x2 neighbourhood around that pixel
    int2 base = clamp(iSrc + int2(-1, -1), int2(0, 0),
                      int2(srcWidth - 2, srcHeight - 2));
    float3 c00 = InputTex.Load(int3(base + int2(0, 0), 0)).rgb;
    float3 c10 = InputTex.Load(int3(base + int2(1, 0), 0)).rgb;
    float3 c01 = InputTex.Load(int3(base + int2(0, 1), 0)).rgb;
    float3 c11 = InputTex.Load(int3(base + int2(1, 1), 0)).rgb;

    float3 vmin = min(min(c00, c10), min(c01, c11));
    float3 vmax = max(max(c00, c10), max(c01, c11));

    // Soft clamp: blend between the original and the clamped value
    color.rgb = lerp(color.rgb, clamp(color.rgb, vmin, vmax), antiringStrength);
  }

  OutputTex[outPos] = color;
}