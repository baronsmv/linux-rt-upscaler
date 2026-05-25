// ============================================================================
//  Adaptive Lanczos (Variable Radius)
//  ----------------------------------
//  Single-pass 2D resampling for downscaling and non-uniform scaling.
//
//  Components:
//    - Variable-radius Lanczos kernel (sinc-based).
//    - Independent X/Y radii.
//    - Optional soft anti-ringing.
//    - Integer-pixel alignment.
//
//  Adapted from Magpie effect by funnyplanter for linux-rt-upscaler.
//  Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

cbuffer Constants : register(b0) {
  float4 bgColor; // color outside the destination rectangle
  uint srcWidth, srcHeight;
  uint dstTotalWidth, dstTotalHeight;
  int dstX, dstY, dstW, dstH;
  uint radiusX;           // pre-computed filter radius in X
  uint radiusY;           // pre-computed filter radius in Y
  float blur;             // kernel softness (1.0 = standard)
  float antiringStrength; // 0 = off, 1 = full hard clamp
  bool tightAntiring;     // true = only central 2x2 for ringing bounds
}

// ============================================================================
//  Lanczos kernel
//  L(x) = sinc(x) · sinc(x / r)    for |x| < r
//       = 1                        for x = 0
//       = 0                        for |x| ≥ r
// ============================================================================
#define PI 3.1415926535897932f

float lanczos(float x, float r) {
  x *= (1.0f / blur); // apply blur stretch
  if (x < 1e-4f)
    return 1.0f;
  if (x >= r)
    return 0.0f;

  float pi_x = PI * x;
  return (r * sin(pi_x) * sin(pi_x / r)) / (pi_x * pi_x);
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

  // ---- Map destination pixel to continuous source coordinate ---------------
  float2 uv =
      (float2(outPos.x - dstX, outPos.y - dstY) + 0.5f) / float2(dstW, dstH);
  float2 srcCoord = uv * float2(srcWidth, srcHeight);

  float2 pp = srcCoord - 0.5f;
  int2 p0 = int2(floor(pp));
  float2 f = pp - float2(p0);

  float3 accum = 0.0f;
  float weightSum = 0.0f;
  float3 vmin = 1e6f, vmax = -1e6f;

  // ---- Walk the sampling window (radiusX/radiusY) -------------------------
  int irx = int(radiusX);
  int iry = int(radiusY);

  for (int iy = -iry + 1; iy <= iry; ++iy) {
    float wy = lanczos(abs(float(iy) - f.y), float(iry));

    for (int ix = -irx + 1; ix <= irx; ++ix) {
      // Clamp to source texture area
      int2 sc = clamp(p0 + int2(ix, iy), int2(0, 0),
                      int2(srcWidth - 1, srcHeight - 1));

      float3 color = InputTex.Load(int3(sc, 0)).rgb;
      float wx = lanczos(abs(float(ix) - f.x), float(irx));
      float w = wx * wy;

      accum += color * w;
      weightSum += w;

      // Anti-ringing bounds
      bool isCentral = (abs(ix) <= 1 && abs(iy) <= 1);
      if (!tightAntiring || isCentral) {
        vmin = min(vmin, color);
        vmax = max(vmax, color);
      }
    }
  }

  float3 v = accum / (weightSum + 1e-7f);

  // Soft anti-ringing clamp
  v = clamp(v, lerp(v, vmin, antiringStrength),
            lerp(v, vmax, antiringStrength));

  OutputTex[outPos] = float4(v, 1.0f);
}