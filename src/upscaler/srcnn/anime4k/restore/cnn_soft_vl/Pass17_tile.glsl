// Anime4K_Restore_CNN_Soft_VL - Pass 17 of 17 - https://github.com/bloc97/Anime4K
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
//        uint  inputLayer;      // array slice to read (0-based)
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  margin;          // context margin (pixels in feature-map space)
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(push_constant) uniform TileParams {
    uint inputLayer;
    uvec2 dstOffset;
    uint fullOutWidth;
    uint fullOutHeight;
    uint margin;
    uvec2 tileOutExtent;
} tile;

layout(set = 0, binding = 3) uniform texture2DArray tex_MAIN;
layout(set = 0, binding = 4) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 5) uniform texture2DArray tex_conv2d_1_tf1;
layout(set = 0, binding = 6) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 7) uniform texture2DArray tex_conv2d_2_tf1;
layout(set = 0, binding = 8) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 9) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 10) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 11) uniform texture2DArray tex_conv2d_4_tf1;
layout(set = 0, binding = 12) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 13) uniform texture2DArray tex_conv2d_5_tf1;
layout(set = 0, binding = 14) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 15) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 16) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 17) uniform texture2DArray tex_conv2d_7_tf1;
layout(set = 0, binding = 18, rgba8) uniform image2D img_output;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_1_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_1_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max((texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max((texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_24 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_25 (max((texture(sampler2DArray(tex_conv2d_7_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_26 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_7_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.121882804, 0.055417646, 0.037575886, 0.0, 0.040015355, 0.10440659, 0.120197006, 0.0, 0.008896276, 0.07269119, 0.09253319, 0.0, 0.009000448, -0.033739295, -0.059260685, 0.0) * g_0;
    result += mat4(-0.048027042, 0.09210703, 0.123745404, 0.0, -0.007914943, 0.05483587, 0.054822505, 0.0, -0.005998682, 0.005822986, 0.009868176, 0.0, -0.05866792, -0.04236153, -0.022935968, 0.0) * g_1;
    result += mat4(-0.091270015, -0.033997003, -0.012321896, 0.0, -0.037983265, -0.078790314, -0.085029654, 0.0, 0.10656225, 0.0008334142, -0.0041227583, 0.0, 0.077364065, 0.033960085, 0.029391684, 0.0) * g_2;
    result += mat4(0.15057671, -0.037442014, -0.037083894, 0.0, 0.015493511, -0.016119987, -0.027061606, 0.0, -0.012329675, 0.0060544596, -0.019787522, 0.0, 0.12182345, 0.11346318, 0.08640806, 0.0) * g_3;
    result += mat4(0.19254518, 0.009179287, 0.023821035, 0.0, 0.020269603, 0.025629226, 0.040180814, 0.0, -0.025135614, -0.07785793, -0.099851295, 0.0, -0.122886, 0.03322616, 0.0509256, 0.0) * g_4;
    result += mat4(0.060054794, 0.053996198, 0.047226787, 0.0, 0.038959846, -0.025839888, -0.030583512, 0.0, -0.034999896, 0.011966571, -0.011057454, 0.0, 0.05765179, -0.041760337, -0.0694113, 0.0) * g_5;
    result += mat4(-0.20393562, -0.0055942894, -0.02089636, 0.0, 0.14781304, -0.01954523, -0.0746086, 0.0, 0.071556985, 0.07512172, 0.067927115, 0.0, 0.084076844, -0.0561336, -0.06856403, 0.0) * g_6;
    result += mat4(-0.039552618, -0.04448951, -0.04170605, 0.0, -0.00886809, 0.06708884, 0.07120977, 0.0, 0.04834384, -0.10599933, -0.11024835, 0.0, -0.015948117, 0.084044695, 0.10778199, 0.0) * g_7;
    result += mat4(0.050153337, 0.012563414, 0.014994658, 0.0, 0.10498867, 0.07151875, 0.06761489, 0.0, 0.061650798, -0.035183728, -0.050987806, 0.0, 0.0017240314, 0.041055307, 0.020366805, 0.0) * g_8;
    result += mat4(0.110105395, -0.044468552, -0.072567016, 0.0, -0.049364448, -0.015713394, -0.021540897, 0.0, -0.01636263, -0.084110685, -0.08281401, 0.0, -0.08940374, 0.047863875, 0.051104594, 0.0) * g_9;
    result += mat4(-0.081597924, 0.002422661, 0.01143175, 0.0, -0.07504751, -0.09938017, -0.1063178, 0.0, -0.10390281, 0.0262197, 0.060155805, 0.0, -0.24289346, -0.0054961476, 0.045964316, 0.0) * g_10;
    result += mat4(-0.1829316, 0.047622137, 0.07963877, 0.0, 0.048703995, -0.0026299425, -0.003712008, 0.0, 0.029338706, 0.096882835, 0.102083966, 0.0, 0.078538164, -0.07247937, -0.06820231, 0.0) * g_11;
    result += mat4(-0.02302231, -0.035528302, -0.030674051, 0.0, 0.029780716, 0.031591274, 0.045867007, 0.0, 0.01335752, 0.037001595, 0.04351411, 0.0, -0.11126892, 0.038589563, 0.06444906, 0.0) * g_12;
    result += mat4(0.0047764573, -0.063372664, -0.065609895, 0.0, 0.0478139, 0.025694113, 0.025097322, 0.0, -0.1019169, 0.029989049, 0.050038517, 0.0, 0.07504127, -0.017047737, -0.026222635, 0.0) * g_13;
    result += mat4(0.0024485083, 0.00640911, 0.008171829, 0.0, -0.014622121, -0.06078096, -0.0800138, 0.0, -0.0062360805, -0.014344496, -0.021332184, 0.0, 0.117842786, -0.103745885, -0.13756834, 0.0) * g_14;
    result += mat4(-0.01942775, 0.08720701, 0.104858086, 0.0, -0.05545872, -0.041375194, -0.035368554, 0.0, 0.080331706, -0.021207837, -0.043905254, 0.0, -0.12515299, 3.445463e-05, 0.018742712, 0.0) * g_15;
    result += mat4(0.013106969, 0.010379314, 0.012753471, 0.0, 0.07086715, -0.020893, -0.03968904, 0.0, -0.06114372, 0.029510446, 0.035070244, 0.0, 0.11180839, -0.087067656, -0.124039896, 0.0) * g_16;
    result += mat4(-0.056521703, -0.001166792, -2.3704073e-05, 0.0, 0.011961608, 0.01848977, 0.019861937, 0.0, 0.012167056, 0.018613879, 0.020505793, 0.0, 0.009734187, -0.0308419, -0.035206888, 0.0) * g_17;
    result += mat4(0.0048758825, 0.018046578, 0.014597015, 0.0, -0.061724614, 0.040989272, 0.05644141, 0.0, 0.070315465, 0.008318584, 0.0028647361, 0.0, -0.11316492, 0.043919202, 0.07653594, 0.0) * g_18;
    result += mat4(0.031487904, -0.010548384, -0.009984509, 0.0, -0.0022647562, 0.0043304027, 0.0029451603, 0.0, -0.0063251094, -0.013420807, -0.011919729, 0.0, -0.022760967, 0.019141173, 0.01782793, 0.0) * g_19;
    result += mat4(0.023055293, 0.028219413, 0.024810018, 0.0, 0.031653803, 0.050207954, 0.04504577, 0.0, 0.03877294, 0.0280465, 0.025589157, 0.0, 0.0019387804, 0.023891818, 0.016049948, 0.0) * g_20;
    result += mat4(0.006562233, 0.03880659, 0.037682824, 0.0, -0.021441424, -0.011277022, -0.012471097, 0.0, -0.030526241, -0.013880651, -0.014213582, 0.0, 0.0075785257, -0.0017350517, -0.0024610942, 0.0) * g_21;
    result += mat4(0.015097556, 0.020325955, 0.015611413, 0.0, -0.014755199, -0.034323387, -0.032325987, 0.0, -0.008603291, 0.010346807, 0.011044969, 0.0, -0.004739154, -0.026397636, -0.01995132, 0.0) * g_22;
    result += mat4(0.0097906375, -0.015094543, -0.016887931, 0.0, -0.0007786067, -0.0069163437, -0.008449091, 0.0, 0.025534432, 0.018064791, 0.017047096, 0.0, 0.00055667467, 0.001493328, 0.003636564, 0.0) * g_23;
    result += mat4(-0.042251963, -0.042396102, -0.040224236, 0.0, -0.004492444, -0.0069470624, -0.0065821502, 0.0, 0.062203273, 0.06213223, 0.053592753, 0.0, 0.06424337, 0.07964681, 0.07316769, 0.0) * g_24;
    result += mat4(0.026366957, 0.02789826, 0.027239393, 0.0, -0.006712127, -0.0035723334, -0.0032348586, 0.0, -0.04960562, -0.062758155, -0.058574595, 0.0, -0.02896146, -0.020999067, -0.021301663, 0.0) * g_25;
    result += mat4(-0.013106142, -0.017057793, -0.014653614, 0.0, -0.04254173, -0.043040022, -0.041918345, 0.0, -0.011146975, -0.0043820064, -0.003768677, 0.0, -0.0027743059, -0.0114479, -0.0082087545, 0.0) * g_26;
    result += mat4(-0.10087762, -0.10447133, -0.1005168, 0.0, -0.04165659, -0.04558967, -0.040086865, 0.0, 0.0016493691, 0.0055392827, 0.0070476984, 0.0, -0.018665023, -0.035552308, -0.03375731, 0.0) * g_27;
    result += vec4(0.018580848, -0.022256816, -0.0266178, 0.0);
    return result + texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos, tile.inputLayer));
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_output, ivec2(valid_xy) + ivec2(tile.dstOffset), result);
}