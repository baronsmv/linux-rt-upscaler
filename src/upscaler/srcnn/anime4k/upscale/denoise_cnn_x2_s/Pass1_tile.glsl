// Anime4K_Upscale_Denoise_CNN_x2_S - Pass 1 of 5 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_tf;
#define go_0(x_off, y_off) (texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer)))

vec4 hook() {
vec4 result = mat4(6.5515305e-05, 0.09565814, -0.0022499533, 0.14627136, -0.0065872427, 0.1441769, 0.17772098, 0.16298898, 0.03727593, 0.02010636, 0.013131043, 0.07891907, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(0.029612074, -0.01204274, 0.07698074, 0.3855172, 0.0045466167, -0.0859741, 0.26930287, 0.67549795, -0.036623597, 0.051749162, -0.04714053, 0.16092339, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.030328937, -0.15884648, 0.0082092965, -0.05052196, 0.041409027, -0.23017453, 0.31568366, 0.05136558, -0.0106390705, -0.12503141, -0.07030922, -0.08512375, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.059616547, -0.12322959, 0.058520414, -0.039292034, 0.08059592, -0.22441447, 0.15380386, -0.17675085, -0.009270574, 0.034731936, -0.048767723, 0.025933916, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.4495482, 0.37551787, -0.4227873, -0.4890034, -0.9007091, 0.7524192, -1.271679, -0.68366605, -0.07302573, 0.09378561, 0.010367829, -0.24593607, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.12684742, -0.11042779, 0.01793761, 0.06982078, 0.12901784, -0.10123104, -0.2129385, -0.15062876, 0.019824497, -0.015181707, 0.070795976, 0.13549626, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.036070887, -0.2733308, 0.05836442, -0.06817092, -0.08980838, -0.514616, 0.2965783, 0.103823625, -0.015213521, -0.16376303, 0.0017071419, -0.0922202, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(-0.053406045, 0.011273207, -0.05544644, 0.09432561, -0.04143601, -0.0783786, -0.39899537, 0.040322974, -0.046442945, 0.052499074, 0.03397099, 0.05516481, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.35976252, 0.197882, 0.031213427, -0.02211337, 0.7940331, 0.327452, 0.30120966, 0.03181121, 0.13782893, 0.060073618, -0.00940469, -0.0358819, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.004601904, -0.0030944077, 0.14569537, -0.016794242);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, ivec3(valid_xy, tile.inputLayer), result);
}