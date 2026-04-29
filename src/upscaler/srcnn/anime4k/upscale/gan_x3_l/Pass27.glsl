// Anime4K_Upscale_GAN_x3_L - Pass 27 of 30 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_12_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_12_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_12_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups2;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.029018598, -0.09923186, -0.1346201, -0.084818475, 0.013764684, 0.054601744, -0.023713779, -0.16826102, 0.038605224, -0.17664196, -0.16562279, 0.14602208, -0.046339583, 0.08062112, 0.20166601, -0.15399997) * g_0;
    result += mat4(-0.022488657, 0.28881705, 0.22283012, -0.1935156, 0.22948948, -0.26604095, 0.12130448, 0.35176682, -0.044228308, -0.14734231, 0.07643742, -0.008511517, 0.04313213, -0.03179344, 0.048205808, -0.046295088) * g_1;
    result += mat4(-0.2531207, 0.10446124, 0.12730333, -0.13316457, 0.2988587, 0.025091104, -0.00482534, 0.037484948, -0.04006528, 0.14588606, -0.2078635, -0.18636562, 0.112230495, 0.15386717, -0.11122423, 0.1115416) * g_2;
    result += mat4(0.058421213, 0.086035125, -0.042249937, -0.22377387, -0.055913106, 0.020280339, 0.10572877, 0.124147646, -0.16199678, 0.25662583, 0.051422223, -0.11681551, 0.3789257, -0.21530285, -0.18586366, -0.2222266) * g_3;
    result += mat4(-0.11123776, 0.056422785, -0.20566264, -0.07211227, -0.011873865, 0.30742383, 0.1306618, 0.06808572, 0.068643585, -0.045474447, -0.11596973, 0.0069175013, 0.0331586, -0.013221628, -0.089815594, -0.17750767) * g_4;
    result += mat4(0.45630908, 0.11607409, -0.05464286, 0.013246808, -0.28643015, 0.025237702, -0.1445959, 0.05237954, -0.07100623, -0.34417382, 0.13903524, 0.21305767, -0.17371523, -0.13203263, -0.09479281, 0.018392125) * g_5;
    result += mat4(-0.018931253, -0.14936836, -0.06770882, 0.10720343, -0.10476732, 0.1157603, -0.2245781, 0.23242487, -0.21631289, 0.12723672, 0.4190526, 0.38829032, -0.192142, 0.034754496, -0.1103798, -0.17207326) * g_6;
    result += mat4(0.10311498, 0.08424212, -0.048713315, -0.2784966, 0.034522116, -0.13184515, -0.22852737, 0.003882436, 0.36972147, -0.21263883, -0.3308556, 0.10331102, 0.2462766, -0.12618823, -0.040451203, 0.03362719) * g_7;
    result += mat4(-0.0150432745, 0.11757923, 0.23359092, -0.19003578, -0.22206408, 0.15738077, -0.14019541, -0.14201044, 0.19273758, -0.003298494, -0.16530107, 0.17979017, 0.24293105, -0.049160067, -0.14296743, -0.12812854) * g_8;
    result += mat4(-0.0020534277, 0.016410163, -0.012038507, -0.0028629426, 0.016464395, 0.0755886, 0.20384903, -0.029324949, -0.13087441, 0.2138074, 0.03701677, -0.1671415, -0.10499825, -0.042930905, -0.007613907, -0.05984843) * g_9;
    result += mat4(-0.07029106, 0.05386552, 0.101365924, -0.008048512, -0.090149835, 0.024272785, -0.16436198, 0.2721913, 0.17460534, 0.0034964401, -0.023265982, -0.0120567605, -0.10151709, 0.059922412, -0.13204409, -0.36116782) * g_10;
    result += mat4(-0.12569033, 0.08523279, -0.047763485, -0.0025170774, -0.108375974, -0.032045245, 0.232404, -0.24801816, -0.09875204, -0.14990453, -0.10958757, -0.23116525, 0.015989894, -0.09210713, 0.19653663, 0.14138049) * g_11;
    result += mat4(0.17831743, 0.04722249, 0.22804007, -0.29099363, 0.29851902, 0.2542661, 0.0067702304, 0.17606215, 0.25847578, -0.3118978, 0.122089565, -0.07010249, 0.014281751, 0.16585219, -0.1659864, -0.30643156) * g_12;
    result += mat4(0.19042191, -0.028259574, -0.009187334, 0.21004388, -0.08070036, -0.07838277, -0.023598602, 0.13891627, -0.10481482, 0.05874796, -0.256131, 0.19640857, 0.19515458, -0.07920633, 0.020810237, 0.11040215) * g_13;
    result += mat4(-0.093089096, -0.09344762, 0.24232084, 0.21563776, -0.23910145, 0.09092736, 0.12202717, 0.27240792, -0.008079913, 0.07417433, -0.11870247, -0.35385913, 0.107840456, 0.033915944, 0.16016287, 0.023731219) * g_14;
    result += mat4(0.21967673, 0.09896617, 0.04236673, -0.20100762, 0.02077549, -0.075936705, 0.008608214, -0.09693712, 0.44249, -0.31763947, -0.027664369, 0.6166134, -0.43993565, -0.025720617, -0.3275949, 0.041507874) * g_15;
    result += mat4(0.20305479, -0.06975863, -0.18130508, -0.11641104, 0.119906515, -0.27588886, -0.15420493, -0.1399163, 0.075970694, -0.16776691, 0.05045285, 0.44775927, -0.036058784, -0.28161573, 0.1877619, 0.10209392) * g_16;
    result += mat4(-0.4250348, -0.007887921, 0.307136, -0.18842702, 0.30411714, 0.05816079, 0.26664746, -0.007951849, -0.18454021, 0.30914694, -0.34967366, -0.18838291, 0.06042888, 0.1902336, -0.062413342, 0.015706044) * g_17;
    result += vec4(-0.0011628491, -0.0046341973, 0.0007886035, -0.04435556);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups2, gxy, result);
}