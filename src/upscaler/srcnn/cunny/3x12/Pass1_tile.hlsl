// CuNNy-3x12-NVL - Pass 1 - https://github.com/funnyplanter/CuNNy
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

    r0 += mul(s0_0_0, M3x4(-8.004e-02, 3.306e-02, 2.809e-03, 1.799e-02, 4.088e-02, -1.101e-01, 1.779e-01, -6.916e-03, 6.212e-02, -1.051e-01, 8.316e-03, -1.999e-02));
    r1 += mul(s0_0_0, M3x4(-1.018e-03, 5.281e-02, -3.671e-03, -9.022e-04, 8.121e-03, 3.896e-01, 6.807e-03, -2.565e-03, -2.056e-03, 2.885e-02, -5.021e-03, 6.286e-03));
    r2 += mul(s0_0_0, M3x4(-6.619e-03, -6.941e-03, -9.951e-04, 2.560e-03, 1.368e-02, -8.019e-03, 8.860e-03, 3.502e-02, -1.219e-02, -1.648e-02, -1.284e-04, 1.618e-02));

    r0 += mul(s0_0_1, M3x4(-5.145e-02, -8.557e-02, 7.632e-02, 1.667e-02, 2.628e-02, 4.722e-01, 1.992e-01, -1.234e-01, 1.607e-02, 1.615e-01, -6.932e-03, -1.517e+00));
    r1 += mul(s0_0_1, M3x4(9.342e-03, 1.045e-01, 1.247e-02, 2.767e-02, -2.459e-02, 9.835e-02, -2.164e-02, 6.366e-02, 1.557e-03, 7.984e-02, 1.361e-02, 1.242e-02));
    r2 += mul(s0_0_1, M3x4(1.802e-01, 2.350e-02, -2.171e-03, 3.287e-02, 7.780e-01, 1.447e-02, -1.550e-03, 1.412e-01, 6.470e-02, 5.975e-03, -4.353e-03, 4.922e-03));

    r0 += mul(s0_0_2, M3x4(3.057e-01, 1.163e-01, -5.224e-02, -4.806e-02, -1.667e-01, 5.029e-02, 1.030e-01, 2.855e-02, -1.322e-01, -5.030e-02, 3.477e-02, 4.541e-01));
    r1 += mul(s0_0_2, M3x4(4.095e-03, -1.366e-01, 1.371e-02, 7.380e-03, 7.256e-03, -3.971e-01, -7.612e-03, -1.147e-02, -6.970e-03, -1.003e-01, -6.160e-03, -3.729e-03));
    r2 += mul(s0_0_2, M3x4(-1.672e-02, -5.558e-04, 1.079e-03, -1.867e-03, 2.246e-02, 3.502e-02, 4.412e-03, 1.433e-02, -1.110e-02, -5.331e-03, -2.294e-03, -2.783e-03));

    r0 += mul(s0_1_0, M3x4(-5.050e-01, -1.129e-01, 1.362e-01, -1.381e-01, 2.457e-01, 4.098e-01, 3.087e-01, -1.106e-01, 2.201e-01, 2.176e-02, 6.282e-02, 2.000e-01));
    r1 += mul(s0_1_0, M3x4(1.641e-02, -2.346e-02, 2.563e-02, -4.359e-04, -2.779e-02, 6.961e-02, -2.510e-02, 2.655e-02, 1.316e-02, 8.984e-03, -6.255e-04, 2.326e-03));
    r2 += mul(s0_1_0, M3x4(1.201e-02, -2.015e-02, -1.423e-02, -3.623e-02, -1.895e-02, 3.178e-02, 2.327e-02, 6.212e-02, 1.200e-02, 4.885e-03, 3.593e-03, 8.842e-03));

    r0 += mul(s0_1_1, M3x4(-8.829e-01, 1.794e-01, -3.974e-01, 6.902e-02, 4.236e-01, -2.352e+00, -8.976e-01, 3.539e-01, 4.229e-01, 1.710e-01, -8.174e-02, 1.806e-01));
    r1 += mul(s0_1_1, M3x4(-2.061e-01, -1.003e-01, -2.644e-01, -1.278e-01, -7.559e-01, -9.074e-01, -8.613e-01, -4.990e-01, -7.363e-02, -1.090e-01, -7.582e-02, -2.663e-02));
    r2 += mul(s0_1_1, M3x4(-1.855e-01, -3.328e-01, 2.014e-02, -1.061e-01, -7.715e-01, -1.080e+00, -3.037e-02, -6.953e-01, -6.446e-02, -8.815e-02, 1.773e-03, -3.069e-02));

    r0 += mul(s0_1_2, M3x4(4.815e-01, -9.921e-02, 9.823e-02, -2.057e-03, -2.357e-01, 3.492e-01, -2.543e-01, 2.569e-02, -2.200e-01, -9.123e-02, -3.606e-02, 1.597e-02));
    r1 += mul(s0_1_2, M3x4(1.336e-02, 1.433e-02, 2.036e-01, 1.491e-02, -2.435e-02, 4.806e-01, 9.176e-01, 3.480e-02, 2.033e-02, 5.692e-02, 7.300e-02, 1.008e-02));
    r2 += mul(s0_1_2, M3x4(3.352e-03, 3.727e-02, 2.577e-03, 3.610e-02, -1.435e-02, -2.008e-02, 1.104e-03, -6.423e-03, 1.849e-02, 1.964e-02, 1.142e-03, -1.254e-04));

    r0 += mul(s0_2_0, M3x4(9.755e-02, 7.786e-02, 4.177e-02, 3.039e-02, -5.141e-02, 1.119e-01, 1.274e-01, 4.471e-03, -2.445e-02, -1.436e-02, 2.118e-02, -6.314e-02));
    r1 += mul(s0_2_0, M3x4(-6.104e-03, -6.230e-02, -6.457e-03, -2.358e-03, 5.778e-03, -2.301e-01, 6.849e-03, -1.679e-02, -4.539e-03, -1.902e-02, -6.001e-04, -1.960e-03));
    r2 += mul(s0_2_0, M3x4(2.637e-03, 3.330e-01, 2.302e-01, 3.634e-02, -9.790e-04, 1.051e+00, 7.835e-01, 7.599e-02, -1.271e-03, 7.008e-02, 7.817e-02, 5.323e-03));

    r0 += mul(s0_2_1, M3x4(-1.597e-01, -4.237e-02, -2.068e-02, 1.278e-02, 7.768e-02, -2.273e-02, 1.392e-01, 1.641e-02, 8.793e-02, -3.311e-02, 4.318e-03, -2.049e-02));
    r1 += mul(s0_2_1, M3x4(1.882e-01, 4.531e-02, 1.395e-02, 5.440e-02, 7.944e-01, -3.128e-02, -2.484e-02, 7.494e-02, 6.330e-02, 6.745e-04, 3.291e-03, 1.395e-02));
    r2 += mul(s0_2_1, M3x4(4.550e-03, -5.659e-02, -2.260e-01, -7.046e-03, -6.486e-03, -1.208e-02, -7.871e-01, 1.704e-01, 2.202e-03, 4.179e-02, -8.120e-02, 1.672e-02));

    r0 += mul(s0_2_2, M3x4(2.425e-01, 2.374e-02, -2.404e-02, 1.450e-02, -1.131e-01, 1.969e-02, 8.958e-02, -1.023e-01, -1.361e-01, -2.301e-02, -4.773e-02, 4.883e-02));
    r1 += mul(s0_2_2, M3x4(-1.753e-02, 9.386e-02, 4.877e-03, 2.227e-03, 1.747e-02, 5.314e-01, 6.404e-03, -3.009e-02, -1.093e-02, 5.469e-02, -1.424e-03, -7.789e-03));
    r2 += mul(s0_2_2, M3x4(5.474e-03, 1.939e-02, -1.011e-02, 9.980e-03, 9.453e-04, -1.498e-02, -2.597e-03, 6.000e-02, -8.301e-03, -3.578e-02, 3.540e-03, -9.692e-03));

    r0 += V4(-3.838e-04, -1.473e-02, 2.105e-04, -1.662e-02);

    r0 = max(r0, 0.0);

    T0[uint3(gxy, tileParams.outputLayer)] = r0;

    r1 += V4(-5.161e-04, -7.702e-03, 5.444e-04, 5.153e-01);

    r1 = max(r1, 0.0);

    T1[uint3(gxy, tileParams.outputLayer)] = r1;

    r2 += V4(-1.625e-04, -4.639e-04, -6.901e-05, 1.916e-01);

    r2 = max(r2, 0.0);

    T2[uint3(gxy, tileParams.outputLayer)] = r2;
}