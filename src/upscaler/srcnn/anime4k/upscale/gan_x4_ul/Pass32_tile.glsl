// Anime4K_Upscale_GAN_x4_UL - Pass 32 of 67 - https://github.com/bloc97/Anime4K
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
//    glslc -fshader-stage=compute --target-env=vulkan1.2 <this_file> -o <output.spv>
//
// -----------------------------------------------------------------------------
//
// MIT License
// Copyright (c) 2019-2021 bloc97
// All rights reserved.
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// -----------------------------------------------------------------------------
//  Constant buffer (binding = 0, set = 0)
//    Packed as 4 uint32 + 4 float:
//      [0] in_width    (uint)  - width of feature map for this pass
//      [1] in_height   (uint)  - height of feature map
//      [2] out_width   (uint)  - full output width (final pass only)
//      [3] out_height  (uint)  - full output height (final pass only)
//      [4] in_dx       (float) - 1.0 / in_width
//      [5] in_dy       (float) - 1.0 / in_height
//      [6] out_dx      (float) - 1.0 / out_width
//      [7] out_dy      (float) - 1.0 / out_height
// -----------------------------------------------------------------------------
//
// -----------------------------------------------------------------------------
//  Push constants (only in tile-mode shaders)
//    layout(push_constant) uniform TileParams {
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  inputLayer;      // array slice to read (0-based)
//        uint  margin;          // context margin (pixels in feature-map space)
//    } tile;
// -----------------------------------------------------------------------------
//
// =============================================================================

#version 450

layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

layout(set = 0, binding = 0) uniform Constants {
    uint in_width;
    uint in_height;
    uint out_width;
    uint out_height;
    float in_dx;
    float in_dy;
    float out_dx;
    float out_dy;
} ubo;

layout(set = 0, binding = 3072) uniform sampler pointSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(push_constant) uniform TileParams {
    uvec2 dstOffset;
    uvec2 tileOutExtent;
    uvec2 fullOut;
    uint inputLayer;
    uint margin;
} tile;

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_12_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_12_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_12_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_12_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_14_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_15_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.06566936, 0.050075732, -0.28377536, -0.008723959, -0.15360966, 0.017306754, 0.14521429, -0.3126355, -0.07001781, 0.24416047, 0.23609962, 0.095428005, 0.051152043, 0.047046803, -0.11905595, 0.084599525) * g_0;
    result += mat4(-0.054007493, -0.1917774, -0.12253726, -0.25697917, -0.13300818, -0.014515598, -0.06988327, 0.07294474, -0.17037617, -0.11330418, 0.15588778, -0.0024750067, 0.18527855, 0.16439237, 0.13763049, 0.14903007) * g_1;
    result += mat4(-0.06097875, 0.017688967, 0.084205635, -0.20286436, 0.06378928, 0.051785655, -0.00819132, 0.2283147, -0.0010928598, 0.19555786, -0.057957973, -0.1283918, 0.0130625125, 0.24465637, -0.029474005, -0.08648904) * g_2;
    result += mat4(0.2977628, -0.21103969, -0.046574663, 0.15004829, -0.22748028, -0.048065472, -0.25989944, 0.2236256, 0.07941025, -0.052161288, 0.04335678, -0.24627966, 0.07268186, -0.038388748, 0.035197932, 0.05556185) * g_3;
    result += mat4(-0.12658507, -0.200711, 0.10936925, 0.21350707, -0.05308915, -0.08038389, -0.21488698, 0.12463842, -0.039825447, -0.061766982, -0.16644825, -0.13220729, 0.12675424, -0.3512296, -0.28100672, -0.002683097) * g_4;
    result += mat4(0.16233717, 0.05970525, 0.028119681, -0.087842815, -0.06486345, -0.06930576, -0.15099292, -0.085598275, -0.11941735, -0.19621682, -0.19929451, -0.12694003, -0.23668842, -0.3260459, -0.1669464, 0.21992308) * g_5;
    result += mat4(-0.15114589, 0.3370156, 0.11051971, 0.15529542, -0.1644359, 0.03944235, -0.04013774, -0.07215706, 0.20360462, 0.083222464, 0.12099312, 0.02515875, -0.087714344, 0.13805264, -0.14398378, -0.27612263) * g_6;
    result += mat4(-0.07686366, 0.061692268, -0.017847976, -0.16373406, -0.06558452, 0.07674664, 0.11457862, -0.21175413, -0.21797107, -0.31008083, -0.016061796, 0.010659135, -0.0031505653, -0.06681698, -0.19412144, 0.16077086) * g_7;
    result += mat4(0.043644525, -0.02776246, 0.14185701, -0.027494097, -0.06645238, -0.19521286, -0.3502527, -0.028178494, -0.032492533, -0.32320002, 0.15325007, -0.3127702, 0.12887025, 0.18266484, -0.08985129, -0.34389883) * g_8;
    result += mat4(-0.05747523, -0.12848844, 0.19728723, -0.108118065, 0.056262556, 0.26523066, -0.17712027, 0.31646273, 0.058449365, 0.38118544, -0.08126795, 0.16811565, -0.024995815, -0.009981597, -0.047409683, 0.18652919) * g_9;
    result += mat4(-0.001337023, -0.32653907, 0.24057804, 0.18893267, 0.044070523, 0.25686195, -0.0058101956, 0.19947663, 0.31318483, 0.12546687, -0.04676781, 0.1793074, -0.19815332, -0.017479869, 0.2998801, -0.011709262) * g_10;
    result += mat4(0.021966469, 0.045877025, -0.22806744, 0.10764939, -0.13102953, -0.096345, 0.0801237, -0.21132103, -0.44632608, 0.02980375, -0.37176967, -0.2655013, 0.27665234, -0.29347885, 0.041475385, 0.024725065) * g_11;
    result += mat4(-0.21308075, 0.041253224, -0.109849155, -0.20893334, 0.09030459, 0.19662417, -0.100110866, -0.20908715, -0.060150456, 0.30329007, 0.18626331, 0.14155315, 0.07804046, -0.0916941, 0.27937013, -0.1512788) * g_12;
    result += mat4(0.13618731, -0.14704673, -0.071122654, 0.019604936, 0.1254093, -0.016677566, -0.087662145, -0.08561128, 0.16301125, 0.1387518, 0.10387402, 0.25537175, 0.07070756, -0.10887832, 0.028897746, 0.17835346) * g_13;
    result += mat4(-0.08490608, 0.026569808, -0.3456361, 0.020109842, -0.18946368, -0.12816896, 0.04407577, 0.029665362, 0.003496549, -0.31034058, 0.023039173, -0.016018149, -0.20683154, 0.23216362, 0.32729226, -0.12827688) * g_14;
    result += mat4(0.013153797, 0.027919725, 0.36677372, 0.12828171, 0.3900067, 0.2961308, -0.16830838, -0.07397908, 0.1868292, 0.09739989, -0.10895602, -0.19859214, -0.1334346, -0.19208196, 0.28900802, -0.06582624) * g_15;
    result += mat4(0.03638428, 0.035884462, -0.16868213, -0.038831823, -0.14761804, -0.08772457, 0.12720594, -0.045940604, 0.037369534, -0.02216757, 0.12334018, 0.08524158, -0.06456619, 0.017709045, 0.08379434, -0.2587099) * g_16;
    result += mat4(-0.14868304, 0.255881, -0.17220873, 0.1882922, -0.11029569, 0.05895402, 0.2143255, 0.18148275, 0.020576546, -0.10496286, -0.19348511, -0.11536339, 0.14612065, 0.27825454, -0.073165655, -0.20478225) * g_17;
    result += mat4(0.11683568, 0.05585525, -0.31354317, -0.060689308, -0.3203063, 0.116788305, -0.14543387, -0.02960584, 0.06610334, -0.11565926, -0.01838577, -0.33486378, 0.055412084, -0.2405772, -0.24344021, 0.23109037) * g_18;
    result += mat4(0.36880726, 0.042794302, 0.38861996, 0.15946254, -0.15122825, 0.3142487, -0.17530881, -0.07510673, 0.0400742, 0.1710061, -0.21697284, 0.26265535, 0.17539124, -0.04652943, 0.14543319, -0.32873863) * g_19;
    result += vec4(-0.003596251, -0.00022212608, -0.010425431, 0.014811408);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf1, ivec3(valid_xy, tile.inputLayer), result);
}