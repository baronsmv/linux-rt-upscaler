// Anime4K_Restore_CNN_UL - Pass 2 of 25 - https://github.com/bloc97/Anime4K
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
//    glslc -fshader-stage=compute --target-env=vulkan1.2 \
//          <this_file> -o <output.spv>
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
layout(set = 0, binding = 4, rgba8) uniform image2DArray img_conv2d_tf1;
#define go_0(x_off, y_off) (texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer)))

vec4 hook() {
vec4 result = mat4(-0.44157687, 0.1715858, -0.11000502, 0.062367063, 0.21790773, 0.15507151, 0.14760862, -0.2598815, 0.14098467, 0.14019097, -0.26298222, 0.10975315, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(0.15774319, -0.16769339, -0.49734345, -0.3935963, 0.115124024, -0.08045373, 0.55867237, 0.48593813, 0.058544844, -0.2705686, 0.3303555, 0.4181385, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(0.16588609, -0.013389144, 0.06600297, -0.09309111, -0.36321074, -0.13877828, 0.4099233, 0.20805255, 0.31892648, 0.16856939, -0.23898357, 0.11751563, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.39999864, 0.46407622, -0.12249342, -0.09798957, 0.122675434, 0.18265116, 0.030651823, 0.14682484, -0.42969155, 0.2486042, 0.13566706, -0.13458017, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.12757893, -0.19025628, -0.16728874, -0.10162156, -0.1577721, -0.174548, 0.29329458, 0.17963637, -0.43279588, 0.088979766, 0.06334896, -0.047701746, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(-0.14359929, -0.12800618, -0.15429202, 0.034745168, 0.15794043, -0.086441815, -0.06520017, 0.26176664, -0.022253495, -0.34480432, -0.009120493, 0.08706416, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.1994137, 0.070990525, 0.3388379, 0.37502727, -0.116911314, 0.2160554, -0.1831974, -0.04184975, 0.2545874, -0.083908126, -0.19057468, -0.13382773, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(-0.46475947, -0.23414738, -0.036689937, 0.018558737, -0.32609373, 0.15265512, -0.055894423, -0.3676328, 0.24501368, 0.12390915, 0.13458043, -0.30162823, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.12621075, 0.046852987, 0.17333286, 0.18997045, 0.3245911, -0.28809196, -0.3660882, -0.5916272, -0.11456223, -0.030912774, 0.17037971, -0.12640971, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(0.42778614, 0.054881692, -0.23388587, -0.031204376);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf1, ivec3(valid_xy, 0), result);
}