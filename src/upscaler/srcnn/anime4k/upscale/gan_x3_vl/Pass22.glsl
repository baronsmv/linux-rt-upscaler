// Anime4K_Upscale_GAN_x3_VL - Pass 22 of 47 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_9_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.26660392, 0.07363331, -0.0630955, 0.04707774, 0.2190672, -0.012001462, -0.5999911, 0.28147182, 0.13756925, -0.124700874, -0.02564129, 0.22770438, 0.101030536, 0.098255195, -0.21563007, -0.075010024) * g_0;
    result += mat4(-0.251709, 0.20354952, -0.32704532, 0.018580899, -0.10529829, -0.15543194, -0.18096688, -0.27817816, 0.34051725, 0.02303076, -0.006826852, -0.09399886, -0.038892258, 0.022739887, 0.058521356, 0.13895498) * g_1;
    result += mat4(0.05894668, 0.100568, -0.21035372, 0.31440088, 0.037351474, -0.022318719, -0.00996168, 0.010143051, -0.33800384, -0.023619255, 0.23860018, -0.24643785, 0.096730575, -0.10366994, 0.050961945, -0.219199) * g_2;
    result += mat4(0.21206303, -0.17116684, 0.014926057, -0.2555803, -0.23777173, -0.3644426, -0.14371839, -0.21673483, 0.39334375, -0.1263852, -0.23373136, -0.43798128, -0.1707486, -0.009590617, 0.0023898776, -0.23449537) * g_3;
    result += mat4(-0.06620709, -0.033145174, 0.27508232, 0.08487005, 0.36242872, -0.30349565, -0.034109794, 0.3935021, 0.046761807, -0.106829435, -0.048241124, 0.011187411, -0.20284426, -0.08020177, 0.011624174, 0.2168835) * g_4;
    result += mat4(-0.12986803, 0.09660072, -0.0859288, 0.23373657, -0.35700363, 0.021483889, 0.13391288, 0.26249766, 0.073043846, 0.15460604, -0.17885107, -0.03155575, 0.21122873, 0.10214664, 0.008124733, -0.13256365) * g_5;
    result += mat4(-0.20986424, 0.01661353, -0.32582346, 0.021188684, -0.11207729, -0.005879808, 0.14655554, 0.20526361, 0.17426926, -0.21366295, -0.08453759, 0.21751851, -0.22087021, 0.18081911, 0.034678783, -0.028321259) * g_6;
    result += mat4(0.06180443, -0.0133624105, -0.09466958, -0.11492345, 0.037676495, 0.17866406, -0.2652301, -0.27896136, 0.066703305, 0.0914678, 0.060967688, -0.1129105, 0.34927168, -0.07907402, 0.250401, 0.18991004) * g_7;
    result += mat4(0.19685721, -0.004515772, -0.24063739, 0.029372582, 0.11698867, 0.07514613, 0.09423268, 0.1620886, 0.14784159, 0.21263896, 0.2852977, -0.12326755, 0.07344623, 0.050873935, -0.23356345, -0.5316184) * g_8;
    result += mat4(-0.13699524, -0.26430392, -0.06886077, 0.03557516, -0.06480295, 0.08807464, -0.17347333, 0.06482862, -0.13731833, -0.2848614, 0.06923784, 0.25189507, -0.12466488, -0.052593954, 0.00086845015, 0.10056825) * g_9;
    result += mat4(0.18202075, -0.03969697, 0.11266586, -0.31405628, -0.18683487, -0.16736764, -0.2904854, -0.03473291, 0.0489973, 0.37474206, 0.2694234, -0.029300861, 0.02498133, 0.3028819, 0.1546703, -0.09094391) * g_10;
    result += mat4(0.022329945, 0.16241878, -0.19467553, -0.06949654, 0.34127444, 0.15979202, 0.018057512, 0.24089065, -0.102250695, 0.01327663, 0.21074775, 0.10166909, 0.3671337, 0.25721171, -0.25048146, 0.03895536) * g_11;
    result += mat4(0.05818574, -0.0058748005, 0.11750601, 0.19012532, 0.3506463, 0.05318807, -0.14448579, -0.09219455, -0.13858557, -0.024810392, 0.057599254, 0.012339387, 0.1620521, -0.18280268, 0.040701784, -0.17565976) * g_12;
    result += mat4(0.39327988, -0.1916084, 0.056305442, -0.288639, -0.034966636, 0.29527235, -0.32901463, -0.11967507, -0.34051013, 0.27244, -0.0063241655, 0.4183678, -0.38721135, -0.13528046, 0.16835152, 0.17126207) * g_13;
    result += mat4(0.014969379, 0.1980705, 0.08781139, 0.144981, 0.3095253, -0.17065018, 0.23785667, 0.26326, 0.009895111, 0.019108804, 0.2241572, 0.048993796, 0.115338214, 0.13549735, -0.21664904, -0.044739243) * g_14;
    result += mat4(0.24587603, -0.03127825, -0.5519671, -0.1913501, -0.041294243, 0.17807598, -0.24955471, -0.2830993, -0.032468125, 0.051955972, -0.04685181, -0.29292116, -0.037471697, -0.09133097, 0.06842207, 0.4217657) * g_15;
    result += vec4(0.03585649, -0.0060541225, 0.04059685, 0.028249348);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf1, gxy, result);
}