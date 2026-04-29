// Anime4K_Upscale_GAN_x3_L - Pass 22 of 30 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf1;
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
vec4 result = mat4(0.137003, -0.06089221, -0.108805895, 0.27130327, -0.3015222, -0.26373127, 0.019133324, 0.035202216, 0.040255867, 0.09030984, -0.46218738, -0.3097094, -0.057662863, 0.123317555, 0.037645355, 0.010423522) * g_0;
    result += mat4(0.29102653, -0.17060617, 0.31592718, -0.15487169, -0.09719322, 0.08212171, -0.24112037, -0.5323616, 0.050776903, 0.26745227, -0.0123307025, -0.0076298076, -0.044822518, -0.15961778, 0.26758936, 0.019300641) * g_1;
    result += mat4(0.19517086, -0.2878986, 0.12765801, -0.12057966, 0.27521843, 0.028182628, 0.32267106, 0.035355434, -0.065272234, -0.015919037, 0.38220987, 0.14314096, 0.052418232, 0.07207548, -0.41493666, -0.03195114) * g_2;
    result += mat4(0.18309553, -0.11183888, -0.052814357, -0.08971906, -0.14353213, -0.20144752, -0.20325397, -0.16143575, 0.028960846, -0.16557908, 0.266044, -0.2373641, 0.12750591, -0.11190832, 0.35028338, 0.17638433) * g_3;
    result += mat4(0.058721025, 0.21000905, -0.2719825, -0.16923684, 0.2887994, 0.08877727, -0.1274528, 0.12557751, -0.09804875, -0.37839252, -0.1465434, -0.1059692, 0.07212408, -0.101579584, -0.16375211, -0.09519384) * g_4;
    result += mat4(-0.145749, -0.15073515, -0.2661711, -0.21265043, -0.3345085, -0.16820145, 0.07732321, 0.13837157, 0.014605319, -0.14113256, -0.3269443, -0.100293055, 0.114504874, -0.4271041, -0.17389913, 0.0033216716) * g_5;
    result += mat4(0.022264633, -0.19477129, 0.050657783, -0.08318149, -0.5125155, 0.030831251, 0.110084355, -0.25779435, 0.08368584, 0.48425493, -0.28335044, 0.23433922, 0.31263804, -0.12789254, -0.14072786, 0.10106589) * g_6;
    result += mat4(0.007650675, -0.082783565, -0.1599306, 0.22329025, -0.01190027, 0.09498623, -0.06526687, -0.074669816, 0.13880949, -0.0060707824, -0.044009406, 0.15161307, -0.121638715, 0.012903123, 0.047266923, -0.41495043) * g_7;
    result += mat4(0.1315474, 0.2878135, -0.03521026, 0.31479505, 0.4425801, 0.22921802, -0.19864602, -0.0049938424, -0.39346734, 0.09232505, 0.20387846, 0.08173493, -0.2582244, -0.23351125, 0.04481434, -0.105453715) * g_8;
    result += mat4(-0.10668876, -0.026544912, 0.19446668, 0.0045490777, -0.024656052, -0.11874863, 0.21377616, 0.16957945, 0.36561254, -0.19234993, -0.16987774, 0.05442733, -0.13925838, -0.09912278, -0.06849117, 0.2862709) * g_9;
    result += mat4(0.33045495, -0.13048914, -0.023560356, -0.21611182, 0.031752963, 0.14722162, -0.18900181, -0.214494, -0.014231522, 0.23605579, 0.04047805, 0.4060913, -0.13969432, -0.20286381, -0.29891747, -0.043839972) * g_10;
    result += mat4(0.12433207, 0.20156589, -0.16986352, 0.07386095, -0.08681933, -0.055620465, -0.043641977, 0.25392216, -0.19010517, -0.018021587, -0.040169913, 0.3845108, -0.18094495, -0.07285529, 0.1848976, -0.24628341) * g_11;
    result += mat4(-0.038218584, 0.1562106, -0.14935517, 0.14979756, -0.24085392, -0.32680586, -0.015209841, 0.31288582, 0.15819284, -0.084411524, -0.18117775, 0.16964395, 0.29338664, -0.020204993, 0.011733066, -0.03798886) * g_12;
    result += mat4(-0.020065956, -0.043856975, 0.016091857, 0.19466555, 0.16528654, 0.049655683, -0.3676622, -0.14080617, -0.094320625, 0.27908608, -0.084430434, -0.07656003, 0.19461128, 0.11947404, -0.05046522, -0.12625407) * g_13;
    result += mat4(-0.013265381, -0.015804514, -0.12068759, -0.06364535, -0.040848896, -0.07602193, -0.04744431, 0.29088646, 0.1358165, 0.010972456, -0.04270195, -0.091147564, -0.2690454, 0.23030208, -0.39135924, -0.22463588) * g_14;
    result += mat4(0.20590256, 0.098045684, 0.3285928, 0.04094028, 0.12415101, 0.244203, 0.048238404, 0.17298737, 0.22513592, 0.048016686, -0.11171281, 0.12644528, -0.40468216, -0.02186692, -0.09637657, -0.20869099) * g_15;
    result += vec4(-0.01212462, -0.018702446, -0.0063916473, -0.015887083);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf1, ivec3(valid_xy, tile.inputLayer), result);
}