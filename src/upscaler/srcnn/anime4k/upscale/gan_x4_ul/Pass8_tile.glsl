// Anime4K_Upscale_GAN_x4_UL - Pass 8 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_3_tf1;
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
vec4 result = mat4(-0.11699225, -0.011926791, 0.15968116, -0.28171888, -0.094884306, 0.12266288, -0.02869124, 0.124487214, 0.11344168, 0.27545413, -0.11473996, -0.18655725, 0.07444298, 0.20979966, -0.34344572, 0.09082154) * g_0;
    result += mat4(0.34916008, 0.13911577, -0.010201517, 0.0037869287, 0.08340967, -0.12156858, -0.117294475, 0.35585365, -0.06922667, 0.06911412, -0.07068636, 0.12846842, 0.015117793, -0.023309045, 0.013241948, -0.107297644) * g_1;
    result += mat4(0.17315003, -0.10761723, -0.072508104, 0.22057249, -0.07545323, 0.07440893, -0.20900318, 0.020722175, 0.10075026, -0.12781784, -0.023600617, -0.08387344, 0.32060823, -0.078003615, 0.114024006, 0.09494562) * g_2;
    result += mat4(0.11551656, -0.000862936, -0.3338336, -0.19441503, 0.14071822, -0.09090158, 0.116582595, -0.14757058, 0.3173076, 0.027060512, -0.18175173, 0.103367195, -0.123774566, 0.004113376, -0.036047045, 0.20972507) * g_3;
    result += mat4(0.2616819, -0.23769857, 0.14694063, 0.52330256, -0.15146148, -0.21730542, -0.067091495, -0.06504361, 0.04726932, -0.043983664, -0.04815243, 0.16768406, 0.19502987, -0.32623842, -0.051590122, -0.13552347) * g_4;
    result += mat4(-0.10593247, 0.043780692, -0.0012781665, -0.027277134, 0.07427171, 0.21340221, -0.0145785725, -0.09647566, 0.07683649, -0.0025731022, 0.22363698, -0.05832384, 0.021017361, -0.07482151, -0.12129065, -0.0019391342) * g_5;
    result += mat4(-0.0340859, -0.14430326, 0.10648293, -0.072308615, 0.11786764, 0.119093865, -0.012822142, -0.037612807, -0.1896853, -0.22999093, 0.4030961, -0.03841633, 0.12869515, -0.18355207, 0.010367995, 0.02159778) * g_6;
    result += mat4(0.053300664, 0.09102034, 0.2953044, 0.20959346, 0.051493607, 0.42663953, -0.24863662, -0.18108594, 0.09425621, 0.13966715, -0.14302093, 0.043921605, -0.16983564, 0.0754303, -0.017989958, 0.17268774) * g_7;
    result += mat4(-0.08402705, -0.09658915, 0.12671614, -0.16052966, 0.03697882, 0.30477068, 0.13104036, 0.0013146247, 0.20226406, -0.07586563, -0.011798672, 0.3262475, -0.06879792, 0.08181783, 0.36202317, 0.3781982) * g_8;
    result += mat4(-0.17125002, 0.33657587, -0.39985514, 0.02585221, 0.1537332, 0.04795972, 0.018550362, -0.22021875, -0.19417998, 0.074346684, 0.12862094, -0.20361246, -0.024607735, -0.2939094, -0.20752306, -0.23394017) * g_9;
    result += mat4(0.1611785, -0.21036223, 0.511955, -0.32777244, -0.1491686, 0.16397569, 0.08984783, -0.06717227, 0.0506624, 0.11203859, -0.05863204, -0.19412707, -0.10711086, 0.19335233, -0.036180694, -0.12216311) * g_10;
    result += mat4(0.07279537, 0.118367635, -0.24924143, 0.077552676, 0.076574005, 0.29696205, -0.4367856, 0.049242187, 0.03598476, -0.23271763, 0.09492026, 0.1604189, 0.23055643, -0.5723609, -0.16704383, -0.1909646) * g_11;
    result += vec4(0.02420742, -0.053550396, 0.09937034, 0.02549033);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf1, ivec3(valid_xy, tile.inputLayer), result);
}