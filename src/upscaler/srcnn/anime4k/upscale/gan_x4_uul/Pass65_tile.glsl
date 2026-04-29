// Anime4K_Upscale_GAN_x4_UUL - Pass 65 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_21_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_21_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_21_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_21_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_21_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_21_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_23_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 1038) uniform texture2DArray tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_24_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_21_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_21_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_21_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_21_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_21_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_21_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_23_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_23_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_24 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_25 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_26 (max((texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_28 (max((texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_29 (max(-(texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.10701419, -0.19440664, -0.13657895, -0.117495134, 0.11351926, -0.08210127, 0.0051790676, 0.22163984, -0.12849367, -0.118760884, 0.028440215, 0.06271742, -0.05561763, -0.16148782, -0.052592654, -0.22535303) * g_0;
    result += mat4(-0.123711504, -0.14676294, -0.115391895, 0.080983736, -0.017832119, -0.063273184, 0.059941225, -0.049034536, -0.052219674, 0.036749475, -0.29203734, -0.02856495, 0.22648478, 0.015175415, 0.21293166, -0.20832887) * g_1;
    result += mat4(-0.081328556, 0.07598546, -0.13756523, -0.06107587, 0.25113305, -0.11791683, 0.113452606, -0.0078082574, -0.07442993, -0.2974806, -0.056567345, -0.21749294, 0.013611423, -0.032841083, -0.076977916, 0.19821857) * g_2;
    result += mat4(0.10560456, 0.015013695, 0.13627833, 0.032404233, -0.02131817, -0.14500482, 0.120675825, 0.031823736, 0.11649639, 0.082596324, 0.08127175, -0.026048733, -0.012239797, 0.08369006, 0.1273803, 0.12210886) * g_3;
    result += mat4(-0.0892015, 0.07059692, 0.069719285, -0.061874084, 0.044701215, 0.09245424, -0.022817707, -0.02148644, 0.18068357, -0.11995518, 0.24286029, -0.045054384, 0.07323844, 0.06554761, -0.16207513, 0.07595062) * g_4;
    result += mat4(0.18337601, 0.07568856, -0.09610938, -0.06572019, -0.23225725, -0.045913246, -0.16005549, 0.10841484, -0.047294065, -0.0044971597, -0.11600348, -0.0985696, 0.01994268, 0.009345386, -0.12112187, -0.07728449) * g_5;
    result += mat4(-0.02642385, 0.12577803, 0.18099304, 0.09237617, -0.14517787, 0.015473747, 0.01148567, -0.1976294, 0.13244452, 0.026473833, -0.04026099, -0.08005897, 0.09972515, 0.014148667, 0.17150447, 0.07458103) * g_6;
    result += mat4(0.103025176, -0.14280592, 0.011362381, -0.002615672, -0.0019504991, -0.1244238, -0.176323, -0.0409311, -0.13593708, 0.09121169, 0.16169107, 0.064790055, -0.17050834, 0.004790829, -0.20973155, 0.040783066) * g_7;
    result += mat4(-0.08482106, -0.06313967, 0.053659916, -0.045122232, -0.173445, -0.10196347, -0.21512675, 0.030526979, -0.04609878, 0.02864437, -0.13620801, -0.05330683, 0.10560492, -0.086872876, 0.2332013, -0.11290048) * g_8;
    result += mat4(-0.12032245, 0.083415076, 0.013942395, 0.12558693, -0.09643306, -0.08665224, -0.08364215, -0.15714419, -0.012963433, -0.018926837, 0.17045903, -0.03450577, 0.05467565, 0.1176962, -0.029627452, -0.17721933) * g_9;
    result += mat4(0.06413174, 0.07644954, 0.015619154, 0.0406442, -0.09510097, 0.082857184, 0.07081759, -0.06094168, -0.10623127, 0.11465217, -0.21940763, 0.06440103, -0.14007917, -0.20644121, 0.062006976, -0.21401502) * g_10;
    result += mat4(-0.090416506, -0.118475, 0.14939576, -0.01684449, 0.14943695, 0.03052435, 0.080091365, -0.0773867, 0.12932321, 0.12060135, 0.14845312, 0.04718311, 0.13032377, -0.16439119, 0.048975646, -0.118689515) * g_11;
    result += mat4(-0.14264718, -0.20367233, -0.10508499, 0.014003226, 0.122711256, 0.12533264, -0.20902152, -0.08875033, -0.13099793, -0.022472287, 0.17604207, -0.13671063, -0.040429622, 0.6475939, -0.017244961, -0.23879616) * g_12;
    result += mat4(0.1600574, -0.18023758, 0.1184686, 0.1348991, 0.037446063, -0.011027512, 0.17671643, -0.199355, 0.2725076, -0.20256595, -0.099972546, 0.23075041, -0.18912004, -0.008967372, 0.040337812, 0.0011864579) * g_13;
    result += mat4(-0.0153634995, 0.02991675, -0.07471954, 0.025803613, -0.18960874, -0.23163852, -0.010988217, 0.22258236, 0.45717034, -0.041301187, 0.059016965, -0.1418097, -0.42032385, -0.009557171, 0.18662642, -0.11312428) * g_14;
    result += mat4(-0.043423057, 0.18310834, 0.2572519, 0.1374164, 0.1505133, 0.18733694, -0.23037662, -0.10971462, -0.32504216, 0.15508054, 0.15461947, -0.3731339, 0.58277595, -0.2969173, 0.084127784, 0.054632857) * g_15;
    result += mat4(-0.18833053, 0.3626468, -0.10378585, -0.18636744, -0.07215689, -0.0340568, -0.2014818, 0.39376506, 0.092539184, 0.019427503, 0.08621937, -0.029048063, 0.04170551, 0.03303338, 0.12886372, 0.22093524) * g_16;
    result += mat4(0.13748164, -0.10530546, -0.059407894, 0.24885765, 0.25748453, -0.2322867, -0.047119506, 0.18135284, -0.12410837, 0.10820877, -0.076054335, 0.14305715, 0.07893051, 0.025212046, -0.06861065, -0.14078265) * g_17;
    result += mat4(0.12955414, 0.10334285, -0.1339673, -0.07533481, -0.09940921, 0.07574928, -0.029290935, -0.0074044047, -0.047509745, 0.12616187, 0.15918884, 0.22636813, 0.0627, 0.13627514, -0.11840879, 0.25489545) * g_18;
    result += mat4(0.12401844, 0.018437453, 0.14081988, 0.20443875, 0.22617432, -0.23241785, 0.019566217, -0.1470485, 0.06928665, -0.012560286, -0.11640072, -0.09635026, 0.19372395, -0.18137501, 0.095964, -0.36745393) * g_19;
    result += mat4(-0.07812969, -0.13952559, -0.08575349, 0.1270944, -0.012434522, 0.09118943, -0.1844579, 0.057183933, 0.17054899, 0.055602986, 0.020217096, -0.17830917, 0.033711255, -0.040958434, -0.0656027, 0.08316588) * g_20;
    result += mat4(0.008265117, -0.0440992, 0.18142514, -0.11072275, -0.035788976, 0.0045379996, 0.10519265, -0.0025924263, 0.1416068, -0.0076917615, -0.107548796, 0.14070505, 0.048619375, -0.08055219, 0.15124267, -0.14900993) * g_21;
    result += mat4(0.023191221, -0.088463016, -0.03773182, 0.09279135, 0.030037321, -0.047114536, 0.0411644, 0.117513955, 0.02564984, 0.3634533, -0.07842253, 0.03945798, -0.09705065, -0.00073423475, -0.116537966, 0.09805546) * g_22;
    result += mat4(0.16699894, 0.06968313, -0.025299484, 0.057924386, -0.13151881, -0.14149357, 0.019038316, -0.27727044, 0.02826252, -0.049611922, 0.19707511, 0.08938078, 0.107304506, -0.06147075, -0.021948906, 0.03686705) * g_23;
    result += mat4(-0.012881243, -0.094086275, 0.23042965, -0.044305936, 0.07882307, 0.04138532, -0.04374878, -0.028959524, -0.014689813, -0.04448379, 0.033379626, -0.010935875, 0.049693886, -0.012109875, -0.07495743, 0.07254774) * g_24;
    result += mat4(0.1349909, 0.113079466, -0.17218146, -0.082038075, -0.041794095, -0.12584618, 0.012202269, -0.07666811, 0.016668953, 0.16685286, 0.062669456, -0.02282906, 0.08557955, -0.07436991, 0.108987726, -0.02062727) * g_25;
    result += mat4(0.0975699, -0.042854395, -0.27839357, -0.02017465, 0.07523807, 0.06038207, 0.19882318, -0.042623498, -0.1643381, -0.06454315, 0.12813903, 0.018587556, -0.07143471, -0.055071846, 0.007254701, 0.08625719) * g_26;
    result += mat4(0.0040934216, 0.21434385, 0.15655868, 0.17250434, -0.0183287, 0.05514319, -0.19112857, -0.07169756, 0.37303272, -0.03185245, -0.052846085, -0.033713702, 0.057584986, 0.06311142, -0.20161806, 0.013350911) * g_27;
    result += mat4(-0.12516226, 0.13068974, -0.00090003706, -0.27179503, 0.11163459, -0.018370617, -0.077084556, -0.37971583, 0.10331944, -0.077023275, -0.07891338, -0.012240651, -0.25734505, -0.061364602, 0.13029832, 0.23223366) * g_28;
    result += mat4(0.16159123, -0.09218027, 0.054632008, 0.115622655, 0.027251892, 0.047268346, 0.11801297, 0.08485814, -0.29647812, 0.119895175, 0.19110309, 0.1580456, 0.16836183, -0.09640805, -0.14934723, -0.16124077) * g_29;
    result += vec4(-0.009459555, 0.08955687, 0.06774535, 0.11750715);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf, ivec3(valid_xy, tile.inputLayer), result);
}