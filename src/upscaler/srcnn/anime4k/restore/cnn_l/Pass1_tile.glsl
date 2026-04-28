// Anime4K_Restore_CNN_L - Pass 1 of 9 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3072) uniform sampler pointSampler;

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

layout(set = 0, binding = 1024) uniform texture2DArray tex_MAIN;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_tf;
#define go_0(x_off, y_off) (texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer)))

vec4 hook() {
vec4 result = mat4(-0.27899465, -0.14974926, 0.6271667, -0.04888494, 0.2164516, -0.47826648, 0.09537477, 0.16404815, -0.009546488, -0.24541017, -0.20505093, -0.11507772, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.22372562, 0.046120282, 0.44437107, 0.54215515, -0.10638798, -0.010795577, 0.19478157, 0.5756847, 0.24542068, 0.11135218, -0.27672207, 0.09624475, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(0.1703517, -0.17810228, -0.34460765, -0.40586865, 0.2102622, 0.08207581, 0.17641851, 0.23701222, -0.32159516, -0.017147528, 0.41743183, 0.19025058, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.4708481, -0.1587934, -0.15760423, -0.11388875, -0.36032093, -0.044305246, 0.19414884, 0.31109568, -0.09320259, -0.23072109, 0.0242641, 0.040976923, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(0.00951417, 0.2746557, -0.49743456, 0.14564055, 0.15047263, 0.08832856, -0.24360974, -0.3517844, -0.12219134, 0.12957081, 0.2876983, 0.13303527, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(-0.12760738, 0.16703783, 0.04391735, 0.34657615, -0.26698044, -0.096000046, -0.46030682, -0.38363042, 0.3510441, 0.2620507, -0.30533043, -0.32785, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.63138646, -0.12703805, 0.38107973, -0.09134196, -0.04012397, -0.1390924, 0.07578805, -0.09274019, -0.045394078, 0.18203364, 0.16900069, 0.13399005, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(-0.13648264, -0.13971807, -0.32322997, -0.08377875, 0.40967095, 0.19853555, -0.26386982, -0.50860924, -0.00555831, 0.06922444, 0.034828495, -0.08413197, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.21196735, 0.24934316, -0.27111465, -0.19941513, -0.30186844, 0.44828892, 0.35906994, -0.35723612, -0.074009515, -0.34400147, -0.22145566, -0.15622428, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.44569078, -0.084358215, -0.014156722, -0.0353374);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, ivec3(valid_xy, tile.inputLayer), result);
}