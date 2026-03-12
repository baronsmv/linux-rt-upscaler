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
Texture2D<MF4> T2 : register(t0);
Texture2D<MF4> T3 : register(t1);
RWTexture2D<unorm MF4> T0 : register(u0);
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

#define L0(x, y) V4(O(T2, x, y))
#define L1(x, y) V4(O(T3, x, y))

void Pass3(uint2 blockStart, uint3 tid) {
	float2 pt = float2(GetInputPt());
	uint2 gxy = Rmp8x8(tid.x) + blockStart;
	uint2 sz = GetInputSize();
	if (gxy.x >= sz.x || gxy.y >= sz.y)
		return;
	float2 pos = (gxy + 0.5) * pt;
	V4 s0_0_0, s0_0_1, s0_0_2, s0_1_0, s0_1_1, s0_1_2, s0_2_0, s0_2_1, s0_2_2, s1_0_0, s1_0_1, s1_0_2, s1_1_0, s1_1_1, s1_1_2, s1_2_0, s1_2_1, s1_2_2;
	V4 r0 = 0.0;
	s0_0_0 = L0(-1.0, -1.0); s0_0_1 = L0(0.0, -1.0); s0_0_2 = L0(1.0, -1.0);
	s0_1_0 = L0(-1.0, 0.0); s0_1_1 = L0(0.0, 0.0); s0_1_2 = L0(1.0, 0.0);
	s0_2_0 = L0(-1.0, 1.0); s0_2_1 = L0(0.0, 1.0); s0_2_2 = L0(1.0, 1.0);
	s1_0_0 = L1(-1.0, -1.0); s1_0_1 = L1(0.0, -1.0); s1_0_2 = L1(1.0, -1.0);
	s1_1_0 = L1(-1.0, 0.0); s1_1_1 = L1(0.0, 0.0); s1_1_2 = L1(1.0, 0.0);
	s1_2_0 = L1(-1.0, 1.0); s1_2_1 = L1(0.0, 1.0); s1_2_2 = L1(1.0, 1.0);
	r0 = MulAdd(s0_0_0, M4(-8.148e-03, 2.568e-02, 4.651e-02, -7.485e-02, 1.790e-02, -8.190e-02, -1.489e-01, 1.323e-01, 3.400e-02, 6.812e-02, 3.208e-02, -2.434e-02, 6.154e-02, 8.815e-02, 6.566e-02, 5.507e-02), r0);
	r0 = MulAdd(s0_0_1, M4(3.119e-02, -4.280e-03, -6.519e-03, 1.538e-01, -2.105e-01, -1.431e-01, -1.406e-01, -4.139e-01, 8.038e-02, -1.392e-01, 9.856e-03, -9.555e-02, 1.765e-01, 2.941e-01, 9.466e-02, 3.756e-01), r0);
	r0 = MulAdd(s0_0_2, M4(-1.209e-01, 4.339e-02, -7.104e-02, -6.860e-02, 4.313e-02, -1.887e-01, 1.963e-02, -4.690e-02, -6.567e-02, -1.265e-01, -4.360e-02, -1.146e-01, -5.670e-02, 1.087e-01, -4.472e-02, 1.739e-02), r0);
	r0 = MulAdd(s0_1_0, M4(-4.968e-02, -1.421e-01, 3.657e-02, -2.672e-01, -7.897e-04, -3.623e-01, 3.450e-02, -2.245e-01, -4.632e-03, -1.128e-01, -1.792e-01, 5.298e-01, 1.125e-01, -1.141e-01, -8.822e-02, 6.274e-02), r0);
	r0 = MulAdd(s0_1_1, M4(-1.880e-01, -3.701e-01, -1.155e-01, 3.115e-01, 3.475e-01, 8.071e-01, 7.021e-01, -3.410e-01, -2.617e-01, 1.043e+00, -3.493e-01, -2.318e-01, -4.900e-01, -5.969e-01, -1.215e-01, -3.721e-01), r0);
	r0 = MulAdd(s0_1_2, M4(3.329e-01, 1.936e-01, 1.228e-01, -1.891e-02, -3.213e-01, -4.152e-01, -1.440e-01, 4.134e-02, 2.842e-01, -5.296e-02, 3.641e-01, 5.137e-01, 1.812e-01, 8.146e-02, 1.061e-01, 3.798e-02), r0);
	r0 = MulAdd(s0_2_0, M4(-6.376e-03, 2.285e-01, 5.671e-02, -8.081e-02, -9.302e-02, -1.174e-01, -1.714e-01, 2.654e-02, -1.334e-02, 1.460e-01, 5.519e-02, -1.432e-01, 3.235e-02, 5.162e-02, 3.121e-02, 6.723e-03), r0);
	r0 = MulAdd(s0_2_1, M4(1.175e-01, -3.771e-02, 5.432e-02, 3.030e-01, 1.248e-01, 3.087e-02, -5.464e-02, 9.374e-02, 1.291e-01, 2.582e-02, 2.026e-01, 3.218e-02, -3.019e-02, -6.113e-02, 1.022e-03, -1.526e-02), r0);
	r0 = MulAdd(s0_2_2, M4(-4.480e-02, 4.266e-02, -1.878e-02, -7.446e-02, 4.263e-02, -1.403e-01, -1.898e-01, -1.598e-01, -4.898e-02, -1.334e-01, -4.467e-03, 2.087e-02, 6.375e-03, 8.764e-02, 7.014e-02, 3.828e-02), r0);
	r0 = MulAdd(s1_0_0, M4(-1.823e-02, -5.078e-02, -4.285e-02, 4.404e-02, -9.971e-03, -3.043e-02, -1.849e-02, 1.066e-01, 1.313e-02, 2.819e-02, 6.397e-02, -4.005e-02, -2.264e-02, -4.141e-02, -6.211e-02, 2.856e-02), r0);
	r0 = MulAdd(s1_0_1, M4(-1.643e-01, -6.951e-02, -5.324e-02, -1.595e-01, 4.259e-02, 1.606e-01, 2.015e-02, -3.517e-04, 7.591e-02, 1.665e-01, 1.284e-01, 1.572e-01, -8.479e-02, -9.076e-02, -3.720e-02, -7.167e-02), r0);
	r0 = MulAdd(s1_0_2, M4(1.875e-01, 4.330e-02, 7.509e-02, 9.155e-02, 1.067e-01, -9.226e-03, 6.569e-02, 1.057e-01, 9.918e-02, 2.543e-03, 6.361e-02, 4.849e-02, -3.967e-02, 9.021e-02, -2.580e-02, -8.976e-03), r0);
	r0 = MulAdd(s1_1_0, M4(7.936e-03, 4.667e-02, 1.710e-01, -5.760e-01, 5.680e-03, 6.270e-01, 3.174e-01, 4.808e-02, 7.891e-03, -5.142e-03, 1.486e-02, -1.813e-02, -2.654e-02, -6.394e-01, -8.960e-02, -4.404e-01), r0);
	r0 = MulAdd(s1_1_1, M4(-9.929e-04, -5.820e-01, 1.195e-01, 4.442e-01, 9.473e-01, -7.623e-01, 3.154e-01, -6.255e-01, 4.396e-04, 7.951e-01, -1.909e-01, 1.098e+00, -2.184e-02, -4.709e-01, -1.576e-01, -5.169e-01), r0);
	r0 = MulAdd(s1_1_2, M4(3.076e-01, 2.549e-01, 2.183e-01, 2.803e-01, -6.310e-01, -3.174e-01, -4.287e-01, -4.186e-01, 1.036e-02, 1.632e-01, -9.137e-04, -2.596e-02, -2.581e-02, -9.876e-03, 6.714e-02, 3.123e-02), r0);
	r0 = MulAdd(s1_2_0, M4(7.675e-03, 5.052e-03, -3.337e-02, 9.983e-02, 1.332e-02, 1.577e-01, 1.304e-01, 1.257e-01, -6.344e-03, 1.044e-01, 5.069e-02, 2.343e-02, 8.552e-02, -9.318e-01, -1.662e-02, -5.734e-01), r0);
	r0 = MulAdd(s1_2_1, M4(-3.231e-02, 9.578e-02, -6.091e-02, -1.283e-01, 8.889e-02, -7.374e-02, 1.334e-01, 2.598e-02, 2.393e-01, 8.617e-02, 3.545e-01, 9.125e-02, 3.194e-01, 6.674e-01, -2.021e-02, -1.412e-01), r0);
	r0 = MulAdd(s1_2_2, M4(9.790e-02, 1.380e-02, 4.626e-02, 9.249e-02, 8.255e-03, 6.021e-02, 2.871e-04, 1.201e-01, 1.724e-01, 1.096e-01, 1.130e-01, 1.430e-01, -4.326e-01, -3.163e-01, -1.880e-01, -1.765e-01), r0);
	r0 = max(r0, 0.0);
	T0[gxy] = r0;
}

[numthreads(64, 1, 1)]
void main(uint3 tid : SV_GroupThreadID, uint3 gid : SV_GroupID) {
	Pass3((gid.xy << 3), tid);
}
