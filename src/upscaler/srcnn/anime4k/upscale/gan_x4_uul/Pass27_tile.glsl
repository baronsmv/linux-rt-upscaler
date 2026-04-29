// Anime4K_Upscale_GAN_x4_UUL - Pass 27 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_6_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_6_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_6_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_8_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_9_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.16280368, -0.3007647, -0.40942207, 0.030815337, 0.07405667, -0.2774033, -0.17283231, 0.29439998, 0.3699874, -0.3105887, -0.14847368, -0.19395609, 0.0452973, -0.007050749, -0.1077042, 0.09585097) * g_0;
    result += mat4(0.18247014, 0.009975951, 0.22485235, 0.027747832, -0.23668393, 0.4114013, -0.051324457, -0.1639705, -0.05903238, -0.23907724, 0.028307369, 0.26740846, 0.15824945, -0.45980626, -0.2874741, -0.08889109) * g_1;
    result += mat4(0.10361935, -0.3442958, -0.14365837, -0.099617116, -0.032554094, -0.14120267, -0.03342406, 0.05498335, -0.055517945, 0.17825112, 0.07104187, -0.06683212, 0.057972897, 0.118643604, -0.16706169, 0.054418873) * g_2;
    result += mat4(0.011006017, 0.07820084, -0.13500318, 0.1641914, -0.009132727, -0.16969028, 0.10708101, 0.1584649, 0.06537785, 0.012797735, 0.33862048, 0.11651383, 0.013557928, 0.2422241, 0.1017567, 0.062895164) * g_3;
    result += mat4(-0.051137764, 0.21534863, 0.028179698, -0.43167275, -0.033175964, -0.31094325, 0.117865756, 0.14298838, 0.2600347, 0.06622512, 0.23248197, 0.05236919, 0.057206035, 0.31706086, 0.35474834, -0.08026979) * g_4;
    result += mat4(0.3341866, 0.061472543, 0.08820765, 0.18130043, -0.23067175, 0.020398427, 0.2055998, -0.043249145, 0.059176553, 0.15833625, -0.038501732, -0.19359344, 0.013098893, -0.113447286, -0.14451598, -0.07114495) * g_5;
    result += mat4(-0.14045192, -0.035960864, 0.1683667, -0.057710778, -0.12191498, 0.30514076, 0.25296882, 0.05210337, -0.30406678, 0.32372236, -0.08775911, 0.05305385, -0.09910785, 0.08077384, -0.030429823, -0.23029453) * g_6;
    result += mat4(-0.06477132, 0.051194742, 0.054058783, -0.08651901, -0.11611027, -0.1414096, 0.017515467, 0.08065079, 0.160593, 0.053242017, 0.16833569, 0.2509967, -0.08866564, -0.027160924, 0.18210976, -0.018735442) * g_7;
    result += mat4(-0.07765899, -0.08653451, 0.018404264, 0.037747417, 0.29692903, -0.21028307, -0.1398246, -0.18331608, -0.14643049, -0.062120195, -0.026070742, -0.016461093, 0.13776016, 0.16835451, 0.19926657, 0.009491423) * g_8;
    result += mat4(0.22430605, 0.13225609, 0.11127026, 0.11934834, 0.11773516, 0.38065204, 0.029911561, 0.02016507, -0.04952572, -0.03617535, -0.13657878, 0.27129802, -0.1468153, -0.15232307, 0.29422712, 0.21878105) * g_9;
    result += mat4(0.1451605, -0.1307874, 0.15195362, 0.37169486, -0.3883121, 0.1892302, -0.011653311, -0.117176816, -0.058879364, 0.006502772, 0.0759263, -0.09286256, 0.022827929, 0.07008768, -0.042277794, -0.087980986) * g_10;
    result += mat4(-0.20223801, 0.63388115, 0.2666767, -0.16103297, -0.24565355, -0.0149277, 0.12688118, 0.010536548, 0.2465687, 0.11190481, 0.049540646, -0.17695107, -0.2384947, 0.060365606, 0.17545441, 0.07588929) * g_11;
    result += mat4(0.09111966, -0.11593248, 0.08454782, 0.288044, -0.07772475, -0.01816507, -5.096444e-05, -0.3003771, -0.03312577, 0.06330272, -0.06429025, 0.2540652, 0.112343386, 0.0268587, -0.3007914, 0.14403644) * g_12;
    result += mat4(-0.028090911, -0.10009091, 0.03360372, -0.41311288, -0.14364164, 0.033205803, 0.028351944, -0.36008695, 0.08499348, -0.08054039, 0.0008087064, -0.29299152, -0.12959489, -0.041748602, -0.02607873, -0.002198112) * g_13;
    result += mat4(-0.08168162, -0.18030183, -0.14979859, -0.0023758279, 0.11401735, 0.1793914, -0.019655662, 0.13919011, 0.04981195, -0.1512701, -0.2777071, -0.092032805, -0.0956048, -0.2193873, -0.22983249, -0.051276267) * g_14;
    result += mat4(0.036644854, -0.23420666, -0.4380995, 0.026250768, -0.1633289, -0.124186166, 0.092637315, -0.027536578, -0.24723285, 0.10599731, -0.16287865, -0.14084546, -0.054123025, 0.10922608, -0.06295828, 0.11139063) * g_15;
    result += mat4(-0.0057521244, -0.17863722, -0.28339812, 0.12678196, -0.008798941, 0.25797576, 0.14833443, -0.06494317, -0.10480434, 0.22954331, -0.15336959, -0.0017664762, -0.155693, -0.23341124, -0.10721382, -0.18765664) * g_16;
    result += mat4(0.1479779, 0.026514363, 0.150549, 0.043383703, 0.060286276, -0.012992416, 0.11384509, -0.04252127, 0.08395568, -0.086466804, -0.044825606, 0.0600901, 0.36257893, 0.10778409, 0.32519555, -0.17719778) * g_17;
    result += mat4(0.019650197, -0.2552763, 0.111707225, -0.028414596, -0.18420072, 0.24862765, -0.27289316, 0.15587737, 0.10823723, 0.18660492, -0.17082447, 0.6391233, -0.11903236, 0.20687774, -0.120824836, -0.103811845) * g_18;
    result += mat4(-0.25654075, 0.11822941, 0.002077498, -0.18428631, -0.13948499, 0.22262993, 0.07610168, -0.041798126, -0.08393731, -0.05455519, 0.017154181, 0.40815148, 0.019547334, -0.19381055, -0.09170064, 0.092561185) * g_19;
    result += vec4(-0.0025385008, -0.009322316, 0.023430334, 0.03963271);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf2, ivec3(valid_xy, tile.inputLayer), result);
}