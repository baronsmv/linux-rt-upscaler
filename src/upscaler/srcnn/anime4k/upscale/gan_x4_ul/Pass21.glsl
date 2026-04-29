// Anime4K_Upscale_GAN_x4_UL - Pass 21 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_6_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_6_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_6_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.104137026, 0.102377966, 0.29650456, 0.16560245, -0.049722087, -0.022562431, 0.1480423, 0.22173022, -0.15099648, 0.25188634, 0.29793224, -0.25045073, -0.166794, 0.17724776, -0.13309427, -0.14215149) * g_0;
    result += mat4(0.0111736925, -0.20109345, -0.004992949, -0.16356087, -0.03629021, -0.17836154, -0.020239769, -0.0027136574, -0.057733543, 0.1929391, -0.25687936, 0.032994594, 0.28941298, -0.24378207, 0.0058246693, -0.04602329) * g_1;
    result += mat4(0.058517553, -0.00855018, -0.10235121, 0.031646684, -0.3329856, 0.28455597, 0.09738041, -0.38193113, -0.11249739, -0.01848674, 0.2163143, -0.06349695, 0.20303167, -0.033269245, -0.2735205, -0.15447442) * g_2;
    result += mat4(0.080081046, 0.07366588, -0.09329567, 0.18479577, -0.118616, 0.09503109, -0.26074445, 0.35643557, 0.30263063, 0.22413187, 0.09882829, 0.12301443, -0.006198813, 0.19721447, 0.10678005, -0.1651503) * g_3;
    result += mat4(-0.06906497, -0.3009552, 0.07767211, 0.05151866, 0.11417627, 0.23357406, -0.048603542, -0.049274545, -0.06154897, -0.12599663, 0.07611352, 0.00786339, 0.14635855, -0.26319003, -0.06853761, 0.088817514) * g_4;
    result += mat4(0.11830914, -0.10345762, -0.09292891, -0.0074040242, 0.0073001185, -0.15325016, -0.011847827, 0.23296888, 0.06515359, -0.06067429, -0.090339884, 0.13176519, 0.23185344, 0.071258485, -0.06901788, -0.0903061) * g_5;
    result += mat4(0.17608684, 0.1722441, -0.00018389517, 0.026899414, 0.11040594, 0.053332347, 0.074438855, 0.0608023, -0.089713804, -0.10031175, -0.09828107, 0.2759653, 0.040628787, -0.014327023, -0.18901895, -0.19466661) * g_6;
    result += mat4(-0.077983975, 0.116868906, -0.23626202, 0.24141665, 0.18514152, 0.12009115, 0.024183134, -0.19578324, -0.2004096, 0.16053474, -0.12452011, -0.24160402, 0.044126388, -0.08934569, 0.26577887, 0.09816567) * g_7;
    result += mat4(0.10499274, 0.2265129, -0.078521736, 0.29265165, 0.0041190055, 0.36288932, -0.103490636, 0.05727936, -0.089100264, 0.04249254, 0.30703348, -0.024190163, 0.026818752, 0.21627031, 0.1413635, 0.5749679) * g_8;
    result += mat4(-0.11887336, 0.27841938, 0.18154635, -0.30292216, -0.14453453, -0.32330868, -0.06806779, -0.13335946, 0.12325082, -0.2776033, -0.2176617, -0.14796872, 0.14378121, -0.1515707, -0.19313759, -0.03666135) * g_9;
    result += mat4(-0.16793656, 0.14827895, 0.31085837, 0.039777525, 0.049468413, -0.19864005, -0.11719598, 0.16815868, -0.02205864, -0.20461129, -0.15883179, 0.026992796, -0.2750394, 0.20748213, 0.24951674, -0.06626439) * g_10;
    result += mat4(-0.22174093, -0.20898962, -0.03558482, 0.23259541, 0.12385461, 0.11644065, 0.13360718, -0.298495, 0.05759325, -0.06470147, -0.1467882, -0.1233936, 0.124703325, -0.004894744, -0.44175613, 0.30384606) * g_11;
    result += mat4(-0.22360735, 0.13903587, 0.123154536, 0.22120447, 0.07635435, -0.08578538, -0.0070886854, -0.16854721, 0.2935059, 0.014837484, 0.011378183, 0.11189771, 0.15975478, 0.1525562, 0.17962816, -0.30664667) * g_12;
    result += mat4(-0.13563982, -0.11331227, -0.35234228, 0.17117529, 0.09372269, -0.018378476, -0.060744487, 0.066920675, -0.12684692, -0.15846166, 0.040910132, 0.15608624, -0.0839549, 0.06397846, -0.11739037, -0.24138166) * g_13;
    result += mat4(-0.3350538, -0.24931656, -0.13913944, -0.078073435, 0.12782471, -0.033278856, 0.22328287, -0.0494411, -0.16591735, -0.03392308, 0.1588464, -0.19808592, 0.19063896, -0.16003527, 0.21511821, 0.10613058) * g_14;
    result += mat4(-0.060294464, -0.09252907, -0.01603874, -0.07597569, 0.03133959, 0.072272286, -0.13213353, 0.15609686, 0.2167412, 0.06884895, -0.2590782, 0.33470517, 0.003332907, 0.03748415, -0.25728425, -0.30776468) * g_15;
    result += vec4(0.0085292775, -0.0498912, 0.02406236, 0.013927507);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf2, gxy, result);
}