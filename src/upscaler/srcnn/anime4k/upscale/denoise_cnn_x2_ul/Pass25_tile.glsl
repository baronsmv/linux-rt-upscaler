// Anime4K_Upscale_Denoise_CNN_x2_UL - Pass 25 of 25 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2DArray tex_conv2d_last_tf;
layout(set = 0, binding = 4) uniform texture2DArray tex_conv2d_last_tf1;
layout(set = 0, binding = 5) uniform texture2DArray tex_conv2d_last_tf2;
layout(set = 0, binding = 6) uniform texture2D tex_MAIN;
layout(set = 0, binding = 7, rgba8) uniform image2D img_output;

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 base_out = (interior_xy * 2) + ivec2(tile.dstOffset);
    pos = (vec2(interior_xy + tile.margin) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec2 full_opt = vec2(1.0 / tile.fullOutWidth, 1.0 / tile.fullOutHeight);
    vec2 f0 = fract(pos * vec2(ubo.in_width, ubo.in_height));
    ivec2 i0 = ivec2(f0 * 2.0);
    float c0 = texture(sampler2DArray(tex_conv2d_last_tf, pointSampler), vec3((vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos, tile.inputLayer))[i0.y * 2 + i0.x];
    float c1 = texture(sampler2DArray(tex_conv2d_last_tf1, pointSampler), vec3((vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos, tile.inputLayer))[i0.y * 2 + i0.x];
    float c2 = texture(sampler2DArray(tex_conv2d_last_tf2, pointSampler), vec3((vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos, tile.inputLayer))[i0.y * 2 + i0.x];
    float c3 = c2;
    if ((base_out.x + 0) < int(tile.dstOffset.x + tile.tileOutExtent.x) && (base_out.y + 0) < int(tile.dstOffset.y + tile.tileOutExtent.y)) {
        vec3 rgb_0 = texture(sampler2D(tex_MAIN, linearSampler), (vec2(base_out) + vec2(0.5, 0.5)) * full_opt).rgb;
        imageStore(img_output, ivec2(base_out) + ivec2(0, 0), vec4(rgb_0 + c0, 1.0));
    }
    if ((base_out.x + 1) < int(tile.dstOffset.x + tile.tileOutExtent.x) && (base_out.y + 0) < int(tile.dstOffset.y + tile.tileOutExtent.y)) {
        vec3 rgb_1 = texture(sampler2D(tex_MAIN, linearSampler), (vec2(base_out) + vec2(1.5, 0.5)) * full_opt).rgb;
        imageStore(img_output, ivec2(base_out) + ivec2(1, 0), vec4(rgb_1 + c1, 1.0));
    }
    if ((base_out.x + 0) < int(tile.dstOffset.x + tile.tileOutExtent.x) && (base_out.y + 1) < int(tile.dstOffset.y + tile.tileOutExtent.y)) {
        vec3 rgb_2 = texture(sampler2D(tex_MAIN, linearSampler), (vec2(base_out) + vec2(0.5, 1.5)) * full_opt).rgb;
        imageStore(img_output, ivec2(base_out) + ivec2(0, 1), vec4(rgb_2 + c2, 1.0));
    }
    if ((base_out.x + 1) < int(tile.dstOffset.x + tile.tileOutExtent.x) && (base_out.y + 1) < int(tile.dstOffset.y + tile.tileOutExtent.y)) {
        vec3 rgb_3 = texture(sampler2D(tex_MAIN, linearSampler), (vec2(base_out) + vec2(1.5, 1.5)) * full_opt).rgb;
        imageStore(img_output, ivec2(base_out) + ivec2(1, 1), vec4(rgb_3 + c3, 1.0));
    }
}