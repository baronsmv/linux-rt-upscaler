// Anime4K_Upscale_GAN_x4_UUL - Pass 77 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_24_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_24_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_24_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_24_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_24_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_24_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_23_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 1039) uniform texture2D tex_conv2d_25_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups5;
#define g_0 (max((texture(sampler2D(tex_conv2d_24_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_24_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_24_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_24_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_24_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_24_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_24_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_24_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_24_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_24_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_24_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_24_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_23_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_23_tf, pointSampler), pos)), 0.0))
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
#define g_26 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_28 (max((texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_30 (max((texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_31 (max(-(texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.011561234, -0.012465957, 0.061722398, 0.004109507, 0.11449728, 0.30646765, 0.11597718, 0.044809423, -0.15796961, 0.09144391, 0.025600316, -0.016890302, -0.06273143, -0.09406291, -0.13892512, 0.107323244) * g_0;
    result += mat4(0.26843497, 0.07754772, -0.040967893, 0.14208253, -0.22981443, 0.09998915, 0.12629654, 0.05489728, 0.20781358, -0.06494287, 0.107708186, -0.12273423, 0.03810808, -0.00919042, 0.07503909, -0.10436984) * g_1;
    result += mat4(-0.04123376, 0.061480578, 0.09167497, 0.0717715, 0.08920449, -0.059116304, -0.051456068, 0.1435225, -0.0054245745, -0.07957629, 0.012718112, -0.1371298, -0.05244197, -0.001466458, 0.018672079, 0.16870362) * g_2;
    result += mat4(-0.0711777, 0.083937705, 0.0055865357, 0.086037554, -0.0026764858, -0.09261858, 0.11146104, 0.034576505, -0.059654012, -0.16707183, -0.010578452, -0.22554928, -0.032461595, 0.023646196, 0.10213768, 0.039538495) * g_3;
    result += mat4(-0.08187879, -0.14176089, -0.11134647, -0.0014680476, -0.01505771, 0.0028695054, 0.13650699, 0.09581829, 0.08451168, 0.0593946, -0.022487655, -0.053191096, -0.13652085, -0.18934551, 0.081316985, -0.10670004) * g_4;
    result += mat4(0.3095398, 0.15461108, 0.08192997, 0.36671337, -0.23491316, 0.16552022, 0.06679685, -0.014910402, 0.17080174, 0.07363078, -0.05000375, -0.10863247, -0.17515467, -0.13650203, 0.17658728, 0.09099435) * g_5;
    result += mat4(0.24561775, 0.085898094, -0.09029496, -0.062148836, -0.13314761, -0.1805575, 0.072130956, 0.010657738, 0.12118199, -0.10993774, -0.2077007, 0.13921109, 0.032653514, 0.099179596, 0.029785015, -0.07210813) * g_6;
    result += mat4(0.05213782, 0.02070249, -0.1519397, -0.15459941, 0.12078409, -0.1018201, -0.15649813, -0.09451276, 0.08978216, 0.033983372, -0.325133, 0.03649046, 0.034768645, 0.01820811, -0.1476437, -0.05215747) * g_7;
    result += mat4(0.25730282, -0.03574445, -0.26939863, 0.056570202, -0.03860821, 0.064086504, 0.049936775, -0.09219466, -0.23501472, 0.11891639, 0.16585156, -0.06937759, 0.17275843, -0.005933774, -0.038747568, -0.1872246) * g_8;
    result += mat4(0.29699612, -0.12036312, -0.17994614, 0.06254196, 0.052887265, 0.10139881, -0.015890123, 0.014276093, -0.08473576, 0.20360646, 0.0719401, 0.116043195, -0.04480997, -0.16405116, 0.06848916, 0.029303674) * g_9;
    result += mat4(0.039084256, 0.16812262, -0.045461234, 0.15141405, -0.053278796, 0.0499866, -0.09262412, 0.024975844, -0.10941919, 0.020637758, -0.13150725, 0.120833196, 0.080852345, 0.14054763, 0.11314371, 0.11749595) * g_10;
    result += mat4(-0.07858139, -0.11847648, -0.08926328, 0.04630698, 0.20156343, -0.11537608, -0.042400904, 0.08154081, 0.27824274, -0.18951182, -0.19521928, 0.16003811, 0.10160072, 0.084651895, -0.081367895, -0.1803879) * g_11;
    result += mat4(-0.015178554, 0.1453211, 0.0029462255, -0.015893389, -0.0070375055, 0.20207931, -0.05530542, 0.08762223, -0.029634364, -0.023058303, 0.04852642, 0.028570767, 0.0017521627, -0.038801666, 0.008321414, 0.013272434) * g_12;
    result += mat4(0.112933494, 0.00077646604, 0.15631917, 0.12212562, -0.035100516, -0.15636574, 0.0869713, -0.040045064, -0.043343354, -0.17186165, 0.040316343, -0.040707536, 0.033326153, -0.07299361, 0.10777621, 0.044213336) * g_13;
    result += mat4(-0.057331394, -0.29746646, -0.21014963, -0.27668902, -0.07744173, -0.19646992, -0.1978878, -0.148482, -0.038296875, 0.023684174, -0.011479595, -0.3131539, 0.1081339, 0.17462969, 0.23045957, 0.06817404) * g_14;
    result += mat4(-0.05616912, 0.44082153, 0.13635121, 0.5260593, 0.068167746, 0.1159533, 0.18762758, 0.06370536, 0.24268357, -0.031904045, -0.03593457, 0.1761274, -0.25467318, -0.27158144, 0.21026418, -0.35541326) * g_15;
    result += mat4(0.04480854, 0.40541658, 0.12650406, 0.14116916, -0.12694973, 0.070857644, -0.1654552, -0.38093325, 0.1730254, 0.23093973, -0.17948884, 0.18496381, 0.19546366, -0.11564827, -0.10936328, -0.13326254) * g_16;
    result += mat4(0.02783123, -0.16448286, -0.27236226, -0.10730039, -0.10582441, 0.2894545, -0.12485313, 0.09168738, -0.13905063, -0.32243901, 0.12184465, -0.078383766, -0.20384146, 0.10552737, 0.1335408, 0.19632344) * g_17;
    result += mat4(-0.036966056, -0.07765606, -0.042519376, -0.18071535, 0.094343245, -0.11750975, -0.115932606, -0.14168039, 0.10521408, -0.1797702, -0.2014665, 0.06983729, -0.043030553, -0.20928553, -0.1358945, -0.19139649) * g_18;
    result += mat4(0.014309759, -0.029078862, 0.11430482, 0.15110584, 0.059152886, -0.05306251, 0.08139934, 0.02904774, -0.15470253, 0.10313861, 0.30107433, -0.16773193, -0.094181724, 0.057134327, 0.00092695246, 0.08184109) * g_19;
    result += mat4(0.02506316, 0.0867775, -0.08693349, 0.0878035, 0.030453114, 0.042106513, -0.017756486, 0.02601538, -0.054069374, 0.048818395, 0.02386837, 0.024829991, 0.023034105, 0.0051381323, -0.020198671, -0.09797366) * g_20;
    result += mat4(-0.023844786, 0.0016428459, 0.123326644, 0.08708688, -0.01703554, -0.06808432, -0.12352092, -0.08645188, 0.009277621, -0.07319661, 0.011372869, -0.22492659, -0.014993174, 0.058244362, -0.105234556, 0.00219484) * g_21;
    result += mat4(0.08174906, 0.12529619, 0.053283885, -0.009235874, -0.04773854, -0.12894803, 0.081467494, 0.016731197, 0.05052568, 0.14297223, 0.10280411, -0.03163778, 0.0055582365, -0.012498803, 0.0059484374, -0.031531356) * g_22;
    result += mat4(-0.05330085, -0.04974306, -0.079764664, 0.010079839, 0.11561185, 0.026386917, -0.1173086, 0.07318347, 0.022758875, -0.053391833, -0.14447209, -0.0064598285, -0.0024759816, -0.006995636, 0.0007184077, -0.069488235) * g_23;
    result += mat4(0.07302404, -0.08720752, -0.037079513, 0.0003512964, 0.02232102, -0.095264226, 0.036082335, -0.00036828392, 0.08033609, -0.04303644, -0.05187976, -0.066657886, -0.059702326, -0.06550579, 0.034914013, -0.038357385) * g_24;
    result += mat4(-0.04311525, 0.04406852, 0.0022629597, 0.055104118, -0.058384016, 0.062843435, -0.03903992, -0.024547735, 0.0030863932, 0.12553258, 0.004523987, 0.041851215, 0.02736582, 0.0037202195, 0.008346716, -0.00066181086) * g_25;
    result += mat4(-0.10727989, 0.033605255, -0.028996287, -0.10822878, 0.14796142, -0.10711968, -0.19416648, 0.07545809, -0.011922665, 0.15432714, -0.07223956, -0.0389031, 0.056309763, -0.031701643, -0.15709357, -0.085562445) * g_26;
    result += mat4(0.015703637, -0.06475049, -0.14153144, 0.059910253, -0.14977545, -0.06390219, 0.13375331, -0.14298701, 0.1305803, -0.050405364, 0.03631835, 0.22620685, -0.050843332, 0.038208447, 0.026526114, -0.017080935) * g_27;
    result += mat4(0.12688361, 0.056371618, 0.10022545, 0.15378883, -0.118205115, -0.013227478, 0.07664092, -0.13813822, -0.16385357, 0.03870268, 0.17708874, 0.008884885, -0.2010594, 0.11686294, 0.19129558, 0.020952912) * g_28;
    result += mat4(0.019549163, -0.15760489, -0.10022573, 0.15503788, 0.14201608, 0.042376533, -0.052286524, 0.11653048, 0.13872318, 0.07111845, -0.12428939, -0.0038820026, 0.15195651, 0.0346821, -0.08822089, -0.003574916) * g_29;
    result += mat4(0.006056049, -0.07287368, -0.18514961, 0.04915554, 0.091064215, 0.27121982, -0.051693153, -0.22751212, -0.18204577, 0.0221348, 0.07865922, -0.22364894, 0.010186452, -0.012915454, 0.049386848, 0.03228151) * g_30;
    result += mat4(0.109998666, 0.012412288, 0.1361162, 0.06420964, -0.19105789, 0.100528404, 0.12032071, 0.11792962, -0.16980593, -0.13456152, -0.08864147, -0.23975545, -0.015304083, 0.054322414, 0.032784272, 0.01145087) * g_31;
    result += vec4(0.07406925, -6.918896e-05, -0.08913489, -0.016446702);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups5, gxy, result);
}