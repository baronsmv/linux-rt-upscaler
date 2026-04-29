// Anime4K_Upscale_GAN_x4_UUL - Pass 53 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_18_tf4;
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
vec4 result = mat4(-0.14945197, 0.16098031, 0.051719245, -0.034232154, -0.10090936, 0.00830591, 0.003511522, 0.047575846, 0.06164254, -0.036461372, 0.06093159, 0.12666239, 0.015167088, 0.22650927, 0.27785966, -0.13839455) * g_0;
    result += mat4(0.20404427, -0.13778454, -0.003130969, -0.0069568753, 0.009411408, 0.00029913452, -0.15609823, -0.036967028, 0.8401452, 0.104523584, 0.16267233, 0.26101708, 0.15797855, -0.005672259, -0.072657965, -0.2940039) * g_1;
    result += mat4(0.023400925, -0.07931777, -0.0024201928, 0.14154646, 0.13505082, 0.061725322, -0.23146541, 0.2235899, 0.028721808, -0.020690065, 0.027728429, 0.3306459, 0.03473293, -0.06322703, -0.017740624, 0.02693956) * g_2;
    result += mat4(0.201981, -0.26569206, 0.3296027, -0.062879294, 0.012529938, -0.006474693, 0.09799416, -0.045322224, 0.10355446, 0.13586703, 0.23875476, 0.08521818, 0.13901752, -0.3213584, 0.0010939257, -0.012409596) * g_3;
    result += mat4(-0.23700963, -0.0033388012, 0.08170323, 0.14243743, -0.18329623, 0.2986226, -0.19831513, 0.14657772, 0.33912238, 0.25595152, -0.24895075, 0.14932986, 0.045179855, -0.009538074, -0.100237936, -0.098446615) * g_4;
    result += mat4(-0.18900044, 0.054638628, 0.06837739, 0.08266906, -0.046341334, -0.19986658, 0.050261546, 0.036085926, -0.07516528, 0.028093588, -0.3476435, -0.10726676, 0.33830363, -0.058144495, 0.102090456, 0.2108081) * g_5;
    result += mat4(-0.09022328, 0.017889388, -0.15765008, -0.10291243, -0.060554795, -0.038358618, 0.16947241, -0.104247436, 0.42979565, 0.14488359, -0.07012738, 0.07480945, -0.02311837, -0.030403437, -0.21153943, 0.009769658) * g_6;
    result += mat4(-0.19631365, -0.021078536, 0.093053594, 0.042771056, 0.07872415, 0.25367248, 0.2904824, 0.081488095, -0.21612023, 0.20601381, 0.09763489, 0.122754775, 0.0024988255, -0.17623907, 0.22360411, 0.18334015) * g_7;
    result += mat4(-0.058749627, 0.071623124, 0.03675938, -0.2588635, 0.016778812, -0.21104309, 0.018952027, -0.31036612, -0.15561692, -0.021656368, -0.22004744, -0.20016085, 0.25435224, 0.02916577, 0.06516691, 0.07729871) * g_8;
    result += mat4(-0.082993135, 0.037327975, -0.09041188, -0.021681158, -0.13288629, -0.016856177, -0.19841108, -0.048110623, 0.017901966, -0.13928522, 0.020148523, -0.2575589, 0.05966198, -0.25391978, 0.1887992, -0.22440273) * g_9;
    result += mat4(0.038387958, 0.25604457, 0.20616667, -0.010662733, 0.0652453, -0.09418516, 0.03907119, -0.07573656, -0.026385533, 0.023236332, -0.0694166, -0.039987978, 0.03619357, 0.024953678, 0.0047133924, 0.10959686) * g_10;
    result += mat4(-0.28358817, -0.08429444, 0.12283427, -0.17352122, -0.28881827, 0.028303733, 0.037494656, -0.18157536, 0.102885716, -0.1597965, -0.15546831, -0.01146783, -0.11535764, 0.07318211, -0.0064606857, -0.17013118) * g_11;
    result += mat4(-0.2722369, -0.16988702, -0.12011997, -0.21110061, -0.02703128, -0.0012027018, 0.15786748, -0.045325976, -0.14155495, 0.024521999, -0.09180482, 0.07973881, 0.15009059, 0.11311702, -0.24193251, 0.21181291) * g_12;
    result += mat4(0.079832554, 0.13819915, 0.0644478, 0.032698773, -0.055964362, 0.0062652268, -0.44648278, 0.020893153, 0.2785451, -0.058252975, 0.06947447, 0.17165478, 0.11666183, 0.032484345, 0.26955023, -0.09007163) * g_13;
    result += mat4(0.074948624, -0.03027186, 0.08031308, 0.0076982, -0.030060723, -0.123520896, -0.01858971, 0.16149811, -0.18218324, -0.1907134, 0.14869457, 0.04311582, -0.14524359, 0.18327981, -0.038959123, 0.052322008) * g_14;
    result += mat4(-0.059443116, -1.2828946e-05, 0.2770255, -0.054349877, -0.09371057, -0.19399741, 0.024748074, -0.21350558, 0.15579434, -0.18651448, 0.03005815, -0.12944081, -0.11453777, -0.2343128, -0.1720614, 0.0016626595) * g_15;
    result += mat4(-0.23639911, -0.083615154, -0.20849767, -0.28589326, 0.3486518, -0.089977995, 0.013625235, -0.13351293, -0.17646289, -0.28506002, 0.13482474, 0.0347251, -0.23015228, 0.06251885, 0.0933548, -0.16809867) * g_16;
    result += mat4(0.1822202, -0.089247055, -0.0019837108, 0.0024590432, 0.3305589, 0.019448044, -0.053130258, -0.12762257, -0.063679375, 0.22454257, 0.04940314, -0.015956238, 0.25156045, -0.070181206, -0.21123977, 0.12588634) * g_17;
    result += mat4(0.2687441, 0.009185896, 0.2552064, 0.12281216, -0.061733842, -0.41198087, 0.015501087, 0.07808448, 0.058844253, 0.08016994, 0.088322714, -0.092968285, 0.08418163, 0.007952845, 0.043222576, 0.070968375) * g_18;
    result += mat4(-0.013054412, -0.21707737, -0.17667364, -0.21544492, 0.1014457, 0.18704009, -0.023388298, -0.057701223, 0.105478585, -0.07900766, 0.074261405, 0.1888776, 0.12542284, -0.1996206, -0.16316931, 0.007791157) * g_19;
    result += mat4(-0.18270205, 0.2025353, 0.3265147, 0.06714097, -0.016193308, -0.20436206, -0.030753197, -0.058978382, -0.14078636, -0.06465846, 0.20873049, -0.109932266, 0.30118617, 0.22391927, 0.07046112, 0.0371617) * g_20;
    result += mat4(0.02550017, 0.16456556, -0.11329017, 0.088022776, 0.23173799, -0.0010375397, -0.05828751, 0.14631982, 0.21526784, 0.22880761, -0.09728381, -0.04741336, -0.0019534798, -0.062897205, -0.065131105, 0.0025237799) * g_21;
    result += mat4(-0.108903095, 0.03159055, 0.20757839, 0.15141101, -0.00817231, 0.003621365, -0.02615051, 0.14909424, 0.3730205, 0.11222444, 0.18234271, 0.15614115, 0.17248969, 0.15939258, 0.10224304, 0.1903116) * g_22;
    result += mat4(0.16533965, 0.015357719, 0.14340413, -0.03258536, 0.273793, 0.08128506, -0.037119016, -0.1599679, -0.15314123, 0.006436269, -0.060659572, -0.13333261, -0.01068674, -0.061791964, 0.17797105, -0.1944123) * g_23;
    result += mat4(-0.061225474, 0.06916346, 0.2188833, 0.049035676, -0.28082103, 0.25311306, 0.16941728, 0.13574886, 0.03735417, -0.0150085725, -0.04081533, 0.16391492, 0.053848673, 0.092159234, 0.06918723, -0.06668832) * g_24;
    result += mat4(-0.023205632, -0.29362342, 0.0782468, -0.11934102, 0.25011548, 0.036887586, -0.17301348, 0.0003987401, 0.017727787, -0.3402023, 0.1384328, -0.48377892, -0.20980822, -0.16546479, 0.115749344, 0.2642447) * g_25;
    result += vec4(-0.20050508, -0.07773812, -0.033446066, -0.032423045);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf4, gxy, result);
}