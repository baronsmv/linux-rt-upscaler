// Anime4K_Upscale_GAN_x4_UUL - Pass 25 of 84 - https://github.com/bloc97/Anime4K
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
// -----------------------------------------------------------------------------
//  Push constants (only in tile-mode shaders)
//    layout(push_constant) uniform TileParams {
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  inputLayer;      // array slice to read (0-based)
//        uint  margin;          // context margin (pixels in feature-map space)
//    } tile;
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

layout(push_constant) uniform TileParams {
    uvec2 dstOffset;
    uvec2 tileOutExtent;
    uvec2 fullOut;
    uint inputLayer;
    uint margin;
} tile;

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_6_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_6_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_6_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_8_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_9_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.069604576, 0.02780287, 0.10479145, 0.0598677, -0.15447794, 0.014002432, 0.15952754, -0.16364509, -0.17146967, 0.27360946, -0.06118358, 0.06562993, -0.0034575097, 0.27649418, 0.025365477, -0.081556045) * g_0;
    result += mat4(0.098523565, -0.014438212, -0.17889059, -0.08759605, -0.097737536, 0.27787977, 0.016156938, -0.11134956, 0.10582375, -0.20247018, 0.08988277, 0.17063816, -0.072689526, -0.1143116, 0.30750987, 0.09236675) * g_1;
    result += mat4(-0.28383443, -0.15268843, 0.42559057, 0.3357241, 0.012547255, -0.09958958, 0.04154182, -0.06517361, 0.08784381, 0.03416716, -0.036624804, -0.034195926, -0.009735854, -0.037226725, 0.044228237, 0.098523915) * g_2;
    result += mat4(0.13222544, 0.1690658, -0.10114831, 0.0418428, -0.03539878, 0.06732558, 0.044486526, 0.18264133, 0.09283543, -0.0875049, -0.27786124, 0.31696528, 0.13372223, 0.06539235, -0.07225442, -0.053972196) * g_3;
    result += mat4(0.10303975, -0.027461063, 0.12720948, 0.11982775, 0.010745893, -0.258443, -0.038602423, -0.031108906, 0.03577269, 0.06814439, -0.30761826, 0.18308763, 0.030638998, 0.00069125916, 0.041647576, -0.037805513) * g_4;
    result += mat4(0.28049946, -0.19036528, -0.20298155, -0.20855707, -0.012317928, 0.08052685, -0.2087141, 0.22641854, 0.10379512, -0.19354534, 0.038190875, -0.31573087, -0.08755006, 0.10582216, -0.103582926, -0.051279992) * g_5;
    result += mat4(-0.019805856, 0.32306147, -0.10066396, 0.1077401, -0.08169178, -0.20293216, 0.015578836, -0.030745748, 0.091820225, -0.13066763, 0.022633377, 0.011552452, -0.123327985, 0.25311312, 0.22652766, 0.011176362) * g_6;
    result += mat4(-0.16592886, -0.003341361, 0.05655243, -0.04907018, -0.14266169, -0.07653183, 0.39557743, -0.044829868, 0.035589613, -0.23692629, 0.02729001, 0.23751497, -0.074999005, 0.06162688, 0.06201382, 0.15069327) * g_7;
    result += mat4(-0.12884079, 0.037352398, -0.12884715, 0.15350881, -0.089926146, -0.1700947, -0.10188416, -0.029826047, -0.031419244, -0.15877514, 0.074799135, -0.123011, -0.007537871, -0.24274765, 0.10594629, -0.042308845) * g_8;
    result += mat4(0.028796997, 0.009780028, 0.08393684, 0.08876159, 0.2958322, 0.13797538, -0.23441544, -0.064725965, 0.13806176, -0.015037291, 0.060964797, -0.30482304, -0.041055765, -0.15156971, 0.20623018, 0.10922641) * g_9;
    result += mat4(-0.0057864957, -0.18726483, 0.037883427, 0.14638895, -0.10522743, 0.09113031, 0.11673609, -0.21051702, 0.028723987, -0.062990315, 0.002952929, 0.01469057, 0.034846026, 0.19609974, -0.1934369, -0.18243392) * g_10;
    result += mat4(0.118073694, 0.119863555, -0.30531943, -0.205375, -0.22113605, -0.28978834, -0.23192821, 0.28978485, -0.021390624, -0.18431179, -0.15690218, -0.14960553, -0.15185611, 0.0028554697, -0.02074978, 0.056506403) * g_11;
    result += mat4(0.31187654, -0.2761366, 0.020066198, 0.031995732, -0.1848675, 0.08065148, 0.14539121, -0.23896545, 0.0257927, -0.054032624, -0.07259492, 0.18765905, -0.17117564, -0.33104083, -0.0332479, 0.15349889) * g_12;
    result += mat4(-0.18720639, 0.19843848, 0.3385621, -0.19166066, 0.21356635, 0.21394755, 0.15651105, 0.037805296, -0.16349375, -0.13504027, 0.19122715, 0.120806016, 0.16379046, -0.0026540656, 0.04739934, -0.07981541) * g_13;
    result += mat4(-0.28539544, 0.21816348, -0.15019035, 0.23157135, 0.121298485, 0.2268759, -0.24653979, -0.025725443, -0.055981506, 0.10309359, 0.12415594, 0.010752708, 0.15175724, -0.12113609, -0.04674751, 0.1452768) * g_14;
    result += mat4(0.084147684, -0.32716796, -0.3735181, -0.06994641, -0.17994325, -0.14905843, -0.06946874, 0.35039115, -0.05100555, -0.08730691, -0.23854558, -0.1746263, -0.011508492, 0.10305763, 0.13472022, -0.28137568) * g_15;
    result += mat4(0.10937542, -0.038041312, -0.0995303, 0.14773457, 0.15991186, 0.22984092, -0.20170724, -0.3805271, 0.11831765, -0.07383792, 0.14768845, -0.311674, -0.019428516, 0.18180147, 0.056651186, -0.10447611) * g_16;
    result += mat4(0.04605112, 0.046965037, -0.08334886, 0.037097372, 0.18561974, 0.3021062, 0.1629304, -0.090214364, -0.005229353, 0.18200208, -0.07720685, 0.25807604, 0.2524869, -0.16809419, -0.4000575, -0.3306678) * g_17;
    result += mat4(0.09674466, 0.07551325, 0.016270272, -0.22326164, -0.1256328, -0.08318501, 0.24199782, 0.008043517, -0.3336808, -0.019305306, -0.18930039, 0.3224243, -0.020935204, -0.21364902, 0.029509636, -0.1468745) * g_18;
    result += mat4(-0.22094682, -0.27292994, -0.1963563, -0.37204334, 0.13046952, 0.2838346, -0.15947977, 0.07602889, -0.023213187, -0.06235404, -0.09553055, 0.03893353, 0.28796852, 0.09727489, 0.13416602, 0.34785405) * g_19;
    result += vec4(0.063622594, 0.0041231937, 0.015656473, -0.044245835);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf, ivec3(valid_xy, tile.inputLayer), result);
}