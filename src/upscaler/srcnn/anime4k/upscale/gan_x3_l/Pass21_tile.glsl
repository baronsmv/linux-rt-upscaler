// Anime4K_Upscale_GAN_x3_L - Pass 21 of 30 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.2216899, -0.006199309, -0.14865121, 0.06256912, 0.082141966, 0.069441915, -0.064958416, -0.014999604, -0.017270254, 0.054063573, -0.30066323, 0.09460075, 0.17069338, -0.26000282, 0.026078973, -0.0024098607) * g_0;
    result += mat4(0.22918217, 0.2753827, -0.2260137, 0.0074888375, 0.007864308, 0.01738929, 0.036404576, 0.15125586, 0.12692557, -0.1064573, -0.105954304, 0.17095445, -0.295937, 0.2284073, -0.28089303, 0.17836742) * g_1;
    result += mat4(-0.23949356, -0.20830329, 0.043005105, 0.11848222, 0.26292896, 0.13052817, 0.14105777, -0.14028162, 0.033770017, -0.12098709, -0.19063175, -0.020637099, 0.032703582, -0.31454226, 0.07559202, 0.067997165) * g_2;
    result += mat4(-0.26934767, 0.25418487, 0.2089665, -0.15689164, 0.068669625, -0.19087234, 0.034052055, -0.038685646, 0.037284948, 0.14673525, -0.001882231, 0.07179596, -0.054052413, 0.2954734, 0.108455196, 0.21742904) * g_3;
    result += mat4(0.24180835, 0.012385412, -0.017178789, 0.032714315, -0.26524556, 0.024244266, -0.226589, -0.0358992, -0.2241718, 0.08004254, -0.017615836, -0.2492002, 0.09387765, 0.18154638, -0.034240507, 0.3605678) * g_4;
    result += mat4(0.24151021, -0.014141217, -0.1259467, -0.19366209, -0.07166293, 0.08856931, -0.08999051, 0.31848234, -0.07388433, -0.16038652, 0.28902727, 0.2382835, -0.15296587, -0.12924191, 0.16233487, 0.05408346) * g_5;
    result += mat4(-0.18532315, 0.116318375, -0.043276392, -0.20643523, -0.1317004, -0.025412546, -0.32449946, 0.08039049, -0.18457016, -0.015615943, -0.01645252, 0.21732457, 0.082662076, 0.1900878, -0.11705433, 0.14767131) * g_6;
    result += mat4(0.052993804, -0.11595191, 0.32436988, -0.003765943, 0.2296748, 0.119828835, -0.019125028, -0.3126433, -0.039699726, -0.24760635, 0.08949547, -0.012501165, 0.33296522, -0.349697, -0.081094205, 0.061596226) * g_7;
    result += mat4(-0.033869196, 0.12660468, 0.12152309, -0.18401411, 0.1442463, 0.18430543, 0.22487932, 0.29795903, 0.17951487, -0.24413475, -0.13472381, 0.3147198, -0.22021247, -0.15316834, 0.013162168, -0.20238425) * g_8;
    result += mat4(-0.0015613904, -0.09523476, 0.024224702, -0.17930624, -0.061623972, 0.06495367, 0.3776854, -0.17299566, -0.36212873, 0.13202415, 0.07052771, -0.1219512, 0.29942214, -0.011110212, 0.36104754, 0.0010065075) * g_9;
    result += mat4(0.16467105, 0.29388088, 0.13385788, 0.118168965, 0.15695275, -0.2269201, 0.097460486, -0.04286567, 0.020316202, -0.07753041, -0.18018067, -0.111885116, -0.17371373, 0.04722513, 0.2188871, 0.1295067) * g_10;
    result += mat4(0.2567296, 0.0027146419, -0.18108767, -0.10636566, -0.04075492, 0.08977396, 0.27601838, 0.041642547, -0.29131287, -0.0026349663, 0.16847563, 0.29684088, 0.23944439, -0.12667872, -0.31902757, -0.023768846) * g_11;
    result += mat4(-0.12111429, 0.046077378, 0.07920395, -0.3619861, 0.0030046673, -0.21324079, -0.14134064, 0.07692796, 0.2308601, 0.050601542, -0.20067136, 0.1312576, 0.078878105, -0.07905382, 0.04887801, 0.11589316) * g_12;
    result += mat4(0.18035689, 0.022012187, -0.05441432, -0.13895841, 0.1792498, 0.06579118, -0.3518265, 0.19284686, -0.36724597, -0.19384578, 0.052024953, 0.069351286, -0.17106277, 0.01428955, -0.022695465, -0.03882866) * g_13;
    result += mat4(0.12341931, 0.21374431, 0.14095145, 0.11081035, -0.1377048, 0.2957615, 0.2647214, -0.21324296, 0.18657272, -0.16867872, 0.13558641, -0.14022234, -0.00384067, -0.19601567, -0.20603377, 0.006892211) * g_14;
    result += mat4(0.05891213, 0.17766091, -0.11099863, -0.10597074, 0.4759035, -0.20892517, -0.35479382, -0.057822235, -0.10161365, -0.11828349, -0.021581944, 0.057930104, -0.46801752, -0.25330284, 0.30126703, -0.31744412) * g_15;
    result += vec4(0.011156243, 0.004168819, 0.082229175, 0.043994825);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf, ivec3(valid_xy, tile.inputLayer), result);
}