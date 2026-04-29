// Anime4K_Upscale_GAN_x3_VL - Pass 17 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.07966754, -0.06966207, 0.02303797, -0.16448943, 0.10318848, -0.410334, -0.22451977, 0.2947905, 0.006431782, 0.2210936, -0.16191624, -0.32029536, 0.19407257, -0.13434124, 0.03879501, 0.17069095) * g_0;
    result += mat4(-0.06373326, 0.21566539, 0.06835463, -0.29900926, 0.1264936, 0.30812046, -0.18849093, -0.29262608, 0.1896114, 0.01970999, -0.27476716, -0.050988406, -0.30970192, -0.079130374, -0.14994004, 0.12752618) * g_1;
    result += mat4(0.020375464, 0.19119026, -0.313698, -0.26453584, 0.07838133, 0.18381923, 0.12585643, -0.06809764, -0.25780505, 0.05716925, -0.07450206, -0.02375656, -0.033622682, -0.10849277, -0.33186463, 0.19414547) * g_2;
    result += mat4(0.0044648047, 0.08281163, -0.04849872, 0.1355915, -0.097715564, -0.08512666, 0.083665445, 0.1250317, 0.15797666, 0.32305694, 0.42864105, 0.36694467, -0.19485113, 0.16141608, -0.16432299, -0.10108335) * g_3;
    result += mat4(0.06326362, -0.05534751, -0.13511105, 0.042043727, 0.20099865, -0.042153213, -0.22423261, -0.09133457, -0.027568584, 0.012865782, 0.13886575, 0.34115347, 0.2610905, -0.045110513, 0.06810152, 0.09738184) * g_4;
    result += mat4(-0.035168797, 0.034930643, 0.25825202, 0.20083296, -0.08928484, -0.21076165, -0.1159743, -0.216512, 0.11886214, -0.0706163, 0.124095425, 0.028673371, -0.31240124, -0.17458299, -0.2053044, -0.008733319) * g_5;
    result += mat4(0.29833966, 0.06774145, -0.03913825, -0.112461224, -0.000111277885, 0.07307257, 0.24769522, -0.27295232, 0.070567, -0.17354357, 0.2742455, -0.382184, -0.17436866, 0.22665188, 0.045708902, 0.03745412) * g_6;
    result += mat4(0.032916605, 0.11094983, 0.17567287, -0.06819124, 0.17541365, -0.118430324, 0.028206939, 0.37577933, 0.011492207, 0.21624072, -0.20114873, 0.222502, 0.012722517, -0.15424041, 0.07858887, -0.09832832) * g_7;
    result += mat4(-0.29937837, 0.08433066, -0.16425402, 0.014552817, 0.083602294, -0.12674652, -0.029379338, 0.020814786, -0.08117312, 0.0074423556, 0.06749342, -0.23778795, -0.20409779, 0.005250363, 0.014023434, -0.08039687) * g_8;
    result += mat4(-0.07325317, -0.102401175, 0.2583051, 0.30287206, 0.117874466, -0.047484834, 0.050214633, -0.16902745, -0.1403704, -0.17889948, -0.043674123, -0.011426891, -0.16280553, 0.076159306, -0.13330574, -0.1950167) * g_9;
    result += mat4(-0.256105, -0.08625361, 0.011796258, -0.02119164, 0.06349923, -0.27358216, 0.118133076, -0.034468293, -0.043460324, -0.2100345, 0.011009716, 0.24111703, -0.20008805, -0.47441798, -0.1211137, -0.31405842) * g_10;
    result += mat4(-0.04759389, -0.1061154, 0.008801774, -0.10977146, -0.025931438, 0.21277407, -0.038004987, -0.07198902, -0.022014204, -0.11847486, -0.038868114, 0.02172665, -0.3208455, -0.11351803, -0.06722725, 0.2296603) * g_11;
    result += mat4(-0.012025998, 0.024963265, 0.17822163, 0.3004866, -0.31125832, 0.034575626, 0.046008132, -0.24627264, -0.09372702, -0.1855233, 0.33742183, -0.034182545, -0.011793393, 0.26905802, -0.029423665, -0.1649043) * g_12;
    result += mat4(-0.63350683, -0.3606824, 0.3736929, -0.14756419, 0.058743123, 0.14858964, 0.18524785, 0.17112412, 0.258455, -0.12432544, -0.051312115, -0.2812558, 0.28210622, -0.17405578, -0.20673786, -0.07849705) * g_13;
    result += vec4(0.08657319, 0.0069808266, -0.0010583929, -0.006461665);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf1, gxy, result);
}