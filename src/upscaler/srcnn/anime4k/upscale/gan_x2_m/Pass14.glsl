// Anime4K_Upscale_GAN_x2_M - Pass 14 of 23 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_2 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.19380243, 0.020101497, 0.021015864, 0.40521726, 0.038862754, -0.3473658, 0.22289194, -0.2075226, -0.15960178, 0.20686232, -0.19066268, -0.24524036, -0.19289994, -0.6356018, 0.040245753, -0.22887161) * g_0;
    result += mat4(-0.06837712, -0.59243137, 0.08107887, -0.18099897, 0.08890105, -0.20113088, 0.0076543097, -0.28404838, -0.39403212, 0.124420464, 0.07661543, -0.16511264, 0.440653, 0.17841326, -0.40957427, -0.055862557) * g_1;
    result += mat4(-0.052128255, -0.17906874, -0.0063690864, -0.3027001, -0.12118662, 0.5986499, -0.35075194, 0.11334461, -0.13089949, 0.48732534, 0.31238684, 0.0636065, 0.21470545, -0.12680373, 0.20702313, -0.14277203) * g_2;
    result += mat4(-0.13521394, 0.5266374, -0.4765612, 0.32102558, -0.07704129, -0.26604977, 0.36475307, 0.27245706, 0.16729634, -0.04975267, 0.18763311, 0.07594951, -0.20137721, 0.07614109, -0.056586545, 0.35838535) * g_3;
    result += mat4(0.22150421, -0.023909386, -0.30742592, 0.54860467, 0.038963366, -0.47929683, 0.001491465, -0.2016597, 0.14891255, -0.12298715, 0.12770613, 0.16882578, 0.52988553, -0.34417477, -0.11196754, 0.038432673) * g_4;
    result += mat4(0.10892675, 0.15687913, 0.4061297, -0.2549851, -0.12231971, 0.7066191, -0.038577385, 0.1871752, -0.23520122, 0.6384404, -0.04857454, -0.23879313, -0.26810166, -0.08090798, 0.3287431, 0.15214305) * g_5;
    result += mat4(0.16076286, 0.08942198, 0.79264593, -0.5107746, -0.10051664, -0.18325275, 0.31161344, 0.023725776, 0.09911152, 0.1552438, -0.22447744, -0.2995641, 0.27984253, -1.107023, 0.010454479, 0.6606262) * g_6;
    result += mat4(0.041668475, 0.16935597, -0.11855577, 0.2013473, 0.2991738, -0.38238418, 0.17906274, -0.27559698, -0.4381387, 0.39814267, -0.40905684, 0.57992136, 0.2830281, 0.12482517, -0.30402762, 0.47808015) * g_7;
    result += mat4(0.05201121, 0.3396993, -0.04965309, -0.25744373, -0.13495848, -0.120026626, 0.15645088, -0.20658544, 0.414069, -0.03110071, 0.070210315, 0.028046172, -0.17324251, 0.14329922, -0.14353131, 0.028436944) * g_8;
    result += mat4(-0.15607943, 0.98266315, -0.15506491, 0.34884667, -0.16584046, 0.07532187, 0.0062847883, 0.8719761, -0.30521882, -0.34961814, -0.055313803, 0.041199762, 0.2634066, 0.31106153, 0.029962108, -0.017541675) * g_9;
    result += mat4(0.1285044, 0.41011113, 0.16163284, -0.40202442, 0.33554438, -0.2626098, 0.18437132, 0.06627138, 0.26390168, -0.23918642, -0.17191365, -0.16348109, 0.30074367, -0.99079835, 0.60264456, 0.050881945) * g_10;
    result += mat4(0.3971443, -0.034655187, 0.11870823, 0.39984652, -0.45068088, -0.054210827, -0.27554438, -0.16074227, -0.14983663, 0.35434055, 0.42479035, 0.07799301, -0.4260275, 0.66214204, -0.095251344, 0.09080398) * g_11;
    result += vec4(-0.012729538, -0.13335368, 0.14840336, 0.025965473);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf1, gxy, result);
}