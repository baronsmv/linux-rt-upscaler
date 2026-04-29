// Anime4K_Upscale_DoG_x2 - Pass 4 of 4 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_HOOKED;
layout(set = 0, binding = 1025) uniform texture2DArray tex_LINELUMA;
layout(set = 0, binding = 1026) uniform texture2DArray tex_GAUSS_X2;
layout(set = 0, binding = 2048, rgba8) uniform image2D img_output;
#define STRENGTH 0.8 //De-blur proportional strength, higher is sharper.

vec4 hook() {
float c = (texture(sampler2DArray(tex_LINELUMA, pointSampler), vec3(pos, tile.inputLayer)).x - texture(sampler2DArray(tex_GAUSS_X2, pointSampler), vec3(pos, tile.inputLayer)).x) * STRENGTH;
	float cc = clamp(c + texture(sampler2DArray(tex_LINELUMA, pointSampler), vec3(pos, tile.inputLayer)).x, texture(sampler2DArray(tex_GAUSS_X2, pointSampler), vec3(pos, tile.inputLayer)).y, texture(sampler2DArray(tex_GAUSS_X2, pointSampler), vec3(pos, tile.inputLayer)).z) - texture(sampler2DArray(tex_LINELUMA, pointSampler), vec3(pos, tile.inputLayer)).x;
	
	//This trick is only possible if the inverse Y->RGB matrix has 1 for every row... (which is the case for BT.709)
	//Otherwise we would need to convert RGB to YUV, modify Y then convert back to RGB.
	return texture(sampler2DArray(tex_HOOKED, pointSampler), vec3(pos, tile.inputLayer)) + cc;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_output, ivec2(valid_xy) + ivec2(tile.dstOffset), result);
}