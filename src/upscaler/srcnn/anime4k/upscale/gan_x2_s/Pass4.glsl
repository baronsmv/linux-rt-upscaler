// Anime4K_Upscale_GAN_x2_S - Pass 4 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.5713254, 0.59251165, -0.14328027, 0.3463698, -0.6896771, -0.14296922, -0.3860265, 0.4501756, -0.39508528, 0.40213254, -0.16835114, -0.0029681697, 0.06473641, 0.18837942, 0.18787977, -0.14020114) * g_0;
    result += mat4(0.08934268, -0.28500432, 0.45083842, 0.16448207, 0.10745752, -0.07937402, 0.17439699, -0.4361477, 0.35800517, -0.16299683, -0.112771064, 0.46456474, -0.016184373, -0.2676676, -0.09250065, 0.30093423) * g_1;
    result += mat4(-0.23437534, 0.30892932, -0.3382499, -0.11436098, -0.09584061, 0.010766669, -0.6745943, 0.19373886, 0.19484869, 0.0063928245, 0.20636424, -0.6427624, 0.22710505, 0.580292, -0.56174964, -0.15055792) * g_2;
    result += mat4(-0.4264334, -0.43369257, 0.29302827, -0.2763896, 0.20638986, 0.066474296, 0.18825729, 0.14629841, -0.70805573, 0.3601201, -0.49326342, 0.4604217, -0.3331877, -0.30442527, 0.33416224, 0.08233912) * g_3;
    result += mat4(-0.043108743, 0.32130125, -0.13206981, 0.56653565, -0.069573626, -0.32312635, 0.17708589, 0.12717012, -0.39452434, 0.7504042, -0.563233, -0.38678297, -0.20246895, 0.399379, -0.1829332, -0.4856879) * g_4;
    result += mat4(0.46322855, -0.14412759, 0.26863632, -0.37377957, 0.18703142, 0.12013766, -0.010468053, 0.36067548, 0.29069972, -0.5482968, 0.1952737, 0.42751312, 0.47847852, -0.13346007, 0.35286024, 0.23347002) * g_5;
    result += vec4(0.08279582, -0.12997188, 0.08899629, 0.018068794);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf, gxy, result);
}