// Anime4K_Upscale_Denoise_CNN_x2_M - Pass 5 of 9 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_4_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.17903937, -0.0014294779, 0.1824805, -0.19555633, -0.0052551827, -0.013796094, 0.06358042, 0.13301018, 0.008874768, 0.06605332, 0.06117636, 0.012946474, 0.048656575, 0.0060409275, -0.0671362, -0.06897735) * go_0(-1.0, -1.0);
    result += mat4(-0.16098012, 0.10772552, -0.13175552, -0.5299018, 0.068713695, -0.048258893, -0.49698257, 0.36581638, 0.21755004, -0.12125899, -0.27382872, -0.12268086, 0.014334542, 0.20573758, 0.45879167, -0.29648975) * go_0(-1.0, 0.0);
    result += mat4(0.06860283, -0.18047708, 0.024707617, 0.11900479, 0.09474589, -0.16559775, -0.054095846, -0.011377782, -0.008733984, 0.105020404, -0.040116277, -0.0022003972, 0.1453799, -0.032110006, -0.018741792, -0.12511599) * go_0(-1.0, 1.0);
    result += mat4(0.20024729, -0.01969923, -0.026999667, -0.39064395, -0.14559332, -0.11634086, -0.13226044, 0.11779975, -0.08838282, -0.0882447, -0.23166943, -0.15760234, 0.030928904, -0.032423917, 0.20324136, -0.19692755) * go_0(0.0, -1.0);
    result += mat4(0.49499384, 0.7327846, -0.6173799, -0.53821295, -0.15000962, 0.11169762, 0.6942423, 0.07956513, 0.06913002, -0.19037646, -0.19826908, 0.68080276, -0.2747096, -0.15832238, 0.47366706, 0.090432756) * go_0(0.0, 0.0);
    result += mat4(-0.18274948, 0.09204629, 0.16644076, 0.05641037, 0.03328184, -0.6218293, 0.26432592, -0.093742386, 0.33038342, -0.24853565, -0.23683667, -0.37430722, -0.20684583, -0.32283148, -0.07633969, -0.08765815) * go_0(0.0, 1.0);
    result += mat4(0.06821987, 0.06395764, -0.14685121, -0.15894371, -0.093540885, 0.057568345, -0.048376244, -0.009256543, -0.26325077, -0.03193119, -0.16857445, -0.02404981, 0.110593356, 0.042911418, 0.06626762, -0.0312436) * go_0(1.0, -1.0);
    result += mat4(0.3108626, 0.37123847, -0.082249805, -0.21339422, -0.3756041, -0.08518717, -0.16853802, 0.011641729, -0.30096757, 0.26942274, -0.08990497, -0.19451031, 0.21974437, -0.04231723, 0.26160353, -0.040834647) * go_0(1.0, 0.0);
    result += mat4(0.11795158, 0.24436565, 0.043223023, -0.0159957, -0.19689156, 0.13223267, -0.013983249, 0.09437164, -0.47648698, -0.00082660443, -0.085406005, 0.10885898, 0.104696035, -0.053257108, 0.024389362, 0.0282572) * go_0(1.0, 1.0);
    result += mat4(0.032890156, 0.0115719065, -0.01898909, -0.03034875, -0.041037276, -0.1026382, 0.03337663, 0.20108728, -0.00023235095, -0.018033072, -0.028535927, 0.07359915, 0.075182244, 0.02959868, 0.15107772, -0.09815672) * go_1(-1.0, -1.0);
    result += mat4(-0.004040557, 0.06707476, 0.039022792, 0.52437925, -0.08027356, 0.040488366, 0.035332825, 0.07683081, -0.03521227, -0.081861034, 0.090804815, 0.10580108, 0.20452882, -0.58755285, 0.04303056, 0.41562977) * go_1(-1.0, 0.0);
    result += mat4(0.09290062, 0.03495193, 0.02347216, -0.012873525, -0.076936446, 0.1453216, -0.03742271, -0.14174925, -0.058219753, 0.19095406, 0.055627216, 0.09437343, -0.010424211, -0.314692, 0.3314579, -0.053285643) * go_1(-1.0, 1.0);
    result += mat4(-0.053961687, 0.1483992, 0.042458896, -0.1966439, 0.13864957, 0.07587672, -0.06519269, 0.09530391, 0.04215073, 0.039545458, 0.21056756, 0.09972659, 0.02987125, -0.08102741, 0.07075036, 0.21867757) * go_1(0.0, -1.0);
    result += mat4(-0.5512795, 0.03104814, 0.27901977, 0.122875504, -0.2656715, 0.007895486, -0.6735937, 0.20810314, -0.31432617, 0.07420857, 0.2573659, -0.35361463, 0.19826569, -0.47774056, 0.15816487, -0.29203883) * go_1(0.0, 0.0);
    result += mat4(0.35078493, -0.07371588, -0.026663188, -0.20976657, -0.009644347, 0.037428845, -0.33933878, -0.010807704, 0.088060796, 0.16753472, -0.12296045, 0.17563403, 0.1501952, 0.07353703, 0.32531765, 0.11667607) * go_1(0.0, 1.0);
    result += mat4(0.096126616, -0.058021486, -0.03439203, 0.06868024, 0.047914367, 0.026945053, 0.04207778, 0.046023168, 0.16024022, 0.07846185, 0.004195093, 0.07272046, -0.10458233, -0.0904536, 0.16049337, 0.015941419) * go_1(1.0, -1.0);
    result += mat4(0.032256138, -0.055398785, 0.079738356, 0.113359064, 0.11975066, -0.074372105, 0.102006756, -0.011490042, 0.15155345, 0.0025528704, 0.23328577, -0.059241068, -0.067783386, -0.18220833, 0.0057692174, 0.039900843) * go_1(1.0, 0.0);
    result += mat4(-0.06173998, -0.07121991, -0.01118306, -0.063749574, -0.032665797, 0.0014987896, 0.03113169, 0.06916617, 0.0066490914, -0.052818965, -0.050131317, 0.10337558, -0.030870482, -0.14671221, 0.12152145, -0.05003445) * go_1(1.0, 1.0);
    result += vec4(-0.010524109, -0.008519857, -0.08958723, -0.07917139);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_4_tf, gxy, result);
}