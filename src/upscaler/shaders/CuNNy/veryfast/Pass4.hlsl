cbuffer __CB1 : register(b0) {
	uint2 __inputSize;
	uint2 __outputSize;
	float2 __inputPt;
	float2 __outputPt;
	float2 __scale;
};

#define MF float
#define MF1 float1
#define MF2 float2
#define MF3 float3
#define MF4 float4
#define MF1x1 float1x1
#define MF1x2 float1x2
#define MF1x3 float1x3
#define MF1x4 float1x4
#define MF2x1 float2x1
#define MF2x2 float2x2
#define MF2x3 float2x3
#define MF2x4 float2x4
#define MF3x1 float3x1
#define MF3x2 float3x2
#define MF3x3 float3x3
#define MF3x4 float3x4
#define MF4x1 float4x1
#define MF4x2 float4x2
#define MF4x3 float4x3
#define MF4x4 float4x4
Texture2D<MF4> INPUT : register(t0);
Texture2D<MF4> T0 : register(t1);
RWTexture2D<unorm MF4> OUTPUT : register(u0);
SamplerState SP : register(s0);
SamplerState SL : register(s1);

uint __Bfe(uint src, uint off, uint bits) { uint mask = (1u << bits) - 1; return (src >> off) & mask; }
uint __BfiM(uint src, uint ins, uint bits) { uint mask = (1u << bits) - 1; return (ins & mask) | (src & (~mask)); }
uint2 Rmp8x8(uint a) { return uint2(__Bfe(a, 1u, 3u), __BfiM(__Bfe(a, 3u, 3u), a, 1u)); }
uint2 GetInputSize() { return __inputSize; }
float2 GetInputPt() { return __inputPt; }
uint2 GetOutputSize() { return __outputSize; }
float2 GetOutputPt() { return __outputPt; }
float2 GetScale() { return __scale; }
MF2 MulAdd(MF2 x, MF2x2 y, MF2 a) {
	MF2 result = a;
	result = mad(x.x, y._m00_m01, result);
	result = mad(x.y, y._m10_m11, result);
	return result;
}
MF3 MulAdd(MF2 x, MF2x3 y, MF3 a) {
	MF3 result = a;
	result = mad(x.x, y._m00_m01_m02, result);
	result = mad(x.y, y._m10_m11_m12, result);
	return result;
}
MF4 MulAdd(MF2 x, MF2x4 y, MF4 a) {
	MF4 result = a;
	result = mad(x.x, y._m00_m01_m02_m03, result);
	result = mad(x.y, y._m10_m11_m12_m13, result);
	return result;
}
MF2 MulAdd(MF3 x, MF3x2 y, MF2 a) {
	MF2 result = a;
	result = mad(x.x, y._m00_m01, result);
	result = mad(x.y, y._m10_m11, result);
	result = mad(x.z, y._m20_m21, result);
	return result;
}
MF3 MulAdd(MF3 x, MF3x3 y, MF3 a) {
	MF3 result = a;
	result = mad(x.x, y._m00_m01_m02, result);
	result = mad(x.y, y._m10_m11_m12, result);
	result = mad(x.z, y._m20_m21_m22, result);
	return result;
}
MF4 MulAdd(MF3 x, MF3x4 y, MF4 a) {
	MF4 result = a;
	result = mad(x.x, y._m00_m01_m02_m03, result);
	result = mad(x.y, y._m10_m11_m12_m13, result);
	result = mad(x.z, y._m20_m21_m22_m23, result);
	return result;
}
MF2 MulAdd(MF4 x, MF4x2 y, MF2 a) {
	MF2 result = a;
	result = mad(x.x, y._m00_m01, result);
	result = mad(x.y, y._m10_m11, result);
	result = mad(x.z, y._m20_m21, result);
	result = mad(x.w, y._m30_m31, result);
	return result;
}
MF3 MulAdd(MF4 x, MF4x3 y, MF3 a) {
	MF3 result = a;
	result = mad(x.x, y._m00_m01_m02, result);
	result = mad(x.y, y._m10_m11_m12, result);
	result = mad(x.z, y._m20_m21_m22, result);
	result = mad(x.w, y._m30_m31_m32, result);
	return result;
}
MF4 MulAdd(MF4 x, MF4x4 y, MF4 a) {
	MF4 result = a;
	result = mad(x.x, y._m00_m01_m02_m03, result);
	result = mad(x.y, y._m10_m11_m12_m13, result);
	result = mad(x.z, y._m20_m21_m22_m23, result);
	result = mad(x.w, y._m30_m31_m32_m33, result);
	return result;
}

#define O(t, x, y) t.SampleLevel(SP, pos + float2(x, y) * pt, 0)
#define V4 MF4
#define M4 MF4x4

#define L0(x, y) V4(O(T0, x, y))

void Pass4(uint2 blockStart, uint3 tid) {
	float2 pt = float2(GetInputPt());
	uint2 gxy = (Rmp8x8(tid.x) << 1) + blockStart;
	uint2 sz = GetOutputSize();
	if (gxy.x >= sz.x || gxy.y >= sz.y)
		return;
	float2 pos = ((gxy >> 1) + 0.5) * pt;
	V4 s0_0_0, s0_0_1, s0_0_2, s0_1_0, s0_1_1, s0_1_2, s0_2_0, s0_2_1, s0_2_2;
	V4 r0 = 0.0;
	r0 = V4(1.026e-04, 2.907e-04, -2.278e-04, -8.361e-05);
	s0_0_0 = L0(-1.0, -1.0); s0_0_1 = L0(0.0, -1.0); s0_0_2 = L0(1.0, -1.0);
	s0_1_0 = L0(-1.0, 0.0); s0_1_1 = L0(0.0, 0.0); s0_1_2 = L0(1.0, 0.0);
	s0_2_0 = L0(-1.0, 1.0); s0_2_1 = L0(0.0, 1.0); s0_2_2 = L0(1.0, 1.0);
	r0 = MulAdd(s0_0_0, M4(-2.078e-02, 2.658e-02, 5.912e-03, -8.754e-04, 3.267e-02, 6.010e-03, -8.934e-03, -7.844e-03, -3.699e-02, -2.191e-02, 1.024e-02, 1.211e-02, 2.276e-03, -2.706e-02, -1.511e-02, -6.482e-03), r0);
	r0 = MulAdd(s0_0_1, M4(4.173e-03, -2.643e-02, 4.702e-03, 8.715e-03, 1.479e-02, -1.440e-01, 3.235e-02, 3.772e-02, 1.870e-01, 1.372e-01, -6.517e-02, -4.455e-02, -1.782e-01, 9.614e-02, 5.090e-02, 1.126e-02), r0);
	r0 = MulAdd(s0_0_2, M4(9.667e-03, -4.513e-04, 6.245e-03, 1.301e-02, -5.169e-03, 1.161e-02, -1.311e-02, -1.338e-02, -2.069e-02, 2.227e-02, -7.714e-03, -3.542e-02, 1.850e-02, -5.652e-02, 1.112e-02, 4.749e-02), r0);
	r0 = MulAdd(s0_1_0, M4(-4.541e-01, 4.950e-02, -2.319e-01, 1.072e-01, 5.148e-02, -1.947e-02, 6.616e-02, 1.984e-02, -7.690e-02, 1.773e-02, -1.006e-01, -6.559e-02, 2.260e-03, -8.378e-03, -3.693e-02, -7.541e-02), r0);
	r0 = MulAdd(s0_1_1, M4(-8.618e-02, -6.200e-01, -3.466e-02, -3.779e-01, 5.723e-01, -2.387e-02, 6.342e-02, -4.658e-01, 1.304e-01, 1.130e-01, 7.051e-01, 5.566e-01, 2.580e-02, 3.877e-01, -5.566e-01, 1.724e-01), r0);
	r0 = MulAdd(s0_1_2, M4(-9.982e-03, 6.074e-03, 5.088e-03, -8.145e-03, -4.550e-02, 9.498e-02, -4.190e-02, -2.528e-02, 1.080e-02, -6.524e-02, -2.383e-02, 1.350e-01, -3.786e-03, 1.538e-01, 2.104e-02, -1.411e-01), r0);
	r0 = MulAdd(s0_2_0, M4(3.114e-02, -2.459e-02, -6.471e-02, 5.313e-02, -9.421e-03, 5.377e-03, 1.764e-02, 4.711e-03, 2.045e-02, 1.029e-02, -2.045e-02, 1.090e-02, 2.616e-02, -3.509e-03, 1.584e-02, 2.190e-02), r0);
	r0 = MulAdd(s0_2_1, M4(1.764e-02, 7.804e-02, -4.490e-02, -1.519e-01, -7.934e-02, 5.097e-03, 5.826e-02, 6.307e-03, -1.490e-02, -3.430e-02, 4.749e-02, -1.289e-02, -1.011e-02, -2.436e-02, 3.430e-02, 2.518e-02), r0);
	r0 = MulAdd(s0_2_2, M4(-3.636e-03, -1.442e-02, -1.291e-02, -2.985e-02, 1.788e-02, 5.287e-03, -1.129e-02, 1.125e-02, 1.328e-02, 3.210e-02, 1.753e-03, 1.867e-02, -4.918e-03, -3.528e-02, 2.455e-03, 5.595e-02), r0);
	static const MF3x3 RY = {0.299, 0.587, 0.114, -0.169, -0.331, 0.5, 0.5, -0.419, -0.081}, YR = {1, -0.00093, 1.401687, 1, -0.3437, -0.71417, 1, 1.77216, 0.00099};
	float2 opt = float2(GetOutputPt()), fpos = (float2(gxy) + 0.5) * opt;
	MF3 yuv;
	yuv = mul(RY, INPUT.SampleLevel(SL, fpos + float2(0.0, 0.0) * opt, 0).rgb);
	OUTPUT[gxy + int2(0, 0)] = MF4(mul(YR, MF3(saturate(yuv.r + r0.x), yuv.yz)), 1.0);
	yuv = mul(RY, INPUT.SampleLevel(SL, fpos + float2(1.0, 0.0) * opt, 0).rgb);
	OUTPUT[gxy + int2(1, 0)] = MF4(mul(YR, MF3(saturate(yuv.r + r0.y), yuv.yz)), 1.0);
	yuv = mul(RY, INPUT.SampleLevel(SL, fpos + float2(0.0, 1.0) * opt, 0).rgb);
	OUTPUT[gxy + int2(0, 1)] = MF4(mul(YR, MF3(saturate(yuv.r + r0.z), yuv.yz)), 1.0);
	yuv = mul(RY, INPUT.SampleLevel(SL, fpos + float2(1.0, 1.0) * opt, 0).rgb);
	OUTPUT[gxy + int2(1, 1)] = MF4(mul(YR, MF3(saturate(yuv.r + r0.w), yuv.yz)), 1.0);
}

[numthreads(64, 1, 1)]
void main(uint3 tid : SV_GroupThreadID, uint3 gid : SV_GroupID) {
	Pass4((gid.xy << 4), tid);
}
