// Anime4K_Upscale_GAN_x4_UL - Pass 7 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.113515526, 0.106837384, 0.20812881, 0.16897917, 0.041623022, -0.1039364, 0.19850619, 0.298937, -0.3082365, -0.031754434, 0.16342433, 0.37504506, 0.09699736, 0.010189174, 0.17887989, -0.09383025) * g_0;
    result += mat4(0.10328652, -0.028724594, -0.03725655, 0.27347645, 0.10183029, -0.16081847, -0.10617321, 0.1901187, -0.03793219, 0.2775493, 0.14563474, 0.00840078, -0.17760493, 0.13339461, 0.089312814, 0.034915876) * g_1;
    result += mat4(0.015832528, -0.045636576, -0.12128991, 0.2608647, 0.24673735, 0.10102276, 0.16210636, -0.46542636, -0.015267993, -0.15264183, 0.25447357, 0.031080268, 0.20901208, 0.14662905, -0.036634948, 0.0845752) * g_2;
    result += mat4(0.09588151, 0.018494375, 0.027304746, 0.13447088, -0.06265565, 0.1733864, 0.334192, -0.113528445, 0.21299788, -0.1472667, 0.29488075, -0.1290995, -0.024090588, -0.3359844, -0.101115264, -0.2198912) * g_3;
    result += mat4(-0.0139789, 0.21625891, 0.022689445, 0.06341661, -0.117535755, 0.2804869, -0.044223994, -0.19280532, 0.12332802, -0.038589306, 0.060168512, 0.003091399, 0.22361282, 0.20717236, -0.098680764, -0.3309222) * g_4;
    result += mat4(-0.06628995, 0.12792988, 0.003792715, 0.1680786, -0.1342965, 0.41055954, 0.062222756, 0.049789477, -0.07372347, -0.18070233, 0.03299076, -0.09340363, 0.32073286, -0.07532172, -0.07331408, 0.20519489) * g_5;
    result += mat4(0.086528674, 0.08663942, 0.25446007, -0.3459604, 0.08586162, -0.2900368, -0.24869849, 0.20104861, -0.5512707, -0.08311233, 0.14626856, -0.15290149, -0.1541716, 0.02692958, -0.0066374447, 0.37172756) * g_6;
    result += mat4(-0.19816272, 0.08062059, 0.072980136, -0.1234166, 0.16083257, 0.07615364, 0.16252695, -0.31896582, -0.3006324, 0.24307664, 0.10824411, -0.22742745, -0.16614948, -0.22890756, -0.07267046, 0.09090352) * g_7;
    result += mat4(-0.10712061, 0.071095675, -0.32983637, -0.09112012, 0.24694498, 0.09215849, 0.05334446, 0.077359654, -0.07286092, 0.34112877, -0.013829287, 0.06670894, -0.09276153, 0.072939105, -0.13622369, 0.14010417) * g_8;
    result += mat4(0.11312907, -0.090158425, 0.3204081, 0.053531416, -0.253243, 0.12732224, -0.02162359, -0.34881824, 0.011340285, -0.2804999, -0.24482724, -0.06718974, 0.015262575, -0.0716948, -0.07537729, -0.20046124) * g_9;
    result += mat4(0.046407733, 0.17073393, 0.027035931, -0.32520708, 0.47023183, -0.11385112, 0.10980019, 0.12331711, 0.039710827, 0.25615647, -0.06121073, 0.22643484, -0.053721283, -0.019124558, 0.24745707, -0.007544153) * g_10;
    result += mat4(0.015645513, 0.24795622, -0.027034724, 0.091168396, 0.13050666, 0.19245213, -0.3235803, 0.12572092, -0.04100238, -0.2667382, -0.06869353, -0.18729845, -0.3253826, -0.15944591, -0.038754206, -0.022384685) * g_11;
    result += vec4(-0.021124197, 0.065632634, 0.024891809, 0.072871104);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf, gxy, result);
}