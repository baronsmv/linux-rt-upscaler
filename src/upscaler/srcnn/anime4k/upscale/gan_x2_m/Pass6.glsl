// Anime4K_Upscale_GAN_x2_M - Pass 6 of 23 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.6336626, -0.23328744, 0.054100014, -0.6572063, 0.22899812, 0.47125596, 0.087406546, 0.5788615, -0.24324284, -0.17465535, 0.23223022, -0.4417298, -0.1195797, -0.14119461, -0.2301777, -0.1748931) * g_0;
    result += mat4(0.2554768, -0.0835268, 0.13054265, 0.033940453, -0.22754695, 0.053536188, -0.10300488, -0.10146903, 0.3104604, -0.5024146, 0.089460805, -0.20216464, 0.6033507, 0.12908716, -0.29953086, 0.292064) * g_1;
    result += mat4(0.09586759, -0.037499018, -0.23253569, 0.63889295, 0.18920106, -0.6646685, 0.07218118, -0.61459464, -0.16397415, 0.3131906, -0.39399612, 0.36777702, 0.39545253, 0.030677503, 0.29420745, -0.02527333) * g_2;
    result += mat4(-0.2464485, -0.117239855, -0.13390337, 0.43170166, 0.10044111, -0.13811369, -0.007668335, 0.06387773, -0.11786689, 0.23223364, 0.12805769, 0.06410502, -0.2818576, 0.21286973, 0.17026524, -0.22247931) * g_3;
    result += mat4(0.12590794, 0.25101408, -0.014941272, -0.06091461, -0.106272854, -0.23196393, 0.64016813, 0.0025616125, 0.16706267, 0.008579063, 0.04476896, -0.5403641, -0.011274305, -0.014704461, -0.068788156, 0.47190762) * g_4;
    result += mat4(0.10427173, -0.11386145, -0.6048206, -0.20245847, -0.011730377, -0.0119483, 0.06255473, -0.5017671, -0.07181296, -0.08626898, -0.035322662, 0.42718327, 0.041101683, 0.017210655, -0.07089471, -0.6541289) * g_5;
    result += mat4(-0.43911383, -0.099413894, -0.22120018, -0.3121928, -0.32394376, 0.1159015, 0.04434728, 0.014404674, 0.040322874, 0.06727233, -0.046662346, -0.066591434, -0.004613069, -0.6566657, -0.13442427, -0.081967555) * g_6;
    result += mat4(0.7393613, 0.059159152, 0.21900342, 0.26184326, 0.15656939, -0.05151207, -0.02730003, -0.055701576, -0.50296444, 0.09566756, -0.10248052, -0.39747316, 0.5877897, 0.83397114, -0.07968032, -0.3097048) * g_7;
    result += vec4(-0.010642331, -0.050244823, -0.009665539, 0.26457447);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf1, gxy, result);
}