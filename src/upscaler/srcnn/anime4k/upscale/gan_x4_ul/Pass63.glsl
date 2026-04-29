// Anime4K_Upscale_GAN_x4_UL - Pass 63 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_27_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_27_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_27_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_27_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_26_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_25_tf;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_28_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups3;
#define g_0 (max((texture(sampler2D(tex_conv2d_27_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_27_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_27_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_27_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_27_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_27_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_27_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_27_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_26_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_26_tf, pointSampler), pos)), 0.0))
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
#define g_26 (max((texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_28 (max((texture(sampler2D(tex_conv2d_28_tf, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_28_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.24645565, 0.05784516, 0.10867771, -0.05984515, -0.028971449, 0.11605379, -0.1291642, -0.014052763, 0.11068091, 0.004926675, 0.20459619, -0.044202894, -0.13706492, -0.04746351, 0.046451483, -0.12730147) * g_0;
    result += mat4(0.16991296, 0.023684578, 0.021467324, 0.112513155, 0.16544406, -0.07930093, 0.11551819, -0.19346547, -0.12460893, 0.12157849, 0.016360888, -0.013482095, 0.09450167, -0.06769771, 0.077387445, -0.0790254) * g_1;
    result += mat4(0.2960009, 0.1488434, 0.006516303, 0.036311023, -0.14754485, 0.055427775, 0.11966719, 0.34234813, 0.061157946, 0.15428309, -0.0006080333, -0.08627383, -0.059905972, -0.22450238, -0.014939416, 0.17368095) * g_2;
    result += mat4(0.07378066, 0.056095265, -0.14646475, 0.052108943, -0.056351613, -0.0075914487, -0.22897565, 0.18092358, -0.30173147, 0.4220325, 0.030691927, -0.04179051, 0.18329756, 0.07725657, 0.04097003, 0.12552805) * g_3;
    result += mat4(-0.10679568, -0.114355184, -0.077642724, 0.03897825, 0.29233125, 0.10134386, -0.0011805982, -0.07966318, 0.06551558, 0.03483564, -0.18145105, -0.09800179, -0.11958348, 0.1625396, -0.030568633, -0.0012501187) * g_4;
    result += mat4(-0.07481191, 0.032259185, 0.28050005, -0.060750138, 0.12653445, 0.058230374, -0.002791269, -0.06543193, -0.0781853, 0.059335645, 0.0038409696, -0.16285823, -0.2594777, -0.16057986, -0.032912817, 0.09385994) * g_5;
    result += mat4(-0.0057511446, -0.05183356, 0.0043450245, 0.06839988, 0.08128163, 0.040296473, -0.01891294, -0.0850551, 0.1050001, 0.10195095, 0.13149269, -0.06505747, -0.024678802, 0.13261814, -0.033877272, -0.035169628) * g_6;
    result += mat4(-0.14846025, -0.13375129, -0.007583847, 0.012587357, -0.09852703, -0.057210695, 0.041786056, -0.21553703, 0.19320351, -0.26314387, 0.05067924, -0.09403354, 0.023944646, 0.07871713, -0.010490625, -0.13831468) * g_7;
    result += mat4(0.11984692, -0.0098591605, 0.12905905, 0.15365292, -0.0012730177, 0.05490899, -0.028208854, -0.1367009, -0.059950594, -0.053963825, 0.2162382, 0.04799995, 0.021240858, -0.07847233, 0.08247004, -0.022988454) * g_8;
    result += mat4(-0.12824033, 0.057294488, -0.14316118, -0.0504033, -0.089879006, 0.034919854, -0.0040405784, 0.031905886, 0.08371419, -0.0362044, -0.0045882226, 0.16748743, 0.054630518, -0.05417787, -0.042437587, 0.25395465) * g_9;
    result += mat4(-0.13144904, 0.2214945, -0.028178846, -0.23956248, -0.15738271, -0.16158687, -0.10207897, 0.042929817, -0.066305175, -0.096577294, 0.04117173, -0.015665123, -0.11068033, 0.0819128, 0.16483264, 0.09976227) * g_10;
    result += mat4(0.19826432, -0.024046648, -0.17804232, 0.16008496, 0.07570708, -0.14472866, 0.04762163, 0.22881216, 0.05690948, 0.22411816, 0.005796563, -0.15312837, -0.123055264, 0.032928593, 0.08476358, 0.08951332) * g_11;
    result += mat4(-0.0019496006, -0.16238998, 0.22266757, -0.2576854, 0.035717808, 0.009473379, 0.017560462, -5.106421e-05, 0.01733539, -0.18899617, -0.14462131, 0.011425934, 0.056977432, -0.018645681, -0.01617488, 0.14064595) * g_12;
    result += mat4(0.015111429, -0.12743704, -0.16131711, 0.09304627, -0.011910577, -0.05745339, -0.039512582, 0.07567732, 0.026060602, 0.028980162, -0.12465325, -0.18355931, -0.20168343, 0.13719437, -0.08599688, -0.18141237) * g_13;
    result += mat4(0.054802295, 0.29837707, 0.03522563, -0.03632989, -0.086978845, 0.00095785136, 0.107393734, 0.044818994, -0.13475525, 0.3006535, 0.07316234, -0.16334157, -0.16008015, 0.020546542, -0.14413168, -0.08525269) * g_14;
    result += mat4(-0.259366, -0.07472293, 0.024179474, -0.038631555, 0.05083423, -0.04494027, 0.06810897, -0.10119448, 0.0068198745, -0.20377721, -0.099571116, 0.06853115, 0.1771495, 0.05278769, 0.116875805, 0.10305356) * g_15;
    result += mat4(0.04593561, 0.20434843, -0.063411824, -0.041401528, 0.11932308, 0.25054318, -0.10001591, 0.034949005, 0.09727825, -0.06489274, 0.05936674, -0.036842782, 0.1862358, -0.11597859, -0.08135922, 0.029445825) * g_16;
    result += mat4(-0.22665091, -0.10780771, -0.04841487, 0.09992152, -0.138711, 0.020387711, 0.015868897, -0.08746323, -0.2086925, -0.015857462, 0.0466177, 0.06748683, -0.01600545, 0.22568497, -0.002262447, 0.016205644) * g_17;
    result += mat4(0.13159914, 0.0085239895, 0.05532446, 0.056012895, -0.1934148, -0.09157347, 0.14135554, 0.052508645, 0.09289656, -0.14269857, 0.030171013, 0.037755817, 0.04909593, -0.18655239, -0.0055961176, 0.1187946) * g_18;
    result += mat4(-0.17952375, -0.024501823, 0.023383398, -0.107995816, 0.08161396, 0.020528542, 0.15347931, -0.0741402, -0.20154397, -0.0015806113, 0.028733943, 0.028272778, -0.2613763, -0.051558394, -0.14001833, -0.050815742) * g_19;
    result += mat4(-0.015107653, -0.0940447, 0.036241457, -0.010593342, -0.045961525, 0.17196755, 0.18697836, 0.031196352, 0.20367323, 0.088155776, 0.045706164, -0.13437189, -0.18159072, 0.36762834, -0.20641692, 0.118886285) * g_20;
    result += mat4(-0.060623996, 0.20019537, 0.18168223, 0.08877838, -0.045696676, 0.061234694, -0.07338814, 0.051613998, -0.25389117, -0.052995674, -0.09211558, -0.16466606, -0.145923, 0.026201494, -0.050066713, 0.08831479) * g_21;
    result += mat4(-0.16469187, -0.16988957, 0.09734995, 0.061539363, -0.13671373, 0.10063324, -0.011433946, -0.086579375, 0.107261725, -0.10270097, -0.012975658, 0.06668877, 0.15680642, 0.07163846, 0.14033522, -0.01405299) * g_22;
    result += mat4(0.132207, 0.03416093, -0.048854396, 0.07515984, 0.078861736, -0.2689559, -0.030746087, -0.11602645, 0.06880567, 0.08204513, 0.06717855, 0.007817995, 0.016181905, 0.040704746, -0.16240671, 0.07026067) * g_23;
    result += mat4(-0.15598467, -0.0022878624, 0.026549233, -0.04394233, 0.20921734, 0.043367602, -0.15613823, 0.04929508, 0.0029379008, 0.04842879, 0.18046685, -0.117088884, -0.22295143, 0.15341441, 0.34251833, -0.16558655) * g_24;
    result += mat4(-0.25135937, 0.043886732, -0.06370679, -0.14021763, -0.21199869, -0.028682569, 0.120286964, -0.12730849, 0.057145018, 0.089308545, 0.18639867, -0.13679394, 0.012308779, -0.22714002, -0.1320638, -0.040500604) * g_25;
    result += mat4(0.049142376, -0.2076546, 0.23179443, 0.14762919, -0.23876101, 0.1215704, 0.16733463, 0.029052794, 0.196647, -0.060006868, -0.05808242, -0.18242458, 0.19578396, -0.05617832, 0.08892038, -0.04199541) * g_26;
    result += mat4(-0.22550662, 0.1297213, -0.07912901, -0.035594005, 0.01997545, -0.24715406, 0.014261541, -0.047214407, -0.22399336, 0.040679913, 0.13449016, -0.02821665, -0.22720997, 0.11576339, 0.12183234, -0.059500802) * g_27;
    result += mat4(-0.12097631, 0.059060633, 0.007883754, -0.19396073, 0.013222453, 0.19267121, 0.04800107, -0.27254722, -0.2901846, 0.21499753, 0.16564848, 0.2441496, -0.14540148, -0.115534924, 0.072310135, -0.085634045) * g_28;
    result += mat4(-0.01119188, 0.09056528, 0.08672538, 0.30530053, 0.040546756, -0.014442347, 0.03800687, 0.08838292, 0.27894083, -0.15870668, -0.088538125, -0.14179976, -0.14808148, 0.29186696, 0.0804609, -0.12542953) * g_29;
    result += vec4(-0.024944633, -0.005018115, -0.03752404, -0.02132803);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups3, gxy, result);
}