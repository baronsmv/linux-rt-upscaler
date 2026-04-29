// Anime4K_Upscale_GAN_x4_UL - Pass 34 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_12_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_12_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_12_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_12_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_14_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_15_tf3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.024876181, 0.049410935, 0.18863276, -0.21360011, 0.120626085, -0.041039187, -0.025031038, 0.15861072, 0.031020435, 0.047245055, -0.013810417, -0.13509113, 0.039912585, 0.0030006578, -0.20477976, -0.006812967) * g_0;
    result += mat4(0.20956035, 0.06598898, 0.39945224, 0.0020346004, 0.03396126, -0.055860132, 0.24823242, 0.07525624, -0.21111757, -0.01021541, -0.024861235, 0.13525884, -0.11488383, 0.17399031, -0.10318724, -0.0632262) * g_1;
    result += mat4(-0.06352241, -0.05806122, 0.11548247, -0.09170009, 0.40792373, 0.10823234, 0.25872982, -0.14128555, 0.15681162, 0.087651595, 0.20255132, 0.1707228, 0.061114226, -0.20349206, 0.28370798, 0.29029718) * g_2;
    result += mat4(0.18111548, 0.055765428, -0.33313075, 0.0006103676, 0.2546437, 0.14968075, 0.010974743, -0.023569109, 0.08389516, 0.11510806, -0.09821152, 0.016062623, -0.044881605, -0.023495123, 0.036569294, -0.09006456) * g_3;
    result += mat4(-0.0032415257, -0.028372264, -0.071512826, -0.19787377, 0.06515368, -0.0302441, 0.18496229, -0.19373836, -0.06467672, 0.06881524, 0.08946629, 0.032331206, 0.28018954, -0.03519139, 0.12457947, -0.10447036) * g_4;
    result += mat4(-0.26683676, -0.035779674, -0.33102936, -0.16464533, -0.03501263, 0.13808376, 0.14350422, 0.22299303, -0.17892793, 0.5684519, -0.22766575, -0.05168531, 0.12079673, -0.028563501, -0.008283765, -0.057736557) * g_5;
    result += mat4(0.26274854, 0.06040585, 0.08909, 0.3820274, -0.12244029, -0.112672985, -0.38198316, 0.16422817, -0.012557389, -0.18269186, 0.00044065682, -0.09841192, 0.031287532, -0.3910334, -0.030273868, -0.08873974) * g_6;
    result += mat4(-0.07051197, 0.06768202, 0.060395453, 0.021798966, 0.08901619, -0.22387257, 0.029923506, 0.2166611, 0.21220657, 0.029643808, -0.08909047, 0.16643848, 0.02217428, 0.10017023, 0.13721336, 0.009448813) * g_7;
    result += mat4(-0.03333011, -0.33377162, 0.2840832, -0.075103775, -0.16588315, 0.24898893, 0.007910625, 0.35778743, -0.036830995, -0.15491192, -0.13378191, 0.02509361, -0.2987233, 0.016634934, -0.09080739, 0.057995312) * g_8;
    result += mat4(0.024250133, 0.38453543, -0.012589143, -0.048741948, 0.04583434, 0.42664826, 0.35224134, -0.108690985, 0.034614064, -0.19162184, -0.09440296, 0.07740561, 0.3153523, -0.02028819, -0.0464603, -0.21693204) * g_9;
    result += mat4(0.12554936, 0.28191876, 0.20692183, 0.02204118, -0.12202598, 0.15557781, -0.15807728, -0.22403438, -0.0050102826, -0.25063172, 0.19841024, -0.0935906, -0.016202275, 0.038872335, -0.032258067, 0.1769041) * g_10;
    result += mat4(0.09860859, -0.12880474, -0.32096177, 0.18863943, -0.108892374, -0.040826876, -0.11872242, 0.014217295, -0.110700965, -0.14552751, -0.19022615, 0.23588236, -0.09166652, 0.06676425, -0.114403374, -0.032579597) * g_11;
    result += mat4(-0.28780296, -0.026555603, 0.14381845, 0.18344115, -0.0932073, 0.13699014, -0.12567475, -0.120724775, 0.24272558, -0.12773077, -0.3670164, -0.037173547, 0.056873374, 0.03516149, 0.076903544, 0.21553768) * g_12;
    result += mat4(-0.10597593, -0.040730987, 0.01580388, -0.14816804, 0.06471183, -0.23214011, 0.189348, -0.041128606, -0.23000284, -0.21311183, 0.24912965, 0.02485546, 0.14808623, 0.040830627, 0.043355484, -0.25108483) * g_13;
    result += mat4(-0.11192612, -0.0769642, 0.26336476, -0.0879536, 0.10262009, 0.13074996, 0.20801952, -0.08162488, -0.08020716, -0.006562019, -0.029345717, 0.16304365, -0.15999863, -0.07409018, 0.025488326, -0.06557731) * g_14;
    result += mat4(-0.0436646, 0.16603959, 0.10123139, 0.17289525, -0.17661704, 0.0985401, -0.062753186, -0.09045243, 0.19563136, 0.21048959, 0.119753934, 0.096117176, 0.043681554, 0.037470255, 0.012589698, 0.34186623) * g_15;
    result += mat4(-0.111708984, 0.14836372, -0.1774937, -0.059907373, -0.12757868, 0.2671399, 0.0795556, -0.121689394, -0.14408125, -0.20676754, -0.32231417, -0.009280711, -0.3287384, -0.03544951, -0.0937731, -0.048848808) * g_16;
    result += mat4(0.22088239, -0.07246235, -0.026009787, 0.01313955, 0.0537936, -0.19702353, -0.21666858, 0.14131804, 0.1057349, 0.10163044, 0.024502473, -0.21511002, 0.032470826, 0.040648606, 0.33920923, 0.2154231) * g_17;
    result += mat4(-0.06127513, -0.33544734, 0.02393552, -0.0050719925, -0.1159799, 0.076991595, 0.05514996, 0.26366106, 0.020541657, -0.1467507, -0.014061093, 0.0154901175, 0.08579732, 0.06905036, -0.2559085, -0.2857713) * g_18;
    result += mat4(0.18818028, 0.07449577, 0.28119013, 0.32452857, 0.14604072, -0.059530415, 0.06402294, 0.17558031, 0.04828705, 0.2532384, 0.082392104, 0.080385216, -0.16187488, -0.094814144, -0.0061105727, -0.21911964) * g_19;
    result += vec4(-0.033699915, 0.023496272, 0.022923317, -0.04813553);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf3, ivec3(valid_xy, tile.inputLayer), result);
}