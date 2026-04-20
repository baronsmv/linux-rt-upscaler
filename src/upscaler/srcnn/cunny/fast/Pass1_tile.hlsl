// CuNNy-fast-NVL - Pass 1 - https://github.com/funnyplanter/CuNNy
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
    uint inputLayer;    // which layer to read from INPUT
    uint outputLayer;   // which layer to write to all outputs
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

#define L0(x, y) min16float(dot(float3(0.299, 0.587, 0.114), O(INPUT, x, y).rgb))

[numthreads(8,8,1)]
void main(uint3 id : SV_DispatchThreadID)
{
    float2 pt = float2(GetInputPt());
    uint2 gxy = id.xy;
    float2 pos = (gxy + 0.5) * pt;

    min16float s0_0_0, s0_0_1, s0_0_2, s0_1_0, s0_1_1, s0_1_2, s0_2_0, s0_2_1, s0_2_2;
    V4 r0 = 0.0, r1 = 0.0, r2 = 0.0;

    s0_0_0 = L0(-1.0, -1.0); s0_0_1 = L0(0.0, -1.0); s0_0_2 = L0(1.0, -1.0);
    s0_1_0 = L0(-1.0, 0.0); s0_1_1 = L0(0.0, 0.0); s0_1_2 = L0(1.0, 0.0);
    s0_2_0 = L0(-1.0, 1.0); s0_2_1 = L0(0.0, 1.0); s0_2_2 = L0(1.0, 1.0);

    r0 += V4(6.093e-02, 1.179e-03, 1.806e-02, -6.992e-02) * s0_0_0;
    r1 += V4(3.015e-03, -4.224e-03, -2.180e-02, -2.643e-02) * s0_0_0;
    r2 += V4(1.540e-02, 1.100e-02, 6.360e-02, 4.463e-01) * s0_0_0;

    r0 += V4(3.691e-01, -8.520e-02, 2.036e-01, 7.349e-02) * s0_0_1;
    r1 += V4(-1.158e-02, 1.407e-02, 2.771e-02, 7.273e-02) * s0_0_1;
    r2 += V4(-8.737e-03, -1.135e-01, -8.099e-04, -3.525e-01) * s0_0_1;

    r0 += V4(1.523e-02, 9.094e-02, -2.778e-02, -6.861e-03) * s0_0_2;
    r1 += V4(4.242e-03, -4.563e-03, 2.327e-02, -2.772e-02) * s0_0_2;
    r2 += V4(-1.014e-02, -1.007e-02, -5.456e-02, -1.189e-01) * s0_0_2;

    r0 += V4(-7.544e-02, 1.298e-02, -3.757e-02, 3.096e-01) * s0_1_0;
    r1 += V4(-1.040e-02, 2.754e-03, 1.169e-01, 9.726e-03) * s0_1_0;
    r2 += V4(7.381e-01, -1.548e-01, 2.285e-01, -4.252e-01) * s0_1_0;

    r0 += V4(-2.978e-01, -5.645e-01, -9.956e-03, -2.510e-01) * s0_1_1;
    r1 += V4(-8.340e-01, -8.240e-01, -5.527e-01, -1.687e-01) * s0_1_1;
    r2 += V4(-7.441e-01, 5.611e-01, 4.398e-01, 5.656e-01) * s0_1_1;

    r0 += V4(2.889e-02, 5.995e-01, 7.107e-02, -1.362e-02) * s0_1_2;
    r1 += V4(-1.516e-02, 8.145e-01, 3.788e-01, -2.730e-02) * s0_1_2;
    r2 += V4(1.063e-02, 3.516e-03, 3.635e-02, -1.155e-01) * s0_1_2;

    r0 += V4(-3.925e-03, -1.148e-02, -2.253e-02, -1.005e-02) * s0_2_0;
    r1 += V4(9.480e-03, -2.408e-03, -2.715e-02, -2.228e-02) * s0_2_0;
    r2 += V4(-1.037e-02, -2.452e-02, -3.012e-01, -1.674e-01) * s0_2_0;

    r0 += V4(1.529e-02, 6.681e-01, 3.094e-02, 5.111e-02) * s0_2_1;
    r1 += V4(8.431e-01, -2.199e-03, 4.065e-02, 2.382e-01) * s0_2_1;
    r2 += V4(1.257e-02, -7.065e-02, -4.877e-01, -8.929e-02) * s0_2_1;

    r0 += V4(2.772e-03, -7.090e-01, -4.582e-02, 1.679e-02) * s0_2_2;
    r1 += V4(9.945e-03, 5.921e-03, 4.050e-04, 2.319e-01) * s0_2_2;
    r2 += V4(-5.354e-03, -6.593e-02, 6.959e-02, 2.536e-01) * s0_2_2;

    r0 += V4(3.827e-04, -2.238e-03, 2.436e-02, 1.030e-02);

    r0 = max(r0, 0.0);

    T0[uint3(gxy, tileParams.outputLayer)] = r0;

    r1 += V4(2.205e-04, -5.557e-05, 3.012e-02, 1.121e-02);

    r1 = max(r1, 0.0);

    T1[uint3(gxy, tileParams.outputLayer)] = r1;

    r2 += V4(-1.399e-04, 1.295e-03, -5.445e-04, -8.903e-04);

    r2 = max(r2, 0.0);

    T2[uint3(gxy, tileParams.outputLayer)] = r2;
}