// Anime4K_Restore_CNN_Soft_M - Pass 3 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_2_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(0.27743992, 0.04277345, 0.019331178, -0.7335445, 0.006292013, 0.19800001, -0.0025032016, 0.16098699, -0.03186617, -0.060173523, 0.08878855, -0.10669283, 0.130609, -0.068515256, -0.03571823, -0.13751523) * go_0(-1.0, -1.0);
    result += mat4(-0.2430821, -0.08233978, 0.082374334, 0.04843392, -0.18989052, -0.041925047, 0.40021122, -0.317836, -0.13517766, 0.032255337, -0.0746507, 0.22114721, -0.045706213, -0.12841983, -0.27830583, 0.05763077) * go_0(-1.0, 0.0);
    result += mat4(-0.08436965, -0.04967552, -0.16798134, -0.1539139, -0.17429228, -0.10166739, 0.35864773, 0.12873615, -0.07667423, 0.04985163, 0.13391761, -0.054322604, 0.085659124, -0.078792974, 0.06481059, 0.058667548) * go_0(-1.0, 1.0);
    result += mat4(-0.17568155, 0.56705236, 0.056562193, -0.020951264, 0.005879628, -0.2502103, -0.19619654, 0.019490348, -0.14527243, 0.16983634, 0.049245857, 0.18316677, 0.055053137, 0.10699275, 0.0016993808, 0.20105995) * go_0(0.0, -1.0);
    result += mat4(0.36284775, -0.05856962, -0.42545465, 0.31931567, -0.15698905, -0.28837132, -0.028697362, -0.024917847, 0.04317283, 0.024557106, -0.052158598, 0.38654143, -0.1782944, 0.43094924, -0.11738149, 0.21554618) * go_0(0.0, 0.0);
    result += mat4(0.22645079, -0.20319854, 0.20733371, -0.18697177, -0.05167819, -0.12845007, 0.5543688, 0.2453291, 0.08027872, -0.0628224, -0.06593836, -0.05795855, -0.24527508, 0.23632833, -0.043366548, 0.14135826) * go_0(0.0, 1.0);
    result += mat4(0.08384414, 0.20807321, 0.030559694, -0.13640808, -0.07641805, -0.10919174, -0.19799095, -0.12955745, 0.093737304, -0.17856954, 0.035103753, -0.044699315, -0.07255943, -0.02331535, 0.2059249, 0.3058302) * go_0(1.0, -1.0);
    result += mat4(0.022345139, 0.16286038, -0.27228013, -0.41105714, -0.0014384583, 0.089546144, -0.08296848, -0.0050463285, 0.07038578, -0.030679917, 0.031246305, 0.36761853, -0.34799108, -0.0405689, -0.19182852, 0.015853593) * go_0(1.0, 0.0);
    result += mat4(0.1021783, -0.11396049, -0.08733628, -0.017449526, 0.042015605, -0.14808236, 0.10072531, -0.07403295, 0.15276712, -0.07807765, -0.10013386, -0.26110634, -0.04858846, 0.066066965, 0.13598624, 0.21687816) * go_0(1.0, 1.0);
    result += mat4(0.07041569, -0.17775945, 0.15697548, -0.15425202, -0.06569677, -0.033233996, 0.22596005, -0.026170855, -0.20729817, 0.1316505, -0.058410037, 0.22166035, 0.09107114, -0.13078825, -0.05639485, -0.02716142) * go_1(-1.0, -1.0);
    result += mat4(0.057966787, -0.15311252, 0.095924966, -0.055951685, 0.082777694, -0.08471956, -0.39918202, 0.10599212, 0.102710955, 0.21808124, 0.12083635, -0.38835892, 0.031709857, 0.13955092, 0.12647778, 0.011549966) * go_1(-1.0, 0.0);
    result += mat4(0.09810508, -0.119743295, 0.06166254, 0.13595435, 0.036198203, -0.028710455, -0.40789905, -0.034894038, -0.12622337, 0.14379597, 0.039958883, 0.19636424, 0.047094557, -0.07987105, -0.04905092, -0.07875785) * go_1(-1.0, 1.0);
    result += mat4(0.34118712, -0.2833933, -0.045028314, -0.40670308, -0.01961924, 0.37131935, 0.29099533, -0.19843055, 0.18604252, -0.0037280058, 0.1091072, -0.40579233, 0.11422739, -0.16490164, -0.0022396361, -0.21486944) * go_1(0.0, -1.0);
    result += mat4(0.0010853866, 0.2223109, 0.2416471, -0.33326814, 0.2549397, 0.6442047, 0.18411863, -0.19081281, -0.43552014, -0.1793875, -0.58699155, -0.01900168, -0.26955804, -0.071371995, 0.07599079, 0.27434483) * go_1(0.0, 0.0);
    result += mat4(-0.19644544, 0.14383379, -0.2599538, 0.001666124, -0.16369823, 0.009537702, -0.3690974, -0.048157427, -0.2040159, 0.01522431, -0.11007749, -0.07012568, 0.17536888, -0.012183123, -0.17366478, -0.15090804) * go_1(0.0, 1.0);
    result += mat4(0.0855136, 0.06863859, -0.17249937, -0.12850079, 0.15325847, 0.22742507, 0.22535504, 0.24032994, -0.109522276, 0.24135293, -0.17784368, 0.08172238, -0.16143093, 0.1358853, -0.09399085, 0.012180792) * go_1(1.0, -1.0);
    result += mat4(-0.04346881, 0.13367178, 0.10387612, 0.04705543, -0.10315795, 0.5816371, -0.090529, -0.017955385, -0.09032907, -0.52505773, 0.10958755, -0.26151448, 0.17246644, 0.011886279, 0.3566306, 0.32170597) * go_1(1.0, 0.0);
    result += mat4(-0.27853554, 0.1558035, 0.070289604, 0.17052644, -0.31982365, 0.29085326, -0.09494764, 0.2270542, 0.10514691, -0.24606484, -0.02049181, 0.126686, 0.16719124, 0.013080999, -0.08577963, -0.07057233) * go_1(1.0, 1.0);
    result += vec4(0.0061747693, -0.029145364, -0.026801255, 0.027419873);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_2_tf, gxy, result);
}