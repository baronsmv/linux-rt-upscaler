// Anime4K_Upscale_CNN_x2_UL - Pass 2 of 25 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_tf1;
#define go_0(x_off, y_off) (texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer)))

vec4 hook() {
vec4 result = mat4(0.058698863, -0.07291426, 0.04927266, 0.09258057, -0.048297565, 0.05610951, 0.07047442, -0.07120319, -0.03516866, 0.0076037147, 0.07701455, -0.059423756, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.0055849426, 0.26572028, -0.21616961, -0.042883366, 0.04323887, 0.04128688, -0.1975783, 0.15745145, 0.017314252, -0.26768935, 0.080519766, 0.021246549, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.045365453, 0.16887768, -0.21514243, -0.49443442, 0.016238604, -0.12318089, 0.21210986, 0.29339197, 0.008509125, -0.0120522, 0.14660002, 0.16444208, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(-0.18049234, 0.27750164, 0.48953623, 0.32381085, 0.13180427, -0.19170003, -0.042992454, -0.24161138, 0.02187773, -0.052547548, -0.23762631, -0.17446616, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(0.10295366, -0.06758289, 0.3209139, -0.089126036, 0.045649666, 0.061549887, -0.22704688, 0.08373262, 0.062346827, -0.012463345, -0.2679532, -0.033193, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.028882261, -0.41653237, -0.55437064, -0.23836315, -0.10729088, 0.056782994, 0.2587744, 0.3095401, -0.057483524, 0.2876223, 0.21580297, 0.07463114, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.014345448, 0.05962805, -0.2022189, -0.08993287, 0.070023656, 0.08089038, 0.114226155, 0.0025734142, -0.010230871, -0.0990795, 0.17906278, 0.048965868, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.26569575, -0.20329566, 0.40301713, 0.5406432, 0.4320893, 0.09291447, -0.24186778, -0.40646008, 0.08337033, 0.114029825, -0.17575161, -0.21976136, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(-0.23839538, -0.5789523, -0.0655242, -0.0007585647, -0.58420926, -0.0028022572, 0.040551513, -0.14223239, -0.08617295, 0.22481681, -0.015953997, 0.18862534, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.041260406, 0.20480168, -0.016556341, 0.021896001);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf1, ivec3(valid_xy, tile.inputLayer), result);
}