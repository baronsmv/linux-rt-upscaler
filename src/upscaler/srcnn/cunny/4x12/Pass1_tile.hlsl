// CuNNy-4x12-NVL - Pass 1 - https://github.com/funnyplanter/CuNNy
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
// dxc -T cs_6_0 -E main -spirv <this_file> \
//     -fvk-auto-shift-bindings \
//     -fvk-t-shift 1024 0 \
//     -fvk-u-shift 2048 0 \
//     -fvk-s-shift 3072 0 \
//     -fvk-use-dx-layout \
//     -fvk-use-scalar-layout \
//     -Fo <output.spv>
//
// =============================================================================
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// 
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
// =============================================================================

cbuffer Constants : register(b0) {
    uint in_width;
    uint in_height;
    uint out_width;
    uint out_height;
    float in_dx;
    float in_dy;
    float out_dx;
    float out_dy;
};

struct TileParams {
    uint inputLayer;
    uint2 srcOffset;
    uint2 dstOffset;
    uint margin;
    uint cropWidth;
    uint cropHeight;
    uint fullOutWidth;
    uint fullOutHeight;
    uint2 validOffset;
    uint2 tileOutExtent;
    uint outputLayer;
};
[[vk::push_constant]] TileParams tileParams;

float2 GetInputPt() { return float2(in_dx, in_dy); }
float2 GetOutputPt() { return float2(out_dx, out_dy); }
uint2 GetInputSize() { return uint2(in_width, in_height); }
uint2 GetOutputSize() { return uint2(out_width, out_height); }

#define O(t, x, y) t.SampleLevel(SP, float3(pos + float2(x, y) * pt, tileParams.inputLayer), 0)
#define V4 min16float4
#define M4 min16float4x4
#define V3 min16float3
#define M3x4 min16float3x4

Texture2DArray<float4> INPUT : register(t0);

[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T0 : register(u0);
[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T1 : register(u1);
[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T2 : register(u2);

SamplerState SP : register(s0);
SamplerState SL : register(s1);

#define L0(x, y) V3(O(INPUT, x, y).rgb)

[numthreads(8,8,1)]
void main(uint3 id : SV_DispatchThreadID)
{
    float2 pt = float2(GetInputPt());
    uint2 gxy = id.xy;
    float2 pos = (gxy + 0.5) * pt;

    V3 s0_0_0, s0_0_1, s0_0_2, s0_1_0, s0_1_1, s0_1_2, s0_2_0, s0_2_1, s0_2_2;
    V4 r0 = 0.0, r1 = 0.0, r2 = 0.0;

    s0_0_0 = L0(-1.0, -1.0); s0_0_1 = L0(0.0, -1.0); s0_0_2 = L0(1.0, -1.0);
    s0_1_0 = L0(-1.0, 0.0); s0_1_1 = L0(0.0, 0.0); s0_1_2 = L0(1.0, 0.0);
    s0_2_0 = L0(-1.0, 1.0); s0_2_1 = L0(0.0, 1.0); s0_2_2 = L0(1.0, 1.0);

    r0 += mul(s0_0_0, M3x4(-7.386e-03, -5.469e-02, 1.746e-02, -7.538e-02, -4.545e-02, -4.873e-01, -4.916e-02, -1.283e-01, -2.024e-03, -3.993e-02, 5.444e-03, 2.504e-01));
    r1 += mul(s0_0_0, M3x4(-7.243e-02, 5.732e-04, 1.089e-01, 2.781e-02, -6.259e-02, 1.818e-03, 5.067e-01, -1.359e-03, 3.032e-02, -5.970e-03, -7.168e-03, -4.071e-03));
    r2 += mul(s0_0_0, M3x4(-3.235e-03, -8.249e-03, 5.048e-03, 2.856e-03, 1.328e-02, 5.994e-02, 2.688e-02, -9.917e-03, -7.008e-03, 1.200e-02, -5.993e-05, 1.259e-02));

    r0 += mul(s0_0_1, M3x4(-4.481e-02, -4.577e-02, -2.425e-01, 8.612e-02, -1.968e-01, 2.938e-02, -9.121e-01, -7.690e-02, -1.899e-02, 3.110e-03, -1.540e-01, -1.780e+00));
    r1 += mul(s0_0_1, M3x4(-1.152e-01, 1.819e-02, 1.569e-02, 2.558e-01, -6.440e-02, -3.147e-02, 5.094e-02, 8.379e-01, -8.025e-02, 9.843e-03, 1.203e-02, 7.306e-02));
    r2 += mul(s0_0_1, M3x4(-1.968e-03, -2.847e-03, -4.148e-03, -2.091e-01, -6.473e-03, 9.986e-03, 4.125e-02, -8.573e-01, 6.614e-03, -3.453e-02, 2.267e-03, -6.174e-02));

    r0 += mul(s0_0_2, M3x4(-4.561e-03, 6.066e-02, 2.461e-01, -6.254e-02, -3.035e-02, 1.289e-01, 8.730e-01, -9.420e-03, -7.786e-04, 1.935e-02, 1.362e-01, 3.951e-01));
    r1 += mul(s0_0_2, M3x4(1.164e+00, -5.721e-04, -2.677e-02, -2.235e-02, 5.593e-01, 1.732e-02, 3.845e-02, 2.547e-02, 1.626e-01, -1.258e-02, -1.786e-02, -6.332e-03));
    r2 += mul(s0_0_2, M3x4(-5.411e-03, -1.579e-02, 6.164e-05, 3.549e-03, -1.140e-03, -7.766e-02, -1.922e-02, -2.055e-02, -3.550e-03, 1.331e-02, 1.014e-03, -1.736e-03));

    r0 += mul(s0_1_0, M3x4(-5.236e-02, -1.606e-01, -1.882e-02, 6.696e-03, -1.711e-01, -3.822e-01, 4.992e-02, 9.131e-02, -2.025e-02, -2.197e-02, -9.928e-03, 4.434e-02));
    r1 += mul(s0_1_0, M3x4(7.801e-04, 1.954e-03, -1.577e-01, -2.695e-01, -9.303e-03, -8.061e-03, -6.738e-01, -8.372e-01, 2.277e-03, 4.330e-03, 2.384e-02, -9.592e-02));
    r2 += mul(s0_1_0, M3x4(4.204e-02, 4.112e-02, -6.321e-03, -9.850e-03, 8.119e-02, -4.919e-02, 5.286e-03, 2.945e-03, 1.587e-02, -4.608e-03, 6.811e-03, -9.825e-03));

    r0 += mul(s0_1_1, M3x4(1.547e-01, 1.787e-01, 2.570e-01, -1.229e-02, 7.285e-01, 6.604e-01, 8.773e-01, 1.478e-01, 5.629e-02, 6.842e-02, 1.870e-01, 2.441e-01));
    r1 += mul(s0_1_1, M3x4(-5.694e-02, -1.830e-01, 2.021e-02, -1.896e-02, -5.155e-02, -8.613e-01, 5.923e-02, -2.199e-02, -4.334e-02, -5.851e-02, -2.120e-02, 4.841e-02));
    r2 += mul(s0_1_1, M3x4(5.260e-02, 3.307e-02, 1.349e-01, 2.220e-01, 3.151e-01, 3.018e-01, 5.776e-01, 8.574e-01, 2.537e-02, 6.137e-02, 4.454e-02, 4.895e-02));

    r0 += mul(s0_1_2, M3x4(-1.901e-02, -3.397e-04, -2.533e-01, 6.013e-02, -2.369e-02, 9.543e-02, -8.429e-01, 1.395e-02, 2.221e-03, -9.763e-03, -1.653e-01, -8.905e-02));
    r1 += mul(s0_1_2, M3x4(-2.009e-01, 1.782e-01, 1.372e-02, -3.673e-03, -2.411e-01, 8.752e-01, -2.155e-02, 1.346e-02, -2.332e-02, 4.865e-02, -5.773e-03, 1.563e-03));
    r2 += mul(s0_1_2, M3x4(2.545e-03, -2.133e-01, -2.288e-02, -7.434e-03, 7.792e-02, -8.770e-01, -7.027e-02, 2.110e-02, 3.652e-03, 5.824e-02, -2.055e-02, 8.632e-03));

    r0 += mul(s0_2_0, M3x4(-4.618e-03, 7.533e-02, 3.191e-04, 2.329e-02, -5.662e-03, 2.104e-01, -1.219e-02, -5.316e-02, 4.399e-03, 8.012e-03, 9.658e-03, -4.013e-03));
    r1 += mul(s0_2_0, M3x4(1.214e-02, -4.554e-03, 1.340e-02, 2.632e-02, 1.650e-02, -7.431e-05, -8.060e-03, -1.084e-03, -2.011e-02, -4.600e-04, -2.877e-02, -1.232e-02));
    r2 += mul(s0_2_0, M3x4(6.979e-02, -2.692e-02, 7.482e-03, 6.417e-03, 3.348e-01, 3.505e-02, 3.129e-02, 5.542e-03, -1.225e-02, -1.401e-02, -1.266e-03, 8.324e-04));

    r0 += mul(s0_2_1, M3x4(-1.724e-03, 5.198e-03, 1.529e-03, -2.257e-02, 3.968e-03, 5.456e-02, 6.396e-02, 1.018e-01, 1.426e-03, -8.712e-03, 7.497e-03, 2.531e-02));
    r1 += mul(s0_2_1, M3x4(-1.016e-03, -1.151e-03, -2.179e-02, 2.617e-04, 2.426e-03, -2.212e-02, 1.129e-02, -7.126e-03, -3.228e-02, 2.641e-02, -1.260e-03, -6.232e-03));
    r2 += mul(s0_2_1, M3x4(-2.182e-01, 3.730e-02, -2.093e-02, -1.364e-02, -1.346e+00, 1.938e-01, -4.649e-02, 5.817e-03, -3.633e-02, -2.405e-02, -1.693e-02, 5.099e-04));

    r0 += mul(s0_2_2, M3x4(1.103e-04, -6.213e-02, -1.111e-02, 3.962e-03, 7.550e-03, -3.073e-01, -4.484e-02, -4.740e-02, -9.361e-03, -1.714e-02, -1.528e-02, 3.008e-02));
    r1 += mul(s0_2_2, M3x4(-3.040e-02, -9.259e-03, -3.092e-03, 2.860e-03, -6.506e-03, 2.856e-02, -3.184e-03, -6.592e-03, 9.029e-03, -1.179e-02, 2.493e-02, 2.025e-03));
    r2 += mul(s0_2_2, M3x4(2.447e-02, 1.106e-01, 5.033e-03, 4.270e-03, 5.833e-02, 3.534e-01, 5.783e-03, -7.361e-03, -2.033e-02, -4.764e-02, 1.376e-02, 2.350e-03));

    r0 += V4(2.371e-02, 1.429e-03, -1.518e-03, -1.126e-03);

    r0 = max(r0, 0.0);

    T0[uint3(gxy, tileParams.inputLayer)] = r0;

    r1 += V4(-8.419e-01, -3.915e-04, 7.733e-04, 1.825e-07);

    r1 = max(r1, 0.0);

    T1[uint3(gxy, tileParams.inputLayer)] = r1;

    r2 += V4(-3.869e-02, 5.169e-03, -1.235e-04, -4.538e-04);

    r2 = max(r2, 0.0);

    T2[uint3(gxy, tileParams.inputLayer)] = r2;
}