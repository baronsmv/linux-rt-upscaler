// Anime4K_Upscale_GAN_x3_VL - Pass 18 of 47 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.07191942, 0.3140507, 0.22113691, 0.11425055, 0.33772144, 0.2411142, -0.05054018, 0.18108025, 0.1453716, -0.05830594, 0.1749647, 0.09090011, -0.05392254, -0.029053958, -0.31549838, 0.059738033) * g_0;
    result += mat4(0.09510324, 0.08078732, -0.19260474, -0.11069926, 0.24988726, 0.051267263, 0.20293756, 0.26742226, 0.16450423, 0.13896441, 0.03573342, -0.19107069, 0.12676238, 0.10198673, 0.14884768, -0.2088339) * g_1;
    result += mat4(-0.01031837, 0.025411772, 0.042114772, -0.05685252, -0.055964757, 0.11324, 0.00448932, 0.16396624, -0.17178524, 0.27165812, -0.09635711, -0.15172988, 0.2671317, 0.16236094, 0.21264014, -0.25292912) * g_2;
    result += mat4(-0.22559996, -0.028498424, -0.1567824, -0.0735544, -0.17081529, 0.14735967, -0.0061476813, -0.17980057, -0.20270798, 0.032933656, -0.29559132, -0.16152963, 0.054025065, 0.0748118, 0.31088996, -0.107099526) * g_3;
    result += mat4(-0.45303443, -0.099132985, -0.13839091, 0.32170072, -0.34101728, -0.37682575, 0.12063899, -0.19869997, 0.1657555, -0.25580558, 0.056302473, 0.17126912, 0.32514557, 9.235195e-05, -0.14467183, -0.07996187) * g_4;
    result += mat4(0.2877269, 0.0261826, -0.08865923, -0.024432473, -0.096166946, 0.2561266, 0.026980402, 0.117528915, 0.3334183, 0.07372863, -0.08858107, -0.37130275, -0.36359683, 0.11301179, 0.091467746, -0.19730526) * g_5;
    result += mat4(-0.550552, 0.12992254, -0.10055661, -0.10932172, -0.19244795, 0.12395271, 0.060307764, -0.53993297, -0.088290274, 0.27347142, -0.4417309, -0.023805201, -0.35758695, 0.09050262, -0.35072213, -0.055425614) * g_6;
    result += mat4(0.18186982, 0.06789516, 0.030788613, 0.10114591, -0.11508006, -0.07924641, -0.046368007, 0.24148594, -0.107171915, -0.3024151, 0.32407254, -0.3586668, -0.012580506, -0.39705497, 0.2469481, -0.045826133) * g_7;
    result += mat4(-0.026137354, 0.32036647, -0.2753551, -0.27253738, 0.017361412, -0.12770222, -0.08593248, -0.15483221, 0.25440103, -0.36099723, 0.25746107, 0.08897639, 0.028374728, -0.02342191, -0.043640897, 0.113993265) * g_8;
    result += mat4(-0.037920885, 0.1657078, 0.004982961, -0.017414536, -0.22377351, 0.061842646, -0.15807268, -0.25205454, -0.21131302, 0.24842763, 0.078252114, 0.21482246, 0.074235536, 0.076578915, 0.27380338, 0.29830837) * g_9;
    result += mat4(0.17564484, -0.07282816, 0.07999462, 0.02969899, 0.15588856, 0.100054234, -0.08245988, -0.07382829, 0.15328896, -0.18413633, 0.098962, -0.1984274, 0.062275123, 0.115510456, 0.090368204, 0.13073486) * g_10;
    result += mat4(-0.07252601, -0.16025335, -0.13433468, 0.22769116, -0.051709075, -0.049860206, -0.0015467379, 0.10867708, 0.14257227, -0.04363354, 0.039784696, 0.009654442, -0.3981904, -0.035521798, -0.3009465, 0.20765312) * g_11;
    result += mat4(0.15802802, 0.20658726, 0.07175077, 0.13363297, -0.26437205, -0.36688936, 0.2642335, 0.2855627, 0.17861994, 0.076894015, 0.11635738, -0.06555138, -0.21570256, 0.15639998, 0.16982861, -0.14948218) * g_12;
    result += mat4(-0.252244, 0.104423165, 0.08296718, -0.23033309, -0.17892015, -0.33409834, -0.18738337, 0.29886454, 0.2821413, -0.42758805, -0.21272181, 0.5394736, 0.35043237, -0.049396887, 0.36223906, 0.18295164) * g_13;
    result += vec4(-0.025732767, -0.005527079, -0.030687628, -0.017071865);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf2, gxy, result);
}