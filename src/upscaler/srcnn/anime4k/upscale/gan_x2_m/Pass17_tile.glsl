// Anime4K_Upscale_GAN_x2_M - Pass 17 of 23 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_9_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.25229862, 0.22394362, 0.0050771693, -0.07544911, -0.11078993, -0.14940143, 0.009394699, 0.0110528935, 0.044721916, 0.26324025, -0.046336185, 0.38099283, 0.053437576, -0.07238376, -0.090147175, 0.5568665) * g_0;
    result += mat4(0.036739275, -0.2334262, 0.032853063, 0.24364692, -0.122930475, 0.1975849, -0.01315444, -0.13528247, -0.014283123, 0.057573725, 0.058717266, 0.16260214, 0.03097313, -0.11750414, -0.18610783, -0.23006414) * g_1;
    result += mat4(0.37318927, -0.26915783, 0.035015646, 0.2676218, 0.1748369, 0.094052985, -0.11020892, -0.14514406, 0.004877109, -0.26225975, 0.13958913, -0.16787122, 0.06908459, -0.10446216, -0.028498875, -0.28281447) * g_2;
    result += mat4(0.1980342, 0.021963626, -0.03271427, 0.28889674, 0.043385092, -0.16916741, -0.008713317, 0.00013464666, 0.0819348, 0.0152427135, -0.14862345, -0.15659885, -0.050634, 0.04153691, 0.042288564, 0.00585241) * g_3;
    result += mat4(-0.17560056, 0.3521319, 0.20137301, -0.25535235, 0.030570813, 0.2411823, 0.053508975, -0.34454364, 0.22279017, -0.41471666, -0.15029109, 0.22158626, -0.08751699, -0.09357398, 0.20704596, -0.20073438) * g_4;
    result += mat4(0.15419295, 0.31318265, 0.004593545, 0.78029615, -0.16751337, -0.32214537, -0.44051525, 0.22405408, -0.0064655836, 0.36599794, -0.26032063, 0.1850997, 0.13661511, -0.49070612, -0.34533858, 0.16373816) * g_5;
    result += mat4(0.09806042, 0.36764845, 0.11531638, 0.073847674, -0.16854957, -0.19408809, -0.16800502, -0.12827317, -0.5168489, 0.030958507, -0.03509507, 0.086487584, 0.01842899, -0.10123225, -0.17940263, -0.028054722) * g_6;
    result += mat4(0.21619087, -0.05322262, -0.31423846, 0.37783054, 0.20402598, 0.53124064, -0.012658878, 0.20003271, -0.17958061, -0.37326333, -0.24583863, 0.057008818, -0.13031931, -0.031875104, -0.2130229, 0.44612458) * g_7;
    result += mat4(0.25865164, -0.28258085, 0.09512834, 0.054259088, 0.25939894, 0.38799945, -0.33007956, 0.6692063, -0.22719514, 0.16910313, 0.056874167, 0.016987909, -0.19956954, -0.20683451, -0.19937307, -0.41771019) * g_8;
    result += mat4(0.23592101, -0.15792374, -0.06965535, 0.30855724, -0.22757038, 0.12033792, 0.3199687, 0.2674324, 0.112318985, -0.14153072, -0.13629095, 0.13337436, 0.09185144, 0.24124412, 0.028630963, 0.22709718) * g_9;
    result += mat4(0.44043523, 0.32490492, -0.117098905, 0.38431495, 0.07962198, 0.1517891, 0.22628377, 0.13990402, 0.38505656, -0.014830039, 0.20684186, 0.065970615, -0.054330014, -0.046108313, 0.49422976, 0.13082288) * g_10;
    result += mat4(-0.08174229, -0.013488396, -0.09494761, 0.31210786, -0.14530393, -0.22510533, -0.30971226, -0.17040919, -0.64233893, -0.07164386, -0.20537859, -0.17981663, -0.0060102916, -0.10167985, -0.24380594, 0.36305648) * g_11;
    result += mat4(-0.23301682, -0.19649999, -0.0016176507, 0.7897105, -0.68460715, -0.06446943, -0.5841334, -0.17928797, 0.021772655, 0.46175778, 0.36450028, 0.27175686, -0.03546283, -0.19889158, -0.24603742, -0.090037055) * g_12;
    result += mat4(0.1085313, 0.04249687, 0.13247591, 0.09551512, -0.37197208, 0.3261908, -0.13848339, -0.13538006, 0.13875476, -0.3748712, -0.21430004, 0.09772982, -0.35635203, 0.13196826, -0.09840773, -0.21841893) * g_13;
    result += vec4(0.062238827, 0.069814906, -0.107347876, 0.64385885);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf, ivec3(valid_xy, tile.inputLayer), result);
}