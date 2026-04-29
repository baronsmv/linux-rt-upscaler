// Anime4K_Upscale_GAN_x4_UUL - Pass 59 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_21_tf2;
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
vec4 result = mat4(-0.057084437, 0.073743545, 0.15843004, -0.06717984, -0.08257869, 0.011292643, 0.13310145, 0.10770132, -0.037585445, -0.08692588, -0.042781748, -0.15288189, -0.02788944, 0.034700274, -0.15450406, -0.1679772) * g_0;
    result += mat4(0.011762893, 0.2054697, 0.1720081, 0.116406426, -0.00428441, 0.18313429, 0.03696885, -0.03316296, -0.117581464, 0.007917693, 0.10178334, -0.2611459, -0.058909763, 0.25219756, -0.16373555, 0.08321643) * g_1;
    result += mat4(0.10082542, -0.13886023, 0.121554285, 0.22873613, 0.08418588, -0.013873943, -0.006858779, 0.19993706, 0.28209662, 0.21149608, -0.035288714, 0.56616104, 0.17169634, 0.057334855, 0.053658336, -0.05077785) * g_2;
    result += mat4(0.12060641, 0.04010452, 0.11028481, 0.04508344, 0.016396279, 0.09882185, 0.18883766, 0.04364962, 0.04107997, -0.05457326, 0.022010474, 0.023509638, -0.017336952, -0.081470236, -0.04518081, -0.04369132) * g_3;
    result += mat4(-0.05629898, 0.12955196, 0.03002122, 0.051797554, -0.11305776, 0.04543245, 0.024578502, -0.038622625, 0.09602566, 0.014378242, -0.123365864, 0.0759256, -0.22232716, -0.040782683, -0.042220388, -0.21084513) * g_4;
    result += mat4(-0.020282147, -0.097285345, 0.23004697, 0.020806778, -0.18959303, 0.22034295, 0.0087907575, 0.010272914, 0.14997281, 0.07306408, 0.04324672, 0.15118538, -0.2749048, 0.11584738, -0.032733474, -0.2070121) * g_5;
    result += mat4(0.037902478, -0.030573819, -0.029344141, 0.01939143, 0.06405306, -0.04419444, -0.101269715, 0.021172248, 0.11327619, -0.009161934, -0.1717592, 0.080221824, -0.06516155, -0.17314622, 0.07386541, 0.031790655) * g_6;
    result += mat4(0.12349413, -0.19455901, -0.16831753, -0.13359772, -0.0037239022, -0.12868004, 0.096363924, -0.0721396, 0.10402346, 0.008250357, 0.012670624, 0.19257796, -0.06830968, -0.0021093774, -0.10247695, -0.26293632) * g_7;
    result += mat4(-0.10189908, 0.075891085, -0.022459852, -0.09753182, -0.2543292, 0.30875823, -0.2053786, -0.15915114, -0.075460285, 0.018414717, 0.040453814, 0.06389237, -0.34178352, -0.022121403, 0.046201658, 0.25735933) * g_8;
    result += mat4(-0.0002718784, 0.0032082999, -0.13571796, -0.2096398, -0.022996102, 0.12278952, 0.070943564, -0.19941543, -0.030735662, -0.095334, -0.24543534, 0.06891416, 0.11364924, -0.24653779, -0.05163778, -0.30017856) * g_9;
    result += mat4(0.1838837, -0.10841437, 0.07848475, -0.08485395, -0.014254071, -0.31484497, 0.15543151, -0.06692559, -0.04198029, -0.11665087, 0.107262425, 0.0067980834, -0.03962521, -0.09969709, -0.12044282, 0.1482598) * g_10;
    result += mat4(0.00026043277, 0.10293026, 0.0140016945, 0.07596427, 0.07216739, -0.024752667, -0.03748558, 0.16382839, -0.031407133, -0.07096495, -0.08130925, -0.16371527, 0.09901695, 0.035516758, 0.17092955, -0.117787674) * g_11;
    result += mat4(0.10926692, -0.19847743, -0.35133052, -0.11942348, -0.0016101972, -0.11737663, 0.07856536, 0.210181, -0.08973985, -0.231985, 0.052060172, -0.07393469, -0.0038560238, -0.13686647, -0.049954094, 0.15444914) * g_12;
    result += mat4(-0.18071556, 0.12298895, 0.41416138, -0.23190585, -0.048501194, 0.1643691, 0.22058153, -0.039875798, 0.0070992573, 0.48900208, -0.16106173, -0.017713644, 0.11375057, -0.038301516, -0.0138126705, 0.20367229) * g_13;
    result += mat4(-0.10906326, 0.17701069, 0.122338474, 0.21938156, -0.31732517, -0.11000095, 0.23848571, 0.013629898, 0.2623052, 0.12693645, -0.13266647, 0.012624822, 0.13243206, -0.07178184, -0.12631601, -0.124319084) * g_14;
    result += mat4(0.27514997, -0.20576999, -0.116263695, -0.17561655, 0.29180488, -0.0996977, -0.22064792, -0.0051669325, -0.008944824, 0.08274995, 0.15000445, 0.2706205, 0.19657025, 0.16320185, -0.048430063, -0.062193163) * g_15;
    result += mat4(0.15720521, -0.1616783, 0.12148419, 0.032654256, 0.0748495, 0.089776576, -0.2883907, 0.16739035, -0.040992603, 0.094912894, -0.1876062, 0.017233582, -0.116178006, -0.3094946, 0.010963433, -0.1276047) * g_16;
    result += mat4(-0.02279651, 0.124006964, 0.27308333, 0.07528875, 0.20459273, 0.044373933, -0.22371659, 0.1501472, 0.09959711, 0.0477301, -0.05257857, -0.05602578, 0.16206701, 0.046072427, -0.0018694117, -0.004612688) * g_17;
    result += mat4(-0.21997832, -0.11779681, -0.07657034, 0.11835144, 0.10847735, 0.2865021, -0.28411987, 0.14887205, 0.069858804, 0.116345115, -0.07407542, 0.09080259, 0.15252139, -0.24571773, 0.09876683, 0.11463688) * g_18;
    result += mat4(0.15223633, -0.00056938396, -0.032920565, 0.14372222, -0.024130384, -0.098482765, 0.028577512, 0.21373022, -0.14334433, 0.019196142, -0.0431513, 0.18337114, -0.032851133, 0.0646035, 0.028978348, -0.00956985) * g_19;
    result += mat4(0.132797, 0.15113503, 0.0032765348, -0.20993358, -0.027147237, -0.08996456, 0.024522208, -0.015556702, -0.022943618, 0.030851666, -0.2941565, 0.04444335, -0.120237455, -0.06628891, 0.17706418, -0.13388899) * g_20;
    result += mat4(0.034199353, -0.030496066, -0.12809198, -0.09803576, -0.014025315, 0.10408433, -0.12252633, 0.013718495, 0.00881372, 0.0976676, 0.119427025, -0.066808775, 0.055229302, -0.013018161, -0.08276607, 0.101116315) * g_21;
    result += mat4(0.15429354, 0.15294066, 0.13662739, -0.11073299, 0.063615054, -0.011573362, -0.12094635, -0.19076118, 0.15640004, 0.13726933, 0.020506479, -0.027316077, 0.0131364865, -0.017896159, -0.06231624, 0.15114687) * g_22;
    result += mat4(-0.047549162, -0.2276344, -0.066257186, 0.08916332, -0.017978407, 0.0068500796, -0.030843439, -0.17989396, -0.06743375, -0.13298953, 0.010617088, -0.22074251, -0.07921998, -0.003123787, 0.078639194, -0.10352951) * g_23;
    result += mat4(0.19592485, 0.045601334, -0.05466065, 0.003048098, 0.21064979, 0.21149376, -0.06651742, -0.049799632, -0.1459615, 0.1450713, 0.025346246, -0.21891195, -0.24621584, 0.10275955, -0.045584872, -0.0059188902) * g_24;
    result += mat4(-0.24433449, -0.056526583, -0.0063764798, 0.16827473, 0.036951, 0.15109439, -0.013099426, 0.088068865, 0.08357865, -0.018223299, 0.022397004, 0.13680162, 0.046609163, 0.13488059, -0.05136011, -0.2054995) * g_25;
    result += mat4(-0.23189409, 0.058366276, 0.029186329, -0.22585711, 0.1441857, 0.0776702, 0.06341345, -0.22043568, 0.13492517, 0.14087246, -0.032663856, 0.10947018, 0.0016668879, 0.01664668, -0.0821675, 0.024196142) * g_26;
    result += mat4(-0.02740043, -0.22889447, 0.24546339, 0.0032793654, -0.16380517, -0.16472526, -0.31983012, 0.05651817, 0.21478343, -0.08361714, 0.26880756, -0.39875728, -0.19244565, -0.09645046, -0.00071002246, -0.16191272) * g_27;
    result += vec4(-0.022868104, 0.112042494, 0.11364425, -0.020370165);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf2, gxy, result);
}