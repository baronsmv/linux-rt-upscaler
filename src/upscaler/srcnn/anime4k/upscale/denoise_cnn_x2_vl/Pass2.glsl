// Anime4K_Upscale_Denoise_CNN_x2_VL - Pass 2 of 18 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_tf1;
#define go_0(x_off, y_off) (texture(sampler2D(tex_MAIN, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy)))

vec4 hook() {
vec4 result = mat4(-0.012326053, 0.050769784, 0.1278702, -0.100782245, 0.14329414, -0.054558773, 0.023473471, 0.056829426, 0.048292916, 0.0046510273, -0.11478287, 0.0011030561, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(0.29542983, -0.55061895, -0.068554066, 0.1433222, -0.072878316, 0.30201668, -0.2223378, -0.06704077, 0.16955832, 0.3279914, 0.17619601, -0.1276919, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(0.09623417, 0.30559412, 0.094622105, -0.076706685, 0.07943858, -0.084815115, 0.12472551, 0.079850115, -0.13044213, -0.21300878, -0.095747225, 0.13412355, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.21291664, 0.17195296, -0.20080926, 0.1064855, 0.10228669, -0.09580175, -0.11217631, -0.09740562, -0.0033135475, -0.053094357, 0.2983595, 0.035281878, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.08955812, -0.45707774, -0.4606922, -0.5754473, -0.11395895, 0.33530128, 0.29705846, -0.18877256, -0.43502945, 0.114171304, -0.3750776, -0.081597246, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(-0.26109028, 0.02662961, -0.10441071, 0.11199392, -0.12038989, -0.09642296, -0.061320662, -0.33058178, 0.20212512, 0.00840794, 0.14357455, -0.038080238, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.09533881, -0.13644339, 0.068756215, 0.079305276, -0.053370547, 0.19572955, 0.0682981, 0.14469264, 0.15582883, -0.057183057, -0.13919263, -0.016394936, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(-0.041189935, 0.39878023, 0.028704925, 0.30194348, -0.04486593, -0.33899093, -0.103968106, 0.21802065, -0.077099144, -0.07389541, 0.18069103, 0.18894517, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(-0.12399862, 0.19246885, 0.034825478, -0.0044787163, 0.13121822, -0.13573012, -0.030162754, 0.1899518, 0.102326415, -0.061512686, -0.005647928, -0.0937634, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(0.019286277, -0.033644073, 0.08196311, 0.0054393094);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf1, gxy, result);
}