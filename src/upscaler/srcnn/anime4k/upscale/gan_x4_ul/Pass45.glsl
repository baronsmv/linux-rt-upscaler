// Anime4K_Upscale_GAN_x4_UL - Pass 45 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_21_tf2;
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
vec4 result = mat4(-0.16376013, -0.21462978, -0.14271215, -0.19764555, 0.004959633, 0.03559098, -0.039930187, 0.12408578, 0.073444515, -0.18976516, -0.020428572, 0.08624831, -0.13308355, 0.056589432, 0.06721722, 0.16169119) * g_0;
    result += mat4(0.032759428, 0.03249251, -0.20465967, 0.07133733, 0.05343703, 0.12841259, -0.20835468, 0.09137038, 0.1938841, 0.25623104, 0.097277, 0.058534052, -0.22656159, 0.18883473, 0.011212467, -0.0037018447) * g_1;
    result += mat4(-0.23469727, 0.15565057, 0.19072291, -0.1836996, 0.16059339, -0.22498783, 0.061382726, -0.20989716, 0.1775421, -0.047837425, -0.09572263, 0.103703596, -0.13672648, -0.15082708, 0.11233271, 0.22601321) * g_2;
    result += mat4(0.01870386, 0.089724526, 0.09773838, 0.034003545, -0.0031496854, 0.033871237, -0.24420398, 0.007905355, -0.02449313, 0.14813906, 0.09018556, 0.12513392, 0.16733788, 0.23793064, -0.1912762, -0.13565488) * g_3;
    result += mat4(0.06970355, 0.10157562, 0.14928305, 0.24936941, 0.059907116, -0.30688918, 0.081315145, -0.10862118, 0.13362534, -0.00026153796, 0.24190883, -0.06487983, 0.09340848, 0.08127848, 0.001434232, 0.067308724) * g_4;
    result += mat4(-0.05588173, -0.08792639, 0.08981383, -0.13087386, -0.1401108, 0.053842388, -0.014714017, -0.16106959, -0.09377347, 0.020844752, 0.08686229, -0.046952497, 0.31264535, 0.03484944, -0.08730081, -0.006767603) * g_5;
    result += mat4(0.25659466, 0.07397599, -0.059985436, 0.071429655, 0.03428176, -0.033710003, -0.16406639, -0.05580733, -0.21191816, -0.15564337, -0.07574189, -0.17225428, -0.019659676, -0.13260631, 0.05916013, -0.12107973) * g_6;
    result += mat4(-0.072627656, -0.080296986, 0.034525134, -0.23515461, -0.1304861, -0.039075147, 0.3999017, -0.22840585, 0.07141298, 0.18324336, 0.054969292, -0.01635769, 0.2520213, -0.07695982, -0.023417236, 0.102722354) * g_7;
    result += mat4(-0.17125753, 0.17100827, -0.31199583, -0.037970837, -0.107630424, -0.07300846, 0.07948616, -0.39042896, 0.17479163, 0.13205178, 0.11497303, -0.11652115, 0.03062989, 0.33838132, 0.14790033, 0.09507217) * g_8;
    result += mat4(0.04507488, 0.35392353, 0.38684472, 0.13546394, 0.11795181, -0.19300266, -0.22795731, 0.463773, -0.12761338, -0.18098523, -0.1456463, -0.09372001, 0.28942215, 0.14363319, -0.03819802, -0.15229422) * g_9;
    result += mat4(-0.12988025, 0.21170932, 0.03447564, -0.13754961, 0.087904826, 0.07837626, 0.09328843, 0.010177785, -0.3745973, 0.12749651, 0.17956547, -0.12897313, 0.19329022, -0.16939743, -0.104944855, -0.09487357) * g_10;
    result += mat4(0.15901774, 0.04067448, -0.21514527, -0.077920794, -0.28198823, 0.028896367, -0.23865238, -0.0071926992, 0.28216872, -0.13635647, -0.18908545, 0.02977451, -0.25345692, 0.20820476, 0.009601449, 0.27883843) * g_11;
    result += mat4(-0.037589654, -0.36836734, -0.17160638, -0.21136808, -0.18195882, -0.18352132, -0.13808772, 0.08068677, -0.015797919, -0.19405758, 0.16463257, -0.10353348, -0.0113609, -0.14714903, -0.15443285, 0.04489155) * g_12;
    result += mat4(-0.21718445, 0.0059077847, 0.19859529, 0.13535082, -0.16072561, 0.19556482, 0.1523886, 0.1251762, -0.0034070462, -0.035521794, 0.034417186, -0.306561, -0.10835829, -0.07181185, 0.036284324, -0.0031866753) * g_13;
    result += mat4(-0.10943835, 0.10428341, -0.06992764, -0.120998256, -0.008993865, 0.05821091, 0.06261459, -0.06388792, -0.028256107, 0.003925002, 0.25350967, -0.13623622, 0.084879614, 0.19291006, 0.06272194, -0.22010769) * g_14;
    result += mat4(-0.0457065, -0.059411805, -0.17807458, 0.09876963, 0.024583695, -0.116159014, -0.105639346, 0.028582737, 0.08507421, -0.121634774, 0.15567276, -0.08701447, 0.035207976, -0.037749242, -0.11775162, 0.25025365) * g_15;
    result += mat4(0.18185188, -0.07264863, 0.077263445, 0.21976566, 0.14656045, 0.047771394, 0.06685994, -0.08333337, 0.0017449517, -0.16983587, 0.14909369, -0.13025558, -0.06653938, -0.01429911, 0.032135215, 0.25310838) * g_16;
    result += mat4(0.042382054, 0.2682427, 0.01764835, -0.14447007, -0.2280379, 0.045982208, 0.075665936, -0.010963417, 0.07917052, 0.20231707, -0.022708723, -0.04420749, -0.017431455, -0.4536474, 0.050049998, -0.10083379) * g_17;
    result += mat4(0.042559944, 0.08244448, 0.20654662, -0.18008594, -0.1978152, 0.089204244, 0.09919466, 0.081702396, -0.030112466, -0.28072456, 0.20105025, -0.081957966, 0.048123248, -0.024997404, 0.07762149, 0.067282006) * g_18;
    result += mat4(0.077762015, -0.0710356, 0.06286203, 0.090047225, 0.1062697, -0.033291563, -0.032123826, 0.031537674, 0.15810831, 0.0884716, -0.12753096, 0.017839061, 0.42752337, -0.09349916, -0.06481517, -0.07046963) * g_19;
    result += mat4(-0.15118897, -0.25734478, 0.31358278, 0.1805141, 0.17088307, 0.18794382, 0.28021103, -0.34057355, -0.030835107, -0.0079853125, -0.26573807, -0.28082734, 0.0044963094, -0.020050643, 0.11479064, -0.11732869) * g_20;
    result += mat4(0.30385575, 0.25909582, -0.052579727, 0.1515613, -0.082644455, -0.09668368, -0.077442855, 0.095288195, 0.004760802, 0.07587048, 0.05381485, 0.10933668, -0.25176695, 0.14999786, -0.02548245, 0.12480703) * g_21;
    result += mat4(-0.12200806, -0.03346429, 0.040096015, -0.0104450155, -0.04190287, 0.15631595, 0.24532063, 0.067783296, -0.044785816, -0.17835703, 0.07349294, -0.23587738, 0.28926384, 0.020304382, -0.19058007, -0.24528348) * g_22;
    result += mat4(0.14653356, -0.09399811, 0.17405438, 0.11741997, 0.1707656, 0.17793506, 0.419244, 0.36248252, 0.19333729, -0.09478834, -0.031501323, 0.3489942, 0.17111845, -0.05753778, -0.033362497, -0.20234007) * g_23;
    result += vec4(-0.098978624, -0.013715648, -0.067908, -0.00071062305);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf2, gxy, result);
}