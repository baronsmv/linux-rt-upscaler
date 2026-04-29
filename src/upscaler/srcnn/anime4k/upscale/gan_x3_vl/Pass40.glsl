// Anime4K_Upscale_GAN_x3_VL - Pass 40 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_20_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups;
#define g_0 (max((texture(sampler2D(tex_conv2d_21_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_21_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_21_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_21_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_21_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_21_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.084550284, 0.28695974, -0.18845658, 0.036873333, -0.03702915, 0.20106933, -0.013779231, -0.09064196, 0.2650543, -0.23769681, -0.025090849, 0.112004876, 0.02858812, -0.33468688, 0.015218963, -0.009193985) * g_0;
    result += mat4(0.019986125, 0.03711447, -0.072495684, -0.18489611, 0.10276208, 0.22991183, 0.024009978, -0.11783073, -0.19585772, 0.13150191, 0.08316458, -0.074719064, 0.10288155, -0.39512005, -0.14987002, 0.0050115753) * g_1;
    result += mat4(0.022747586, 0.00711762, -0.19764912, 0.02849651, 0.034982137, -0.15019011, -0.23275712, 0.015071641, -0.12003277, 0.07394686, 0.0016380423, -0.07764185, -0.027983893, -0.11473845, -0.076731786, 0.17937833) * g_2;
    result += mat4(-0.13547164, 0.014350364, -0.0680784, 0.015241785, -0.019645115, 0.1367833, 0.018514454, 0.061408024, 0.05381124, 0.008636759, -0.05929157, -0.045654505, 0.29703617, -0.14939637, 0.017480306, 0.03320388) * g_3;
    result += mat4(0.16749536, -0.5068873, -0.054959137, 0.5028366, -0.22012903, -0.18610893, 0.03606436, 0.16536428, -0.18980072, -0.035605285, 0.22413859, -0.05201868, 0.032878175, 0.14102045, 0.09135491, 0.028493756) * g_4;
    result += mat4(-0.08715977, -0.0069041327, 0.13424577, -0.15170926, -0.12459944, 0.139362, 0.23367397, 0.06992671, 0.10383856, 0.12649116, -0.10238732, 0.022956299, 0.10903374, -0.1060183, 0.0012752792, 0.09608246) * g_5;
    result += mat4(0.07170078, 0.097870566, 0.18391322, 0.16910231, -0.1267208, 0.261178, 0.049107287, 0.032856256, 0.04621799, 0.14521311, 0.30777922, 0.07517666, 0.13072045, -0.07817935, -0.0057332893, 0.042636685) * g_6;
    result += mat4(-0.14621416, -0.24651968, 0.12061317, -0.05200859, 0.014879963, -0.1331666, -0.21076989, 0.047090866, 0.108966425, -0.1072571, -0.04034989, 0.17689784, -0.30637997, 0.1334576, -0.09599567, -0.16958676) * g_7;
    result += mat4(-0.15277179, 0.3040327, 0.33014333, 0.09105886, 0.0946242, 0.06878733, -0.022571186, 0.012422955, -0.014575288, -0.014345794, 0.13639238, -0.2948898, -0.09921163, -0.090119295, 0.43447036, -0.1519424) * g_8;
    result += mat4(0.055695374, -0.018237038, -0.03149495, -0.26079783, -0.13239612, 0.08098567, 0.010524064, 0.2580244, 0.019125992, -0.11228541, 0.2497276, -0.1600721, 0.04776844, 0.074449435, -0.2169092, 0.22888823) * g_9;
    result += mat4(0.1993489, 0.16312787, 0.17672649, 0.06839388, -0.12656055, 0.2534753, -0.22719325, -0.15975192, 0.18121919, -0.02482891, -0.1758899, -0.06285482, -0.062030714, -0.030519357, 0.08887617, 0.033442013) * g_10;
    result += mat4(0.09227225, -0.22740443, -0.011862239, 0.10482141, 0.015177834, 0.15367627, 0.15005216, 0.282921, -0.09772425, 0.10730146, -0.06640197, 0.07101983, 0.14829135, 0.083728194, -0.0743765, -0.09980271) * g_11;
    result += mat4(0.085638225, -0.1827499, 0.06827563, 0.019491995, -0.0011983203, 0.022348093, 0.10796647, -0.07942398, 0.13093562, -0.08755021, -0.01282162, -0.12193386, -0.07074474, 0.025357427, 0.09938728, -0.14343725) * g_12;
    result += mat4(0.015263603, 0.07848516, 0.06398182, -0.1281127, 0.011302997, -0.1424875, 0.03465649, 0.05781734, -0.019214824, 0.07257173, -0.19007434, -0.013839539, -0.088996276, -0.06987128, -0.14060202, 0.07935333) * g_13;
    result += mat4(0.089654885, 0.18821386, -0.10908745, -0.1945955, 0.28777096, -0.27091888, -0.117128626, 0.13311313, -0.15800829, -0.031426586, -0.09576625, -0.045514874, -0.05638241, 0.22475603, 0.19451538, 0.06693039) * g_14;
    result += mat4(0.108449794, 0.03863312, 0.09138021, 0.024396805, -0.20986842, 0.09761748, 0.08867459, -0.15282214, -0.08067849, -0.016950522, 0.26711652, 0.085504845, 0.060858846, 0.01342649, 0.075316414, -0.024188342) * g_15;
    result += mat4(0.0010497145, -0.1259321, 0.057801772, -0.035549402, -0.11513258, -0.018429652, -0.10117708, 0.11573959, 0.1427766, -0.032213476, -0.01586306, 0.017653462, -0.041694127, 0.1393299, 0.14011054, -0.038647145) * g_16;
    result += mat4(-0.22414106, -0.13671458, -0.07397391, -0.09691265, -0.110350996, 0.061211936, 0.19481628, -0.06409933, 0.136633, -0.04669014, 0.058727175, 0.043561198, 0.07559326, -0.0040795025, 0.087900914, -0.020880874) * g_17;
    result += mat4(0.02741521, -0.07276462, 0.15752992, 0.061364397, 0.07611034, 0.32745734, -0.16256663, -0.15516974, 0.04587384, -0.10178523, 0.09862578, 0.086561374, 0.2331702, -0.16688296, -0.07780254, 0.079894625) * g_18;
    result += mat4(-0.012604072, 0.14701019, -0.1202553, 0.0007438331, 0.09805167, -0.12829433, 0.10536026, 0.044031054, -0.01909643, 0.08925314, -0.029631758, -0.0843997, -0.098011285, 0.2326875, -0.0059059164, 0.054862864) * g_19;
    result += mat4(-0.26984945, 0.21170485, 0.016418483, 0.05436341, -0.13604105, -0.015747178, 0.21282208, -0.084069654, -0.1519696, 0.07782159, -0.0767402, 0.049681228, -0.17597915, -0.033314597, 0.19277339, -0.15969992) * g_20;
    result += mat4(0.011572451, -0.040921126, 0.06736629, -0.05296152, 0.0750723, 0.15619396, -0.33569458, -0.045480207, 0.052975655, -0.019853046, -0.1586733, -0.0971954, 0.12981664, -0.23612434, -0.065897234, 0.09027556) * g_21;
    result += mat4(0.2591393, -0.21753159, 0.012262199, 0.17810525, 0.0437195, 0.13112774, -0.27936146, 0.16000053, 0.16150814, 0.0060378034, 0.011343986, 0.0711386, 0.10716892, -0.018265475, 0.117098734, -0.042729706) * g_22;
    result += mat4(-0.12928756, 0.13401757, -0.28467083, -0.09971548, -0.02296809, -0.124093436, 0.17238498, -0.07679452, 0.020145075, -0.1027165, -0.100577906, -0.022585977, -0.14362176, -0.3100744, -0.030349141, 0.08573548) * g_23;
    result += vec4(0.04458631, 0.05340509, 0.02098219, -0.060097195);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups, gxy, result);
}