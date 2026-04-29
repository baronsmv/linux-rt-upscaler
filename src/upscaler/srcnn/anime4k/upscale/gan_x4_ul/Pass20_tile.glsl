// Anime4K_Upscale_GAN_x4_UL - Pass 20 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_8_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_9_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.003937308, 0.3325553, -0.051680394, -0.016791617, -0.22406012, -0.1772422, -0.40026435, 0.061494246, -0.052263122, 0.050062478, 0.12657858, 0.25956464, -0.25395867, -0.14557794, 0.065642186, -0.0036497142) * g_0;
    result += mat4(0.14910382, -0.1219233, -0.08730868, 0.12936969, -0.38082328, -0.04098752, -0.21931636, 0.22471759, -0.22303404, 0.005031252, 0.29523098, -0.06785384, -0.29611492, -0.13362305, -0.28399295, -0.015605514) * g_1;
    result += mat4(-0.092055865, 0.23942079, -0.15355012, -0.2754471, 0.3476136, -0.17973644, 0.20373236, 0.47628164, 0.18442081, 0.2272365, 0.39171374, -0.2109089, -0.081467606, -0.19725452, 0.015637135, -0.07057403) * g_2;
    result += mat4(0.10774966, 0.123727456, -0.12286534, 0.16600358, 0.1364775, -0.21570408, 0.074118935, -0.045826353, -0.035832357, -0.28274775, 0.052669924, 0.07969379, 0.17066151, 0.14648491, -0.06644816, -0.14589809) * g_3;
    result += mat4(-0.119286284, -0.09573102, 0.090612456, 0.04023182, 0.09588572, 0.177818, 0.23690048, -0.058244612, -0.016383434, 0.2576226, 0.25695682, -0.014298511, -0.024256507, 0.30848315, -0.041158218, -0.03914358) * g_4;
    result += mat4(-0.29271403, 0.059981633, 0.0021134338, -0.19035797, -0.0037269308, 0.10220867, 0.07883107, -0.13369656, 0.026632074, 0.37791765, 0.13582648, -0.09352286, -0.082421385, -0.15049607, -0.29702196, -0.024250919) * g_5;
    result += mat4(0.06582016, -0.16060877, 0.103828825, 0.06621281, 0.18454358, -0.15770862, 0.0062189074, -0.29478952, -0.38229987, -0.008481092, 0.0146497395, -0.012977512, -0.086033165, 0.24041377, 0.15929726, 0.1291446) * g_6;
    result += mat4(-0.26255193, -0.17674851, 0.016529905, -0.29671943, -0.11499627, 0.057172883, 0.024476945, 0.20377044, -0.246527, -0.2740495, 0.27754322, 0.0035727941, -0.08662866, -0.26152274, -0.1885568, -0.12391516) * g_7;
    result += mat4(0.012594749, 0.09329428, -0.024767002, 0.09388145, 0.053089734, 0.06234544, 0.2099255, 0.46252325, 0.123893864, 0.082300425, -0.07509414, 0.15968856, -0.34341866, -0.13525012, 0.15489148, 0.35870647) * g_8;
    result += mat4(0.15168503, 0.30187908, 0.015656032, 0.013370691, -0.06671537, 0.11837605, -0.08213855, -0.15433209, -0.17091727, -0.0625883, 0.008888305, 0.039089687, 0.15172026, -0.0836314, -0.13341047, -0.029075664) * g_9;
    result += mat4(-0.07207691, -0.36168703, 0.022065176, 0.06053417, 0.10515104, -0.15767829, 0.19980878, 0.17313905, 0.016179686, 0.18054177, 0.19189085, -0.14294004, 0.22004858, -0.28201142, 0.2872886, -0.20112494) * g_10;
    result += mat4(0.34156498, 0.1817744, 0.13134623, 0.05987189, 0.037724342, -0.090201005, 0.10240794, 0.22642598, -0.5217192, -0.033472296, -0.14296426, -0.094750494, -0.03383312, 0.30726826, 0.049418118, 0.10151059) * g_11;
    result += mat4(0.032571465, 0.048514433, -0.10347128, -0.1084494, -0.036202013, -0.008492653, -0.11478463, -0.14242981, -0.16216394, 0.22039019, 0.17737237, -0.1416988, -0.099641696, 0.09431141, -0.17891696, 0.15241605) * g_12;
    result += mat4(-0.22881852, 0.040407304, -0.08619452, 0.08407503, 0.027044954, 0.121950984, 0.17166145, -0.056074105, 0.20592104, 0.05306128, -0.249151, -0.15258761, -0.028193245, -0.033121727, 0.009724152, -0.060050894) * g_13;
    result += mat4(0.055882175, -0.19219743, -0.08486314, 0.25344363, -0.15363735, -0.16262405, -0.16883601, -0.360693, -0.02007423, -0.18265313, -0.13402134, 0.012125967, -0.15832315, 0.35946545, 0.057530846, -0.20121863) * g_14;
    result += mat4(-0.026532218, 0.0999541, -0.18022218, 0.040167805, -0.07300608, 0.23191977, -0.13492207, -0.21953888, -0.006438377, -0.11377467, 0.29050368, 0.08367901, -0.1185086, -0.19436763, 0.19460331, -0.12790322) * g_15;
    result += vec4(0.0048366417, -0.01623872, 0.0149186235, -0.0021957709);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf1, ivec3(valid_xy, tile.inputLayer), result);
}