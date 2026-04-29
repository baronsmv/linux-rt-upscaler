// Anime4K_Upscale_GAN_x3_L - Pass 16 of 30 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.20878315, 0.073090814, 0.34913197, 0.04554434, -0.3036766, 0.04255219, 0.060676616, 0.24025755, -0.019680336, -0.15252031, -0.03416314, -0.072506554, 0.013241457, -0.10496547, 0.050562985, -0.033250205) * g_0;
    result += mat4(-0.18049034, 0.09664636, 0.41482204, 0.23575203, -0.05704124, -0.044852983, 0.1783455, -0.017561441, -0.06852369, 0.014129533, -0.21115111, -0.22699773, 0.38242704, 0.01165174, 0.04190493, -0.2141891) * g_1;
    result += mat4(-0.011946614, -0.16289592, 0.041371312, 0.40975794, 0.0041022287, -0.23657559, 0.10817027, -0.26924378, -0.12006245, 0.26678962, 0.072988346, -0.2085322, 0.0048250603, 0.12894252, 0.07966851, 0.24471562) * g_2;
    result += mat4(0.18590502, 0.0845459, -0.12875262, 0.26096, 0.029233042, 0.36381075, 0.117661506, 0.006412487, 0.20946807, 0.07426911, 0.029169528, 0.0654646, 0.16450708, 0.12593012, -0.109644994, 0.14572893) * g_3;
    result += mat4(0.1973355, -0.2275125, -0.28223652, 0.31719315, 0.3813502, 0.2693579, -0.037815563, -0.16148391, 0.12829015, -0.0030689894, 0.022164742, 0.035949815, -0.3378249, -0.13235879, 0.15883659, -0.17731927) * g_4;
    result += mat4(-0.2885664, 0.14904943, -0.19845994, 0.23251331, -0.30293494, 0.02003626, 0.20378608, 0.27291408, -0.16427508, -0.1587996, -0.22501752, -0.04937006, -0.115756296, 0.09290222, -0.26140857, -0.014537909) * g_5;
    result += mat4(-0.1513065, -0.31879196, -0.2727547, -0.4583672, 0.3103975, -0.09158548, 0.009788355, -0.09834531, 0.011489709, 0.042706747, 0.37254226, 0.15954055, 0.2172001, 0.09373807, 0.29088458, -0.35286763) * g_6;
    result += mat4(0.23374696, 0.33407655, 0.23616461, -0.09521148, -0.14927168, 0.11939751, 0.42869845, -0.16612507, -0.2706815, 0.16172597, -0.5814591, -0.11577833, 0.065650895, -0.3334003, -0.41168052, 0.32357255) * g_7;
    result += mat4(0.3248823, -0.27207342, -0.048840526, -0.217887, -0.018053366, -0.24292938, 0.1603505, 0.06505262, -0.010766065, 0.07076721, 0.22251016, -0.041497335, -0.09878612, 0.2061045, 0.080330074, -0.029014835) * g_8;
    result += mat4(-0.26376098, -0.04971863, -0.03045489, 0.009807002, 0.11108562, 0.0693266, 0.15279642, -0.1372833, 0.18326105, -0.059612468, -0.005589879, 0.021735538, -0.027800532, -0.14984077, -0.116767704, -0.06531209) * g_9;
    result += mat4(0.19206688, 0.21824414, 0.03791829, 0.22117318, 0.01257811, -0.044042267, 0.25616458, 0.082941554, -0.1181948, -0.17940602, -0.20808466, -0.06987383, 0.0019713745, -0.1609917, 0.153718, -0.32214788) * g_10;
    result += mat4(-0.19472712, -0.007020553, -0.36049378, -0.24589752, -0.011828978, 0.38882232, -0.3257698, 0.08382738, -0.09556564, -0.20949766, -0.32732338, 0.08303877, -0.107999764, 0.2836336, -0.0661124, 0.24043255) * g_11;
    result += mat4(-0.1972939, 0.12734106, -0.09953153, -0.45152718, -0.15855458, 0.08746372, 0.11452114, 0.030538268, 0.11946308, 0.17044471, -0.24375156, -0.10093911, 0.19120134, -0.14312318, -0.14860255, -0.1223525) * g_12;
    result += mat4(0.14979935, -0.3136038, -0.25878516, 0.12995318, -0.075706124, -0.104598634, 0.1455947, -0.6167443, 0.06843719, -0.16347055, 0.04413483, 0.08870554, -0.29839858, 0.07214889, 0.049274225, -0.15555117) * g_13;
    result += vec4(-0.004266169, -0.020547107, -0.0031655694, 0.0643683);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf, gxy, result);
}