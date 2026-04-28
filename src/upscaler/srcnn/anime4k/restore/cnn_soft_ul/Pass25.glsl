// Anime4K_Restore_CNN_Soft_UL - Pass 25 of 25 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_MAIN;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_3_tf1;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_3_tf2;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf1;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf2;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_5_tf1;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_5_tf2;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_7_tf1;
layout(set = 0, binding = 1039) uniform texture2D tex_conv2d_7_tf2;
layout(set = 0, binding = 2048, rgba8) uniform image2D img_output;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_7 (max((texture(sampler2D(tex_conv2d_4_tf1, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_4_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_4_tf1, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf2, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_13 (max((texture(sampler2D(tex_conv2d_5_tf1, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_5_tf2, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_16 (max(-(texture(sampler2D(tex_conv2d_5_tf1, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_5_tf2, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_19 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_22 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_25 (max((texture(sampler2D(tex_conv2d_7_tf1, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_7_tf2, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_28 (max(-(texture(sampler2D(tex_conv2d_7_tf1, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_7_tf2, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.053345524, 0.066197485, 0.07259881, 0.0, 0.05303127, 0.06742834, 0.07375377, 0.0, 0.094053976, -7.700613e-05, -0.02473139, 0.0, 0.005308593, 0.03030767, 0.039729137, 0.0) * g_0;
    result += mat4(-0.108758785, 0.037586506, 0.065435104, 0.0, 0.027483977, -0.05654698, -0.076396726, 0.0, 0.105040714, 0.05024414, 0.021126145, 0.0, -0.0674868, -0.0055504893, 0.02190656, 0.0) * g_1;
    result += mat4(-0.053890713, 0.0071396744, 0.016984116, 0.0, -0.045092918, 0.025137635, 0.041979324, 0.0, -0.03408237, 0.0019260172, 0.005701325, 0.0, -0.02040999, -0.01315308, -0.00639404, 0.0) * g_2;
    result += mat4(-0.073155664, -0.06887698, -0.072435565, 0.0, -0.08694837, -0.05531286, -0.055365037, 0.0, -0.06690585, -0.00129934, 0.013128711, 0.0, -0.045931015, 0.017999481, 0.021670034, 0.0) * g_3;
    result += mat4(0.14758188, -0.052864034, -0.06617946, 0.0, -0.025215192, 0.005785653, 0.02022865, 0.0, -0.07359226, -0.034944568, -0.01911832, 0.0, -0.059109453, 0.0018033485, -0.022261323, 0.0) * g_4;
    result += mat4(0.079963796, 0.018210623, -0.0025736517, 0.0, 0.06693135, -0.038985185, -0.04726813, 0.0, -0.03559407, -0.0083629545, -0.005753532, 0.0, 0.043954816, -0.022223696, -0.039470144, 0.0) * g_5;
    result += mat4(0.060458526, -0.0033674864, -0.006985535, 0.0, -0.013925546, 0.051077038, 0.053856038, 0.0, -0.033647064, 0.043235198, 0.05311577, 0.0, 0.0391791, -0.044376004, -0.054064214, 0.0) * g_6;
    result += mat4(0.0069859014, -0.0050665336, -0.010343517, 0.0, -0.027551029, 0.049856182, 0.058316905, 0.0, 0.0121670095, -0.013107907, -0.0151846, 0.0, 0.007648614, -0.0051277154, -0.0053846613, 0.0) * g_7;
    result += mat4(0.06848036, 0.026777437, 0.024801696, 0.0, -0.08711668, 0.049429595, 0.067019165, 0.0, -0.09006778, -0.042166695, -0.02230536, 0.0, -0.048024856, -0.020088708, -0.009932858, 0.0) * g_8;
    result += mat4(-0.05171447, 0.0029948682, 0.014913949, 0.0, 0.02287364, -0.042476606, -0.052956346, 0.0, 0.02762833, -0.044026252, -0.056759696, 0.0, -0.0519502, 0.047626793, 0.06422155, 0.0) * g_9;
    result += mat4(-0.0031128856, 0.013134638, 0.021534251, 0.0, 0.049189907, -0.039677586, -0.057255603, 0.0, -0.009908353, -0.0013683038, 0.0028079485, 0.0, 0.0002268831, 0.012356764, 0.009817244, 0.0) * g_10;
    result += mat4(-0.04058634, -0.01822148, -0.014306331, 0.0, 0.107378654, -0.04138371, -0.058573496, 0.0, 0.03701269, -0.009420217, -0.02310707, 0.0, 0.039931968, 0.001769326, -0.007929419, 0.0) * g_11;
    result += mat4(0.027129134, 0.01044246, 0.008198051, 0.0, -0.019978391, 0.014817045, 0.014294805, 0.0, -0.009071333, -0.018233696, -0.020756468, 0.0, -0.016967475, -0.010472854, -0.0066578956, 0.0) * g_12;
    result += mat4(0.012473992, -0.019771596, -0.02515739, 0.0, -0.008238026, 0.026189122, 0.034326296, 0.0, 0.01735337, -0.021417223, -0.027291182, 0.0, 0.01815212, -0.012736875, -0.021111157, 0.0) * g_13;
    result += mat4(0.022218483, -0.023485998, -0.03540812, 0.0, 0.016531168, -0.0033816632, -0.010179393, 0.0, -0.03181473, -0.0072774286, 0.0014077872, 0.0, -0.0025735856, -0.015998563, -0.016743565, 0.0) * g_14;
    result += mat4(-0.01740865, 2.3718083e-05, 0.0032518203, 0.0, 0.009272118, -0.01676428, -0.019791994, 0.0, 0.013665012, 0.02245221, 0.022923533, 0.0, 0.020898446, 0.012111701, 0.009756352, 0.0) * g_15;
    result += mat4(-0.0043926076, 0.019400991, 0.022581568, 0.0, 0.003538965, -0.031301565, -0.0345112, 0.0, -0.02405352, 0.006159623, 0.016130725, 0.0, -0.0097925, 0.01677507, 0.027652735, 0.0) * g_16;
    result += mat4(-0.03267886, 0.014923966, 0.027258545, 0.0, -0.033668566, -0.010421195, -0.0026646685, 0.0, 0.015094835, -0.0023233194, -0.015871005, 0.0, -0.01258443, 0.00507582, 0.0053544766, 0.0) * g_17;
    result += mat4(0.012708346, 0.014336439, 0.012533707, 0.0, -0.0019346073, -0.0070978077, -0.009478742, 0.0, -0.011659758, -0.009855903, -0.008657096, 0.0, 0.0098037105, 0.010785594, 0.008409619, 0.0) * g_18;
    result += mat4(0.0056228717, 0.013483413, 0.008108323, 0.0, -0.0013697809, 0.0026797573, 0.0037666177, 0.0, 0.0130932415, 0.019868238, 0.01968549, 0.0, 0.011160769, 0.012374028, 0.012855804, 0.0) * g_19;
    result += mat4(0.0011662204, 0.00025071716, 0.0022244148, 0.0, -0.017808594, -0.013589306, -0.01396329, 0.0, -0.008117086, -0.0068251803, -0.004963602, 0.0, -0.0069141523, -0.009125296, -0.008327947, 0.0) * g_20;
    result += mat4(-0.027597412, -0.02631107, -0.022816146, 0.0, 0.009350171, 0.013661565, 0.015324706, 0.0, 0.032538984, 0.02918167, 0.026186563, 0.0, 0.018760988, 0.024502547, 0.023201061, 0.0) * g_21;
    result += mat4(0.013216693, 0.00991115, 0.01178417, 0.0, 0.0076343333, 0.004714098, 0.0074490295, 0.0, -0.0064893183, -0.014818341, -0.01199717, 0.0, -0.008334491, -0.009955103, -0.011240684, 0.0) * g_22;
    result += mat4(-0.013846397, -0.012687341, -0.015767701, 0.0, -0.0019117722, -0.0072347773, -0.0074835457, 0.0, 0.013531867, 0.014263165, 0.012797156, 0.0, 0.008260445, 0.0070536416, 0.0065693366, 0.0) * g_23;
    result += mat4(0.0017003485, 0.0021871394, 0.0003407296, 0.0, 0.0054420815, 0.00801073, 0.008788295, 0.0, -0.012685104, -0.0150940735, -0.017530257, 0.0, -0.030698642, -0.030817484, -0.028548386, 0.0) * g_24;
    result += mat4(-0.008882145, -0.008943836, -0.007986094, 0.0, -0.010494911, -0.011511255, -0.00892924, 0.0, 0.014072905, 0.014985031, 0.011853883, 0.0, -0.015823284, -0.017817877, -0.01684662, 0.0) * g_25;
    result += mat4(0.012270136, 0.011127063, 0.010729208, 0.0, 0.00027298275, 0.001011805, 0.001318525, 0.0, 0.0029811305, 0.0029161042, 0.0060088155, 0.0, 0.00021241597, -0.0013439909, 0.0013205905, 0.0) * g_26;
    result += mat4(-0.03467924, -0.035764243, -0.03348244, 0.0, 0.023858175, 0.02580526, 0.026217844, 0.0, -0.016814101, -0.016412167, -0.012021982, 0.0, -0.0007905926, -0.0019904284, -0.0015143935, 0.0) * g_27;
    result += mat4(0.046779703, 0.04961137, 0.046104047, 0.0, -0.023665644, -0.022809561, -0.02236428, 0.0, -0.054706786, -0.056090504, -0.052543454, 0.0, -0.015520943, -0.01587306, -0.0142722875, 0.0) * g_28;
    result += mat4(0.020273875, 0.020399818, 0.021745082, 0.0, 0.037485637, 0.039574977, 0.03556703, 0.0, 0.036673885, 0.04102765, 0.033708427, 0.0, 0.024422405, 0.027724478, 0.0252598, 0.0) * g_29;
    result += vec4(-0.0036656514, 0.006677459, 0.007698717, 0.0);
    return result + texture(sampler2D(tex_MAIN, pointSampler), pos);
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_output, gxy, result);
}