// CuNNy-faster-NVL - Pass 1 - https://github.com/funnyplanter/CuNNy
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
    uint2 dstOffset;
    uint margin;
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

    r0 += V4(1.353e-01, 1.984e-02, 1.211e-02, 7.598e-01) * s0_0_0;
    r1 += V4(-1.652e-02, 1.962e-02, 3.038e-01, -2.677e-02) * s0_0_0;

    r0 += V4(-3.271e-01, 1.228e-02, -7.949e-01, -7.767e-01) * s0_0_1;
    r1 += V4(-1.923e-03, 5.059e-01, 3.410e-01, 4.174e-02) * s0_0_1;

    r0 += V4(2.191e-02, 5.508e-03, 3.210e-03, 1.244e-02) * s0_0_2;
    r1 += V4(2.057e-02, -5.037e-03, 1.729e-01, -6.058e-03) * s0_0_2;

    r0 += V4(-7.642e-02, -2.865e-02, -5.194e-03, 1.476e-02) * s0_1_0;
    r1 += V4(9.685e-03, -4.657e-03, -2.844e-01, 5.297e-01) * s0_1_0;

    r0 += V4(7.368e-01, -3.904e-02, 7.920e-01, 1.424e-02) * s0_1_1;
    r1 += V4(-8.027e-01, -1.428e-02, -5.293e-01, -2.466e-01) * s0_1_1;

    r0 += V4(-5.454e-03, -1.669e-02, -4.788e-03, -2.104e-02) * s0_1_2;
    r1 += V4(6.826e-01, 1.992e-02, -2.191e-01, 5.138e-02) * s0_1_2;

    r0 += V4(-2.345e-03, -1.705e-01, -5.146e-03, -3.928e-03) * s0_2_0;
    r1 += V4(8.427e-04, -2.452e-02, 5.649e-02, -1.625e-03) * s0_2_0;

    r0 += V4(-5.449e-02, 4.110e-01, 6.028e-03, 1.676e-03) * s0_2_1;
    r1 += V4(1.616e-01, 1.001e-02, 2.011e-02, 4.106e-02) * s0_2_1;

    r0 += V4(2.678e-04, 1.965e-02, -2.196e-03, -5.237e-04) * s0_2_2;
    r1 += V4(-5.201e-02, 6.417e-03, 1.263e-01, -2.240e-02) * s0_2_2;

    r0 += V4(9.737e-03, 3.376e-04, -6.982e-05, 1.065e-04);

    r0 = max(r0, 0.0);

    T0[uint3(gxy, tileParams.inputLayer)] = r0;

    r1 += V4(-1.634e-03, 6.261e-03, 7.272e-03, 1.764e-03);

    r1 = max(r1, 0.0);

    T1[uint3(gxy, tileParams.inputLayer)] = r1;
}