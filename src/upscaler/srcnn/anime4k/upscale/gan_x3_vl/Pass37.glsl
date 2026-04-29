// Anime4K_Upscale_GAN_x3_VL - Pass 37 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_20_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_21_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.26941684, 0.036219094, -0.07560285, -0.26895636, 0.044311106, -0.05137545, -0.2322296, -0.03678458, -0.1297458, -0.05439981, 0.20655335, 0.21557501, -0.15205787, 0.17939065, -0.23068883, 0.2923722) * g_0;
    result += mat4(-0.18076229, 0.026389921, 0.24002524, 0.13083115, 0.101710886, 0.15513568, 0.11232542, -0.10519931, -0.020665402, 0.17358172, 0.008605432, -0.20540753, -0.16048996, -0.117280565, 0.29549748, 0.09058516) * g_1;
    result += mat4(0.25597388, 0.082029305, -0.10319984, -0.22495286, -0.27525312, -0.2427153, -0.04050147, 0.19406061, -0.15651433, 0.1356335, -0.043527655, -0.16124776, -0.036669318, -0.0032990375, -0.085704334, 0.22756006) * g_2;
    result += mat4(0.051867485, -0.24008298, -0.17850713, 0.025297651, -0.3650358, -0.2176735, 0.2021243, 0.15193781, 0.19604576, 0.1891993, 0.037731584, -0.052179646, 0.11834566, -0.1379031, -0.2373384, 0.014617894) * g_3;
    result += mat4(0.09285297, -0.11562465, -0.12399718, 0.13007185, -0.17964637, 0.014563686, -0.074939504, -0.026646245, -0.07532688, -0.22010872, 0.003612656, 0.10351008, 0.04961115, 0.20100375, -0.22187702, -0.17823507) * g_4;
    result += mat4(-0.12011126, 0.09486046, 0.0086389035, -0.10428294, 0.06444772, 0.0023705198, 0.019175975, -0.01996667, -0.12081064, -0.22708468, -0.038654026, 0.27200446, 0.3914547, 0.2632333, 0.40427366, 0.10581144) * g_5;
    result += mat4(-0.04486948, 0.015250527, -0.011455859, -0.01188025, 0.20036544, -0.11762138, -0.31135175, 0.124225006, -0.036055125, -0.42933324, -0.08072662, 0.003972841, 0.042441923, -0.12717016, 0.08839082, 0.053717572) * g_6;
    result += mat4(0.13684005, -0.05297912, -0.026370518, -0.09088581, -0.094107635, 0.20296267, -0.18902333, -0.26307258, -0.068126924, 0.10832254, -0.066805795, 0.03337222, -0.053696163, 0.18476287, -0.089606225, 0.013725743) * g_7;
    result += mat4(-0.043879077, -0.040578876, 0.06594204, -0.020670997, 0.13122465, 0.075165644, -0.010130328, 0.24178858, 0.06730869, 0.113522425, 0.19904599, 0.0073498543, 0.42964056, 0.17178564, 0.084659666, -0.24664184) * g_8;
    result += mat4(-0.12285546, -0.1358985, -0.11090004, -0.11844171, 0.09297483, -0.22406663, 0.047864, 0.03641851, 0.0365943, 0.100511536, -0.22012307, -0.016841182, 0.08523964, 0.15804283, -0.05356537, 0.21060708) * g_9;
    result += mat4(0.19209427, -0.13248959, -0.07607655, 0.051149122, 0.11642458, 0.099497885, -0.26437026, -0.324092, 0.043865014, -0.05075767, -0.19902268, 0.22255316, -0.017222278, -0.16437344, 0.13457586, -0.0018609265) * g_10;
    result += mat4(-0.000601963, 0.020355195, 0.18065485, 0.12808195, -0.117500536, -0.08638299, 0.08601238, 0.14027888, 0.075331904, -0.11529773, -0.1415374, -0.17192268, 0.26774237, 0.32726994, 0.019540906, -0.048459146) * g_11;
    result += mat4(0.13638663, -0.24208723, 0.097826414, -0.15800993, -0.042421468, -0.09006148, -0.037229672, 0.14824185, -0.17421173, 0.25361627, 0.019297253, 0.006751278, 0.3832628, -0.2272271, 0.110637285, -0.055976037) * g_12;
    result += mat4(-0.004539398, 0.095810585, 0.16587941, 0.07004706, -0.2715203, 0.19236542, 0.34606242, 0.10482813, 0.045676876, -0.00715472, 0.051209465, 0.14672725, -0.12688708, -0.004962278, -0.09647747, 0.032963306) * g_13;
    result += mat4(-0.10475787, -0.07177458, 0.08670406, -0.07522681, 0.034563806, 0.09974455, -0.0766157, -0.15083836, -0.18490194, -0.24109948, 0.08864707, -0.06437733, -0.028089454, -0.039389037, -0.10697504, -0.15656655) * g_14;
    result += mat4(-0.13425583, 0.081750415, -0.10361864, 0.08273783, -0.111270554, 0.11590486, -0.15661974, 0.05408825, -0.0718009, 0.30851424, 0.02040609, 0.1636755, 0.07446875, -0.17443664, 0.15280458, 0.1481998) * g_15;
    result += mat4(-0.284261, 0.05864242, -0.06124804, 0.22360328, 0.21680816, -0.008231985, -0.17734775, -0.001956721, -0.13693857, -0.012719592, 0.045048296, 0.08310407, 0.04783058, -0.17998756, 0.1645331, -0.09859071) * g_16;
    result += mat4(0.048696257, -0.13751513, -0.0047537195, -0.14069663, -0.03338046, 0.070993476, 0.10792572, -0.129749, -0.0044776825, -0.2988422, 0.22649752, -0.06848238, -0.029648019, -0.063617565, -0.024357993, -0.113194376) * g_17;
    result += mat4(-0.11811312, 0.011456743, -0.2775974, 4.4019973e-05, 0.09702063, -0.19398709, -0.13290964, -0.030809943, -0.0614852, -0.30568314, 0.22979493, 0.019983308, 0.14955766, -0.13779299, 0.20106222, 0.25381064) * g_18;
    result += mat4(-0.04759845, 0.2240889, 0.25071913, 0.023906428, -0.084556535, -0.026651192, -0.078656286, 0.10334545, 0.1696217, 0.17458726, -0.053354427, -0.048202634, -0.104181975, -0.16721416, -0.12434673, -0.015573024) * g_19;
    result += mat4(0.052810643, -0.110003166, 0.13987248, -0.26855007, -0.077974305, -0.051788885, 0.15868334, -0.25068295, -0.22068459, -0.04198552, -0.024428006, -0.00417208, -0.12136332, 0.1832669, -0.061507918, -0.12375168) * g_20;
    result += mat4(-0.024210382, 0.08638061, -0.05814393, 0.061041117, 0.2061646, -0.037258796, -0.0017197772, 0.14881982, 0.18087907, 0.03670567, 0.1891443, -0.16923326, -0.17485145, -0.07395503, -0.058735035, 0.21229668) * g_21;
    result += vec4(0.034866143, 0.034214873, -0.0020411036, 0.006542157);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf1, gxy, result);
}