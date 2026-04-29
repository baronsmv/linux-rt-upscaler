// Anime4K_Upscale_GAN_x4_UL - Pass 10 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_3_tf3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.0753999, 0.03658432, 0.18477479, 0.1749442, -0.5686113, 0.07571735, 0.3006386, -0.10368173, 0.31511122, 0.19695596, 0.022956114, 0.10611498, 0.11219441, 0.07497535, -0.051178914, 0.40932408) * g_0;
    result += mat4(-0.53745884, -0.26310006, -0.14212249, -0.10600016, -0.3300384, -0.11597243, -0.10909209, 0.1591658, 0.20530003, 0.10293979, 0.44854087, -0.14645655, -0.17974512, -0.22815758, 0.055204354, 0.07649109) * g_1;
    result += mat4(-0.11100687, -0.020421045, -0.06534363, -0.006278175, -0.20759039, 0.41434816, 0.019221503, -0.18696092, -0.17718618, -0.27402994, -0.31856942, 0.17581874, 0.19913019, -0.12737915, -0.23136902, 0.29896608) * g_2;
    result += mat4(-0.19094995, -0.008856119, -0.1510312, 0.027294202, -0.038605593, 0.26966265, 0.07470327, -0.21256901, -0.004842345, -0.007547481, 0.0102520995, -0.101378344, 0.06716397, 0.32778296, 0.09866201, 0.105650894) * g_3;
    result += mat4(-0.07321942, -0.20841677, -0.2987479, -0.025003504, 0.51052386, 0.11103265, -0.24727266, 0.05006711, -0.04068963, -0.17566985, 0.22884814, -0.08789049, 0.15666409, -0.2519647, 0.1815161, -0.29741505) * g_4;
    result += mat4(0.32267484, 0.30005294, -0.32079622, 0.30390024, 0.47575063, 0.15858233, -0.049186833, -0.08754423, -0.30718598, -0.23053262, -0.4130956, 0.15375546, -0.2504387, 0.14406683, -0.03541755, -0.116562754) * g_5;
    result += mat4(0.089908786, 0.16712907, 0.2827455, -0.1158676, 0.100818515, -0.13472387, 0.0018383784, 0.28862092, 0.16807888, 0.21766861, -0.008835093, -0.013818307, 0.29853174, 0.44468543, 0.109368436, 0.05118149) * g_6;
    result += mat4(0.068973444, 0.0794158, 0.008132662, -0.025349714, -0.241619, -0.562253, -0.06472331, 0.26760724, 0.14286947, -0.108172484, -0.18315507, 0.082276024, -0.056612104, 0.15318224, 0.09156046, 0.059472494) * g_7;
    result += mat4(0.17709294, 0.11063602, 0.016538871, -0.04356374, -0.4417025, -0.23322596, 0.1735871, -0.13079296, -0.014818513, 0.085076906, 0.31257257, -0.0979718, 0.23537876, 0.22838776, -0.1946557, -0.21086106) * g_8;
    result += mat4(0.16094512, -0.20355348, 0.1149018, -0.19766387, -0.043893784, -0.12358672, -0.03911131, 0.23320928, -0.08093544, 0.09920411, -0.40996867, 0.08985439, -0.26298022, -0.35406327, 0.27618915, -0.17629734) * g_9;
    result += mat4(0.17672168, 0.33174667, -0.1032466, -0.27387938, -0.02977908, -0.025017925, -0.20994124, -0.08694916, -0.02364592, -0.09470408, 0.020289965, 0.012267187, -0.36518613, -0.3328729, -0.006646349, 0.2829864) * g_10;
    result += mat4(-0.37110084, -0.35592732, 0.23536026, 0.23718278, 0.047251917, -0.005406326, -0.3790981, -0.06730541, -0.059093118, 0.17381823, 0.08860589, -0.08435597, 0.063891046, 0.111061476, -0.17462096, -0.21782869) * g_11;
    result += vec4(-0.036752474, -0.0199064, -0.031221999, 0.027302064);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf3, ivec3(valid_xy, tile.inputLayer), result);
}