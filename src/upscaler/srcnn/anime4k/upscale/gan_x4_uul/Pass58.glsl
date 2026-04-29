// Anime4K_Upscale_GAN_x4_UUL - Pass 58 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_21_tf1;
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
vec4 result = mat4(-0.1756655, 0.2394621, -0.08748251, 0.12350313, 0.2136366, 0.07180196, -0.063014165, -0.052154776, -0.048294004, -0.11931733, -0.07316665, -0.016064208, -0.16288999, 0.17369701, -0.035828933, 0.0003992723) * g_0;
    result += mat4(-0.28360948, 0.05576701, 0.044312038, -0.08181158, -0.17544775, 0.10725244, 0.19446151, -0.19915965, 0.20983706, -0.048648514, -0.06845115, -0.06666123, -0.058113296, -0.1400215, 0.018594868, 0.03359526) * g_1;
    result += mat4(0.1685084, -0.073783316, -0.20972507, -0.113601886, 0.04464233, 0.1066123, 0.07970566, -0.12577637, -0.050229155, -0.13494389, -0.2558168, -0.0042490545, 0.005460988, 0.0076199966, 0.0025213186, 0.044763103) * g_2;
    result += mat4(-0.0052317875, 0.0027467392, -0.14741494, 0.07422548, 0.069331884, 0.05495023, 0.011922025, -0.068583466, -0.09747392, -0.03871967, 0.019188546, -0.24301958, -0.09219407, 0.09321753, 0.13795844, 0.028697817) * g_3;
    result += mat4(0.16926937, -0.0071689105, 0.1393118, -0.05259209, 0.12629338, 0.13920256, 0.12663081, -0.051457815, -0.17981507, 0.12771882, 0.09692452, 0.08349755, -0.09658173, -0.17841125, -0.20769149, -0.0763144) * g_4;
    result += mat4(-0.21198377, -0.14739051, -0.08248044, 0.1661816, -0.05062238, -0.1363927, 0.13842218, 0.1367609, 0.04016191, -0.17620887, -0.056923762, 0.02746218, -0.07269395, -0.08043915, -0.10160525, 0.062392905) * g_5;
    result += mat4(-0.14993137, -0.095249705, 0.17030515, -0.012608146, -0.07266432, 0.014926277, -0.0047261617, -0.010011702, 0.009128133, 0.07995534, 0.05507624, -0.26496184, 0.3488721, -0.09683456, 0.020622155, 0.06607447) * g_6;
    result += mat4(-0.21903756, 0.34106353, 0.17070994, 0.077885374, -0.011344036, 0.012352647, -0.171021, 0.06153072, -0.012573895, -0.085864305, -0.07954067, -0.034453984, 0.0023422232, 0.26898122, -0.086993374, -0.12912525) * g_7;
    result += mat4(-0.048054293, -0.058729056, 0.058039352, 0.0077087884, 0.07013047, -0.19018608, -0.17199957, 0.12733743, -0.11381175, 0.0036818564, -0.036225986, -0.04890944, 0.1931185, -0.050229732, -0.055666275, 0.010115753) * g_8;
    result += mat4(-0.10551637, 0.015622803, 0.013705792, -0.2789802, 0.039018016, -0.11402238, 0.14938816, 0.08859123, -0.19127499, -0.21991971, -0.03997634, 0.2888021, 0.5119256, -0.0182172, -0.4097011, 0.0650889) * g_9;
    result += mat4(-0.15852791, -0.008691007, 0.027062492, -0.021986786, -0.121833265, -0.032671, -0.109205626, -0.026337394, 0.14460158, 0.07089407, -0.16064858, -0.06329875, 0.16661745, 0.10511746, 0.069920555, 0.12870672) * g_10;
    result += mat4(0.19965324, 0.2015641, 0.05944082, 0.076328635, -0.042850234, 0.100452326, -0.04502685, 0.15974133, 0.0432549, 0.16362476, 0.05391766, -0.20400761, 0.09843942, -0.114038505, -0.044906083, -0.084004216) * g_11;
    result += mat4(0.0014203127, 0.072613284, 0.18832877, -0.1519538, 0.17094725, 0.023459934, -0.08103932, -0.18414992, 0.050177015, -0.06879559, -0.26551455, -0.20276074, -0.4067025, 0.06735142, -0.02654105, 0.108480014) * g_12;
    result += mat4(0.11884444, -0.20847607, -0.39635405, -0.027750423, -0.17062746, -0.11462501, 0.03766563, 0.22330031, 0.08840299, -0.02593574, 0.30610138, 0.017082121, -0.073421106, -0.03310496, -0.022566084, 0.12895042) * g_13;
    result += mat4(0.13146816, 0.03408076, 0.068583496, 0.040359933, 0.058004156, -0.18711473, -0.012030321, 0.054367706, -0.21604696, 0.029737698, -0.18165046, -0.032207813, 0.19296853, -0.06486989, 0.1930012, -0.26257816) * g_14;
    result += mat4(-0.0003308146, -0.1018507, 0.10688593, -0.086943775, -0.06309165, 0.11305288, 0.40455562, 0.07220006, 0.17344922, 0.21377957, -0.106255956, -0.08522667, -0.081184156, -0.17647071, -0.056697357, -0.030556178) * g_15;
    result += mat4(0.15709074, 0.13488838, -0.108037606, -0.049638074, 0.16628793, 0.22323613, 0.18880367, 0.110625856, -0.17176348, 0.0442544, -0.24436983, 0.20503913, -0.015147643, -0.087451935, -0.14789064, 0.015226477) * g_16;
    result += mat4(-0.029338064, -0.058311418, 0.023408614, 0.23031227, 0.10385574, 0.027987834, 0.09013144, 0.28468946, 0.0031934478, -0.19209816, 0.034222614, -0.28228182, 0.16321793, -0.18102172, 0.018543411, -0.16518813) * g_17;
    result += mat4(0.04458001, -0.13962908, -0.13753751, 0.08451667, -0.25742018, 0.21066302, 0.10019894, -0.15584072, -0.01348787, 0.0033656303, 0.04586261, 0.021628007, -0.036585297, 0.26717108, -0.15728012, 0.103385106) * g_18;
    result += mat4(0.0044587324, -0.19981517, -0.22820733, -0.022784092, 0.05868396, 0.07768994, -0.03181301, 0.054078016, 0.14406122, 0.2340996, -0.2972908, -0.16759236, -0.27278668, 0.019484127, 0.032888357, -0.17713867) * g_19;
    result += mat4(0.05132516, 0.002060976, -0.11749896, 0.005121125, -0.07908039, -0.07778476, -0.19288218, -0.113970414, -0.09135908, -0.009404741, -0.15993251, 0.15056853, -0.06927528, -0.03733133, -0.24843821, 0.15608594) * g_20;
    result += mat4(0.11080882, 0.032175705, -0.04760623, -0.14559296, 0.03192353, 0.101781964, 0.12357085, -0.025075397, 0.12224393, 0.00500326, 0.05720067, -0.087521225, -0.032957695, 0.027808554, 0.13563655, -0.2128763) * g_21;
    result += mat4(-0.12507181, -0.12221015, -0.024783826, -0.1233778, 0.15383248, 0.19294359, -0.10415819, -0.20353647, 0.119121395, 0.13289572, 0.030740019, -0.015015452, -0.07683901, 0.10667189, -0.041018065, 0.22529341) * g_22;
    result += mat4(0.1489391, -0.059898213, -0.046357498, 0.022468781, -0.24517635, -0.13018654, 0.2039975, 0.21484332, 0.028208151, -0.20970574, -0.10110034, 0.12773193, 0.07744774, -0.118900456, -0.007357081, 0.018511213) * g_23;
    result += mat4(0.10130345, 0.2007317, -0.02755449, -0.05844333, -0.09601821, -0.006501421, -0.05792646, -0.02546418, -0.12300777, -0.044581413, 0.08369023, 0.013736111, -0.117478505, -0.03133182, -0.07848863, 0.114977054) * g_24;
    result += mat4(0.06206287, -0.13663986, -0.2633325, -0.06723374, -0.0368251, 0.10849614, -0.12641706, -0.101314045, 0.1668918, -0.1774165, -0.07337273, -0.14278898, 0.09879653, 0.11570133, 0.049410257, -0.28515536) * g_25;
    result += mat4(0.075859904, 0.46286193, -0.0065651555, 0.019701669, 0.097126104, -0.21981543, 0.11008625, -0.24778378, 0.22997652, -0.08742972, 0.026607014, 0.0001746832, -0.183374, 0.35722917, -0.054048, -0.12029537) * g_26;
    result += mat4(0.29831323, -0.24104582, -0.11618897, 0.10247404, 0.0058463574, 0.22800444, -0.069028065, 0.22541459, -0.18233538, -0.32635194, -0.13827065, -0.21868181, 0.25495726, -0.30253872, 0.055982653, 0.07193308) * g_27;
    result += vec4(0.13571368, -0.145653, 0.09633155, 0.022155894);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf1, gxy, result);
}