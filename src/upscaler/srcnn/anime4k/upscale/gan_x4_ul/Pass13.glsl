// Anime4K_Upscale_GAN_x4_UL - Pass 13 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_3_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_3_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_3_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.4954155, -0.097350635, 0.2804199, -0.13652386, -0.14972939, 0.19721153, -0.23526497, -0.2423665, 0.12555814, -0.0705443, 0.043938212, 0.19388582, 0.09386085, -0.43720174, 0.29635525, 0.26856044) * g_0;
    result += mat4(0.14495872, 0.0610595, -0.20516497, 0.19073643, -0.008849148, 0.08743844, -0.12433487, 0.03215462, -0.01670364, -0.34068078, 0.15872881, -0.27169266, 0.33020407, 0.008234461, -0.12094001, 0.17628567) * g_1;
    result += mat4(0.04740511, -0.15941422, 0.124839395, 0.081435576, 0.09804199, 0.058109295, -0.025289856, -0.29283887, -0.1833574, -0.09766394, 0.06008274, 0.05992534, 0.47684956, -0.08688919, -0.02071398, -0.08875196) * g_2;
    result += mat4(0.051867574, -0.1671438, -0.015705047, -0.13457336, 0.13484482, -0.06867962, -0.0494534, -0.13416421, 0.031772017, 0.0070866095, 0.011681956, -0.2802077, -0.048953146, -0.0164331, 0.09649591, 0.040060654) * g_3;
    result += mat4(-0.4341213, 0.0894957, -0.16301447, 0.18785268, -0.28154027, 0.21622275, 0.22126062, 0.2361705, -0.087688446, 0.38882533, 0.020676106, -0.17769825, -0.18067831, 0.0878923, -0.18052578, 0.009196582) * g_4;
    result += mat4(-0.14932597, -0.025830185, -0.07313429, 0.28342503, 0.19499254, 0.122385964, 0.02120492, 0.15144306, -0.23691256, 0.043697022, -0.053712673, 0.2025457, -0.05035754, 0.04117272, 0.12530772, -0.2590774) * g_5;
    result += mat4(0.15071404, 0.015031444, 0.24973233, -0.036299556, 0.30665022, 0.15286064, -0.03598529, 0.060580775, 0.10571382, -0.06852027, -0.13089266, -0.33822387, 0.04771977, -0.15371466, -0.14530133, 0.0127773) * g_6;
    result += mat4(-0.04100588, 0.080336295, -0.0012170919, -0.18198122, -0.12988265, 0.11356896, 0.21294571, -0.080107085, -0.1408792, -0.24597132, 0.046940666, -0.029645668, 0.1568284, -0.07500836, -0.13504413, -0.17453668) * g_7;
    result += mat4(0.38996047, -0.027129678, 0.2774081, 0.11160041, 0.2672792, -0.09991047, -0.1424887, -0.12418898, 0.15399674, -0.0089404015, 0.2265917, -0.08212792, 0.25704643, -0.013109098, -0.31268027, 0.10123544) * g_8;
    result += mat4(0.033000022, 0.15843867, -0.21515252, -0.046294916, -0.35692936, 0.08798134, 0.23537703, 0.0043003275, -0.1383531, 0.1972939, -0.2003098, 0.1543574, 0.053583264, 0.29797947, 0.13025342, 0.038611986) * g_9;
    result += mat4(0.10687409, 0.077787064, 0.27379388, 0.13262683, -0.23440802, 0.1360886, -0.20802121, 0.06401844, 0.26749787, 0.29900748, -0.04572612, 0.3015703, -0.3005316, 0.16046184, -0.0419697, -0.23878895) * g_10;
    result += mat4(-0.063034855, 0.07657174, -0.17484638, 0.07603076, -0.06233915, -0.11565521, 0.02205211, -0.025715057, 0.102525316, 0.044643577, 0.112743095, -0.08565946, -0.121290885, -0.1572643, 0.19650643, -0.13887478) * g_11;
    result += mat4(-0.36125946, -0.1215746, 0.15642375, 0.26731244, 0.24759081, 0.1720814, 0.3640398, -0.32403925, -0.06189445, 0.23764968, -0.02306858, 0.17816281, -0.06804958, 0.06811998, -0.07474977, 0.24738653) * g_12;
    result += mat4(0.054465637, 0.057861228, 0.059370693, -0.12227704, -0.024842938, -0.10762688, -0.13456275, 0.10306674, 0.058080807, -0.3396897, -0.08585732, 0.016198207, -0.09374, 0.3309844, 0.00036378333, -0.16453783) * g_13;
    result += vec4(0.016481666, 0.009086331, -0.036633138, 0.0041078017);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, gxy, result);
}