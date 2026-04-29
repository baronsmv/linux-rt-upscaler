// Anime4K_Upscale_GAN_x3_VL - Pass 26 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_14_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_15_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.058371756, -0.15223853, -0.16356315, -0.16802065, -0.19054104, -0.036780667, -0.19440329, -0.2248528, -0.005347806, 0.071672164, -0.0771526, 0.2924663, -0.0774155, -0.14556612, 0.114560455, 0.27062297) * g_0;
    result += mat4(-0.3445877, 0.19475816, 0.09710621, 0.21995266, 0.20887254, 0.09341146, 0.22033042, 0.23206021, 0.033344083, -0.07287835, -0.18038799, -0.1591713, -0.07109204, -0.01323598, -0.110603236, 0.22050153) * g_1;
    result += mat4(-0.2549611, -0.11848451, -0.022745349, 0.3926633, 0.01083691, 0.09032976, 0.051901888, -0.008881073, -0.113227226, -0.06107646, -0.2835598, 0.006955209, 0.057944898, -0.024794495, 0.21598488, 0.013463527) * g_2;
    result += mat4(0.081732295, 0.14985989, 0.012442874, -0.055946667, -0.29241166, 0.054421537, 0.16944103, -0.027691018, 0.32594857, -0.20029362, 0.24102916, -0.2836753, 0.027726209, 0.13321714, -0.08945177, -0.18618472) * g_3;
    result += mat4(-0.019850472, 0.014862859, -0.40852943, 0.049327563, -0.08516907, -0.024971958, -0.24877243, -0.12475686, -0.0059337337, -0.15594041, 0.014721621, -0.007462477, 0.017745093, -0.07287227, -0.08225071, 0.16203512) * g_4;
    result += mat4(0.0622282, -0.1562546, -0.19524418, -0.0004125873, -0.28058666, -0.10427074, 0.01347889, 0.087949455, 0.205533, 0.22994758, 0.058676008, 0.016087666, -0.27204573, -0.13226426, 0.45560098, 0.19548674) * g_5;
    result += mat4(0.10312986, -0.11663352, -0.21141005, 0.060728226, 0.04790389, 0.4554892, -0.2993332, 0.090701774, -0.15572315, -0.08100787, 0.38805684, 0.12010196, -0.19057408, 0.0433082, 0.17466016, 0.2343365) * g_6;
    result += mat4(-0.035952494, 0.0069249035, 0.018094797, -0.022886304, -0.16588111, -0.06751834, 0.067921944, 0.0408952, -0.10368173, -0.1867776, 0.08716087, 0.32557133, -0.17160255, 0.21748102, -0.27042568, 0.010276504) * g_7;
    result += mat4(0.1353541, -0.09830681, -0.024150403, 0.20349647, 0.0834164, -0.23606645, 0.1878813, -0.10913659, 0.101774715, -0.122187294, -0.10274547, 0.088820286, 0.0952697, 0.2059741, -0.06964167, -0.06740629) * g_8;
    result += mat4(0.035706226, 0.116456866, 0.00867265, -0.1580804, 0.08455965, 0.2931992, -0.0652682, -0.27945194, -0.28506938, 0.18549383, -0.30028465, -0.058111582, 0.17342384, 0.07022962, -0.107152976, 0.058686964) * g_9;
    result += mat4(0.26401508, 0.06263026, 0.07814346, 0.1653557, -0.06065454, 0.13713975, -0.35849124, -0.2712066, 0.0016249327, -0.028205892, 0.12781107, 0.19252528, -0.02890903, -0.07810885, -0.31435448, 0.25607604) * g_10;
    result += mat4(-0.007452971, -0.11137609, -0.17482384, -0.2254985, -0.054940246, -0.4866264, -0.012218613, 0.07933414, -0.059196893, -0.22073849, -0.19979995, 0.045081053, 0.08083855, -0.18446396, 0.063239574, 0.15218821) * g_11;
    result += mat4(0.019093331, 0.14936107, 0.006522308, -0.06813928, -0.06954633, 0.076614395, 0.27179638, 0.08497197, -0.028945964, 0.24470884, -0.09067254, -0.02809542, -0.3260882, -0.019783175, 0.29227713, -0.1503793) * g_12;
    result += mat4(0.0038467604, 0.15844361, -0.17461929, 0.0036902665, -0.18804209, -0.10455593, 0.19846849, 0.0045625297, -0.021197336, -0.12760538, -0.21889874, -0.15576892, 0.08428448, -0.051786594, -0.28837204, 0.16710553) * g_13;
    result += mat4(-0.039501086, 0.20741075, -0.023215454, -0.15562606, 0.2704772, -0.004882398, 0.06743958, 0.09672041, 0.2045052, 0.30854276, -0.023670265, -0.42425725, 0.22383718, 0.03339793, 0.09593589, -0.28993925) * g_14;
    result += mat4(-0.0060895267, -0.32284054, 0.08005629, 0.22948626, 0.0779126, 0.051218465, -0.19901748, 0.04607648, 0.20720762, -0.25467792, 0.190241, 0.14972371, 0.0024004376, -0.25745007, -0.12783068, 0.11001452) * g_15;
    result += mat4(0.11667156, 0.23464362, -0.063853756, 0.39974514, -0.009121619, -0.24133451, -0.03714007, 0.009775786, 0.051351607, 0.056225047, -0.23616025, 0.031748235, -0.16796593, -0.030489858, -0.14123768, 0.24537739) * g_16;
    result += mat4(0.013762163, -0.25353146, 0.15549485, -0.28925058, 0.2193342, 0.039180417, 0.06402014, -0.4502174, 0.062770426, -0.00075927033, 0.33666995, 0.23031248, -0.00079948275, -0.13443127, -0.06645994, -0.23359178) * g_17;
    result += vec4(-0.008095479, -0.06195082, -0.018640047, 0.02992503);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf, ivec3(valid_xy, tile.inputLayer), result);
}