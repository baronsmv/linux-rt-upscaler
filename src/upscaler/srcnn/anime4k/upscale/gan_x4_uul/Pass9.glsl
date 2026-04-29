// Anime4K_Upscale_GAN_x4_UUL - Pass 9 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.11662476, 0.30973792, 0.21844758, 0.19193952, 0.10547289, -0.28103492, 0.153185, 0.22902022, 0.14545941, -0.36453786, 0.27674347, 0.082761206, 0.018604625, -0.15195464, -0.014881725, -0.3170343) * g_0;
    result += mat4(-0.09369265, 0.0030548668, 0.123169556, 0.29990658, 0.0059669684, -0.30507565, 0.22437601, 0.26314184, 0.055285115, 0.08910655, -0.07781467, 0.34908244, 0.12883523, -0.1218909, 0.46330363, -0.00058599625) * g_1;
    result += mat4(-0.13166216, -0.11733475, 0.3777369, -0.11452789, -0.012198889, 0.019259788, 0.19055355, 0.14045803, 0.2352836, 0.18440361, -0.119568326, 0.15006012, 0.12928642, 0.2181605, -0.1755796, -0.1481423) * g_2;
    result += mat4(0.20824851, 0.1454897, 0.016380647, 0.08601717, -0.0287675, -0.17842998, 0.24576826, 0.024758099, -0.06907304, -0.33883977, -0.18469703, -0.11530369, -0.13971063, 0.09056448, 0.10467011, 0.087848045) * g_3;
    result += mat4(0.47120807, -0.15463045, 0.03930625, 0.18975684, 0.17118797, 0.077672035, 0.029735595, -0.0064234287, 0.35503763, 0.23442392, 0.09259758, 0.06642276, 0.16423592, 0.16245009, 0.043012362, -0.16605885) * g_4;
    result += mat4(0.14847134, -0.41317105, 0.21329704, -0.115592465, -0.04099491, 0.22865698, -0.011546307, 0.124923006, 0.02029704, 0.014588208, -0.0032878371, 0.09777601, 0.27264157, 0.26693115, -0.083503485, -0.11275104) * g_5;
    result += mat4(0.0073214495, -0.30733636, -0.28372166, -0.23081271, -0.24020568, 0.17335413, -0.08835816, -0.1407258, 0.043210473, 0.29907116, -0.15998003, -0.10616064, -0.19272846, 0.07347569, 0.065403186, 0.21924807) * g_6;
    result += mat4(0.1390639, 0.07071387, -0.10704547, -0.22267987, 0.14110383, 0.31690794, -0.14299001, -0.2633626, -0.37578335, -0.11325702, -0.012588563, 0.05235386, -0.05790653, 0.29747054, -0.11362069, -0.034965772) * g_7;
    result += mat4(0.334025, 0.06966542, -0.30425888, -0.049219113, 0.05522049, -0.064109504, -0.19639532, -0.06540687, -0.3323081, -0.11462512, 0.12793858, -0.044268914, -0.13001205, -0.4268851, 0.09755515, 0.22260398) * g_8;
    result += mat4(-0.070916615, -0.032426283, -0.031039508, 0.113172114, -0.083208784, 0.09998266, -0.057585325, -0.017305639, 0.07392591, 0.11129369, -0.12461519, -0.13633083, 0.11811745, -0.049483757, -0.16540588, -0.19690844) * g_9;
    result += mat4(-0.0761509, 0.06887501, -0.17220098, -0.2689129, -0.15664133, 0.014503109, 0.013423933, 0.07106888, 0.08206795, -0.26531503, -0.19532347, -0.09172804, -0.0701496, 0.029842263, -0.15747191, 0.03876475) * g_10;
    result += mat4(0.05873964, 0.21549611, -0.15765984, 0.11783242, 0.09904579, -0.1505368, 0.009470319, 0.11437343, 0.07330138, -0.12074719, 0.046029083, 0.07719378, -0.14860357, 0.012415384, -0.15716434, 0.096243195) * g_11;
    result += mat4(0.38489017, 0.10751408, 0.28326878, 0.10983613, -0.08363852, 0.060594987, -0.1407845, -0.2330205, -0.0033884577, -0.025575818, -0.21328409, -0.013343768, 0.37102774, -0.018506272, 0.15474491, 0.20658477) * g_12;
    result += mat4(-0.21097998, 0.11116577, 0.0066421195, -0.053172227, 0.041547738, -0.115422554, 0.18638755, 0.15930174, -0.11901881, -0.14221598, 0.113654196, -0.035343777, 0.0037377405, 0.0054536746, -0.16508429, -0.112160645) * g_13;
    result += mat4(-0.168217, 0.33982185, -0.14226285, -0.061567828, 0.38622376, 0.16323963, 0.009866034, 0.24718387, 0.15684012, 0.16934262, -0.07659216, -0.27921352, 0.31008887, -0.117847964, 0.033022024, -0.0028089648) * g_14;
    result += mat4(0.13425586, -0.1403824, -0.14900951, 0.044306386, -0.39742225, -0.086779915, 0.023442117, -0.015157307, -0.33325103, 0.07626949, -0.14105129, 0.3872729, -0.09532729, 0.21603268, 0.08987563, -0.048167326) * g_15;
    result += vec4(-0.045520097, -0.028044129, 0.01954312, -0.04157413);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf, gxy, result);
}