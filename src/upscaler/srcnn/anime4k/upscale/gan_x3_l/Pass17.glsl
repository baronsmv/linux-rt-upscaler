// Anime4K_Upscale_GAN_x3_L - Pass 17 of 30 - https://github.com/bloc97/Anime4K
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
vec4 result = mat4(0.06760422, 0.16268754, -0.14517367, -0.023386402, -0.23272006, 0.48739922, 0.06399116, -0.032946702, -0.17306012, 0.334446, 0.17779559, -0.2660973, -0.3468709, 0.51220256, -0.010311926, -0.040047005) * g_0;
    result += mat4(-0.0538168, -0.048309397, 0.064760834, 0.09675621, 0.20269404, -0.2615111, -0.27282992, -0.12584937, 0.10904846, -0.15973651, -0.076846495, -0.09462694, 0.12722874, 0.21629119, -0.35314724, -0.086036965) * g_1;
    result += mat4(-0.049174394, -0.05765949, 0.21250841, 0.17151582, 0.15764381, 0.040890984, 0.05118504, -0.14658877, 0.05469671, 0.13701054, 0.20377803, -0.39008877, -0.0016028697, 0.13317284, -0.11653242, 0.12591232) * g_2;
    result += mat4(0.21234287, -0.3048995, -0.12653783, -0.109162085, -0.050768167, -0.17156011, 0.05592974, 0.27197394, -0.19419932, -0.046344608, -0.05445905, -0.13253787, 0.05778321, 0.16979085, -0.04466505, -0.06867837) * g_3;
    result += mat4(-0.18974759, 0.22814974, -0.007522141, -0.10096491, -0.26759568, 0.32048568, 0.2660603, 0.112091035, 0.41875598, -0.1051111, 0.06525224, 0.27191457, 0.017352497, -0.31743342, 0.29108858, 0.26573792) * g_4;
    result += mat4(0.031855166, -0.122523904, -0.28207538, 0.12833035, -0.025733596, 0.008542537, -0.1891138, 0.16361842, 0.058317598, -0.007289248, 0.03349703, -0.038986582, 0.18147361, -0.3912238, 0.024964351, 0.14339498) * g_5;
    result += mat4(0.37369347, -0.012460246, -0.037854888, 0.067713045, -0.06288331, 0.26436228, -0.058873445, 0.04463945, -0.04286497, -0.04824939, 0.17835206, -0.036378298, 0.33058742, -0.14685723, 0.1025378, 0.051385757) * g_6;
    result += mat4(-0.131484, -0.040644694, -0.14443769, 0.1950223, 0.09507341, 0.48859578, -0.26267928, 0.24538381, -0.063596986, -0.18749404, -0.031884808, -0.07132067, -0.04606875, 0.03708701, -0.26145473, 0.2371378) * g_7;
    result += mat4(0.094301306, -0.08795415, -0.035933804, 0.21765485, -0.29858732, 0.11440603, 0.14095801, 0.18262209, -0.08135902, -0.45404965, 0.20399955, -0.06393024, 0.023793167, 0.16001467, -0.11817577, -0.16322103) * g_8;
    result += mat4(0.07168084, 0.0879652, -0.083207026, -0.045181375, 0.07845201, -0.15828066, 0.05710845, 0.05699917, -0.061211787, 0.039662443, 0.036026876, 0.14224064, -0.23701179, 0.01259322, -0.091701694, 0.42408752) * g_9;
    result += mat4(0.017442457, -0.1311232, -0.22520894, -0.049517628, -0.20945188, -0.035541452, -0.13055338, -0.04001523, -0.09402065, -0.19641486, -0.10066238, 0.115912616, -0.10684873, 0.02787531, 0.28450257, 0.02690632) * g_10;
    result += mat4(-0.2659566, 0.43625832, -0.0695883, -0.2624756, -0.2827253, -0.22893822, 0.26025924, 0.24121284, 0.2272709, 0.2178127, -0.15199527, 0.32607552, 0.005909836, 0.056527212, 0.19446251, -0.010751997) * g_11;
    result += mat4(0.1273358, -0.28996274, -0.19322409, 0.018734567, 0.48555133, -0.17389202, 0.13595583, 0.46163267, -0.08973322, -0.30239192, 0.49897516, 0.021815563, -0.2589829, 0.0039008032, 0.056682784, 0.048075546) * g_12;
    result += mat4(0.415353, 0.112207405, 0.20997275, 0.033321556, -0.1327579, 0.12338585, 0.61820966, -0.3411527, 0.018252999, 0.05708125, -0.24571265, 0.11019793, 0.24145919, 0.20340635, -0.0693869, 0.16271423) * g_13;
    result += vec4(-0.07107039, 0.0061239223, 0.0013546069, 0.02994767);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf1, gxy, result);
}