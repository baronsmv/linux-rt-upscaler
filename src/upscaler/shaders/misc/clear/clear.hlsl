[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

cbuffer Constants : register(b0) {
  float4 clearColor;
  uint2 size;
};

[numthreads(16, 16, 1)] void main(uint3 dtid : SV_DispatchThreadID) {
  if (dtid.x >= size.x || dtid.y >= size.y)
    return;
  OutputTex[dtid.xy] = clearColor;
}