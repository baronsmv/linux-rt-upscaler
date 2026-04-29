// Anime4K_Upscale_GAN_x3_VL - Pass 7 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.0040288265, -0.015393535, -0.07260242, -0.15472066, -0.19534549, -0.39122432, 0.16078798, -0.5742789, 0.15768866, 0.2655791, 0.15935476, -0.047498103, 0.064498045, 0.076590106, -0.4061225, 0.37775257) * g_0;
    result += mat4(0.2614361, 0.017933317, 0.1832562, 0.06045294, -0.4276279, -0.10364118, 0.25701275, -0.19153634, -0.07767676, -0.04028147, 0.48517522, 0.04272645, 0.15032586, -0.009070223, -0.077463955, -0.30442774) * g_1;
    result += mat4(-0.28623474, -0.23038289, 0.24896185, -0.0850123, 0.2147713, -0.04781785, -0.53589386, 0.18313637, 0.14259681, 0.010933099, -0.15293483, -0.3547061, -0.041572977, 0.12857276, 0.07659088, 0.41463402) * g_2;
    result += mat4(-0.23288313, -0.10809953, 0.03761914, 0.11731379, 0.2614991, 0.30079544, 0.09526279, 0.60236603, -0.27493668, -0.059467852, -0.11954311, -0.1494763, 0.1530606, -0.06316779, -0.16075373, -0.19744329) * g_3;
    result += mat4(-0.23136528, 0.15367796, -0.114170656, -0.075603075, 0.115280285, 0.065568104, -0.2712825, 0.08988661, 0.07555022, 0.20744222, -0.17012368, -0.070289165, -0.13714345, 0.047158517, -0.0038408411, 0.42667535) * g_4;
    result += mat4(-0.023408122, 0.21510267, 0.048198875, -0.034309026, -0.4022738, 0.27354932, -0.3187103, -0.08941432, -0.39407676, 0.040392227, 0.30848974, 0.0047349343, 0.074711114, -0.0855602, -0.10068395, -0.29605198) * g_5;
    result += mat4(-0.17653674, 0.079635404, -0.26055837, 0.02086439, 0.09741846, -0.30796355, 0.024595756, 0.004988738, -0.03251247, 0.06604017, 0.21450306, -0.11361557, 0.13276732, 0.14402844, 0.10751112, 0.028939316) * g_6;
    result += mat4(0.28167632, 0.08593957, 0.08560364, 0.09389072, 0.06070772, 0.1481636, -0.2830234, -0.08872352, 0.08137253, -0.17761461, 0.06556175, 0.38331816, -0.04286456, 0.18249401, -0.015249578, 0.1113206) * g_7;
    result += mat4(0.03386872, -0.16347472, 0.046639867, 0.2082717, 0.05713075, 0.22504792, 0.33825234, -0.1434717, 0.14420202, -0.31768665, -0.028941685, 0.295254, 0.07706925, -0.19025062, 0.25294247, -0.08384886) * g_8;
    result += mat4(0.14903983, 0.07136475, 0.15917307, -0.11220863, -0.061577477, -0.24206571, -0.033777636, 0.19905542, 0.25331694, 0.28196925, 0.17308664, -0.20262258, 0.19050619, 0.059853118, -0.29986638, -0.48297527) * g_9;
    result += vec4(0.012018454, 0.019300776, -0.029552516, -0.007941907);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf1, gxy, result);
}