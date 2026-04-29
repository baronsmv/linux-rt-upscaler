// Anime4K_Upscale_GAN_x4_UL - Pass 52 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_21_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_21_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_21_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_21_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_23_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_24_tf3;
#define g_0 (max((texture(sampler2D(tex_conv2d_21_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_21_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_21_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_21_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_21_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_21_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_21_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_21_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_23_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_23_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_25 (max(-(texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.30036786, -0.071122974, -0.207808, -0.104709424, -0.30407256, -0.095840186, -0.1369558, 0.37065065, 0.21078417, -0.13468549, -0.10461771, -0.06559755, -0.17034003, 0.05641996, -0.27700323, -0.1126542) * g_0;
    result += mat4(0.07799722, -0.0022081465, 0.14035574, 0.11457114, -0.09680132, 0.023358248, 0.14260097, 0.06518944, -0.050158285, 0.039226543, -0.22615871, 0.022831999, -0.08471979, 0.30239135, -0.09285331, -0.18434998) * g_1;
    result += mat4(-0.014649615, 0.070524774, -0.17721784, -0.14220548, 0.08645409, -0.09074901, 0.04698468, 0.053715184, 0.06270154, -0.075639635, 0.099860035, -0.090023175, 0.36329654, -0.22055952, 0.010457819, 0.07253135) * g_2;
    result += mat4(-0.027649708, 0.38244903, -0.10621971, 0.2275538, -0.05934175, -0.0010945094, -0.041326273, 0.035898875, 0.03707596, 0.056224752, 0.056418143, 0.07318794, -0.11713561, 0.27461806, -0.14259866, 0.21453623) * g_3;
    result += mat4(0.08535502, 0.29779312, 0.009322038, 0.033960924, 0.23723385, 0.10624898, 0.18388863, -0.1633756, -0.0005816555, 0.11368908, 0.16717602, 0.11334834, -0.05806499, -0.065826096, 0.19527037, 0.31419072) * g_4;
    result += mat4(-0.1170813, 0.055507258, 0.036362253, 0.13286461, 0.026856778, 0.063697964, -0.024295578, -0.054315507, -0.19848196, 0.01567515, 0.14405379, 0.13924678, -0.047252674, -0.16682114, -0.04054276, -0.013275098) * g_5;
    result += mat4(0.036398828, -0.10294437, 0.031097291, -0.23271134, 0.14264303, -0.08633302, 0.12239915, 0.018420607, -0.09747599, -0.071311615, -0.046238452, -0.17322837, 0.040957235, -0.26349834, -0.21181144, -0.05238187) * g_6;
    result += mat4(-0.27340204, -0.080384396, -0.07198998, -0.05323366, 0.14557876, 0.019228118, -0.22286792, 0.20184729, -0.06020158, -0.07255352, -0.11773837, 0.15114646, 0.1300954, -0.12685491, 0.017485369, -0.14980994) * g_7;
    result += mat4(-0.0071375193, -0.24509165, 0.047664706, -0.06106591, -0.1671985, 0.19413634, -0.042350926, 0.03802284, 0.07089803, -0.23365532, 0.18229541, 0.042384386, -0.055314403, 0.25988257, -0.12660997, -0.0090976395) * g_8;
    result += mat4(0.3142646, 0.3923734, 0.17459705, 0.29964787, 0.043381196, -0.21502787, -0.077350974, 0.064285494, 0.2858196, 0.03305409, 0.042962402, 0.19540143, 0.13053122, -0.08383207, -0.12208418, 0.1985712) * g_9;
    result += mat4(0.039936565, -0.0480129, 0.045163006, -0.0016258726, -0.06560048, -0.1440137, 0.073342375, -0.16961938, 0.05413496, -0.1767555, 0.32295126, 0.1549113, -0.03689245, -0.060345363, 0.10861416, 0.051116258) * g_10;
    result += mat4(0.04611299, -0.07580715, 0.2404435, -0.02150482, -0.07586656, -0.10504455, 0.0837787, 0.14586666, -0.08992915, -0.011791581, -0.18516701, 0.18664369, -0.08699046, 0.23641954, 0.1359928, -0.008187404) * g_11;
    result += mat4(-0.09519243, -0.1259728, -0.1609327, 0.0042067054, -0.022335263, -0.089343786, 0.02145024, -0.22889718, -0.082472935, 0.06351865, 0.19912359, -0.041878484, 0.03906691, -0.009029629, -0.095140696, -0.0047787162) * g_12;
    result += mat4(0.2018249, 0.060700044, 0.17174731, -0.020011077, 0.08717426, 0.19148429, 0.06265732, -0.070558965, 0.15527514, 0.1371965, 0.04782656, -0.057176862, 0.005966481, -0.078806885, -0.09565087, -0.08971814) * g_13;
    result += mat4(0.060476594, 0.1829843, -0.14988089, 0.097976886, 0.13092533, 0.16842246, 0.148756, 0.041732185, -0.09868615, -0.05051786, -0.17886515, -0.47046304, -0.0027662877, -0.24125081, -0.20464475, 0.18860999) * g_14;
    result += mat4(-0.12249708, -0.23579642, 0.10373326, -0.11471274, -0.113536574, 0.21705507, -0.020286752, 0.14155044, 0.11744049, -0.10634323, -0.0992358, 0.29779306, 0.009242147, 0.082793355, -0.29470173, 0.09098504) * g_15;
    result += mat4(-0.37456152, 0.27716953, 0.066162, -0.08820556, 0.01543293, 0.1646333, -0.029137572, -0.025982376, 0.0329685, -0.12119456, -0.06776284, 0.05002431, 0.18109421, 0.19071397, 0.031709924, 0.115208045) * g_16;
    result += mat4(0.1638029, 0.07643556, 0.09049366, -0.10921795, 0.03733727, -0.15501708, 0.28316185, -0.098067865, -0.11070625, -0.009504683, 0.2291032, -0.13025075, -0.027869487, 0.011681814, -0.13047922, -0.015909566) * g_17;
    result += mat4(0.1461215, 0.0023516659, 0.15640813, -0.015727978, -0.018806554, 0.017339358, -0.035492163, 0.08160196, 0.10238898, 0.16611558, 0.09202315, -0.10608295, 0.18774536, -0.0316489, 0.27076882, 0.20529412) * g_18;
    result += mat4(0.17409241, -0.1274282, 0.16840927, -0.11176582, 0.09690932, -0.060094807, -0.13033284, -0.024426423, -0.029923867, 0.34295294, -0.10374731, 0.036210388, -0.21488675, -0.048156295, -0.009829659, -0.32526785) * g_19;
    result += mat4(0.04754761, 0.0104225315, -0.14926155, -0.12426483, -0.18664256, 0.089919254, -0.07276312, -0.34654847, 0.08682614, 0.054667328, -0.096311085, 0.28998274, 0.2721617, -0.08974601, -0.078995354, 0.01578445) * g_20;
    result += mat4(-0.16916896, 0.38615093, 0.006609843, -0.13223584, -0.091017894, -0.18239939, 0.010400899, 0.13135849, -0.056513984, -0.1355764, 0.050879743, -0.04195772, -0.041539118, -0.09790294, -0.23622996, -0.1903508) * g_21;
    result += mat4(0.09427743, 0.3532207, -0.07493266, -0.018535644, 0.08661698, 0.36009344, -0.05961479, -0.13691968, 0.0118486015, -0.116584554, -0.08686342, 0.27281806, -0.041298125, -0.07257819, -0.11279752, 0.0034089864) * g_22;
    result += mat4(-0.07194181, -0.087237455, 0.13797516, -0.14510183, -0.043742094, -0.060987025, 0.07932815, -0.03253621, 0.13781914, 0.056654815, -0.077196084, 0.24276413, 0.04511319, -0.051754497, 0.2584921, -0.18890971) * g_23;
    result += mat4(-0.14871578, -0.1849769, -0.08268788, 0.26459882, -0.26126868, -0.23579857, 0.083229534, 0.028019072, -0.25955105, 0.20885234, -0.00086575525, -0.1324121, -0.2294164, 0.17757727, 0.021580774, -0.112975426) * g_24;
    result += mat4(0.16707626, -0.19732544, 0.12970364, -0.09347803, -0.002893719, 0.1150841, 0.055206075, -0.039382495, -0.32302466, 0.14221917, -0.32339764, 0.128217, 0.05848064, -0.08679818, 0.24213648, -0.32777923) * g_25;
    result += vec4(0.08522166, -0.04316711, -0.03290581, 0.024280401);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf3, gxy, result);
}