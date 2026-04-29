// Anime4K_Upscale_GAN_x4_UUL - Pass 36 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_9_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_9_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf3;
#define g_0 (max((texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_9_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_9_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_9_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_9_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_9_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_9_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.019602967, -0.05145609, 0.04244019, 0.25405738, -0.33712572, -0.17893799, -0.066478856, 0.15569499, -0.27161816, 0.12593569, -0.05901425, -0.13174452, -0.11021793, 0.03920678, 0.060773216, -0.021032797) * g_0;
    result += mat4(-0.12685195, 0.024931995, -0.22060166, -0.23765254, -0.15206909, 0.052627444, -0.054144315, 0.1210148, 0.1602431, 0.026197273, 0.110542305, -0.073509805, 0.047236316, 0.044307224, 0.014555091, 0.10564006) * g_1;
    result += mat4(-0.09860682, 0.019021804, 0.1671445, 0.042727083, -0.16453904, 0.101818964, 0.03915569, 0.37744778, -0.009018904, -0.009364516, -0.121752, -0.1430464, -0.11879523, 0.15660012, 0.092872, 0.008389549) * g_2;
    result += mat4(0.09203148, -0.19622965, 0.10806049, 0.032417808, -0.06358329, 0.053477164, -0.0033462588, -0.1622076, -0.22893262, -0.15781075, -0.1675613, 0.2557495, -0.108154416, 0.00092219823, -0.18630715, 0.17942573) * g_3;
    result += mat4(-0.07604931, 0.24687444, 0.10485161, -0.0032204043, 0.2355443, 0.07362102, -0.20874, 0.04919508, 0.019878346, -0.035358075, 0.19044363, 0.10661991, 0.12998112, 0.10245926, -0.02966564, -0.21623161) * g_4;
    result += mat4(-0.13730675, 0.011630983, 0.05381945, -0.06594779, -0.20880567, -0.16293554, 0.12331983, -0.07883885, -0.12325015, 0.03357514, -0.21320228, 0.09743771, -0.29196948, 0.07080584, 0.18549103, -0.10713538) * g_5;
    result += mat4(-0.028444685, 0.13853551, 0.19415158, -0.02389972, -0.04180172, 0.014012021, 0.09578899, -0.092844814, 0.27863276, -0.073668964, 0.14896569, 0.178071, -0.24466358, -0.11134794, 0.13081808, 0.14496848) * g_6;
    result += mat4(-0.1556054, -0.13415574, -0.09857606, 0.30523264, 0.08764274, -0.037559148, -0.16858782, -0.11990224, 0.17670709, 0.10452295, 0.09820371, 0.085555285, 0.14616655, -0.064138934, -0.06468503, 0.18437701) * g_7;
    result += mat4(-0.024759063, -0.007020983, -0.25910473, -0.16003223, 0.0006832176, -0.21500164, 0.18051593, -0.21023016, 0.21901055, -0.012773149, 0.11869215, 0.043327942, -0.08801425, -0.09576547, -0.022282854, 0.3436183) * g_8;
    result += mat4(-0.12599704, 0.1573739, -0.18289468, 0.031533517, 0.052889764, -0.2899998, -0.06888571, 0.024767991, 0.1449007, 0.13209689, 0.28273448, -0.013996074, -0.031406544, 0.12544149, -0.047050513, 0.10494411) * g_9;
    result += mat4(-0.11651752, 0.28501326, 0.060793746, -0.1883375, 0.26459783, -0.06930145, 0.28831685, -0.13368587, -0.10180277, -0.068450116, -0.09070248, 0.16990706, -0.035528105, 0.08474028, -0.031924196, 0.0828799) * g_10;
    result += mat4(-0.17398041, -0.13055407, 0.0637754, -0.20454763, 0.081867374, 0.22947273, -0.06115945, 0.14527729, 0.3462909, 0.171278, -0.18330246, 0.045597162, -0.041992005, -0.0065232897, -0.09864108, 0.00873217) * g_11;
    result += mat4(-0.012977971, 0.16809268, -0.16662882, -0.37359142, -0.028308313, 0.11063376, -0.12019489, 0.13814619, 0.063988656, 0.22554557, -0.08410297, -0.0913463, -0.029542763, 0.15869254, -0.0021580574, 0.17143992) * g_12;
    result += mat4(0.08960112, -0.34852883, 0.3086523, 0.36042222, 0.05802867, -0.035582196, -0.01600274, 0.008117766, -0.008915955, 0.10546812, 0.038216136, -0.14320342, 0.18713285, -0.08814888, -0.0147240935, -0.0076010344) * g_13;
    result += mat4(-0.50983155, -0.040480338, -0.015697489, -0.020704566, 0.14625196, -0.07928827, 0.10175586, -0.006522381, 0.20132822, -0.017236393, 0.42775294, 0.29241857, -0.15762952, 0.1366608, 0.041226275, -0.021501385) * g_14;
    result += mat4(0.037395936, 0.15184547, -0.053403616, 0.06780214, -0.08231112, -0.30428946, -0.1273035, 0.21938033, -0.15715978, -0.046725, 0.25453484, 0.07395502, 0.07715246, 0.03596223, -0.093663685, 0.096829675) * g_15;
    result += mat4(-0.09069946, 0.27910122, -0.057103194, 0.1052261, -0.053569946, -0.018461138, -0.039887205, -0.20134343, 0.24427019, 0.07117475, 0.21163048, -0.14486235, 0.0018477996, -0.219897, -0.09160915, -0.028700631) * g_16;
    result += mat4(0.03186668, -0.042110894, -0.06872467, 0.015007692, -0.12133147, -0.20203532, -0.14033763, -0.09270293, -0.13041773, -0.066198066, -0.20825256, -0.17211214, 0.15924487, 0.04158315, 0.1586535, 0.08482204) * g_17;
    result += mat4(-0.25748026, -0.19240272, -0.09985262, 0.010599122, -0.28925768, 0.09412584, 0.29553664, -0.035109073, -0.09598807, -0.16096024, -0.0535374, -0.35389316, 0.235558, -0.015157362, 0.07283362, 0.095931105) * g_18;
    result += mat4(0.13491848, 0.017084226, 0.18945768, 0.117540136, 0.2557805, -0.029065477, 0.1451515, -0.08317802, -0.057725884, 0.22283138, 0.13996813, 0.19705944, -0.2921995, -0.080231175, -0.27066326, -0.0482235) * g_19;
    result += mat4(-0.051322196, -0.40912375, -0.14924087, 0.033685323, 0.041344143, 0.055450242, 0.09305712, -0.034863934, -0.102900185, -0.11097147, -0.065564185, 0.11914823, 0.2890554, -0.09894942, 0.053307623, -0.05579918) * g_20;
    result += mat4(-0.213933, 0.090429194, 0.084889874, -0.21953723, -0.27030995, -0.14362201, -0.19741529, -0.0833757, 0.23496687, 0.3228457, 0.29274747, 0.117888294, -0.048562698, 0.1290755, 0.09031278, -0.06844491) * g_21;
    result += vec4(0.12783583, 0.053930607, -0.055463474, -0.14634338);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf3, gxy, result);
}