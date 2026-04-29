// Anime4K_Upscale_GAN_x3_VL - Pass 13 of 47 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_3_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.28125653, 0.25701848, 0.20101643, 0.5281567, 0.26044676, -0.0461423, 0.23783551, -0.24269718, -0.048285794, -0.14693165, 0.10931955, 0.055711113, -0.23280147, -0.01317713, -0.17544006, 0.21709861) * g_0;
    result += mat4(-0.08328998, -0.031984776, -0.07394345, -0.30742306, 0.2663806, 0.18147124, 0.07257191, 0.120762065, 0.3541939, 0.26340798, -0.46390432, 0.018954063, 0.10409174, -0.10490177, 0.10593656, 0.0628627) * g_1;
    result += mat4(-0.032924887, -0.15148862, 0.18510309, 0.16908437, 0.10370028, 0.022468375, -0.11225163, -0.09905774, 0.13124186, -0.10389915, 0.13148285, -0.07210047, -0.12430891, 0.15495282, -0.1387402, -0.1870354) * g_2;
    result += mat4(-0.06593955, 0.08320663, 0.045904607, -0.19401237, -0.09821163, 0.1250965, -0.09813775, 0.06319873, 0.196712, 0.06502086, -0.18785718, -0.2192117, -0.2976963, 0.035152618, -0.011372132, 0.16548428) * g_3;
    result += mat4(0.16684611, 0.30011636, 0.028905347, 0.05727758, -0.22959393, -0.244406, 0.1341724, -0.102163084, -0.12952183, 0.11940772, 0.50821495, -0.009484609, -0.06948309, 0.0072816983, -0.15294522, 0.2092066) * g_4;
    result += mat4(0.022403454, -0.007886967, -0.06732929, -0.018902952, -0.0013836037, -0.29473454, -0.044799604, 0.072756514, -0.030483285, 0.26202264, 0.17527826, -0.008713192, 0.29756203, 0.13983198, 0.07839081, 0.019387554) * g_5;
    result += mat4(-0.16632473, 0.114597425, -0.04930454, 0.21361813, -0.0512679, -0.24750078, 0.41110075, -0.06739092, 0.3819155, 0.27142018, 0.002062295, -0.21381181, -0.17034262, -0.5128788, 0.1978073, 0.052122597) * g_6;
    result += mat4(-0.29126012, -0.1758868, -0.29398203, 0.19212133, 0.08524374, 0.06918904, -0.22941263, 0.090433136, -0.053510923, -0.17689814, 0.1758969, 0.009342475, 0.27690578, 0.25371844, 0.24096957, -0.22880019) * g_7;
    result += mat4(0.068742655, 0.22967601, 0.29380092, -0.15837927, -0.16055553, 0.1671522, 0.117854536, 0.082386516, 0.273745, -0.46557623, 0.3121532, 0.026219485, 0.2669753, -0.29373366, -0.25829294, 0.07983141) * g_8;
    result += mat4(-0.19932887, -0.14828281, -0.40875518, 0.04568025, 0.047040872, -0.01525455, 0.14397773, -0.11989029, 0.17056611, 0.1253716, 0.4775329, -0.10225481, -0.24495989, 0.04492594, -0.035991665, -0.08934401) * g_9;
    result += mat4(0.06003682, -0.017648386, 0.20581077, -0.3805033, 0.15103109, 0.06460132, 0.16655886, -0.26180133, 0.06786087, -0.08443782, -0.26908222, -0.07582944, -0.117463715, -0.22386667, 0.061124742, -0.07322523) * g_10;
    result += mat4(0.044447657, 0.44650033, -0.1944857, 0.21535386, 0.10800574, -0.035085898, -0.28545883, 0.15166284, 0.06842558, 0.057331495, 0.48083216, 0.19788021, 0.051137898, 0.14926943, 0.3127889, 0.106091596) * g_11;
    result += vec4(0.026539318, -0.015506256, 0.0048546535, 0.0075091156);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf2, gxy, result);
}