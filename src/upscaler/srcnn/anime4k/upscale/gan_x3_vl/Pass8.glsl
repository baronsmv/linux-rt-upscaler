// Anime4K_Upscale_GAN_x3_VL - Pass 8 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.100268096, 0.23665515, -0.09436204, -0.28319857, -0.12872986, 0.08509328, -0.18415087, -0.03999439, 0.2617383, -0.15970403, -0.22670083, -0.03881397, 0.13375872, 0.16361052, -0.182056, -0.05152662) * g_0;
    result += mat4(0.06983459, 0.05918782, 0.0019706702, 0.19103576, 0.0012266171, 0.16021517, -0.28444147, -0.08221082, -0.22690836, -0.28738838, -0.30523723, -0.06292484, -0.45787656, -0.4256781, 0.15011774, 0.19713745) * g_1;
    result += mat4(-0.108251706, -0.09575882, 0.14541572, -0.023061674, -0.09192183, 0.20073768, 0.09588695, -0.12282409, 0.49980986, 0.035110943, 0.05705307, 0.1849613, 0.3072823, -0.2778156, -0.122733004, 0.23415174) * g_2;
    result += mat4(-0.16456233, -0.29974493, 0.28406498, 0.25605485, -0.011572488, -0.08334007, 0.07203565, -0.094384134, 0.22027689, -0.21240151, -0.4200112, 0.12086537, -0.2557046, -0.21156469, 0.19297566, -0.122556984) * g_3;
    result += mat4(-0.0512366, -0.21540374, -0.42458904, -0.14916559, -0.006133572, -0.047171656, 0.19129787, 0.22396603, 0.33921507, 0.12842081, 0.09855959, 0.12153268, 0.29035586, 0.36441955, -0.1877515, -0.13069488) * g_4;
    result += mat4(0.13884968, -0.18599026, -0.252318, 0.06907854, -0.06035006, 0.09183405, -0.28984216, 0.09260213, -0.37774235, -0.0048559248, 0.0033081435, -0.2721911, -0.10626775, -0.000512303, -0.049684875, -0.032722652) * g_5;
    result += mat4(-0.2273582, 0.1474099, -0.059321042, -0.15232776, 0.0116628725, -0.08633413, 0.05804712, -0.07626975, -0.10478975, 0.21511218, 0.41905594, 0.06739017, 0.30586454, -0.18381259, 0.09150968, 0.052257504) * g_6;
    result += mat4(0.11706192, -0.22794026, 0.0827107, 0.08569464, -0.21939716, 0.45023325, 0.37169182, 0.042208318, 0.11287388, 0.32384142, -0.413992, 0.05821689, -0.3391042, 0.15291925, -0.36155325, 0.0664715) * g_7;
    result += mat4(-0.34493464, -0.15583536, -0.14152767, -0.12836038, -0.09319977, 0.25707567, 0.14277849, 0.40507147, -0.031562362, 0.23948264, 0.1699104, 0.27782723, 0.08283791, -0.26529413, -0.106602244, -0.07465849) * g_8;
    result += mat4(0.1887244, 0.252802, 0.32356924, 0.016438756, -0.08394548, -0.15049113, 0.04155357, -0.16676176, -0.31628004, 0.15818349, 0.095658414, -0.19542241, 0.07927821, 0.066871084, 0.09443255, -0.07224674) * g_9;
    result += vec4(-0.0043032477, 0.009764352, 0.005997259, -0.007073129);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf2, gxy, result);
}