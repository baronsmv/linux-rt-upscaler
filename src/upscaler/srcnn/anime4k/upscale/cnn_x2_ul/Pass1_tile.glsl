// Anime4K_Upscale_CNN_x2_UL - Pass 1 of 25 - https://github.com/bloc97/Anime4K
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
vec4 result = mat4(-0.27576035, -0.07072761, -0.1630093, -0.11306897, 0.14765891, -0.039999995, 0.04671886, -0.06138944, 0.11445724, 0.10989976, 0.12772457, 0.19654717, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.076798744, -0.026944768, -0.24994318, 0.2515569, -0.16839856, 0.17563075, 0.30983326, -0.26057217, -0.07267306, -0.16690817, -0.028771983, -0.32779765, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.22670166, -0.08031973, 0.1576897, -0.09411961, 0.10889907, 0.09876773, -0.12708376, 0.20890583, 0.13792023, 0.046159253, 0.008415701, 0.028718324, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.123937644, -0.0040695923, 0.1577942, -0.25086892, -0.11906424, 0.024612824, 0.04019426, -0.20309904, -0.001790695, -0.022292957, -0.24705121, -0.020513516, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.12275696, 0.087533146, 0.22975677, 0.3249744, -0.46705425, 0.049937986, -0.3746097, 0.6908184, -0.02694045, 0.10467642, 0.24765752, 0.29053956, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(-0.085650265, 0.06399875, 0.16803174, -0.000924935, -0.012419805, 0.3505107, -0.013437306, -0.37681264, -0.06174721, 0.3525594, -0.7133205, 0.16013019, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.2400495, 0.08462758, 0.025238732, -0.019882765, -0.09665332, -0.030001955, -0.10374011, -0.2661804, -0.1017717, -0.04910443, 0.102630705, -0.01290848, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.13510828, -0.09396734, -0.30896646, 0.13402982, 0.7047196, -0.09083812, 0.29420912, -0.30652946, 0.089854665, -0.04834406, 0.017005004, -0.22518355, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.28510967, 0.04660653, 0.24457681, -0.21047631, -0.12409636, -0.5526988, -0.1340479, 0.2336875, -0.048938934, -0.31569406, -0.021553513, -0.084858574, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(0.0357343, 0.024812812, 0.040654864, -0.002103711);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, ivec3(valid_xy, tile.inputLayer), result);
}