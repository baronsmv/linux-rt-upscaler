// Anime4K_Upscale_GAN_x3_L - Pass 18 of 30 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_8_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_9_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.0014731521, -0.15165007, 0.04889816, -0.23228844, 0.11362322, 0.07071926, -0.23770805, -0.04347728, -0.16787082, -0.008313435, -0.42370048, 0.08681679, 0.10611205, -0.012660734, 0.10022364, 0.027629996) * g_0;
    result += mat4(-0.35393402, 0.018436229, 0.10629333, 0.029471794, -0.21129252, -0.301571, 0.0045201713, -0.15636055, 0.298371, 0.11426107, 0.018450111, -0.13657977, 0.22216578, 0.009629214, 0.5373198, 0.30699998) * g_1;
    result += mat4(-0.1504586, -0.16447587, -0.2739809, -0.14074785, 0.39510623, -0.08384201, 0.14561974, -0.43195033, -0.055713434, 0.12800978, 0.2829296, -0.23494978, 0.14326042, -0.09509476, -0.3169162, 0.124649614) * g_2;
    result += mat4(-0.23705968, 0.15959233, 0.11467344, 0.15141489, -0.096755706, 0.023953263, 0.13856179, 0.024189185, 0.13272291, 0.46271062, 0.55494446, -0.14286532, 0.1501738, 0.28827608, 0.058801714, 0.029045105) * g_3;
    result += mat4(-0.002308931, 0.07281086, -0.5197955, 0.079986535, 0.38919175, 0.3164044, 0.35857818, 0.09364757, 0.17373051, -0.1447216, -0.05244769, 0.15533692, 0.046295535, -0.19459103, -0.33215967, -0.15369573) * g_4;
    result += mat4(0.11478203, -0.29375935, -0.19501545, -0.081721894, -0.103483915, 0.041965716, 0.056954723, 0.19596405, -0.13819647, 0.010641367, -0.11124998, -0.08675409, 0.036859434, 0.23720297, 0.14129876, -0.044769786) * g_5;
    result += mat4(0.08397742, -0.12651941, 0.17676216, -0.084249385, 0.36716628, 0.039452277, -0.27606088, -0.36796048, 0.31680533, 0.14186403, 0.4466997, 0.13315229, 0.011085958, -0.17513317, 0.13940759, 0.27495402) * g_6;
    result += mat4(-0.1870658, 0.18817395, 0.010469263, -0.39973256, -0.57167524, -0.38714117, -0.26255277, 0.14361858, 0.018649995, 0.15935089, -0.21745402, -0.0056655053, -0.15408997, -0.03154883, -0.29631105, 0.27472818) * g_7;
    result += mat4(-0.07735958, 0.042861674, 0.36729267, -0.2362879, -0.15516327, -0.009109079, 0.063800156, -0.253287, 0.4471074, 0.0944695, -0.26948866, -0.07759066, 0.045151226, -0.13749917, 0.14566323, -0.13593693) * g_8;
    result += mat4(0.28955856, 0.09293573, 0.07423561, 0.1616493, 0.22285056, 0.01639275, 0.026332684, -0.14958683, -0.32087958, -0.3138252, -0.17335242, -0.38171476, -0.25562596, -0.022701526, 0.17425084, -0.042576227) * g_9;
    result += mat4(0.24964347, -0.07078707, 0.18416835, -0.054758202, -0.061644293, -0.0964391, 0.14583856, -0.34874785, -0.3402768, 0.14743538, 0.36047265, 0.04471611, 0.015971184, 0.25227246, -0.011749087, -0.18359871) * g_10;
    result += mat4(-0.059328917, -0.07904788, -0.23883855, -0.06956805, -0.040810965, 0.09536262, 0.0018617791, -0.1898438, 0.1794419, 0.11382087, -0.16192305, 0.22020166, 0.03995484, -0.19086155, -0.2970539, 0.14597812) * g_11;
    result += mat4(-0.034995254, 0.060782332, -0.0519364, 0.41303346, -0.06989344, 0.21384521, 0.31474474, 0.12592849, 0.17633408, -0.2764535, 0.36884397, -0.015302021, 0.02951528, 0.094452016, 0.13392285, 0.14435606) * g_12;
    result += mat4(0.13522784, 0.101011604, 0.04657966, -0.043399148, 0.008192044, 0.0027336285, 0.011269824, 0.09976881, -0.026473437, -0.124423906, -0.19602631, -0.09871594, -0.10603456, 0.057509303, -0.09007557, -0.14438893) * g_13;
    result += vec4(-0.07283617, -0.09245546, -0.006695486, -0.013076421);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf2, ivec3(valid_xy, tile.inputLayer), result);
}