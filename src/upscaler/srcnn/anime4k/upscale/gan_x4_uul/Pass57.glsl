// Anime4K_Upscale_GAN_x4_UUL - Pass 57 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_18_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_18_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_18_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_18_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_18_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_18_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_20_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_21_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_18_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_18_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_18_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_18_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_18_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_18_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
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

vec4 hook() {
vec4 result = mat4(-0.18663658, 0.3184948, -0.03130499, 0.08619949, 0.1010918, -0.14248852, -0.19823664, 0.20816846, 0.1601186, 0.049822237, 0.19602141, -0.026865052, -0.0707687, 0.052736435, -0.044807665, 0.066063635) * g_0;
    result += mat4(0.090361156, -0.14197296, -0.23846631, 0.030756485, -0.0624579, 0.0894411, -0.018925495, 0.09622091, -0.08767592, -0.22811596, -0.12307663, 0.053256057, -0.15243548, -0.037156895, -0.29896295, -0.13589491) * g_1;
    result += mat4(-0.29185727, -0.03742425, 0.050431598, -0.05952872, 0.102163635, 0.04785122, -0.02358519, 0.16697437, 0.35186693, -0.19035606, -0.12011042, 0.004166742, -0.006959278, 0.06360376, 0.060225107, -0.15626898) * g_2;
    result += mat4(0.17662838, -0.08894764, -0.14361143, 0.06789356, 0.07816827, 0.10883019, -0.037535142, 0.05493086, -0.041386984, -0.17820516, -0.06743507, 0.08163263, -0.00907744, 0.0041825743, -0.035713505, -0.09867839) * g_3;
    result += mat4(-0.092638604, 0.0022278796, 0.12437326, 0.103134066, -0.27689874, 0.052095678, -0.042521577, -0.07290392, 0.14657746, -0.10676447, 0.035665326, -0.15043491, 0.0066268444, 0.247856, -0.10799263, 0.076561935) * g_4;
    result += mat4(-0.014709424, -0.1234443, 0.09863729, -0.09065224, 0.03188603, 0.0851371, -0.18773592, -0.04526794, 0.04222761, 0.13524239, -0.0077108, 0.014710063, 0.0269728, 0.100834206, 0.00087144354, 0.017908119) * g_5;
    result += mat4(0.065123245, 0.010967681, 0.27781358, -0.00086392177, -0.012103939, 0.21815085, -0.19618537, -0.21287219, -0.3108788, -0.0065051983, -0.10177379, 0.00486042, 0.06495405, 0.28793743, 0.1447245, -0.11581186) * g_6;
    result += mat4(-0.19184732, 0.23525754, 0.14849417, -0.032214705, 0.06332956, 0.036836755, -0.17779079, 0.26069695, 0.017703978, -0.013938178, -0.0028144084, 0.024686655, 0.084200725, 0.0023977484, 0.0010214453, -0.11825634) * g_7;
    result += mat4(0.114283256, -0.11113899, 0.0062027536, -0.11118651, -0.05354193, 0.0024898893, -0.10009308, -0.099993765, -0.09983121, -0.15856577, 0.13581747, 0.11929527, -0.15411879, 0.016686188, -0.15182848, 0.26796317) * g_8;
    result += mat4(0.084827624, -0.08612916, 0.071429096, 0.17416593, -0.04714606, 0.0013476897, 0.013517696, 0.067101866, -0.14903635, 4.9428472e-05, 0.31473428, -0.2949479, -0.12335906, -0.13552824, 0.3479192, -0.19230734) * g_9;
    result += mat4(0.028616413, -0.07255833, -0.021122474, -0.07113967, 0.11709503, -0.20123373, 0.08584415, -0.06978945, 0.03877887, 0.24208583, -0.18075196, 0.0062123733, -0.13526495, -0.04156013, -0.0016269569, -0.020975487) * g_10;
    result += mat4(0.1310379, 0.055372015, -0.006403729, -0.11766523, -0.05418542, 0.03959835, 0.12431779, 0.15253036, -0.021798976, -0.06289866, -0.018096093, -0.021867894, 0.08258678, -0.19130546, -0.020614639, 0.09396607) * g_11;
    result += mat4(-0.08746167, 0.072900996, 0.033214487, 0.04609681, -0.1540511, -0.097863495, -0.18814996, 0.07652809, -0.07314888, -0.12512076, 0.1748569, -0.090817355, 0.20444715, 0.056615118, 0.09610565, -0.25237694) * g_12;
    result += mat4(-0.059253007, -0.30781618, 0.008390624, -0.016397322, -0.033560965, -0.039022774, 0.25333324, -0.1995156, -0.1036445, 0.050644662, -0.16967307, 0.1757263, 0.030297084, 0.046241727, 0.04354335, 0.1062731) * g_13;
    result += mat4(0.2573244, -0.10674188, 0.089680746, 0.05325685, -0.15355112, -0.21602766, 0.3439777, 0.035753187, -0.0219718, -0.049062088, -0.08788193, -0.24782267, 0.07051089, -0.05783363, -0.02401024, -0.20907155) * g_14;
    result += mat4(-0.33404592, -0.093173616, -0.2040588, 0.19875275, 0.12674141, -0.16908246, -0.2689318, 0.0823597, -0.032498408, 0.11139243, 0.020390712, 0.14647515, 0.113650456, 0.038491633, 0.15963453, -0.030297514) * g_15;
    result += mat4(-0.04374134, -0.0129180765, -0.13164769, -0.07293398, 0.11262717, -0.15997183, 0.33422503, 0.073849976, -0.00015811941, 0.18877828, 0.07747786, -0.08188554, -0.18219465, 0.006220583, -0.011983187, -0.056153063) * g_16;
    result += mat4(0.062033445, 0.07369542, -0.11406438, 0.14734034, 0.039975222, 0.07175253, 0.16200112, 0.14343244, -0.025669737, -0.24007507, 0.00080462516, -0.023895608, 0.23648714, -0.09611056, 0.21158028, 0.0735973) * g_17;
    result += mat4(-0.08414368, -0.021285746, 0.0005669404, -0.10731338, -0.0064515774, 0.11334401, 0.03800766, -0.1455488, -0.1261212, -0.22332892, -0.0027348709, 0.2139515, -0.0738863, 0.17665327, 0.09825643, -0.13923496) * g_18;
    result += mat4(-0.10201197, 0.21781366, 0.18577348, 0.14449175, 0.17314741, -0.1521729, 0.05358103, 0.13423039, -0.117372, -0.06376533, 0.0036501242, 0.24701707, -0.1009802, -0.09763199, -0.12387096, 0.04915735) * g_19;
    result += mat4(0.12683278, 0.10003063, 0.026354205, 0.20679879, -0.05543329, 0.0609024, 0.12071361, -0.017081672, 0.09073765, 0.26451552, 0.11525583, 0.15612826, 0.15255655, -0.089416705, -0.066638984, 0.14400561) * g_20;
    result += mat4(-0.035610262, -0.21110137, 0.16128647, 0.16987562, -0.075286984, 0.10626652, 0.02610956, 0.072617754, 0.08083012, -0.076612055, -0.20788178, -0.18980946, -0.124521755, -0.09931777, 0.058994036, -0.1573874) * g_21;
    result += mat4(0.040990368, -0.076015316, 0.23061185, 0.06046172, -0.20775267, 0.07282112, -0.06703266, -0.15523846, -0.09839281, 0.04264288, 0.062170573, 0.050776828, 0.082359515, 0.08156233, 0.08537614, -0.15101717) * g_22;
    result += mat4(-0.1249208, 0.13122208, -0.12867546, 0.1732467, 0.25579265, -0.012121687, 0.055682763, 0.16973646, 0.12742467, -0.18509331, -0.07107552, 0.18292974, 0.09319081, 0.05175007, 0.032850564, -0.22456838) * g_23;
    result += mat4(0.081253335, 0.0648804, -0.15536025, -0.06642495, 0.16779053, -0.06261765, 0.20884722, 0.035119522, 0.10021793, -0.034050878, -0.20697917, 0.3424921, 0.14770742, 0.053394657, 0.03791968, -0.00457689) * g_24;
    result += mat4(-0.30276582, 0.11398664, 0.23705474, 0.19467491, 0.03581071, 0.010649232, -0.059531577, -0.13225733, -0.05157955, -0.056399573, -0.05065601, 0.115134716, -0.06892023, -0.02327887, -0.026891273, -0.051847365) * g_25;
    result += mat4(-0.0038954976, 0.30134967, 0.07478171, 0.27801678, -0.25552303, -0.3496495, -0.04389904, -0.073157154, -0.3068193, -0.14130415, -0.09492658, -0.07742016, -0.098369256, 0.07939278, 0.06842935, -0.058692418) * g_26;
    result += mat4(0.033151552, -0.17501067, -0.24207892, -0.020800477, 0.40200472, 0.38354096, -0.09372771, 0.13056894, 0.1521215, -0.022638181, 0.076644436, 0.19175975, 0.17724091, -0.007068142, 0.08166245, 0.075242795) * g_27;
    result += vec4(-0.06944472, -0.040001452, -0.014700824, -0.030359665);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf, gxy, result);
}