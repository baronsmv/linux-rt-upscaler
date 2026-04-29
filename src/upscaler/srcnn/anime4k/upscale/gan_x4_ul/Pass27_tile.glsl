// Anime4K_Upscale_GAN_x4_UL - Pass 27 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_9_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_9_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_9_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.12601665, 0.16175638, -0.19269617, 0.107886985, -0.28229153, -0.47275612, -0.23898768, 0.11874162, -0.0438132, 0.1620992, -0.07009845, -0.088367306, -0.13653506, -0.24453755, 0.07402701, 0.112232625) * g_0;
    result += mat4(-0.1342178, -0.06971262, 0.12556942, 0.01929168, 0.23838176, 0.018971201, -0.05296016, -0.08929702, 0.040384937, -0.09414689, 0.07239966, 0.057094514, 0.022977736, 0.23681253, 0.07352691, 0.1401568) * g_1;
    result += mat4(0.13201892, 0.04062019, 0.052444696, 0.039319273, 0.029174356, 0.024773024, 0.24973504, 0.20124938, -0.11042911, -0.32369703, 0.13876265, 0.07454285, -0.29048622, -0.0073187165, 0.18820713, 0.1310624) * g_2;
    result += mat4(-0.052355357, 0.14466842, -0.20304704, -0.10945343, -0.13633797, -0.0362287, 0.21200177, -0.115031704, -0.007819006, -0.0060177785, 0.10633933, -0.06184755, 0.09415192, -0.109933, -0.025773333, 0.13335694) * g_3;
    result += mat4(-0.15166026, -0.363905, 0.16473109, 0.36505404, 0.056683872, 0.0061098817, 0.4168733, -0.044268914, 0.2840304, -0.27333218, -0.032296672, 0.08772143, -0.0003773526, 0.34500858, 0.16723311, -0.08633425) * g_4;
    result += mat4(0.17295076, 0.058134206, 0.10268273, -0.05562554, -0.01107067, -0.16301824, -0.15832978, -0.35605776, -0.059426963, -0.16527529, 0.08868478, -0.1846189, -0.017306576, 0.10800906, -0.012656846, 0.29250982) * g_5;
    result += mat4(-0.0046278895, -0.41774723, 0.24683201, 0.023414413, -0.0560346, 0.3508538, -0.018426506, -0.22601782, -0.22005035, 0.24708134, 0.20629126, 0.017688079, -0.21966107, 0.0007773641, 0.27158982, -0.15457745) * g_6;
    result += mat4(0.28892994, -0.0948736, -0.22442342, 0.18630128, 0.056576118, -0.17367427, 0.036432527, -0.12435009, 0.049795005, 0.13438956, 0.38832325, 0.040559538, -0.18281, -0.027084656, 0.14047231, 0.16336608) * g_7;
    result += mat4(0.07984998, 0.10912455, -0.25223976, -0.07150487, 0.39511418, -0.16752689, -0.012659484, 0.14530154, 0.15754412, -0.10894477, -0.1896881, -0.12754244, -0.2143525, -0.18319069, -0.13740367, 0.049823396) * g_8;
    result += mat4(-0.2693335, -0.22025953, -0.08723098, 0.030883936, -0.01043496, 0.049120355, 0.027913291, 0.2757188, 0.2999968, 0.1511124, 0.03902692, 0.012411737, 0.3374636, 0.07545474, 0.0019430651, -0.2693774) * g_9;
    result += mat4(0.22447923, 0.18749979, -0.2726834, -0.054140817, -0.028611785, -0.1420322, -0.26904938, 0.034827393, -0.16475505, -0.13389514, 0.004789874, -0.041023012, 0.13383822, -0.33016685, 0.14386353, -0.16444317) * g_10;
    result += mat4(0.06270732, -0.1334095, -0.15366173, -0.05587756, 0.10967794, 0.20958632, 0.0024631543, 0.0054002493, 0.1983807, 0.21552248, -0.027546072, 0.03749206, 0.09604704, -0.015076683, -0.18674834, -0.048891157) * g_11;
    result += mat4(0.3359941, 0.005712003, 0.12872687, 0.17963566, 0.13625218, -0.07016191, 0.41262105, 0.12859339, -0.029220538, 0.042857308, -0.09492956, -0.006781853, -0.002147385, 0.09192873, -0.034135956, 0.04365597) * g_12;
    result += mat4(-0.0655155, 0.09802182, -0.009230572, -0.11295286, -0.04042111, -0.167074, -0.042077914, -0.3769242, 0.3564197, -0.41506588, 0.010919382, 0.19179656, -0.30047882, -0.12062898, -0.09184107, 0.18559954) * g_13;
    result += mat4(-0.02611887, 0.18515642, -0.26166156, -0.11706778, 0.1758253, -0.04787028, -0.1428414, 0.20101525, -0.19495995, -0.114093624, 0.15655537, 0.09985385, -0.28163755, 0.04849391, 0.08238636, -0.084574856) * g_14;
    result += mat4(0.00010702968, -0.1017887, 0.18226019, -0.059170388, 0.18746078, 0.060440563, -0.14334333, -0.1825296, 0.27030236, 0.028283298, -0.09769837, -0.0023890818, 0.18596847, 0.07152733, -0.06317227, -0.12367107) * g_15;
    result += mat4(0.24603085, 0.056102052, 0.13449737, -0.23569027, -0.05986085, 0.27015293, -0.2839155, -0.089338146, -0.057650078, 0.25799945, -0.2778006, 0.32337326, 0.15381968, -0.10049262, -0.0764022, 0.07623496) * g_16;
    result += mat4(0.15472987, 0.087436944, -0.14177966, 0.22156389, 0.020608503, 0.2505864, 0.20408471, 0.031214792, -0.059114598, -0.15656275, 0.228334, -0.11210813, -0.06963447, -0.033369016, -0.09053422, -0.007444799) * g_17;
    result += vec4(0.010953258, -0.03096994, -0.08644558, -0.025292031);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf2, ivec3(valid_xy, tile.inputLayer), result);
}