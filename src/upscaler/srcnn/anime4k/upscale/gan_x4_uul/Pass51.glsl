// Anime4K_Upscale_GAN_x4_UUL - Pass 51 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_15_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_15_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_15_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_15_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_15_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_15_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_17_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_18_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_15_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_15_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_15_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_15_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_15_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_15_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_15_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_15_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_15_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_15_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_15_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_15_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_17_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_17_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_25 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.07275335, 0.14898193, 0.05103475, -0.24677557, -0.04590853, 0.18598412, 0.17042433, 0.25112963, -0.25387946, 0.16816492, 0.042718515, -0.07254226, -0.123994775, 0.018808274, 0.112001434, 0.025319412) * g_0;
    result += mat4(0.2535324, 0.24990268, 0.0028210187, 0.10466241, -0.061642785, 0.28444982, 0.076121055, 0.053076364, -0.52522933, 0.2632941, 0.19820404, 0.05237143, 0.26571947, 0.10656059, 0.043669626, 0.04990818) * g_1;
    result += mat4(0.08245741, 0.14015213, 0.18104555, 0.10484035, 0.16811769, -0.041335564, -0.033331893, 0.033417568, 0.11096319, 0.030447075, -0.09328212, 0.04628232, -0.07635939, 0.07020028, -0.2722409, -0.060951874) * g_2;
    result += mat4(0.010335018, 0.32633916, 0.12625806, -0.3094073, 0.29249397, -0.3108912, 0.11901825, -0.07490385, 0.17830479, -0.20337716, 0.054164883, 0.28893295, 0.18187387, 0.053543147, -0.10075131, 0.0034320771) * g_3;
    result += mat4(-0.02826832, 0.11724661, -0.06962717, 0.12613653, -0.23680139, 0.004728264, 0.043008044, -0.22754075, -0.0716446, -0.14434932, -0.17710604, -0.11561461, 0.37956393, -0.16996142, 0.040763404, 0.07495938) * g_4;
    result += mat4(0.06707339, 0.40558064, 0.21503006, -0.2594568, -0.22734876, 0.26095417, 0.053693745, -0.14698361, 0.07437207, 0.24770571, 0.120787956, -0.030818382, -0.047236454, -0.48851666, -0.0031445923, 0.22892044) * g_5;
    result += mat4(-0.04945736, 0.26467103, 0.049671993, 0.047162287, 0.061514832, 0.15016414, -0.10250111, -0.3007125, 0.20936479, 0.27691036, -0.02891184, -0.025837302, 0.19422647, 0.11701095, -0.08495193, -0.13676211) * g_6;
    result += mat4(-0.10254167, -0.16630745, -0.34381193, 0.06600585, -0.10242925, -0.055404972, 0.021561349, 0.10897398, -0.10120918, -0.13307574, -0.014301925, 0.1969603, -0.14377114, -0.089617215, 0.0022043488, 0.0038541725) * g_7;
    result += mat4(-0.14566253, 0.22117427, 0.050736886, 0.12268627, -0.080971554, 0.0658161, -0.09683872, -0.0103765065, 0.18371643, -0.019395225, -0.120815344, 0.13516186, 0.05761091, 0.008207175, 0.36346915, 0.026339587) * g_8;
    result += mat4(0.07948127, -0.08477327, -0.16991964, 0.2505722, -0.1902803, 0.079657145, -0.048453137, -0.09438733, -0.122441165, -0.06270245, -0.05311665, 0.13945523, -0.17516851, 0.1292089, -0.17136113, -0.055618342) * g_9;
    result += mat4(-0.002150108, 0.02283226, -0.13090558, 0.033127207, 0.06023704, -0.06849595, 0.046912603, 0.034401193, 0.010757264, 0.19490354, 0.0116163725, 0.18590987, 0.025350608, -0.11296784, 0.049074072, -0.10146356) * g_10;
    result += mat4(-0.02068922, 0.030495135, 0.120516464, 0.15653776, -0.1632823, -0.055421073, 0.07736736, -0.250596, -0.056524616, -0.038208432, -0.14350441, 0.09898008, 0.0051016, 0.15592806, 0.14021751, 0.019436443) * g_11;
    result += mat4(-0.14777614, 0.17289229, 0.2744722, -0.038262386, 0.043346573, 0.22880417, 0.035564966, -0.07677456, 0.11968518, -0.22628254, 0.06328974, -0.15619329, 0.06524249, 0.046800073, 0.110473916, -0.15548) * g_12;
    result += mat4(0.25480956, 0.14005896, 0.09140913, 0.054437663, 0.0004533271, -0.034787837, -0.1323544, -0.12815407, -0.084788546, 0.09716086, -0.13819875, 0.17354825, 0.10694976, 0.0016070876, 0.16901751, -0.29687676) * g_13;
    result += mat4(0.110094875, 0.05579302, -0.0027500705, -0.23052558, 0.029316107, 0.025380356, -0.2670241, 0.21118346, -0.17167161, 0.021439673, 0.075709194, 0.035738192, 0.069175325, -0.11928909, 0.0609199, -0.07018926) * g_14;
    result += mat4(0.053545795, 0.30914584, 0.0083375275, 0.024702856, 0.091693155, -0.12650286, -0.05307018, -0.009256227, -0.17785516, 0.019424014, 0.0064009326, -0.064602405, -0.23181896, 0.18487184, -0.041830298, 0.015233306) * g_15;
    result += mat4(0.0983137, -0.02332874, -0.16712289, 0.110043615, 0.20248997, 0.46069786, -0.04481748, 0.037059803, -0.111577116, -0.023646941, 0.044005208, -0.046400744, 0.27068818, -0.02549177, -0.23175907, -0.013831666) * g_16;
    result += mat4(-0.060007934, -0.10096949, 0.054297656, 0.07113129, 0.04455678, 0.26144683, -0.34634766, -0.046529762, -0.031835936, -0.10379009, 0.19875336, 0.018076476, -0.07739257, -0.013014384, -0.11888874, 0.22789921) * g_17;
    result += mat4(-0.12075386, 0.13691123, 0.084494345, -0.15709634, -0.09436252, 0.038024623, 0.06776821, -0.07152998, -0.13886653, 0.029662577, 0.1038584, -0.038791, -0.09553779, -0.18302377, -0.01212077, 0.14089715) * g_18;
    result += mat4(-0.057872534, -0.00011801619, -0.18532518, 0.076057665, -0.42539987, -0.07312798, -0.04669854, -0.23879579, -0.012684431, 0.09458908, -0.09142282, -0.12451197, 0.2476217, 0.074229516, -0.082316175, -0.044077393) * g_19;
    result += mat4(0.28468457, -0.040408906, -0.106139034, -0.27775, -0.09903486, 0.10510825, -0.030768666, 0.025477748, 0.052054677, 0.06462344, 0.08219105, -0.31942672, -0.1009352, -0.1137351, -0.03437056, 0.19018868) * g_20;
    result += mat4(0.102790736, -0.015214254, 0.13167804, -0.010143135, 0.20543955, 0.109071806, 0.009985071, 0.044157047, -0.0702753, 0.12881173, 0.11038061, 0.050384365, 0.0945336, -0.0092124175, 0.02406746, -0.16884717) * g_21;
    result += mat4(-0.016257925, -0.29831296, 0.0016857416, -0.25284603, -0.093083024, 0.076591246, -0.16160022, 0.11423315, 0.009033389, 0.29160973, -0.017032826, -0.15522738, -0.011398442, 0.21191356, -0.07039929, 0.11179371) * g_22;
    result += mat4(-0.22552256, 0.23648272, 0.04632884, 0.19379017, -0.013058757, 0.04581136, 0.07059032, -0.016221967, 0.19233103, 0.22866032, -0.06603767, -0.07290105, -0.1454335, -0.20352724, -0.11494829, -0.008654449) * g_23;
    result += mat4(-0.22305818, 0.062374588, 0.09524618, 0.13345708, -0.017654542, -0.29984674, 0.14792737, 0.3332384, 0.15762518, -0.114883184, -0.044198688, 0.1029124, -0.19856718, -0.23805596, -0.14726463, 0.244083) * g_24;
    result += mat4(0.14181834, -0.15349664, -0.21518064, 0.05561381, -0.098451905, 0.32704952, -0.0208272, -0.02572841, 0.0006366284, 0.086487964, 0.23271829, -0.1431307, 0.16303279, -0.07606844, 0.028287608, 0.10664057) * g_25;
    result += vec4(0.082762346, -0.07846427, -0.039599236, -0.016365785);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf2, gxy, result);
}