// Anime4K_Upscale_GAN_x4_UUL - Pass 34 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_9_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_9_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_9_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_9_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_9_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_9_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_9_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_9_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_9_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_9_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.27487782, 0.18671569, 0.014598359, -0.10942123, 0.06431285, 0.13095526, 0.16187827, -0.05404472, 0.06109171, 0.12339281, 0.037517212, 0.022657571, 0.057030313, -0.008228847, -0.072607644, 0.03075785) * g_0;
    result += mat4(-0.11736518, 0.19170946, 0.38883322, -0.04370131, 0.08346483, 0.10550525, 0.07936755, 0.028102577, 0.01148332, -0.11665535, 0.06383731, -0.14827923, 0.11657963, 0.077285066, -0.0977731, -0.061747603) * g_1;
    result += mat4(0.24491212, 0.058865275, -0.25556007, -0.041585945, 0.3193469, -0.05451695, -0.001404186, -0.13020252, 0.07431936, 0.2289785, -0.10098844, 0.023408994, -0.23390095, 0.22575194, -0.025926162, -0.021137672) * g_2;
    result += mat4(-0.34047288, -0.16864823, -0.091643326, 0.12608078, -0.06984128, 0.27387246, 0.05079481, -0.08338553, 0.2120012, 0.14819127, -0.033582117, -0.24173228, 0.047510203, -0.1803568, 0.053134385, 0.087940834) * g_3;
    result += mat4(0.02928209, 0.22820388, -0.4671619, -0.031732026, -0.057300556, 0.004144317, 0.10569882, -0.020268245, -0.3543468, -0.13405709, -0.08611896, 0.18175112, -0.120712005, 0.14141698, 0.20102608, 0.23618817) * g_4;
    result += mat4(0.066653736, -0.059595298, 0.15454593, 0.21592279, 0.27390355, -0.11746084, -0.049416482, -0.29596555, -0.054056685, 0.124672204, 0.057716236, 0.10225304, -0.09174892, 0.19980122, -0.05336024, 0.055571303) * g_5;
    result += mat4(-0.18484752, -0.36230278, 0.049307425, 0.12563172, -0.024801265, -0.022736475, -0.11068124, 0.2804873, 0.12878488, 0.13737386, -0.3159429, 0.14334643, 0.30960616, 0.19170786, -0.19692647, 0.3274579) * g_6;
    result += mat4(0.0033271008, 0.01712824, -0.14945795, 0.15134253, 0.072035566, 0.063491106, -0.040498145, -0.27111852, 0.09643232, -0.21030812, 0.02619506, -0.006282209, -0.043037314, -0.24948022, -0.0960549, 0.08886981) * g_7;
    result += mat4(-0.1683291, 0.004775721, 0.19721816, -0.0016262251, 0.04053106, 0.019257752, -0.036447894, -0.016047643, 0.18024184, -0.010098442, 0.060056653, 0.21040897, 0.06810947, 0.16518652, 0.10927958, 0.015990514) * g_8;
    result += mat4(0.17782916, -0.019990172, -0.04214169, -0.044349745, -0.096376285, -0.17118435, -0.0046379915, -0.33545214, 0.27945635, -0.08301872, 0.20809698, -0.2167783, -0.2896225, 0.25324273, -0.1393815, -0.1035578) * g_9;
    result += mat4(-0.11153186, 0.08945358, -0.19106413, -0.070531435, 0.20065232, 0.22111228, 0.31270432, 0.029758435, -0.06838312, 0.124104455, 0.016042404, -0.15672235, 0.25810337, -0.14822677, 0.056693383, -0.102702715) * g_10;
    result += mat4(-0.5346728, -0.010835411, -0.19025792, 0.20262082, -0.2937675, 0.0636634, 0.051419638, 0.3031389, -0.024283586, 0.114449784, -0.06731985, 0.033319853, -0.18419428, -0.05939938, -0.004707921, 0.06668735) * g_11;
    result += mat4(0.037002433, -0.093464166, -0.09644219, -0.07630172, 0.051610224, -0.13968097, 0.24660867, -0.07587348, 0.040383674, -0.16485368, 0.020389866, 0.20876431, -0.27873826, -0.112587206, -0.072660305, -0.04472093) * g_12;
    result += mat4(-0.06779488, 0.16197906, 0.06188925, -0.008886099, 0.24061024, -0.05935547, -0.005190499, 0.038443245, 0.09116801, -0.079416126, -0.07764381, -0.24856304, 0.32130104, -0.1689679, 0.2610274, -0.19916224) * g_13;
    result += mat4(0.084091805, -0.009050908, 0.0428426, -0.22958456, 0.09502613, -0.079103395, -0.0072180657, 0.07783402, -0.08293811, -0.03740794, -0.2847399, 0.06101355, -0.025973216, 0.0043736286, -0.09274589, -0.03786617) * g_14;
    result += mat4(-0.054818746, -0.058793657, 0.16997126, 0.08030429, 0.06598645, -0.11494638, -0.13028891, -0.05864371, -0.035407092, -0.10433668, -0.18799901, 0.0070647947, 0.12834336, -0.07709033, 0.07298517, -0.052353203) * g_15;
    result += mat4(-0.022882696, -0.0670688, -0.14851306, -0.06401987, 0.078636736, 0.51110995, 0.024791796, -0.061570935, -0.115464, 0.04116418, 0.054929867, 0.01905232, 0.06346473, 0.22244757, 0.19133015, -0.10632591) * g_16;
    result += mat4(0.08766506, 0.0026022529, 0.14686164, 0.080684945, 0.44264203, 0.34035525, 0.071974285, -0.09354271, 0.045810618, 0.03615794, -0.23397596, -0.052015793, 0.046337537, -0.14722544, 0.16304798, 0.122426964) * g_17;
    result += mat4(0.1585944, 0.16835997, -0.39288864, -0.11356811, -0.368774, -0.01703612, -0.29590556, 0.0009732469, 0.05849885, 0.19281316, -0.18295161, 0.052255064, 0.16215171, 0.15769695, -0.07581377, 0.29655725) * g_18;
    result += mat4(-0.2632724, -0.043094896, 0.23100272, -0.15726788, 0.31514347, -0.016838718, 0.07559306, -0.09395952, 0.2679746, -0.0211063, -0.042562332, 0.12023959, -0.22845441, -0.04967498, -0.1734489, -0.021029461) * g_19;
    result += mat4(-0.12129031, -0.24458979, 0.05676389, 0.44583562, -0.38308915, -0.08873493, 0.09653457, -0.017415477, 0.16643335, 0.049770217, -0.026928242, 0.032578394, 0.10163162, -0.06586171, -0.03279269, 0.0011147729) * g_20;
    result += mat4(-0.021562686, 0.13768315, 0.014967394, 0.12019759, 0.21548302, -0.053921327, 0.21206903, -0.09338285, 0.26822838, -0.16232637, -0.032934565, -0.25873, -0.033419203, -0.16388978, -0.3022585, 0.19349702) * g_21;
    result += vec4(-0.029419709, -0.051388465, 0.032251272, 0.006132939);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf1, ivec3(valid_xy, tile.inputLayer), result);
}