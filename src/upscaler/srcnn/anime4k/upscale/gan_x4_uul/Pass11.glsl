// Anime4K_Upscale_GAN_x4_UUL - Pass 11 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf2;
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
vec4 result = mat4(-0.17167501, -0.20074758, -0.091966644, 0.17859644, 0.118206196, 0.34780696, -0.13851282, -0.15981564, -0.076300435, 0.15581897, 0.14410381, -0.15348436, -0.15534315, -0.2340937, -0.11868538, 0.0851946) * g_0;
    result += mat4(0.054577276, -0.2794922, -0.11732257, 0.120796256, -0.1978545, -0.051208086, -0.07047726, 0.15230909, -0.26737535, -0.0122873, 0.026735889, -0.13376889, -0.15112357, 0.07320343, 0.31711194, -0.2877825) * g_1;
    result += mat4(-0.20589454, -0.13458282, -0.014493836, -0.007392441, -0.083313756, 0.0069659096, -0.0074436525, -0.02603582, 0.02844895, -0.03466271, -0.15414406, 0.0131968865, -0.023258701, -0.0410315, 0.16994998, 0.11258594) * g_2;
    result += mat4(0.26200938, 0.086695306, -0.115744606, 0.06443161, -0.2161834, -0.08266891, 0.1765909, -0.20307815, 0.025309294, 0.33511654, -0.0001637002, -0.059903737, 0.101451375, -0.013754625, -0.11448642, -0.09510312) * g_3;
    result += mat4(-0.18455864, 0.036392804, 0.15850407, 0.4627119, 0.022083975, 0.15103343, 0.19111873, -0.06110459, 0.29009378, -0.089215584, 0.0095581515, -0.08869528, 0.15069005, -0.17065643, 0.26667884, -0.14760415) * g_4;
    result += mat4(0.047154248, -0.004531016, -0.15437222, -0.31048393, 0.09027498, 0.08990544, 0.2252978, 0.36424273, 0.15726654, -0.56078666, -0.08649826, -0.22744723, 0.16684572, 0.12967846, 0.12568599, -0.104463704) * g_5;
    result += mat4(0.3277519, 0.05652085, 0.22621375, 0.28361705, -0.19233695, -0.14974803, 0.18974204, 0.2078392, 0.07101538, 0.14084798, 0.11973675, 0.20132545, 0.07275875, 0.093166135, 0.07810121, 0.14855048) * g_6;
    result += mat4(-0.066067055, 0.07116497, 0.16419168, -0.042009585, 0.048940875, -0.14183162, 0.106968045, -0.18822758, 0.16543157, -0.06218013, -0.15914337, 0.13385944, 0.12195849, -0.17245843, -0.11288994, 0.06605676) * g_7;
    result += mat4(0.033830874, 0.27364245, -0.13338806, -0.12021034, 0.0624405, -0.10521141, 0.028734906, -0.06998827, 0.088741004, 0.16279134, 0.26099658, -0.046972543, -0.23423652, 0.15810764, 0.0008583185, -0.29681998) * g_8;
    result += mat4(0.10305078, -0.17637174, -0.07091048, -0.00831249, 0.40148687, 0.20420474, 0.05468663, 0.20745115, -0.12189844, -0.16298126, -0.41976577, 0.018498925, -0.19579916, 0.097037986, 0.110560134, 0.024746) * g_9;
    result += mat4(-0.31636187, -0.06314442, -0.1491463, -0.36367223, 0.13375707, -0.46219668, -0.08560705, 0.00979978, -0.33054784, -0.048843995, -0.5661279, 0.2450401, 0.049516775, 0.05733291, 0.008123728, 0.13401002) * g_10;
    result += mat4(-0.09406586, -0.1038661, 0.18738243, 0.4952333, 0.124727175, -0.1438255, -0.12731665, -0.19241591, -0.29327804, 0.1374427, -0.15773357, -0.21447569, 0.0020323892, -0.032879442, 0.019189913, 0.022784567) * g_11;
    result += mat4(0.27434522, 0.12163328, 0.2289956, -0.12183031, -0.000272515, -0.023530856, 0.099465564, 0.121231996, 0.3175001, 0.124576926, -0.090265624, -0.1386641, -0.20303635, 0.23467141, 0.0842663, 0.42639464) * g_12;
    result += mat4(0.111336865, -0.10426442, -0.22704108, -0.08042834, -0.13705374, -0.06750703, 0.005238288, -0.020887226, 0.04180084, -0.10919923, -0.2624013, 0.017800566, -0.03857038, 0.21999447, 0.028879922, -0.12443005) * g_13;
    result += mat4(-0.021032276, 0.25167516, 0.18236992, 0.021120392, -0.14439242, -0.3752765, -0.4087792, 0.12474052, -0.07753308, 0.24097584, 0.01818881, 0.25023264, 0.3096247, -0.21351217, -0.31819695, 0.01839186) * g_14;
    result += mat4(-0.04455319, -0.33904293, -0.1072782, -0.07438099, 0.21500371, 0.2610481, 0.11105567, -0.07383555, -0.18360671, -0.02730343, -0.19995123, -0.3209995, 0.008217429, -0.1731404, 0.00079199206, 0.058588315) * g_15;
    result += vec4(-0.05414109, -0.03095426, 0.058985617, 0.012448636);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf2, gxy, result);
}