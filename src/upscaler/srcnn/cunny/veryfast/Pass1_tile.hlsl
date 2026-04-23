// CuNNy-veryfast-NVL - Pass 1 - https://github.com/funnyplanter/CuNNy
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
    V4 r0 = 0.0, r1 = 0.0;

    s0_0_0 = L0(-1.0, -1.0); s0_0_1 = L0(0.0, -1.0); s0_0_2 = L0(1.0, -1.0);
    s0_1_0 = L0(-1.0, 0.0); s0_1_1 = L0(0.0, 0.0); s0_1_2 = L0(1.0, 0.0);
    s0_2_0 = L0(-1.0, 1.0); s0_2_1 = L0(0.0, 1.0); s0_2_2 = L0(1.0, 1.0);

    r0 += V4(-6.888e-02, -6.888e-02, -6.888e-02, -6.888e-02) * s0_0_0;
    r1 += V4(1.851e-01, -4.871e-03, -3.070e-02, 1.101e-02) * s0_0_0;

    r0 += V4(-1.549e-01, -1.549e-01, -1.549e-01, -1.549e-01) * s0_0_1;
    r1 += V4(7.661e-02, -6.060e-02, -9.364e-01, -1.294e-01) * s0_0_1;

    r0 += V4(-1.108e-01, -1.108e-01, -1.108e-01, -1.108e-01) * s0_0_2;
    r1 += V4(1.214e-01, 9.223e-01, 8.652e-01, 6.247e-01) * s0_0_2;

    r0 += V4(-1.392e-01, -1.392e-01, -1.392e-01, -1.392e-01) * s0_1_0;
    r1 += V4(3.154e-01, -6.001e-03, 2.772e-02, -1.979e-03) * s0_1_0;

    r0 += V4(-5.328e-02, -5.280e-02, -5.328e-02, -5.305e-02) * s0_1_1;
    r1 += V4(-5.801e-01, 7.592e-02, 1.241e-01, -1.242e-02) * s0_1_1;

    r0 += V4(-6.413e-02, -6.404e-02, -6.413e-02, -6.413e-02) * s0_1_2;
    r1 += V4(-1.627e-01, -9.043e-01, -5.475e-02, -1.605e-01) * s0_1_2;

    r0 += V4(-1.563e-01, -1.563e-01, -1.563e-01, -1.563e-01) * s0_2_0;
    r1 += V4(5.394e-02, 1.075e-02, -8.110e-03, 7.134e-03) * s0_2_0;

    r0 += V4(-7.254e-02, -7.254e-02, -7.254e-02, -7.254e-02) * s0_2_1;
    r1 += V4(1.842e-01, -1.932e-02, -5.528e-03, -3.423e-02) * s0_2_1;

    r0 += V4(-4.679e-02, -4.720e-02, -4.679e-02, -4.725e-02) * s0_2_2;
    r1 += V4(2.033e-02, -1.645e-02, 1.672e-02, 2.765e-02) * s0_2_2;

    r0 += V4(-6.993e-04, -2.343e-04, -6.993e-04, -3.475e-04);

    r0 = max(r0, 0.0);

    T0[uint3(gxy, tileParams.inputLayer)] = r0;

    r1 += V4(3.500e-03, 2.636e-04, 3.864e-04, 4.680e-03);

    r1 = max(r1, 0.0);

    T1[uint3(gxy, tileParams.inputLayer)] = r1;
}