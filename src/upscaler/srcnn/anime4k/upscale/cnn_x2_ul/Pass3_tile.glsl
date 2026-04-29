// Anime4K_Upscale_CNN_x2_UL - Pass 3 of 25 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_MAIN;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_tf2;
#define go_0(x_off, y_off) (texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer)))

vec4 hook() {
vec4 result = mat4(0.07228457, 0.007666297, 0.0023270524, -0.13672906, -0.06545506, -0.049757745, 0.16956232, 0.048654493, 0.05838961, 0.02529347, -0.21557869, -0.12801598, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(0.14399123, 0.33404213, 0.30544546, -0.024566652, -0.07515048, -0.18194102, -0.3067775, -0.3386222, -0.06924871, 0.08277239, 0.30782035, 0.1812733, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.0034141026, 0.03465326, 0.13170029, 0.19363083, 0.07877697, 0.12887354, 0.31288412, 0.039260264, -0.14135145, -0.21657607, -0.08192631, -0.016260598, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.2796338, 0.3380564, -0.2591034, 0.053368755, 0.017104708, -0.18027966, -0.083344355, 0.29481766, -0.088741906, -0.03886714, 0.15531075, 0.34214082, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.35849893, 0.39669302, -0.4743166, -0.30070198, -0.04679741, 0.029014967, -0.11585943, 0.547813, 0.037943944, -0.3137137, -0.16505164, 0.1461349, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(-0.19912307, -0.69915354, 0.12588218, -0.25780293, 0.06785873, -0.06666295, 0.21257555, -0.30608517, 0.22777, 0.47556394, 0.12453673, -0.23966943, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.066451795, 0.036735266, 0.0883064, 0.2535588, 0.111621, 0.026139118, 0.02632312, -0.37550557, -0.026438652, -0.042137396, 0.026273955, -0.24945815, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.550942, -0.4508381, 0.0018671635, 0.21252398, -0.10602345, 0.13596801, -0.0023862422, 0.029529708, -0.06045382, 0.22975087, -0.1594863, -0.33607775, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(-0.0114465775, 0.011813566, 0.09969644, 0.055403743, 0.02460606, 0.13673273, -0.22494976, -0.24256726, 0.024602994, -0.1862818, 0.015388349, 0.39983493, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.32573584, 0.02118458, 0.06321103, 0.01701115);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf2, ivec3(valid_xy, tile.inputLayer), result);
}