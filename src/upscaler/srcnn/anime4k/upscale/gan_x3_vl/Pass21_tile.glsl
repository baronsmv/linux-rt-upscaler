// Anime4K_Upscale_GAN_x3_VL - Pass 21 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.3275295, -0.10256548, 0.07990071, 0.07344491, 0.09675708, 0.38602263, 0.046949226, 0.13522291, -0.06548349, -0.2141768, 0.1442215, 0.07076354, -0.28706893, -0.09510657, -0.33361802, 0.17997606) * g_0;
    result += mat4(-0.3902465, -0.37943545, 0.34070873, -0.06515231, 0.3773959, 0.23564592, 0.12646881, 0.34798717, 0.08959239, -0.09920428, -0.05263061, 0.08593119, -0.11256286, 0.03323808, 0.28942552, -0.07692077) * g_1;
    result += mat4(0.049924586, -0.046135597, 0.027276453, 0.22358407, -0.17782047, 0.04982942, 0.032420523, 0.14843605, -0.07956747, 0.15165776, 0.024053019, 0.10179323, -0.12331457, 0.17385468, -0.14274296, -0.19595052) * g_2;
    result += mat4(0.08946966, 0.21978298, -0.13464683, -0.15201972, 0.07488354, -0.083067894, 0.2545266, -0.00071388343, -0.09486165, 0.17796224, -0.17153804, -0.13825884, -0.005259369, 0.25042844, -0.17753051, -0.23244008) * g_3;
    result += mat4(-0.101277605, 0.08002136, 0.052613195, -0.0025906193, -0.05422038, 0.06328493, -0.312865, -0.09892072, -0.05911775, -0.30448103, 0.18317235, -0.06668996, -0.30352446, 0.05390891, -0.2406475, 0.24649437) * g_4;
    result += mat4(0.2113683, 0.17140104, -0.30644476, -0.12725203, 0.11536456, -0.19401324, -0.21433993, 0.051369216, -0.15230572, 0.42077595, 0.2791827, 0.0865297, 0.13286951, 0.01140499, 0.020872416, -0.034236103) * g_5;
    result += mat4(0.27759182, -0.1335802, -0.08618739, 0.16586313, 0.15327361, -0.33924958, -0.21265858, -0.20737244, -0.009371618, 0.11073709, 0.4726342, -0.0316658, 0.05112286, -0.032339208, -0.17583671, -0.25219595) * g_6;
    result += mat4(-0.026518747, 0.12324775, -0.31155992, 0.21424666, -0.16678652, 0.06348117, 0.11070292, -0.11495743, -0.10694724, 0.12424144, -0.0021484715, 0.06512352, 0.15463142, -0.11476437, 0.2896172, 0.4012892) * g_7;
    result += mat4(-0.001160076, -0.14888513, 0.14301488, -0.04740031, 0.029436165, -0.23340538, -0.15105838, 0.16811034, -0.06946912, 0.020841839, 0.24280222, 0.021100134, 0.07717933, -0.22419651, -0.006414409, 0.11330106) * g_8;
    result += mat4(0.11547635, -0.25639054, -0.018852018, 0.24935618, 0.14466232, -0.108216226, -0.09197662, -0.20300743, 0.20194042, 0.3676584, -0.14426023, 0.33430305, -0.069588944, -0.05887257, 0.194153, -0.25895235) * g_9;
    result += mat4(0.007937854, 0.10338447, -0.08498367, -0.17928837, 0.27194974, 0.0847048, 0.18792148, -0.14510484, 0.12530808, 0.10366565, -0.13497144, 0.21842767, -0.09612641, 0.1777584, 0.07427717, 0.1062342) * g_10;
    result += mat4(-0.07232676, 0.01870754, 0.17989273, -0.12123426, 0.08253994, -0.13098013, -0.17457142, 0.2662375, 0.16095823, -0.04657838, -0.19479601, 0.037022784, -0.08683312, 0.25411013, 0.041371927, 0.2900686) * g_11;
    result += mat4(-0.285272, -0.3171985, -0.0049645463, 0.14884493, 0.09718065, -0.31102726, -0.24681929, 0.03831946, 0.12201028, -0.101639956, -0.10093202, -0.053675085, 0.02908511, 0.091725975, -0.036547046, 0.02928812) * g_12;
    result += mat4(0.18724014, -0.056803793, 0.15476856, -0.02362879, 0.052199673, 0.06359232, 0.4151323, -0.01882742, -0.019109733, -0.07776646, -0.3151209, 0.053818975, 0.046562992, -0.17907584, 0.13174902, 0.14436677) * g_13;
    result += mat4(-0.21648815, 0.022653956, -0.55097306, -0.008152276, 0.12439029, -0.04533779, -0.12331872, 0.078978874, 0.052233644, -0.1477579, -0.18353766, 0.40710232, -0.23357393, -0.39480248, -0.018859219, -0.07072299) * g_14;
    result += mat4(0.043721616, 0.14363645, 0.024111703, 0.014027298, 0.012885652, 0.17223589, 0.047403537, -0.09311825, -0.24859756, -0.1791887, -0.064629294, -0.26104984, 0.12781571, -0.011062096, 0.1922415, 0.16987853) * g_15;
    result += vec4(0.05144489, 0.033752657, 0.008907633, -0.03164656);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf, ivec3(valid_xy, tile.inputLayer), result);
}