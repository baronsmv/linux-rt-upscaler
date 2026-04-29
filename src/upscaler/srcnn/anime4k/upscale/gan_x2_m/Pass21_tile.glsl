// Anime4K_Upscale_GAN_x2_M - Pass 21 of 23 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv0ups1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max(-(texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.15938057, -0.23559119, -0.28445953, 0.05912659, 0.5229142, -0.02843545, -0.004113748, -0.056947608, 0.1367782, -0.026573306, -0.0056468234, 0.2564603, 0.25593445, 0.08957574, 0.26139608, -0.053708326) * g_0;
    result += mat4(0.1382045, -0.103480555, 0.05831098, 0.000735441, 0.20176832, -0.087079, -0.07839967, -0.0750771, -0.31373122, -0.27509713, -0.23071732, -0.2560584, 0.110963896, -0.052200988, 0.0015331429, -0.30707568) * g_1;
    result += mat4(-0.056460302, 0.2147989, 0.40628514, -0.058157466, -0.17940372, -0.033689886, -0.022241283, -0.0018471872, 0.26578268, -0.098452985, -0.01501511, -0.35676336, -0.07152056, -0.07245194, -0.32194778, 0.03888747) * g_2;
    result += mat4(0.09541087, 0.24680884, -0.045627397, -0.08557985, 0.08790337, 0.10179883, 0.3007415, 0.044102084, 0.1064372, 0.2994135, 0.15280741, 0.2683849, 0.24750276, -0.021364288, -0.004039902, 0.28266376) * g_3;
    result += mat4(-0.26525706, -0.08389754, -0.10918147, -0.06878537, -0.080960914, 0.03737948, 0.107663736, -0.0025957434, -0.10748625, 0.03004828, 0.03505711, 0.075969726, 0.06360464, -0.02740913, 0.025467616, 0.017698402) * g_4;
    result += mat4(-0.2370006, -0.07687027, 0.015225365, 0.17986605, 0.37507248, 0.2088343, 0.17946883, 0.2379337, -0.25194344, 0.035336476, -0.15362923, -0.008527836, 0.045963865, 0.025127884, 0.06973296, 0.063168526) * g_5;
    result += mat4(0.09583503, 0.15350054, -0.15248272, 0.045916792, -0.18339546, -0.29747355, 0.027330166, -0.39461568, 0.095963046, -0.1775004, -0.19221638, -0.15368307, 0.056089737, 0.18232727, 0.03182419, 0.30851522) * g_6;
    result += mat4(-0.053062204, -0.0018095247, -0.04514637, 0.05689337, 0.07561519, 0.17035827, -0.0048587993, 0.38348997, -0.063476466, 0.09454219, 0.03969728, 0.11693653, -0.0012066896, -0.25955358, -0.14428577, -0.19967856) * g_7;
    result += mat4(0.034378257, 0.16030714, 0.05160261, 0.21927983, -0.14469208, 0.041181874, 0.034202367, 0.07983977, 0.22149332, -0.08595994, -0.102985874, -0.07265774, -0.123233125, -0.12819915, 0.08662329, -0.12866889) * g_8;
    result += mat4(-0.1511104, -0.056531575, -0.023363205, -0.1909304, -0.15387732, 0.0671428, -0.15435332, 0.32735124, -0.3293996, 0.055349957, -0.043602336, 0.08102016, 0.200238, 0.13393362, 0.0044564987, 0.16932343) * g_9;
    result += mat4(-0.09768015, 0.09503259, 0.12768175, 0.109941825, 0.006567291, -0.102840215, -0.05611706, -0.06865725, -0.2605998, 0.00585688, -0.035119556, -0.06810342, -0.090756536, -0.079376444, -0.22370447, -0.05727839) * g_10;
    result += mat4(-0.101120085, 0.028628688, 0.07296149, 0.15868604, 0.047761433, 0.07732842, -0.016735386, 0.049528413, 0.45619023, 0.062347047, -0.026208224, 0.046785966, -0.05715451, 0.04459997, -0.13676195, 0.07778552) * g_11;
    result += mat4(-0.051393595, -0.12524572, -0.36763692, 0.039426118, 0.0349489, 0.07154008, -0.12969223, 0.30249006, -0.15237582, -0.06685149, -0.042049125, -0.0065471376, 0.017375907, -0.07143284, -0.018227521, -0.02778629) * g_12;
    result += mat4(-0.048270147, -0.07275859, 0.05502608, -0.034233145, 0.12822276, -0.02580663, -0.035358194, 0.05195595, 0.044340245, 0.04435722, 0.017985033, 0.007126749, -0.052825354, -0.059360538, -0.09412195, 0.060212586) * g_13;
    result += mat4(-0.18645881, -0.04506676, -0.035483524, 0.0063163475, -0.13747677, -0.046985928, 0.0015511635, 0.019160518, -0.4315584, -0.06979354, -0.001936674, 0.0034739177, 0.3490474, 0.15375568, -0.0085117165, 0.017511753) * g_14;
    result += mat4(0.20412005, 0.017221482, 0.08719384, -0.016668927, 0.10308073, -0.1013255, 0.087567665, -0.1004404, 0.9800944, -0.25387812, 0.36526182, -0.21970014, 0.36388537, -0.111629054, 0.21855496, -0.10375334) * g_15;
    result += vec4(-0.14657217, -0.04252579, -0.24773599, 0.13271233);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups1, ivec3(valid_xy, tile.inputLayer), result);
}