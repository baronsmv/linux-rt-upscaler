// Anime4K_Restore_CNN_Soft_M - Pass 1 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_MAIN;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_tf;
#define go_0(x_off, y_off) (texture(sampler2D(tex_MAIN, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy)))

vec4 hook() {
vec4 result = mat4(-0.073079124, 0.11507942, 0.028201895, -0.021776304, -0.25251916, -0.08662003, 0.38814726, 0.4146095, 0.06326891, 0.01635252, 0.06423356, 0.13488062, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.059791833, -0.03105604, 0.041643705, 0.35197195, -0.17314838, 0.067622855, -0.032012507, 0.09691628, -0.11094062, 0.007625051, 0.094762206, -0.05824145, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.120281175, 0.027440755, -0.026316144, -0.025291128, -0.41698205, -0.05966847, -0.28400028, -0.06946398, -0.10906026, -0.015854035, -0.028724853, -0.06626416, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.068752654, -0.12652585, 0.38200122, 0.17978846, 0.2749825, 0.015504972, 0.21765926, 0.2246602, -0.062151223, 0.07457783, 0.13588274, -0.037328478, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(0.3718559, 0.025637252, -0.4048626, -0.41484925, 0.24768798, 0.09984098, -0.5663632, -0.6659978, 0.212067, -0.08328392, -0.5277322, -0.016879432, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(-0.11072714, -0.010321538, 0.11265787, 0.0055236337, -0.13345073, 0.004847663, 0.3744461, -0.4038564, -0.09893075, 0.031325124, 0.2883957, -0.04268903, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.10444391, -0.60588187, 0.02543334, 0.10911738, -0.10860678, 0.15701362, 0.29235297, 0.045803998, 0.076250754, -0.10799697, 0.08841044, 0.08145623, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(-0.04246739, -0.1225759, 0.11280305, -0.12079673, 0.5289142, -0.011892906, -0.0800465, 0.05915611, -0.126204, 0.08239301, -0.0092391195, -0.07672885, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(-0.11922264, 0.14036109, -0.09491126, 0.05112697, -0.12543046, -0.08662423, -0.041537095, 0.048038274, 0.11672854, -0.006516173, -0.023524825, 0.030505095, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.07697861, 0.41154122, 0.042374082, -0.087270625);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, gxy, result);
}