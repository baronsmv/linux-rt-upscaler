// Anime4K_Upscale_GAN_x2_M - Pass 10 of 23 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.35645446, -0.01804877, -0.53608185, 0.32968932, 0.13975728, -0.1716116, 0.09503091, -0.12088551, 0.30239868, 0.9217966, 0.016221086, -0.26894137, -0.0047026747, 0.54764843, -0.2826915, 0.0016894634) * g_0;
    result += mat4(-0.15123259, 0.2014175, 0.05961645, -0.32386652, -0.25275725, 0.3658508, -0.104193784, -0.02756655, 0.2696138, 0.17608197, 0.17685752, 0.6808081, -0.40293297, 0.48387393, 0.25278264, 0.28291366) * g_1;
    result += mat4(-0.18928573, -0.18908137, 0.47045723, 0.5454373, 0.31339395, -0.0064702537, -0.37307036, -0.37479213, 0.2235379, -0.370863, 0.02827034, 0.024350066, -0.32538193, -0.33686417, 0.8949382, 0.3324315) * g_2;
    result += mat4(-0.17215039, -0.14995, -0.4451278, 0.30758965, 0.21607, 0.08995007, 0.09553425, -0.21233945, -0.14442022, 0.09295349, -0.29228872, -0.3875935, 0.11704046, -0.4206096, 0.35226774, -0.08189522) * g_3;
    result += mat4(-0.12517966, 0.060051568, -0.38888076, 0.08354471, 0.17010468, -0.34286287, -0.06961373, 0.032387406, -0.025718998, -0.1661844, -0.075671494, 0.10289619, -0.28309906, -0.14461538, 0.22726184, 0.4752376) * g_4;
    result += mat4(0.15411675, 0.17533994, 0.3406641, -0.0597274, -0.21072194, 0.1517182, 0.032032263, 0.18653658, 0.20970167, -0.10793765, -0.05335404, -0.095203936, 0.2917104, -0.1170929, -0.11652503, -0.46912733) * g_5;
    result += mat4(-0.272871, 0.07467413, 0.16981912, 0.57318956, 0.35038894, -0.06679483, 0.3777534, -0.01522816, 0.2588504, -0.008976239, 0.31769443, 0.07070477, 0.059302222, 0.28855336, -0.14700443, -0.08605704) * g_6;
    result += mat4(-0.27067363, -0.2191635, -0.2377148, -1.0028448, -0.25673935, 0.10997322, -0.39032057, 0.06524818, 0.5248202, 0.40049195, 0.6711809, 0.2878331, 0.19606547, -0.092196286, 0.27838528, 0.03120515) * g_7;
    result += mat4(0.3029178, -0.027027214, 0.13855064, -0.16550988, 0.2354576, -0.1715326, 0.12981784, 0.5013446, 0.24411377, -0.13030572, -0.08595908, -0.104394995, 0.16794646, -0.044388745, 0.2807999, 0.39108425) * g_8;
    result += mat4(-0.05535261, -0.15662162, 0.14935054, 0.10706811, 0.026958441, -0.15323113, -0.19261432, -0.24361719, -0.2607876, 0.038486157, -0.04509224, 0.18722118, -0.14478058, 0.03614682, -0.12608361, -0.5203596) * g_9;
    result += vec4(-0.17363991, 0.071162574, -0.09289675, 0.013446863);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf1, gxy, result);
}