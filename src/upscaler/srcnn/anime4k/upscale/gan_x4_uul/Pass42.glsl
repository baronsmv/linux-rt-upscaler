// Anime4K_Upscale_GAN_x4_UUL - Pass 42 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_12_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_12_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_12_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_14_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_15_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_12_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_12_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_12_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_12_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_12_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_12_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_14_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_14_tf, pointSampler), pos)), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.1761742, -0.44747975, 0.059779506, 0.03766182, 0.03141564, 0.056810793, 0.008301192, 0.14369194, 0.17527783, -0.0017236042, 0.09834237, 0.09575803, -0.008661739, -0.104841106, -0.16932498, 0.11579545) * g_0;
    result += mat4(-0.12777811, 0.032608256, -0.07513904, -0.0039272117, 0.12906359, -0.026142448, -0.037676588, -0.10154283, 0.043286253, -0.051307295, 0.041824408, 0.18696383, -0.09039417, -0.06348285, -0.12320969, 0.03376613) * g_1;
    result += mat4(0.104417875, 0.10663846, -0.101657666, 0.01425698, -0.008538496, -0.025354145, 0.035612363, -0.05219493, 0.026766634, -0.10843467, -0.021850081, 0.09590063, -0.09614841, -0.054467317, -0.017985666, 0.13570157) * g_2;
    result += mat4(0.07591282, 0.13617313, 0.19501148, 0.14904675, -0.13086428, 0.21186173, 0.20964113, -0.009169893, -0.20719013, -0.14911315, -0.075036585, 0.22582716, 0.10560652, 0.06860698, 0.07254264, 0.19700265) * g_3;
    result += mat4(0.20456348, 0.24539794, 0.12823294, -0.16726765, -0.1531631, -0.19301818, -0.07844603, -0.046090215, -0.20239432, 0.03090601, -0.0994392, 0.0952079, 0.0022682967, -0.08098104, -0.03782831, 0.020748707) * g_4;
    result += mat4(0.03633377, -0.09185641, 0.09126538, -0.047538064, -0.13509507, 0.03449196, -0.11007355, 0.2173493, 0.20409976, 0.025805485, -0.09973431, -0.19965756, 0.20450562, -0.16382888, 0.058049567, -0.011116461) * g_5;
    result += mat4(0.08500784, 0.1650986, -0.16035236, 0.13470611, -0.1060791, 0.18405674, -0.06643479, 0.04466202, -0.0758685, 0.08887386, 0.2379966, -0.17876488, 0.09099816, -0.13912867, -0.022313673, 0.014845894) * g_6;
    result += mat4(-0.30880445, -0.25211424, 0.08918694, 0.060770545, -0.28389496, -0.23819323, 0.24819243, -0.116066344, 0.06437278, -0.14691679, 0.046198275, -0.006334894, -0.29351792, 0.11259146, 0.20746972, -0.4178989) * g_7;
    result += mat4(-0.106741056, -0.18458399, 0.0067779664, -0.15917686, 0.014802229, -0.17655735, -0.01837346, -0.013440738, -0.036119413, 0.091039784, -0.050894205, -0.030827638, 0.22975314, -0.110873595, -0.29769754, 0.046003085) * g_8;
    result += mat4(0.016886916, 0.064219564, -0.17515728, -0.26352295, -0.06157579, 0.20600513, 0.3151227, 0.058217525, -0.008353625, 0.3203168, 0.17482461, -0.014621326, 0.126173, 0.42937633, -0.32928523, -0.18174276) * g_9;
    result += mat4(0.08384935, 0.012600786, -0.10611915, 0.2905753, 0.31809968, -0.2115759, -0.11971381, 0.17892627, 0.21938775, -0.08610796, -0.07833694, 0.025847232, 0.15850039, -0.0050456845, -0.15777875, -0.17553087) * g_10;
    result += mat4(0.07441658, 0.2089438, 0.09365662, -0.05719887, 0.22574152, -0.13032901, -0.12378451, 0.083824284, -0.15680449, -0.122956805, -0.13531187, 0.08218225, -0.062917516, 0.0080551095, -0.15378468, 0.16125157) * g_11;
    result += mat4(-0.050182775, 0.44902998, 0.18556629, 0.011656178, -0.08106504, -0.027293755, -0.026111403, 0.16687864, 0.3194157, 0.29866177, -0.043069556, 0.09596009, 0.032058172, 0.41144785, -0.3589045, 0.13055441) * g_12;
    result += mat4(0.23642781, 0.041985907, -0.10103298, 0.052018266, -0.07686496, 0.0155056175, 0.18786597, -0.2506586, -0.17439952, -0.3177631, 0.113115676, -0.14640856, -0.008198415, 0.011810333, -0.050316535, -0.14926358) * g_13;
    result += mat4(-0.39796874, -0.062100228, 0.07615961, -0.023087898, -0.22297885, -0.090215296, -0.11415266, 0.16724303, 0.04577964, -0.08540938, -0.063765004, -0.18341166, -0.088879146, -0.05323474, -0.008252758, 0.018424602) * g_14;
    result += mat4(0.20078817, -0.060623486, -0.0990207, 0.08031568, -0.15245742, -0.18889837, 0.15183337, -0.007422197, 0.09565667, -0.23462932, -0.16531046, -0.21983044, 0.014405007, -0.03047801, 0.124785386, 0.07483329) * g_15;
    result += mat4(0.09068068, 0.020738058, 0.076772, -0.30366233, 0.103929624, -0.22885206, 0.16361028, -0.1170221, 0.12693621, 0.053154428, -0.015516178, 0.16410422, -0.09879072, -0.034197513, 0.08162684, -0.114710785) * g_16;
    result += mat4(0.07250333, 0.035765056, -0.22287408, 0.07087545, 0.2388845, -0.17439961, 0.19510424, 0.15644315, -0.026337821, 0.14344972, -0.094487876, -0.15113162, -0.030316673, -0.07807948, -0.057335343, -0.06561144) * g_17;
    result += mat4(-0.22793378, -0.090403825, -0.058371782, -0.14358567, -0.012014318, -0.06519256, -0.024871968, -0.21873134, 0.12088611, -0.08515825, 0.095237084, 0.17710285, -0.12732038, -0.008813873, 0.050080344, -0.054026045) * g_18;
    result += mat4(-0.14742918, -0.15626287, -0.09105866, -0.10570933, 0.002858163, -0.09366216, 0.0738335, -0.16642094, -0.14428791, 0.027129209, 0.0056066504, -0.105539836, -0.15898356, 0.09733231, -0.09281279, -0.058596354) * g_19;
    result += mat4(-0.17503378, -0.07734258, -0.07499573, -0.0036713225, -0.09865644, 0.13322629, 0.05817975, 0.07716319, 0.1798274, 0.20163825, 0.14732292, -0.008401361, -0.010455682, 0.1436539, -0.013620519, 0.21749584) * g_20;
    result += mat4(0.12678513, 0.009905442, -0.04881402, 0.015975054, -0.31984022, 0.085915014, 0.15399966, -0.001702288, -0.1199135, -0.45281914, -0.16187267, 0.07849383, -0.20719478, -0.23045829, 0.006563257, -0.12863535) * g_21;
    result += mat4(0.019257441, 0.06068494, 0.00059041375, 0.23092182, 0.27663466, -0.06695913, -0.1036311, 0.051746387, 0.12334096, 0.26376775, 0.13009991, 0.041141927, 0.15175597, -0.07524408, -0.22195654, -0.109512396) * g_22;
    result += mat4(-0.16434675, 0.18122146, -0.17783065, -0.29658446, 0.044498317, -0.13306247, 0.03333715, 0.38770738, 0.2770302, -0.21413137, -0.29719895, 0.034777734, 0.054781754, 0.32892776, 0.11601829, -0.029398393) * g_23;
    result += vec4(-0.12481139, 0.022676378, -0.058046315, 0.03696718);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf1, gxy, result);
}