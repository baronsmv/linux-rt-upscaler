// Anime4K_Upscale_GAN_x4_UL - Pass 15 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_3_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_3_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_3_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_3_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.056797255, -0.032698087, 0.029859383, 0.12932985, -0.31103006, 0.09165681, -0.15708402, 0.38043964, -0.13528557, 0.2859556, 0.14288856, 0.13102476, -0.08694984, -0.11780176, 0.16207103, -0.11293293) * g_0;
    result += mat4(-0.008796308, 0.118975446, -0.081319205, 0.2084897, 0.08794772, 0.10214503, -0.08378455, -0.10624162, 0.05444449, 0.22647963, -0.12047645, 0.10406878, -0.031486277, 0.045164254, 0.47999045, -0.18060975) * g_1;
    result += mat4(-0.0077636116, 0.05870985, 0.24050762, 0.31322572, 0.08778678, 0.14943774, 0.050537623, -0.102939114, 0.3195675, -0.14615574, -0.26218277, -0.25581908, -0.0019809192, -0.03835245, 0.031318333, -0.1428093) * g_2;
    result += mat4(0.11256259, -0.19089468, -0.06846508, 0.033907987, -0.35249296, -0.06160221, 0.27247807, -0.048603278, 0.040144738, -0.0032360333, -0.2515736, 0.43086162, -0.055536952, -0.11406552, 0.382992, 0.27862927) * g_3;
    result += mat4(-0.03384886, 0.10702642, 0.003908078, -0.009494176, 0.2838821, -0.12845019, 0.12637386, 0.19460931, -0.034333568, 0.012672623, 0.21387313, 0.15411916, 0.14327122, -0.1352761, -0.2997244, -0.017908785) * g_4;
    result += mat4(-0.29253754, 0.33169383, 0.0082393335, -0.20709762, 0.2854362, -0.20728073, -0.22790352, 0.09301863, 0.13168077, -0.07411445, 0.09350424, -0.046449713, -0.11836855, -0.30250466, -0.13257061, 0.3576938) * g_5;
    result += mat4(-0.13777697, 0.056764964, -0.36749512, 0.04235051, -0.041132767, -0.16603513, -0.023862578, -0.014339848, -0.38274148, 0.28778306, 0.15228234, 0.20225881, -0.02469988, -0.101541154, 0.26388898, -0.20009927) * g_6;
    result += mat4(0.15456057, 0.27760306, -0.06929698, -0.24072653, 0.1415152, -0.1549776, 0.030720191, -0.0019005954, -0.06598489, -0.11686977, 0.12704816, -0.30917537, -0.14339961, 0.12742354, -0.23345275, -0.3419119) * g_7;
    result += mat4(0.18928154, -0.19353028, -0.15966406, -0.19417015, 0.10313398, 0.0046505663, 0.21482769, -0.23275238, -0.20456892, -0.5014606, -0.10783419, 0.25891942, -0.24919175, -0.10028775, -0.2961402, 0.077766955) * g_8;
    result += mat4(-0.085105784, 0.06528528, 0.102185756, 0.099264726, -0.00020144526, -0.08768721, -0.09324967, 0.30346313, -0.084492646, -0.14017163, -0.043167874, -0.20060216, 0.09593379, 0.28399333, 0.08168489, -0.33063418) * g_9;
    result += mat4(0.15791257, 0.057779472, -0.20147012, 0.07967618, 0.04262509, 0.039220728, -0.15080509, 0.17438835, -0.044964172, -0.14530478, 0.31693324, 0.08582341, -0.1061789, 0.2800015, 0.33440664, 0.09700403) * g_10;
    result += mat4(-0.14642169, -0.07778901, 0.13264288, -0.24182376, 0.23503877, 0.005028356, -0.30113846, 0.22778516, -0.1648793, -0.033169918, -0.20036162, -0.35071707, -0.06705746, 0.12431054, -0.022009062, -0.07124459) * g_11;
    result += mat4(0.06766408, 0.09030523, 0.22668982, -0.38617492, -0.10099634, -0.029897379, 0.24775109, -0.20888264, 0.056208886, 0.0044284128, 0.16691649, 0.22874106, 0.0038740179, -0.07576401, 0.27207628, 0.11311432) * g_12;
    result += mat4(-0.11319886, -0.3020603, 0.08133381, 0.19350809, 0.032002088, -0.038216423, -0.12224599, 0.08397432, 0.021123007, 0.075326644, 0.29643238, 0.20064169, 0.042381126, -0.002854783, -0.027586436, -0.06968597) * g_13;
    result += vec4(0.038540784, 0.053720564, 0.012191528, -0.029126916);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf2, ivec3(valid_xy, tile.inputLayer), result);
}