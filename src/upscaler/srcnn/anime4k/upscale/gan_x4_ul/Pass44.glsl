// Anime4K_Upscale_GAN_x4_UL - Pass 44 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_20_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_21_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_18_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_18_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.0200372, 0.025164925, -0.051542915, 0.17349012, 0.22963412, -0.08854868, -0.18460453, -0.009592984, 0.3433165, 0.24978307, -0.30430827, -0.53036386, -0.08970036, 0.003792772, -0.17533037, 0.05531384) * g_0;
    result += mat4(-0.120206885, -0.088055685, -0.028581804, -0.029799921, 0.1553587, 0.048395723, -0.019582719, 0.25623065, -0.16238682, 0.21795171, -0.041007563, 0.2657337, -0.2737889, 0.1436563, 0.08519452, 0.051322795) * g_1;
    result += mat4(-0.008416596, -0.037384458, -0.01667205, -0.113932766, -0.220761, 0.20724533, -0.039649304, -0.0017309792, 0.041707594, 0.12224719, -0.059473436, 0.09303625, 0.048647325, 0.08052407, -0.23728494, -0.36954325) * g_2;
    result += mat4(-0.24027216, 0.2160822, 0.16243383, 0.14543773, -0.0690304, -0.10372756, -0.108916, 0.119548805, -0.19430643, 0.17126071, -0.07952119, -0.13491428, 0.16480479, 0.024287088, -0.12048609, 0.032947384) * g_3;
    result += mat4(-0.22957891, -0.10071905, 0.13317196, 0.20797506, 0.05998575, -0.029331183, 0.18397254, -0.10808303, -0.042644747, 0.17222235, 0.29700902, -0.04193782, 0.14778145, 0.13812043, 0.118143596, -0.057448573) * g_4;
    result += mat4(-0.14184432, -0.0236615, -0.17279948, 0.18716908, 0.11995038, -0.1185408, 0.1980219, 0.18067634, -0.038657866, -0.030831996, 0.33048138, -0.12548326, 0.12749283, -0.06766755, -0.17756845, -0.11182692) * g_5;
    result += mat4(0.040251233, 0.010135124, 0.024763199, 0.0457518, -0.2875318, 0.084092565, 0.028671606, 0.026579974, 0.017806578, 0.048673276, -0.114675, 0.05184245, 0.03820837, -0.01438677, 0.071568385, 0.07407311) * g_6;
    result += mat4(0.32025474, -0.19955283, -0.1420089, 0.05544955, 0.19069096, 0.2885597, -0.119959064, -0.056846753, -0.0062394375, 0.104673326, -0.162723, -0.017674185, -0.10826556, 0.042586546, 0.06138012, -0.03990229) * g_7;
    result += mat4(-0.0050156214, -0.15407455, -0.07907167, -0.13220526, -0.017592989, 0.2021805, -0.016687173, -0.056055553, -0.101649925, 0.1281, 0.05800204, 0.43441603, -0.024814442, 0.22591786, -0.2340531, 0.10235692) * g_8;
    result += mat4(0.24094208, 0.20049766, -0.03091491, 0.024811655, -0.022125067, -0.078261666, -0.08867578, -0.038298346, 0.12770705, -0.3216306, 0.18978754, -0.01107385, -0.038726375, -0.34504443, 0.49312648, 0.13409658) * g_9;
    result += mat4(0.0630035, 0.12272932, 0.032202568, -0.18289864, -0.0741027, 0.050733794, 0.07594249, 0.05300468, 0.042907406, 0.24372669, -0.028120704, 0.093619086, 0.11598335, 0.101204365, -0.17834216, -0.17095858) * g_10;
    result += mat4(-0.08183699, -0.07916702, -0.062332753, 0.1686114, -0.016465722, -0.0046439907, -0.025219526, 0.09196341, -0.28213915, -0.4013967, 0.2070858, 0.23499006, 0.31538546, -0.063582435, 0.17215486, -0.05670036) * g_11;
    result += mat4(-0.01627626, -0.085867815, -0.044567704, -0.068304785, 0.24002759, -0.18444167, 0.051936157, -0.084095374, -0.027830267, 0.0020481357, 0.05791986, 0.15611658, 0.28899965, -0.20653085, -0.075661235, -0.14174046) * g_12;
    result += mat4(-0.08468525, 0.058726486, -0.06389248, -0.01455625, 0.27516794, -0.09621903, -0.1269632, 0.021708349, 0.06876667, 0.09899092, -0.060870275, -0.036878586, 0.016620016, -0.032395374, 0.21142422, 0.114436075) * g_13;
    result += mat4(0.106104285, -0.37164697, -0.16798657, -0.1352658, -0.07100603, -0.10133517, 0.026537118, -0.015494572, 0.05662935, -0.018886555, -0.007515541, 0.12669149, 0.1449747, -0.23413232, 0.22381899, -0.15549453) * g_14;
    result += mat4(0.25238156, -0.019380376, -0.05552284, 0.033374626, -0.005643143, -0.020936595, -0.20558305, -0.15705742, -0.006181828, -0.1994116, -0.046375062, 0.13563119, -0.28634745, 0.0880065, -0.042301185, -0.29208398) * g_15;
    result += mat4(-0.17484008, -0.021532, 0.21034543, -0.0034605127, 0.014549843, 0.1751193, -0.12673648, 0.0064667664, -0.19978295, 0.1404624, 0.06869049, -0.020720724, 0.12267954, 0.25009266, -0.20387867, -0.15889901) * g_16;
    result += mat4(0.25143266, 0.17484929, 0.24925528, -0.03215604, -0.0974627, 0.15165818, 0.08267684, -0.202364, 0.24375704, -0.26883098, -0.15251026, 0.051847905, 0.10552426, 0.048911758, -0.113630824, -0.25745502) * g_17;
    result += mat4(0.047861718, 0.010482632, -0.28139532, -0.18458135, -0.08900709, 0.14439812, 0.017580662, -0.086692065, 0.14848581, 0.012461116, 0.13328992, 0.1823087, 0.1341251, 0.099720836, -0.123326704, -0.1529806) * g_18;
    result += mat4(-0.13218595, -0.020096691, 0.089338526, -0.050373968, -0.12718384, -0.34216353, -0.05081511, -0.100018986, -0.12318239, 0.043791108, -0.3888225, 0.11529475, 0.17406003, -0.2179613, -0.18560894, -0.16957083) * g_19;
    result += mat4(0.21191274, -0.16949633, -0.04258746, -0.15323012, 0.36763668, 0.18696135, -0.035708304, 0.08924961, -0.10829788, -0.086305946, 0.18746884, 0.19478951, 0.2759173, 0.059790425, 0.029030167, 0.22933595) * g_20;
    result += mat4(0.117172234, 0.2812114, -0.034787145, 0.067007184, -0.18443052, -0.01740869, 0.012421643, -0.23641962, 0.09629342, -0.122772515, -0.1556607, -0.13235089, 0.13715908, 0.11799065, -0.025866343, 0.03717886) * g_21;
    result += mat4(-0.06885674, 0.20376506, 0.032389764, -0.1343853, -0.24107948, -0.2061297, -0.15523757, 0.045462113, 0.15680042, 0.24913467, -0.1266525, 0.15182254, -0.19809371, -0.11994996, 0.024678899, 0.34593883) * g_22;
    result += mat4(0.08096669, 0.03794547, -0.08631197, -0.074983165, -0.19917545, 0.08625112, -0.2224293, -0.13218154, -0.16452844, 0.21913971, 0.15406418, -0.14238952, -0.23737735, -0.13383593, 0.04449909, -0.14110228) * g_23;
    result += vec4(-0.047341306, -0.010470165, -0.060366448, -0.0063673723);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf1, gxy, result);
}