// Anime4K_Upscale_GAN_x4_UL - Pass 25 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_9_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_9_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_9_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_9_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.07763047, 0.27418226, -0.14338551, -0.11081361, 0.18755837, 0.13486148, -0.103934124, 0.15729067, -0.30118144, -0.23599705, -0.03624479, -0.13197371, 0.2509935, -0.053046692, 0.22451721, 0.062433634) * g_0;
    result += mat4(-0.009606105, -0.11484272, 0.014596453, 0.05732435, -0.28318888, 0.14493735, -0.12094529, -0.021383354, -0.19675042, -0.20649005, -0.117224075, -0.044716556, 0.07876854, 0.0063603655, 0.14384452, 0.34768546) * g_1;
    result += mat4(-0.20010832, 0.26670012, -0.07552091, 0.16396587, -0.0011262367, -0.10468841, 0.17872465, -0.041907642, -0.04863038, -0.13880715, -0.12238532, -0.00602456, -0.11301867, 0.13501893, -0.15452485, 0.0051267557) * g_2;
    result += mat4(0.015291708, -0.2517837, -0.24560767, 0.10868371, -0.1582953, -0.30957448, 0.29895902, -0.25554538, 0.24216072, -0.045922607, -0.08923091, -0.25642177, -0.33101156, -0.0058916584, 0.1821658, -0.05911768) * g_3;
    result += mat4(0.15687323, 0.055351928, -0.32324156, 0.1137441, 0.41560605, 0.41545513, 0.12071179, 0.10673924, -0.11547584, -0.37552577, 0.077131264, -0.12138124, -0.13219355, -0.22411941, 0.03978703, 0.3492272) * g_4;
    result += mat4(0.07044036, 0.11714306, -0.13374294, -0.055823848, -0.06303139, -0.1482969, -0.110342264, 0.036638733, 0.314413, 0.1842789, 0.17475197, 0.043438207, 0.0015348946, -0.3156743, -0.056865085, -0.053799774) * g_5;
    result += mat4(0.21131508, 0.4045569, 0.083308145, 0.14813706, -0.02388631, -0.061720062, 0.24854286, 0.30907345, 0.027408333, -0.007549164, 0.19938764, -0.17439002, 0.025626602, 0.08443904, -0.2024683, -0.06329822) * g_6;
    result += mat4(-0.015397141, 0.18421206, 0.08390624, -0.119724214, 0.17461216, 0.25613582, 0.056294072, -0.30151296, -0.1661106, 0.004817213, 0.20178172, -0.1557543, 0.31574607, 0.016265873, -0.11313175, 0.101584174) * g_7;
    result += mat4(-0.036003333, -0.2948743, 0.08890492, -0.2424807, 0.20558605, -0.005326227, -0.14824234, 0.13657871, -0.08299064, -0.2654781, 0.07763288, -0.20758678, 0.12413959, -0.09051654, -0.27145076, 0.1981802) * g_8;
    result += mat4(0.06444485, 0.041239545, 0.4109527, 0.25702617, -0.17460653, 0.2697094, 0.18714386, -0.10359985, 0.034952056, 0.058017034, 0.36967984, 0.1442043, -0.102753505, -0.07272067, 0.09906319, -0.02692305) * g_9;
    result += mat4(-0.3257422, -0.25091344, 0.05630559, -0.22858965, 0.0969714, 0.0627054, -0.09547412, -0.21921997, 0.11027036, -0.2087131, -0.0034146109, -0.042596426, 0.1338729, -0.029776977, -0.136488, 0.048176914) * g_10;
    result += mat4(0.42944148, 0.07361601, 0.039996527, -0.06972752, 0.12532753, -0.05265781, -0.061011825, 0.12728149, -0.007630841, 0.010768823, -0.08062439, 0.15050723, 0.059922203, 0.034361467, 0.2352152, -0.059999254) * g_11;
    result += mat4(0.1987271, -0.068179525, -0.33349162, 0.018712096, -0.069019474, 0.16223519, -0.012386762, -0.058549248, 0.23421755, -0.11690985, -0.18661754, -0.12185474, -0.022877546, -0.11763273, 0.0713361, -0.036679223) * g_12;
    result += mat4(-0.0042756563, -0.20779006, -0.14918481, 0.096974574, -0.015246231, -0.11454528, 0.14464086, 0.19934529, -0.0877081, 0.38296238, -0.010145265, -0.4274725, -0.20933542, 0.03727663, -0.004354278, -0.024973618) * g_13;
    result += mat4(-0.15737206, -0.20578605, 0.2868647, -0.13985285, 0.13827614, -0.048706137, 0.10751875, -0.09783745, 0.04060606, 0.21132666, 0.0064998385, -0.03548873, 0.11786483, -0.15699282, 0.2044634, 0.007233451) * g_14;
    result += mat4(-6.82634e-05, 0.23951311, -0.06425014, 0.07997111, 0.11085256, 0.15976904, 0.13375166, 0.21199653, -0.35401696, 0.065035254, -0.030974375, -0.08552442, 0.37972608, 0.10081147, 0.2001372, 0.17563076) * g_15;
    result += mat4(0.2773931, 0.1178841, 0.027378619, 0.2863328, -0.30616024, 0.06384452, -0.16728342, 0.06004475, 0.011872468, 0.05471154, -0.32518378, -0.18874332, -0.12623757, 0.23276375, 0.068185456, 0.21938467) * g_16;
    result += mat4(-0.18750657, -0.22679184, -0.024820909, -0.095249355, -0.14394966, -0.27550733, -0.19173676, 0.20593777, 0.07831533, 0.2730425, 0.34470567, 0.07874521, 0.09838028, -0.13954316, 0.18111953, 0.18931043) * g_17;
    result += vec4(-0.03305349, -0.054945398, 0.02216584, -0.091164745);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf, gxy, result);
}