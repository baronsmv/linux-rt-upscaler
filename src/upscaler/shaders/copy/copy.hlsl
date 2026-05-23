// ============================================================================
//  Identity Copy
//  -------------
//  Copies the source texture to the output, respecting a destination rectangle.
//
//  Used to bypass Lanczos when no resampling is needed (1:1 pixel mapping).
//
//  Components:
//    - Point sampling (integer texture load).
//    - Destination rectangle with background fill.
//
//  Note: This shader does not perform any operation. It is a simple blit.
//
//  Written for linux-rt-upscaler. Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> InputTex : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

cbuffer Constants : register(b0) {
  float4 bgColor;          // color outside the destination rectangle
  uint srcWidth;
  uint srcHeight;
  uint dstTotalWidth;
  uint dstTotalHeight;
  int dstX;                // top-left corner of the destination rect
  int dstY;
  int dstW;                // width and height of the destination rect
  int dstH;
};

[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID) {
  uint2 outPos = dtid.xy;
  if (outPos.x >= dstTotalWidth || outPos.y >= dstTotalHeight)
    return;

  int x = int(outPos.x);
  int y = int(outPos.y);

  // Outside the destination rectangle: just fill with background color
  if (x < dstX || x >= dstX + dstW || y < dstY || y >= dstY + dstH) {
    OutputTex[outPos] = bgColor;
    return;
  }

  // Map to source coordinates (point sample)
  float2 uv = (float2(x - dstX, y - dstY) + 0.5) / float2(dstW, dstH);
  int2 srcCoord = int2(uv * float2(srcWidth, srcHeight));
  srcCoord = clamp(srcCoord, int2(0,0), int2(srcWidth-1, srcHeight-1));
  OutputTex[outPos] = InputTex.Load(int3(srcCoord, 0));
}