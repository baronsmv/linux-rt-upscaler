// Anime4K_Upscale_GAN_x3_VL - Pass 32 of 47 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_15_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_15_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_15_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_17_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_18_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_15_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_15_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_15_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_15_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_15_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_15_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_17_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_17_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.06229179, 0.07447952, 0.17544238, -0.029056227, 0.23295781, -0.25401062, 0.060630303, -0.26968777, -0.06298657, 0.23999286, 0.07138117, -0.12207766, 0.3314945, -0.060328502, -0.05256118, -0.11967128) * g_0;
    result += mat4(0.009106781, -0.15019597, 0.107759155, -0.013013227, -0.1201809, 0.18982023, -0.084957175, 0.03017393, 0.02300354, 0.16276407, 0.20732218, -0.07420877, -0.18172643, 0.14273722, -0.11420885, -0.13387239) * g_1;
    result += mat4(-0.091283925, 0.125469, 0.15440796, 0.03595249, 0.1367125, -0.26021275, -0.034883995, 0.1384171, 0.034683395, 0.012753063, 0.059117932, -0.060619134, 0.018635055, -0.20502415, 0.026565414, 0.25979492) * g_2;
    result += mat4(0.016796626, 0.15069105, -0.061102454, 0.023371994, -0.08180385, 0.018199123, -0.0563611, 0.23894419, -0.06728213, 0.11131519, 0.03154735, -0.05907408, -0.1616918, -0.247807, 0.12373462, 0.04899162) * g_3;
    result += mat4(-0.29031062, 0.28420377, 0.038582914, 0.27378574, -0.08802812, 0.053966224, 0.018315062, 0.0067930855, 0.036932472, -0.041048605, 0.03820459, -0.0073364014, 0.10362766, 0.026039885, -0.23032854, -0.1956355) * g_4;
    result += mat4(-0.12793514, 0.28202888, 0.12303155, 0.29286426, -0.28697783, 0.012021052, 0.27789843, 0.055134546, 0.1095386, -0.05251396, -0.2255559, -0.17143604, -0.1668448, -0.047896937, 0.083351046, 0.14768548) * g_5;
    result += mat4(-0.16652593, -0.1171025, 0.046261553, -0.092330426, 0.45466834, -0.12058069, -0.3161383, -0.008391166, 0.16704272, 0.08296244, -0.15564027, -0.27613795, 0.020327646, -0.122191355, -0.050283693, 0.03534835) * g_6;
    result += mat4(-0.01564193, 0.13914119, 0.07802687, -0.1896753, -0.23644254, 0.15426877, 0.064588614, 0.15104239, -0.007543932, 0.14882818, 0.0395721, 0.04181466, -0.07785041, -0.31100297, 0.1204594, 0.12991908) * g_7;
    result += mat4(0.13514097, -0.06449617, 0.038062695, -0.24076426, 0.07944077, -0.0040154266, 0.026618825, -0.2406117, -0.020159021, 0.027010564, -0.21324417, -0.0008397984, 0.15394984, 0.07287525, 0.12330107, 0.20474261) * g_8;
    result += mat4(-0.034830973, -0.021657703, -0.14613967, 0.1852407, 0.28907514, 0.0729019, -0.104028866, -0.067935266, 0.005923615, -0.07949258, -0.01123202, -0.057730585, -0.006548943, -0.045705102, -0.1578812, 0.048652157) * g_9;
    result += mat4(0.07865155, -0.1089475, 0.2799939, 0.04209442, -0.062469423, 0.06282737, -0.309991, 0.056344055, -0.1911143, 0.14326468, 0.08484205, -0.19620831, -0.082943305, -0.10082107, -0.1514525, -0.014929943) * g_10;
    result += mat4(-0.2911379, 0.3363872, -0.043308917, 0.22365907, 0.034437142, -0.020528575, 0.21208636, 0.3034834, 0.012269259, 0.03488268, 0.030740876, 0.20943925, 0.005626004, 0.1601836, -0.012430659, -0.06502019) * g_11;
    result += mat4(0.15755813, 0.016292375, 0.02457799, 0.13753077, 0.12852463, 0.058444835, 0.29067582, -0.14437278, -0.10174013, 0.029764764, 0.0038154817, -0.18069993, 0.12908849, 0.09049112, 0.020467235, 0.02675185) * g_12;
    result += mat4(-0.30425274, 0.172061, -0.04473515, -0.27572066, -0.04441604, -0.0135015845, -0.02134299, -0.030247632, -0.18199432, 0.13888723, -0.1234305, 0.093817785, 0.09853002, 0.12676361, -0.0044124853, -0.0006500754) * g_13;
    result += mat4(-0.086448506, -0.09585741, 0.18680948, -0.1595373, -0.0013524789, -0.15327513, -0.24068208, -0.005388094, -0.05461273, 0.08730604, -0.105776325, 0.10966634, 0.17866546, 0.02331487, -0.26239154, 0.05888688) * g_14;
    result += mat4(-0.10371749, 0.18664865, -0.085673355, 0.07728855, 0.2016191, 0.14631543, -0.05918329, -0.033308215, 0.13446982, 0.17957696, 0.02237709, -0.111385815, 0.15208769, -0.2766956, -0.042062268, -2.918234e-05) * g_15;
    result += mat4(-0.3349197, 0.1320308, 0.034178462, 0.09385523, 0.03969266, -0.09389873, -0.114752054, 0.03206358, -0.14895694, -0.12865661, 0.01785704, 0.09169438, 0.101165384, -0.014787588, 0.08328934, 0.121291555) * g_16;
    result += mat4(-0.06074213, 0.18984905, 0.11707254, 0.12558164, -0.20235488, 0.13861518, 0.07092135, -0.3614094, 0.09027116, 0.14745344, 0.083361, -0.23089439, -0.14834873, 0.10834447, -0.24824911, -0.048383813) * g_17;
    result += mat4(0.1632019, 0.09772291, -0.21687613, 0.16953598, 0.03563443, -0.14966665, -0.12472958, -0.104619995, 0.124128886, 0.12477276, 0.5057336, -0.04884431, 0.07567298, 0.28349468, 0.17712036, 0.019731894) * g_18;
    result += mat4(0.10584999, 0.017437998, -0.1409027, 0.01700227, -0.26804322, -0.01906643, -0.15364946, 0.078551315, -0.38588783, -0.20918682, -0.13819021, -0.12914348, 0.22142257, 0.20084332, 0.07179306, -0.4147244) * g_19;
    result += vec4(0.04500602, -0.043274067, -0.024793796, 0.03252472);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf1, gxy, result);
}