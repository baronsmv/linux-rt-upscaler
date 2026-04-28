// Anime4K_Restore_CNN_Soft_S - Pass 3 of 4 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(set = 0, binding = 3) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_2_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(0.024004154, -0.26474997, -0.5256586, 0.051624652, -0.16621786, 0.2964122, 0.6044247, -0.14335106, 0.17002718, -0.2679876, -0.30162668, 0.1273794, -0.17601459, -0.1782376, 0.104725115, -0.16351137) * go_0(-1.0, -1.0);
    result += mat4(-0.121676154, 0.047741555, -0.06738679, -0.056402843, 0.004424971, -0.35099635, -0.073440626, 0.039784692, 0.15204315, -0.1165704, 0.11231046, -0.27369732, 0.33737272, -0.11880767, 0.09637475, -0.14709689) * go_0(-1.0, 0.0);
    result += mat4(-0.017987821, -0.08798823, -0.062515825, -0.046803873, -0.05871703, 0.27013004, 0.19397618, -0.052147817, 0.003271283, -0.0029015478, -0.07390092, -0.09348337, -0.1574738, 0.06750957, -0.07661155, 0.054327156) * go_0(-1.0, 1.0);
    result += mat4(-0.15215784, -0.72508365, -0.3202069, 0.20295432, -0.19125701, 0.021401431, -0.051837035, -0.025939213, 0.25565025, -0.12872623, 0.13169816, 0.27377388, -0.008718429, -0.05864064, 0.028844763, 0.1144993) * go_0(0.0, -1.0);
    result += mat4(-0.30012092, -0.1322455, -0.11868545, 0.09857058, 0.082795605, -0.075334676, -0.3752773, -0.02918163, -0.67764, -0.38598236, -0.21023573, 0.38274166, -0.07398165, -0.07213789, -0.28427607, 0.1266569) * go_0(0.0, 0.0);
    result += mat4(-0.37507388, 0.18809201, -0.21982779, 0.27208912, 0.022066567, -0.27627763, 0.12345216, -0.30041683, 0.017002959, -0.091398515, -0.25207692, -0.29253414, -0.08231422, -0.14665812, -0.07868529, -0.24562219) * go_0(0.0, 1.0);
    result += mat4(0.08686712, 0.080837384, 0.20736577, 0.008233064, 0.14957365, 0.21801959, -0.04870689, 0.42149112, 0.27255878, 0.33320278, -0.08467146, 0.10381615, 0.055278245, 0.085710146, 0.009097151, 0.29092705) * go_0(1.0, -1.0);
    result += mat4(0.0012207404, -0.023874281, -0.027035477, 0.005157451, 0.19330226, 0.33711615, -0.16495204, 0.549021, 0.44879642, 0.1978837, -0.20492741, 0.28099406, 0.2631811, 0.40786585, -0.055340275, 0.2575511) * go_0(1.0, 0.0);
    result += mat4(0.29127392, -0.06287165, 0.12715077, 0.14784902, -0.3183704, 0.42057636, -0.11483724, -0.3019506, 0.010730576, 0.29091576, -0.046116166, -0.23528357, -0.0037143505, 0.1191774, -0.06084074, 0.011641706) * go_0(1.0, 1.0);
    result += mat4(-0.2579205, 0.036545023, 0.11691888, 0.04996418, 0.21318026, 0.21370813, -0.14114271, 0.031217605, -0.06979331, -0.0690704, 0.04618086, 0.025164584, -0.10994228, 0.109930746, 0.103678934, 0.12193115) * go_1(-1.0, -1.0);
    result += mat4(-0.19843774, -0.11237926, 0.007291354, 0.16480611, -0.15669724, 0.46283355, 0.077065215, 0.112273656, 0.17143534, -0.19934891, -0.25481275, 0.034591813, -0.27032652, -0.2702769, 0.04816228, -0.031614583) * go_1(-1.0, 0.0);
    result += mat4(-0.16307239, -0.11295217, 0.05861256, 0.14225823, -0.015648091, 0.11741865, 0.113366075, 0.023935538, 0.19560932, -0.10553561, -0.042583376, -0.048160724, -0.3116519, 0.13957061, -0.0044852323, -0.015472912) * go_1(-1.0, 1.0);
    result += mat4(-0.15629178, 0.06463271, -0.13176678, 0.025518289, -0.021733627, 0.22236359, 0.019508492, -0.11629477, 0.10801276, -0.021957984, -0.11272639, -0.03615053, -0.121420704, 0.2520835, 0.043395765, 0.1699031) * go_1(0.0, -1.0);
    result += mat4(0.2886654, 0.21755892, 0.21757497, 0.08442575, -0.109903164, -0.67295986, 0.22886126, -0.027185453, 0.3761606, 0.23199768, 0.05908783, -0.1496158, 0.10832971, -0.3530352, 0.20234483, -0.07615918) * go_1(0.0, 0.0);
    result += mat4(0.11043024, 0.18943349, 0.42394367, 0.029350199, -0.15085667, 0.020204183, -0.081609115, 0.07907012, 0.33805525, 0.0066280114, 0.0018284445, 0.022983696, 0.004984607, 0.0429299, -0.14568979, -0.29143327) * go_1(0.0, 1.0);
    result += mat4(-0.16376027, -0.20387048, 0.06522074, 0.17484841, -0.13885716, -0.04380927, -0.03535832, -0.16978237, -0.004799155, -0.25407305, -0.039976966, -0.011992087, -0.22535577, -0.09583549, 0.0334331, 0.016292758) * go_1(1.0, -1.0);
    result += mat4(-0.38688713, -0.20232083, 0.23887886, -0.10438324, -0.24170811, -0.074868314, 0.03977399, -0.22810821, -0.08257971, -0.11902456, 0.106009185, -0.078289054, -0.11932821, 0.024207884, 0.10070917, 0.79348284) * go_1(1.0, 0.0);
    result += mat4(-0.4018743, 0.050456528, 0.035341598, -0.03788609, 0.12964934, -0.44461823, 0.029031694, 0.29604837, -0.102386944, -0.13805065, 0.0055692918, 0.14659804, -0.22499937, 0.14680648, -0.3443954, -0.06994176) * go_1(1.0, 1.0);
    result += vec4(-0.0063428865, 0.0057986965, -0.12526293, -0.059240736);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_2_tf, gxy, result);
}