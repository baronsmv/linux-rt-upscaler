// Anime4K_Upscale_GAN_x4_UUL - Pass 33 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf;
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
vec4 result = mat4(-0.018240726, -0.023228848, -0.037755717, 0.009697539, -0.06391762, -0.22754766, 0.32287842, 0.0321051, -0.081117265, 0.09789689, 0.13194586, 0.033958163, -0.16528013, 0.25348902, 0.013538278, -0.122477636) * g_0;
    result += mat4(0.21895553, 0.32368854, 0.09295876, 0.008549726, -0.17221816, -0.009608649, 0.008025734, -0.12808394, 0.095984474, -0.055960163, 0.1857312, -0.01410566, -0.29036984, -0.11915815, -0.22480978, -0.010984804) * g_1;
    result += mat4(0.021460485, -0.069948144, -0.20457397, -0.06368738, 0.041937023, 0.058391638, 0.08521619, -0.14939685, -0.17603025, -0.2704823, 0.1297126, 0.08506167, -0.036500573, -0.15101454, 0.2705927, -0.11495338) * g_2;
    result += mat4(-0.015002146, -0.11097708, -0.04153528, 0.009949436, 0.05756999, 0.0021354982, 0.011803671, -0.059338056, 0.14856763, 0.1583689, -0.18323529, -0.061641436, -0.15716806, -0.0712248, -0.26153558, 0.1281614) * g_3;
    result += mat4(0.12309243, -0.019010289, -0.48949012, 0.22548608, 0.06878324, 0.06457863, -0.16647714, -0.19459985, -0.2501109, -0.1472345, -0.04101737, 0.30518964, 0.07157429, 0.03916779, 0.17215528, -0.27554017) * g_4;
    result += mat4(0.04666684, 0.21871185, -0.06709083, -0.05889728, 0.16164586, 0.057062894, 0.13912962, 0.02538998, 0.28736678, -0.11419385, 0.06581755, 0.17950252, -0.0021713986, -0.21133782, 0.18057212, -0.13002412) * g_5;
    result += mat4(0.07720478, -0.059798796, 0.10859078, -0.054959364, -0.17407586, 0.12507877, -0.03956437, 0.13279653, 0.10017548, -0.29822072, -0.023122882, 0.09967618, 0.09163447, -0.26512557, -0.019125078, -0.26062354) * g_6;
    result += mat4(0.007360602, -0.05319189, 0.26773262, 0.21440737, 0.041763037, -0.0078692185, 0.104448885, 0.10134778, -0.0907065, 0.024284367, 0.003045257, -0.047127664, -0.25469595, -0.028164914, -0.043226935, 0.057833903) * g_7;
    result += mat4(0.055060904, 0.12964465, 0.0100004645, 0.11081481, -0.18145356, -0.06301884, 0.002863084, -0.09317529, -0.032467086, 0.053214524, -0.20222305, -0.17389554, -0.02374549, 0.081627876, 0.13586336, -0.13289934) * g_8;
    result += mat4(-0.12577327, 0.10578063, 0.2519808, 0.026089173, 0.10365033, 0.2503572, 0.08068646, -0.13609827, 0.0993266, -0.18147932, -0.24582084, -0.0027736255, 0.22986256, 0.0027441771, -0.2843601, -0.24845399) * g_9;
    result += mat4(0.407128, 0.02000054, -0.025044682, -0.07539943, 0.123638265, 0.13025928, 0.06359813, -0.06765932, 0.25122678, -0.07864227, -0.2603126, -0.4042432, -0.14067987, -0.23111042, 0.22302234, 0.2521762) * g_10;
    result += mat4(-0.1394529, -0.31797844, -0.19563127, 0.06399499, 0.10406692, 0.12298246, -0.08451652, 0.067356326, -0.10545609, 0.1542806, -0.09520273, -0.4893699, 0.016285073, -0.05184254, 0.01668572, 0.28672934) * g_11;
    result += mat4(0.18358573, 0.07086077, 0.081096895, 0.08466328, -0.037679147, -0.010346395, -0.10832653, 0.24460128, -0.035456736, 0.20034707, -0.09119996, 0.026973516, 0.018956725, -5.4123822e-05, -0.022495521, 0.022271384) * g_12;
    result += mat4(0.2034902, -0.33097568, -0.06138338, 0.0043093674, 0.2108118, 0.07654584, 0.12894695, 0.06086084, 0.09708061, 0.08280423, 0.03982084, -0.013282445, 0.1286689, -0.014037032, -0.028497966, 0.3555501) * g_13;
    result += mat4(-0.07103243, -0.13886544, -0.14505245, -0.16215186, 0.19933704, 0.20801912, 0.11129495, -0.060560636, 0.022709953, 0.030686028, 0.048585244, -0.1738981, -0.27648082, -0.05651471, -0.45279422, -0.110658295) * g_14;
    result += mat4(-0.010698494, -0.014529519, 0.06092168, -0.13276085, -0.31590307, -0.034779727, 0.13390115, -0.2154148, 0.31362757, -0.16912729, -0.17177378, 0.04694781, 0.2817023, -0.20776759, 0.051466487, 0.0033499447) * g_15;
    result += mat4(0.14116827, -0.004569741, -0.34971637, 0.14838621, -0.23526837, 0.12044124, 0.24962978, -0.47152176, 0.42074892, -0.08043922, -0.029038593, -0.0067655854, -0.074845135, -0.06440738, 0.19292484, 0.22176756) * g_16;
    result += mat4(0.1824485, 0.14171454, 0.17320803, 0.12185365, 0.114776775, 0.06394961, 0.26359382, -0.4180487, -0.16079833, 0.0073073236, -0.12868631, -0.15573654, -0.07210191, -0.012453217, -0.14852667, 0.016012993) * g_17;
    result += mat4(-0.0665514, -0.23494612, 0.098041154, -0.13429102, -0.09597223, -0.02225127, 0.3641938, -0.11276776, -0.116225325, -0.09660111, 0.24925885, 0.26824257, -0.013628071, -0.024492549, 0.056771886, -0.039691154) * g_18;
    result += mat4(0.1038324, -0.13783209, -0.29168722, -0.13033277, -0.111158535, -0.12511612, -0.08763829, 0.05513153, 0.0047156885, 0.13744187, 0.07963748, 0.00240008, -0.13253629, 0.019641487, -0.113318674, 0.11268771) * g_19;
    result += mat4(0.017130049, -0.050066452, -0.1321411, 0.12105113, -0.19122683, 0.12728047, -0.11631363, 0.11703079, -0.16408561, 0.073255256, 0.18040007, -0.027916772, 0.117218666, -0.18100376, -0.059619226, -0.10517939) * g_20;
    result += mat4(-0.21253966, 0.2606339, 0.10612866, 0.1311986, 0.19595386, 0.07200261, -0.22423409, -2.2849147e-06, 0.28697285, 0.036045954, -0.19823448, -0.054925486, -0.12410156, 0.30472383, 0.2330069, -0.12509976) * g_21;
    result += vec4(0.022758514, -0.03611776, 0.0064447913, 0.00068006525);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf, gxy, result);
}