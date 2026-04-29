// Anime4K_Upscale_GAN_x4_UL - Pass 49 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_24_tf;
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
vec4 result = mat4(0.058696087, -0.016692411, 0.25976986, 0.099469885, -0.09152728, -0.2148431, -0.08802325, -0.016499085, 0.13282052, 0.0980272, -0.1158862, 0.19684108, -0.11994136, -0.059662573, -0.016995221, -0.1027122) * g_0;
    result += mat4(-0.010595027, 0.06406856, 0.23653634, 0.16295283, 0.09336285, -0.027337749, 0.015952548, 0.0376953, 0.095897034, 0.30973884, -0.08175905, -0.22890201, 0.04396234, -0.13037258, -0.025949383, -0.06218012) * g_1;
    result += mat4(-0.07620231, -0.30194682, -0.076309256, 0.14013915, 0.07061645, 0.09126501, 0.1150165, -0.25510675, -0.029847346, 0.11263369, -0.02107326, -0.076345, -0.0836896, -0.10574222, 0.049557228, 0.18204224) * g_2;
    result += mat4(0.31275895, 0.2131336, -0.17616041, -0.1532927, -0.0800748, 0.14726815, 0.011492155, 0.102820344, 0.10141421, -0.014893769, -0.25251386, 0.041055515, -0.10404861, -0.00033553177, -0.19449559, 0.060588796) * g_3;
    result += mat4(0.16963251, -0.013009328, 0.09477736, -0.1371889, -0.057696134, -0.11377323, -0.009975633, 0.10865341, 0.018116307, -0.12912029, 0.00446529, -0.07526829, 0.21180825, 0.023429712, -0.15647651, 0.11771583) * g_4;
    result += mat4(-0.10107582, -0.06897041, 0.07265895, -0.13229463, -0.032618273, -0.1995065, -0.04359697, 0.010246897, 0.08059705, -0.056275643, -0.18562363, 0.076477356, -0.032394793, -0.022298874, 0.04084915, -0.08365395) * g_5;
    result += mat4(0.17930493, 0.05326699, -0.13416114, -0.20071405, 0.04909069, -0.11235366, -0.11290477, 0.054805405, -0.18932551, -0.23691942, 0.00930692, 0.055858135, -0.18744826, 0.124326915, -0.12145515, -0.05469838) * g_6;
    result += mat4(-0.083303414, 0.14274205, -0.17837334, -0.22321583, 0.024028191, -0.22178806, 0.003354423, -0.13398252, 0.11718759, -0.026552575, 0.104777284, -0.16523509, 0.26287836, 0.029216014, -0.04382982, -0.1816694) * g_7;
    result += mat4(0.36169127, 0.036328353, 0.38394243, -0.044287164, 0.026606947, -0.015364243, 0.040234428, -0.14585258, 0.023770748, 0.014420717, -0.18471159, 0.12606202, 0.071438275, 0.015476816, 0.11971924, -0.012690996) * g_8;
    result += mat4(-0.23509689, 0.0076271794, -0.5163756, 0.08395759, -0.18723673, 0.018408693, 0.08788511, 0.15232271, -0.36024943, -0.09240755, -0.30047625, -0.17155606, -0.06985937, 0.20842774, -0.22400227, -0.21664825) * g_9;
    result += mat4(-0.05239372, 0.11904273, -0.08821749, -0.04636995, -0.16663203, -0.11476132, 0.08088593, -0.03589705, -0.01017948, -0.048168585, 0.010544936, 0.13717537, 0.16119, -0.037817374, -0.0762783, 0.03526467) * g_10;
    result += mat4(-0.040259548, -0.14698508, 0.10502734, -0.105779156, 0.17744789, 0.05297252, 0.021307468, -0.21976848, -0.030510878, 0.09223678, -0.09474818, 0.2469629, 0.0013956686, 0.18587582, -0.04157682, 0.1704521) * g_11;
    result += mat4(0.07285109, -0.010645814, -0.07633459, 0.0998653, -0.034591697, -0.20350501, 0.10648686, 0.13691725, 0.042239573, -0.12919825, 0.08137461, -0.027513884, -0.0028005934, 0.03199354, -0.016124157, -0.058441218) * g_12;
    result += mat4(0.05280611, 0.11754696, -0.10911552, 0.316396, 0.15148664, -0.061536465, -0.102609016, 0.037154227, 0.15367137, -0.042577345, 0.06558037, 0.17360497, 0.20247519, -0.032606795, -0.10807613, 0.051761452) * g_13;
    result += mat4(0.0022353246, 0.11659671, -0.14492981, -0.20829871, 0.13133155, 0.12089799, 0.019354021, -0.2658604, 0.04921859, 0.22848538, 0.21938437, 0.16021933, -0.06768084, 0.134724, 0.047685273, 0.077655315) * g_14;
    result += mat4(0.019583335, -0.11596351, 0.20498835, 0.13917811, -0.028330192, -0.07062669, -0.19952956, 0.08023568, 0.0053012795, -0.10001755, 0.24791576, 0.014599471, 0.18118413, 0.027773563, -0.017590087, 0.037026614) * g_15;
    result += mat4(0.097719975, -0.035079796, 0.11477913, -0.13726783, 0.20932943, -0.10429427, 0.13141108, -0.19026637, -0.06115164, -0.23775233, 0.090050876, 0.031347554, 0.0350951, 0.052728195, -0.07699315, 0.24431244) * g_16;
    result += mat4(0.16608196, 0.20575161, -0.40825596, 0.24043176, 0.31130707, -0.046513405, 0.14605568, -0.1021257, 0.1593242, 0.32908028, -0.13133794, -0.08078372, -0.21714397, 0.054140713, 0.15257664, -0.09940761) * g_17;
    result += mat4(-0.1323459, -0.28875232, -0.01497331, 0.030733688, 0.12423061, 0.073697634, -0.2566797, 0.04460948, 0.2865253, -0.13094993, 0.06848032, -0.080888934, 0.09375976, -0.039186817, -0.26337674, -0.098654084) * g_18;
    result += mat4(-0.22869076, -0.06542219, 0.15441294, 0.053751558, -0.10786946, 0.21515097, -0.12272559, 0.113470495, -0.039961167, -0.05458959, 0.056336533, -0.16626738, -0.11003154, 0.16398644, 0.21803926, 0.14490128) * g_19;
    result += mat4(0.005704737, 0.050607253, -0.060669646, 0.02315674, 0.27544695, -0.05550004, -0.32093555, -0.027370991, -0.0070907134, 0.114890516, -0.037459094, 0.26141244, 0.3948764, 0.055632085, 0.12894577, 0.2616119) * g_20;
    result += mat4(-0.16639514, -0.17228165, 0.2578368, 0.18405698, -0.16141811, -0.19922118, 0.0774084, 0.22068399, -0.12284921, 0.10599979, 0.039710265, -0.027798124, -0.103033185, -0.04742161, -0.30192822, -0.08567758) * g_21;
    result += mat4(-0.0868937, -0.10361983, 0.023334388, 0.008042379, 0.26398548, 0.15074515, -0.052286822, -0.10586637, 0.07187348, 0.099190384, -0.1389896, -0.0019672879, -0.14919114, 0.016451705, -0.038644433, 0.04510475) * g_22;
    result += mat4(0.0478762, -0.0032748727, -0.15553872, 0.17001377, 0.010854262, -0.106533505, 0.4341412, 0.24823058, -0.19182336, 0.08669677, 0.030827353, 0.05449623, 0.020789523, 0.13378422, 0.04309073, 0.30953705) * g_23;
    result += mat4(-0.33780453, -0.15031691, -0.18126999, 0.023555402, 0.30662948, -0.013749685, 0.28102842, 0.008741284, -0.14455633, -0.18823312, 0.016984712, -0.261531, 0.33998242, 0.055556037, 0.07087725, -0.10207668) * g_24;
    result += mat4(0.25463784, 0.04663675, 0.24814023, -0.14536841, 0.1517421, 0.13530119, -0.12027553, -0.030012354, 0.15529017, 0.06190467, -0.042643487, -0.14222258, -0.036342848, -0.029681267, -0.0059485766, -0.006802466) * g_25;
    result += vec4(-0.07437017, -0.009831191, 0.0028422514, 0.015599199);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf, gxy, result);
}