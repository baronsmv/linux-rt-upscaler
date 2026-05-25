// ============================================================================
//  Overlay Blend
//  -------------
//  Blits an overlay texture using premultiplied alpha blending.
//
//  Parameters:
//    - overlayPos  : top-left corner of the overlay in screen coordinates.
//    - overlaySize : width and height of the overlay region (pixels).
//
//  Distributed under the GPL-3.0 license.
// ============================================================================

Texture2D<float4> ScreenTex : register(t0);
Texture2D<float4> OverlayTex : register(t1);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> Output : register(u0);

cbuffer OverlayParams : register(b0) {
  int2 overlayPos;  // x, y in screen coordinates
  int2 overlaySize; // width, height
};

[numthreads(16, 16, 1)] void main(uint3 id : SV_DispatchThreadID) {
  if (id.x >= overlaySize.x || id.y >= overlaySize.y)
    return;

  int2 screenPos = overlayPos + id.xy;
  float4 screenColor = ScreenTex[screenPos];
  float4 overlayColor = OverlayTex[id.xy];

  // Premultiplied alpha blend
  float3 blended = overlayColor.rgb * overlayColor.a +
                   screenColor.rgb * (1.0 - overlayColor.a);
  Output[screenPos] = float4(blended, 1.0);
}