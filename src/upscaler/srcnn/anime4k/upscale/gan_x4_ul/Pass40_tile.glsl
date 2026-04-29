// Anime4K_Upscale_GAN_x4_UL - Pass 40 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_15_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_15_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_15_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_15_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_17_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_18_tf3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.0752077, -0.0029171302, -0.27563673, -0.014811605, 0.02846672, 0.032712437, 0.23822306, -0.05769253, -0.15474099, 0.093151525, 0.06375694, -0.13745429, -0.04572417, 0.3199813, -0.022760388, 0.16357492) * g_0;
    result += mat4(0.02650099, 0.0128598865, -0.13053481, 0.037058145, -0.055677533, -0.079210766, -0.03356954, 0.1069868, -0.07710097, 0.12506554, -0.13472609, -0.026160635, 0.1821316, 0.052085042, -0.19033344, -0.090145096) * g_1;
    result += mat4(-0.03734377, 0.07147657, 0.10820697, -0.024222745, 0.1403612, -0.1505265, -0.17980108, 0.26694953, 0.0217602, 0.037542872, -0.08249127, 0.042201407, 0.2006786, -0.059707034, 0.03880093, -0.1826765) * g_2;
    result += mat4(-0.11878983, -0.28029415, -0.04900442, -0.13629057, -0.05066402, -0.05337549, 0.07343749, -0.1209636, 0.16849558, -0.106414795, 0.05464871, 0.17617467, -0.2489627, 0.29946232, -0.123174965, 0.056576844) * g_3;
    result += mat4(-0.17408213, 0.09776442, 0.057589754, 0.18333124, -0.09720728, 0.16222644, -0.005483807, 0.15910664, 0.30478597, 0.014245162, -0.31090343, 0.06744939, 0.019972727, -0.113528624, 0.10990966, -0.10937443) * g_4;
    result += mat4(0.12755792, 0.16373649, 0.019118445, 0.21310984, -0.10995382, -0.08398977, 0.0009497389, -0.12245982, -0.25080305, 0.26576582, 0.073143534, 0.09062886, 0.3211899, -0.012361862, -0.094413824, 0.016505178) * g_5;
    result += mat4(0.04496885, 0.057987563, -0.06828201, -0.25538024, -0.25729346, 0.1581948, -0.08318907, -0.26187086, -0.06994225, -0.0108814975, 0.27547085, 0.19735947, -0.25765172, 0.23375468, -0.02491318, 0.19695699) * g_6;
    result += mat4(-0.18447195, 0.3949247, 0.23520981, 0.16501734, 0.014326944, -0.21483032, -0.09887618, -0.1530724, 0.087982565, -0.30155778, -0.09407708, -0.07609285, 0.12439066, -0.046371937, -0.10052105, 0.042462338) * g_7;
    result += mat4(0.45384184, 0.23962094, -0.09288032, 0.43883595, 0.017768994, -0.28214878, -0.30303338, 0.06788283, 0.23333043, 0.012060692, 0.08277374, 0.18042035, 0.18759233, -0.009545223, -0.027723255, 0.016402755) * g_8;
    result += mat4(-0.3158644, -0.1611719, -0.044279657, -0.03122654, 0.20287034, 0.19071461, -0.032826696, -0.25104183, 0.03608647, -0.027464861, 0.118140586, -0.016250696, -0.2791853, -0.15649952, -0.17356332, -0.0036406678) * g_9;
    result += mat4(0.037999913, 0.0075079957, -0.03212704, 0.06418637, -0.069481015, 0.012727689, 0.1326516, 0.21288529, -0.24180269, -0.05297486, -0.06864697, -0.1550755, -0.11256537, 0.34002435, -0.08510081, 0.18888487) * g_10;
    result += mat4(-0.16029695, -0.04566749, -0.14091927, 0.13358699, -0.10535976, 0.0039140307, -0.023005482, -0.011232076, 0.3731448, -0.08050772, 0.24036883, 0.003388208, 0.2694246, -0.10064168, -0.09378355, 0.08715414) * g_11;
    result += mat4(-0.009987239, -0.16815887, 0.079718135, 0.3046235, 0.08460679, 0.010675847, 0.026123201, 0.042994894, 0.14086412, 0.16343307, 0.030049993, -0.13560392, -0.028959347, -0.051606726, 0.20051792, 0.2660683) * g_12;
    result += mat4(-0.041822806, -0.059724808, 0.03475158, -0.21370164, 0.2706948, 0.029740596, -0.045692813, -0.18892711, -0.072185665, -0.033861183, -0.1753473, -0.15868294, -0.04698167, -0.15849903, -0.10530276, 0.09699679) * g_13;
    result += mat4(-0.14366704, 0.0054797325, 0.019186102, 0.2016934, -0.12337197, 0.03666924, -0.08487317, -0.02910447, 0.19810423, 0.19303478, -0.12032341, 0.012882501, 0.07518216, -0.16929416, 0.11856349, 0.19008183) * g_14;
    result += mat4(0.29109573, -0.2495297, -0.23351379, 0.06592844, 0.22335382, -0.12432068, 0.23873796, 0.03394475, -0.111712426, -0.031314444, 0.042552706, 0.26120943, -0.100280665, 0.33024225, 0.00090209645, 0.08790097) * g_15;
    result += mat4(0.19417305, 0.019389676, -0.0022192579, -0.10152884, -0.07527296, 0.09672377, 0.1896058, -0.08312996, -0.098250404, -0.005925583, -0.080828406, -0.04157932, -0.2395506, -0.2046314, -0.18201615, -0.23270196) * g_16;
    result += mat4(-0.14487964, -0.06290274, 0.041151002, 0.069312826, -0.036889106, -0.026325129, -0.06404841, -0.070130795, 0.19873784, 0.008724542, 0.33345434, -0.12738648, 0.010419843, 0.0016074138, 0.028482364, -0.05086976) * g_17;
    result += mat4(-0.2099938, 0.22374807, 0.0014840614, -0.09744533, -0.36373836, 0.070096895, 0.18809755, 0.055123232, -0.12190152, -0.089326, 0.037977137, -0.2779433, -0.0022680282, 0.1324952, 0.19014698, 0.11292094) * g_18;
    result += mat4(0.0045333416, -0.27289414, -0.10013291, 0.03997672, 0.18506177, 0.15360181, 0.0620571, 0.18008661, 0.03184327, -0.047722574, 0.21967985, 0.12443793, 0.11032391, 0.016790923, -0.32427138, 0.11624099) * g_19;
    result += mat4(0.098094285, -0.017424708, -0.13152607, -0.14184679, -0.2696629, 0.026611622, 0.4969703, -0.23566079, 0.18346384, 0.17655236, 0.046510983, 0.20738232, -0.08645157, 0.25616655, 0.1875624, 0.22396664) * g_20;
    result += mat4(-0.049922127, -0.026013017, 0.17512889, 0.18352829, 0.22210887, 0.008942828, 0.004796096, -0.08654042, 0.0025269054, -0.1767342, -0.05939487, -0.27815545, -0.058232002, -0.033121955, 0.14671248, 0.24188647) * g_21;
    result += vec4(0.0011495166, -0.055540904, 0.0047202418, 0.03799147);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf3, ivec3(valid_xy, tile.inputLayer), result);
}