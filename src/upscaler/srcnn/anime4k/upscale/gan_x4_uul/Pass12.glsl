// Anime4K_Upscale_GAN_x4_UUL - Pass 12 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf3;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.15813187, 0.15032968, -0.358124, 0.054663192, -0.25664124, -0.047136743, 0.024661854, 0.29019728, -0.1586862, -0.12748682, 0.40721273, 0.02187444, 0.011839724, -0.41867453, -0.2442098, -0.24595131) * g_0;
    result += mat4(-0.15485683, 0.31738782, -0.3137046, 0.082112595, 0.0737305, 0.11812223, 0.19734107, -0.18905711, 0.088300474, -0.16933976, 0.15907732, -0.11422951, -0.056749936, -0.373262, -0.06974283, -0.2820898) * g_1;
    result += mat4(-0.26680642, 0.19024834, 0.002037017, -0.064218, -0.15495898, 0.2750016, 0.23787461, -0.17998067, -0.012667507, 0.27450457, 0.24563935, 0.21562263, -0.0075859334, -0.08958551, -0.093937464, -0.078713246) * g_2;
    result += mat4(-0.17318735, -0.008759622, 0.15150657, 0.2992114, 0.022198962, -0.07318335, -0.14881803, 0.13562077, -0.0022031132, -0.19316684, 0.2535826, -0.05084298, -0.32218117, 0.1267631, -0.042296994, 0.036732808) * g_3;
    result += mat4(0.25161934, -0.09492602, 0.13423127, 0.032517985, -0.06686973, -0.061583497, -0.1828305, 0.122823365, -0.21438296, -0.30841893, 0.1731841, -0.29667705, -0.29025105, 0.13186353, -0.043046407, -0.34681532) * g_4;
    result += mat4(-0.14662783, -0.11100817, 0.073842436, -0.14357355, 0.24532394, 0.061293274, 0.037153088, -0.08022293, 0.11296792, 0.25762567, 0.1803339, 0.24524696, -0.06480696, 0.06504735, 0.04941994, -0.20177524) * g_5;
    result += mat4(-0.06278919, -0.25327423, 0.08713618, -0.11191733, 0.33828825, 0.058243927, 0.05450901, -0.37079945, 0.08136556, 0.24741262, -0.27361023, -0.068275, 0.050629843, 0.21304448, 0.2734626, -0.16750076) * g_6;
    result += mat4(0.11121274, -0.115385205, 0.22477418, -0.06725809, -0.15530252, -0.031487826, -0.17961866, 0.025540952, 0.08094816, 0.22538602, -0.1449456, 0.033616643, 0.11810663, 0.1127742, 0.17407128, 0.059245285) * g_7;
    result += mat4(0.43453342, -0.12170353, 0.09817627, 0.14755897, 0.17435667, -0.22251855, -0.32671428, 0.107192695, 0.26639727, -0.2892611, -0.1413853, -0.082134426, 0.016464738, 0.08648902, 0.06256596, -0.023842275) * g_8;
    result += mat4(0.3739318, 0.118386924, -0.10602344, 0.051698774, 0.116221406, -0.34542432, -0.13280031, -0.53044075, -0.19284041, 0.14490364, -0.2050812, 0.12533414, 0.22506653, -0.07526672, 0.035203286, 0.026242174) * g_9;
    result += mat4(-0.5327144, 0.1649795, -0.11507187, -0.234499, 0.061057597, 0.06764596, 0.20559542, -0.07742593, 0.2165637, -0.1549744, 0.026953368, 0.3037089, 0.110090226, -0.1258564, 0.13759027, 0.16844687) * g_10;
    result += mat4(0.24411613, -0.004854083, -0.009286953, -0.00086425553, -0.22064768, 0.0014907656, -0.08684952, 0.029716417, -0.241052, -0.13597979, -0.10451872, -0.26793602, -0.08911106, 0.024757262, 0.17348441, 0.29419208) * g_11;
    result += mat4(-0.07577307, 0.030659143, 0.97284687, -0.09018963, 0.059575, 0.09799077, 0.065673314, 0.22537662, -0.0015259798, 0.24301144, -0.09336371, -0.14226802, -0.33286256, 0.027389184, -0.5026264, -0.15279126) * g_12;
    result += mat4(0.14727022, -0.10878168, -0.1100343, 0.12144918, -0.03657926, -0.029442519, -0.0017414992, -0.2532462, 0.18112376, -0.058077507, 0.35388008, 0.32712713, 0.17805058, 0.13992003, 0.17930086, 0.39848652) * g_13;
    result += mat4(-0.25576255, 0.18205768, 0.08984218, 0.10292959, -0.15820667, -0.090718776, 0.1579229, 0.43783715, 0.078025974, 0.21724561, -0.25238967, -0.23599494, -0.08510723, 0.17738545, 0.13962658, 0.16159406) * g_14;
    result += mat4(-0.11219203, 0.075433955, -0.11129301, -0.09385265, 0.22908452, 0.051752828, -0.0993372, -0.2636262, 0.04221882, -0.37118244, -0.1460174, 0.11764387, 0.22468969, -0.197521, -0.13387764, 0.30982286) * g_15;
    result += vec4(0.0379655, 0.052258957, -0.017226165, -0.0132343555);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf3, gxy, result);
}