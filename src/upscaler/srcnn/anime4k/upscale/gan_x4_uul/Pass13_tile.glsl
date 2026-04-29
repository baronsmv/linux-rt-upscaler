// Anime4K_Upscale_GAN_x4_UUL - Pass 13 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_3_tf4;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.113150194, -0.012228015, -0.10810589, 0.18282048, -0.14255662, 0.37686804, -0.34455574, -0.17653705, -0.10299696, 0.17156567, 0.06475307, 0.21704634, 0.05987743, -0.20447443, -0.22365163, 0.26045614) * g_0;
    result += mat4(0.25273082, 0.28410602, 0.13341063, 0.15524255, -0.038504723, -0.2987473, 0.5113095, -0.041018266, 0.15720472, -0.07154719, -0.104476094, -0.36850104, -0.09235334, -0.02460906, 0.1918179, 0.108431995) * g_1;
    result += mat4(-0.16259582, -0.14792964, 0.01875614, 0.19722176, 0.30285388, 0.17894153, 0.02760128, -0.1352214, 0.28634933, -0.0074598296, -0.09348916, 0.12859564, -0.08578008, -0.30871972, -0.19463369, 0.029592479) * g_2;
    result += mat4(0.41718173, -0.08798418, -0.12914781, -0.016728701, -0.004022609, -0.36890173, 0.009880859, -0.1725598, -0.1853788, 0.06624611, 0.010526983, 0.11285315, 0.22359152, 0.04253032, -0.28357792, -0.106521696) * g_3;
    result += mat4(0.23125984, 0.063943766, -0.1724623, -0.17019297, 0.08842359, 0.18506196, 0.20219392, -0.07514321, -0.152088, 0.40809697, 0.22866395, 0.29942676, -0.10514515, 0.14835912, 0.255409, 0.005298396) * g_4;
    result += mat4(0.118000366, 0.040876955, -0.15260358, -0.34197953, 0.16392517, 0.037801206, 0.26511702, -0.16595386, -0.3013676, 0.032535754, 0.2059592, 0.20713131, -0.074489266, -0.0827021, -0.0930588, 0.12812042) * g_5;
    result += mat4(0.12129869, -0.19799119, -0.42776105, -0.15996172, 0.19189952, -0.48698276, 0.14109898, 0.033108126, -0.06918676, -0.28060475, 0.067065634, -0.117751226, 0.07274701, 0.016352981, 0.11877358, -0.30382705) * g_6;
    result += mat4(-0.037769582, -0.0039873547, -0.27957156, -0.027259788, -0.005021477, 0.20690842, -0.43643278, 0.12125521, 0.095314205, 0.13150905, -0.1545535, 0.5004901, 0.078181274, 0.1480264, -0.037564073, -0.07784829) * g_7;
    result += mat4(0.03755771, 0.22955105, -0.03231175, -0.16500925, -0.2564081, -0.13914458, -0.031046085, 0.10951839, -0.14864902, -0.068928115, 0.0909355, -0.14147623, -0.1901003, 0.35303396, 0.07698175, -0.09974956) * g_8;
    result += mat4(-0.050013836, 0.21334587, 0.107435666, 0.22424911, -0.20007136, 0.5500792, -0.40816012, 0.25101343, 0.19421935, 0.035117567, 0.20783037, 0.17410451, -0.28405052, 0.06190316, 0.38027903, 0.051337413) * g_9;
    result += mat4(-0.46978363, -0.11272793, 0.12973092, 0.021777695, -0.020381203, -0.1912334, -0.16367903, 0.32833096, 0.08339247, 0.008160841, 0.37062842, -0.014087529, 0.094892465, -0.012870317, -0.010378546, 0.015417017) * g_10;
    result += mat4(-0.030511223, -0.08355093, 0.08717814, 0.32149768, 0.19554101, 0.2929336, -0.07563172, 0.2604295, 0.2978335, -0.20227137, 0.1991364, 0.04514103, 0.12003651, -0.12325602, 0.10554548, -0.012967588) * g_11;
    result += mat4(0.20080462, -0.0441012, -0.12478753, 0.072197564, -0.11796578, 0.1803613, 0.16319636, 0.05116462, -0.025635032, 0.18309167, 0.016345788, 0.19902118, -0.27134508, -0.24213642, -0.12992004, 0.42813647) * g_12;
    result += mat4(0.11977094, 0.010334066, 0.100837916, 0.1320789, 0.1863875, -0.31015033, -0.0759456, 0.033703748, 0.11986626, -0.28383213, 0.26054385, 0.09489738, -0.0829573, 0.05104106, -0.103039704, -0.3475618) * g_13;
    result += mat4(-0.3418708, 0.095728405, -0.046365432, -0.15324275, -0.15171754, 0.12827595, 0.061078403, 0.12247848, -0.32564154, 0.27075362, -0.03819952, -0.41804206, -0.22586496, -0.06467655, 0.055885177, 0.104513146) * g_14;
    result += mat4(0.025562786, -0.12636441, -0.12522306, -0.1816289, -0.21966882, 0.075359344, 0.095027685, -0.27646592, 0.12653323, -0.08085943, 0.09971742, 0.24018568, 0.053527232, -0.0054027676, 0.07405578, -0.14746837) * g_15;
    result += vec4(0.0619906, -0.042231698, -0.01461747, 0.016205417);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf4, ivec3(valid_xy, tile.inputLayer), result);
}