// Anime4K_Upscale_CNN_x2_UL - Pass 23 of 25 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_2_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_2_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_3_tf1;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_3_tf2;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_4_tf1;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf2;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_5_tf1;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_5_tf2;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_last_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_2_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_2_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_2_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_2_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_7 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max((texture(sampler2D(tex_conv2d_4_tf1, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_4_tf2, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_16 (max(-(texture(sampler2D(tex_conv2d_4_tf1, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf2, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_19 (max((texture(sampler2D(tex_conv2d_5_tf1, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_5_tf2, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_22 (max(-(texture(sampler2D(tex_conv2d_5_tf1, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_5_tf2, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_25 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_28 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.016576298, -0.013039568, -0.07158028, -0.056509558, -0.06965122, -0.1272158, -0.07288651, -0.10423224, 0.048223313, 0.03172697, 0.014178331, 0.002855858, 0.004538786, 0.034928907, 0.03173054, 0.03412037) * g_0;
    result += mat4(0.09168274, 0.056355372, 0.023804985, 0.009515965, 0.024203284, 0.01641063, 0.016683895, -0.012702561, -0.038824845, -0.037673414, -0.010391583, -0.014636746, 0.03192526, -0.02340906, 0.027524544, -0.015568387) * g_1;
    result += mat4(-0.0966996, -0.041418746, -0.055650715, 0.002117608, 0.00031688716, -0.008733063, -0.024573568, -0.03425321, -0.036262326, 0.04404278, -0.014729649, 0.05618371, 0.008530102, -0.015607405, 0.015309457, -0.013621667) * g_2;
    result += mat4(0.0361472, 0.025806008, 0.0583716, 0.06861344, 0.06315231, 0.10136267, 0.050169814, 0.07334672, -0.029601635, -0.06431154, -0.030672554, -0.042512666, -0.051434014, -0.039382752, -0.050772913, -0.08629934) * g_3;
    result += mat4(-0.02201249, -0.03920109, -0.030633967, -0.0530296, -0.016168922, 0.0019067918, -0.014961821, 0.017761061, 0.012465623, 0.01857369, 0.009440995, -0.014336409, 0.0056113736, 0.012547043, 0.019320931, 0.025894852) * g_4;
    result += mat4(0.079413086, 0.055332463, 0.023716403, 0.005429431, 0.0043804864, 0.026764238, 0.011610661, 0.03245363, -0.032408644, -0.056873523, -0.0019144824, -0.026196169, -0.03347332, -0.0174185, -0.00020654689, 0.023554688) * g_5;
    result += mat4(-0.055310458, -0.079070315, 0.0066684894, -0.034588877, -0.07334732, -0.000985991, -0.011984627, 0.08308032, 0.011794159, -0.0144758625, 0.03586815, 0.009038553, -0.0016798767, 0.045218308, 0.016524237, 0.045677744) * g_6;
    result += mat4(0.0083010085, 0.028407311, 0.06600332, 0.07460616, 0.071611166, 0.09643883, 0.034676284, 0.05824412, -0.07973774, -0.030707551, -0.03709346, 0.012161441, -0.02977386, -0.018077906, 0.0017052453, 0.012292145) * g_7;
    result += mat4(0.01893072, 0.032129273, 0.010857875, 0.037224095, -0.01413747, -0.047471486, 0.05192984, 0.03202811, -0.05082615, -0.027038824, -0.008331923, 0.03062506, -0.01725524, 0.039917417, -0.010607958, 0.04724454) * g_8;
    result += mat4(0.03497211, 0.07911703, 0.016746478, 0.057458322, 0.06088827, -0.0053583174, -0.013933355, -0.10673472, -0.005456845, 0.020259444, -0.03139623, -0.008973998, -0.054345034, -0.035464175, -0.025964592, -0.0021018258) * g_9;
    result += mat4(-0.047960743, 0.021779433, -0.11492737, -0.033511925, -0.067273304, -0.07730279, -0.04037016, -0.045080706, 0.09207083, 0.009399112, 0.03178142, -0.011313022, 0.021366931, 0.0051248465, -0.008097426, -0.018301165) * g_10;
    result += mat4(0.014282785, -0.01572224, -0.027472818, -0.050844453, 0.0054380163, 0.052591007, -0.04270195, -0.02309884, 0.05152891, 0.03629938, -0.004667278, -0.024925238, 0.010567401, -0.07481508, 0.037315298, -0.04241005) * g_11;
    result += mat4(-0.0013873621, 0.028364213, -0.031026626, 0.015620681, 0.004142558, -0.004863661, -0.013809934, -0.021330781, -0.0016021075, -0.002762517, -0.024034528, -0.03442779, -0.0013054899, -0.0042632925, 0.020974873, -0.0022553254) * g_12;
    result += mat4(0.018562179, 0.034197688, 0.015277717, -0.01111744, -0.0032272537, -0.013426753, 0.017978273, -0.0015077988, -0.0051653306, 0.012690824, 0.001157489, 0.021362923, -0.01262595, 0.0054670637, -0.03031384, 0.012800636) * g_13;
    result += mat4(0.012069964, -0.016048005, 0.01373877, -0.013298124, 0.03194061, -0.013332437, 0.016943898, -0.0058277305, -0.009428097, -0.023061408, -0.013659186, 0.015731167, -0.001986914, -0.019521309, 0.014714155, -0.00522106) * g_14;
    result += mat4(0.0007342483, -0.026249036, 0.030117435, -0.015873922, -0.008929299, -0.0023522351, 0.0164302, 0.023790896, -0.03889036, -0.024644645, 0.006634364, 0.046513416, -0.013473101, -0.0140229, 0.0019859916, 0.011869367) * g_15;
    result += mat4(0.02573362, 0.02375676, 0.00059617084, -0.016921667, -0.0671785, 0.008825013, -0.0013130646, 0.07261784, 0.010327604, 0.019814448, -0.008936156, 0.013669365, 0.020260049, -0.013921513, 0.018746642, -0.02843792) * g_16;
    result += mat4(-0.023912461, -0.02845122, 0.017157353, -0.0075884, 0.00036027908, 0.012657872, 0.0061078435, 0.014107368, 0.032003447, 0.020891502, -0.0067286897, -0.030822601, -0.06574523, -0.028198881, 0.032242246, 0.061325297) * g_17;
    result += mat4(0.0074854135, 0.085437536, -0.06426021, -0.011461227, -0.023055596, -0.025802588, 0.005154878, 0.0056105317, 0.0058093905, -0.1922738, 0.14643134, -0.035682995, -0.026076004, -0.053763065, 0.04269994, 0.05141156) * g_18;
    result += mat4(-0.011764035, -0.011518187, -0.010223651, 0.015880484, 0.023317069, -0.05618372, 0.0059863995, -0.059199195, 0.04408538, 0.084830545, -0.042056326, -0.057687927, 0.0037303802, -0.082143255, -0.0018375175, -0.071053974) * g_19;
    result += mat4(0.0044008377, 0.03906328, 0.010832349, 0.046560295, -0.011535675, -0.004254791, -0.011572009, -0.008665021, 0.021482797, 0.0338495, 0.019407712, 0.010986841, -0.05098764, 0.009778762, -0.05300968, 0.021800417) * g_20;
    result += mat4(-0.021229895, 0.003305197, 0.0024396733, 0.02508984, 0.012702334, 0.033208802, -0.03008867, 0.0046940153, -0.030033346, -0.03792949, -0.05176272, -0.022788247, -0.012390274, -0.0135713285, -0.021557398, -0.06371822) * g_21;
    result += mat4(-0.08850463, 0.0793453, 0.020550407, -0.05461798, -0.009402199, -0.027972376, -0.005156784, 0.02965216, 0.017268548, 0.04429356, 0.009809255, 0.031682562, 0.031172305, 0.03379402, 0.04395453, 0.062268186) * g_22;
    result += mat4(0.01247631, -0.100407876, 0.042796645, -0.06502109, 0.032900713, 0.13428093, -0.033733122, 0.016222714, -0.0178732, -0.002501202, 0.0035485916, -0.015802957, -0.012150594, -0.0022097295, -0.023347225, -0.038795106) * g_23;
    result += mat4(0.05938152, 0.059704512, 0.030237982, -0.04353414, 0.055702258, -0.0029182534, -0.09416582, 0.08440017, 0.008828504, -0.03065552, 0.0646233, 0.03629834, -0.04788823, 0.071730554, -0.084519096, 0.05947715) * g_24;
    result += mat4(-0.109025195, 0.08866299, -0.047770992, 0.08894294, 0.014965939, 0.059702646, 0.032068793, -0.053778123, 0.019529643, 0.008203253, 0.014628202, -0.017464165, 0.0060448833, 0.027196955, -0.018907491, -0.0026503608) * g_25;
    result += mat4(0.081304245, 0.06199502, -0.045204166, -0.08596196, 0.028582547, 0.011568329, 0.024607504, 0.007910688, 0.035362624, -0.08241612, -0.06848065, -0.026512494, -0.04969066, -0.065509185, 0.050000466, 0.05400427) * g_26;
    result += mat4(-0.015837632, -0.087357126, 0.015269297, 0.00058823347, -0.01621553, -0.020170743, 0.049107697, -0.043301217, -0.025253763, 0.021026319, -0.047297694, -0.06751796, -0.020940255, -0.019703854, 0.020391362, -0.0049682967) * g_27;
    result += mat4(0.042480465, -0.010125742, -0.016281988, -0.023186147, -0.040653005, 0.022371864, -0.028837234, 0.009938319, 0.0576169, -0.09105783, 0.06033278, -0.057518024, -0.08265035, -0.094854854, 0.10116602, 0.06394465) * g_28;
    result += mat4(-0.0027242866, 0.007224464, -0.026375424, 0.0052841473, -0.09330453, 0.010634226, 0.024063759, -0.005130613, 0.0070950384, 0.048039638, 0.029983977, 0.042704105, -0.018214077, -0.020184115, -0.0073092347, 0.01891303) * g_29;
    result += vec4(0.026287671, 0.015689341, 0.021467328, 0.0052872337);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_last_tf1, gxy, result);
}