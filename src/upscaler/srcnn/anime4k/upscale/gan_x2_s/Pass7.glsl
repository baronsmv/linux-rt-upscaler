// Anime4K_Upscale_GAN_x2_S - Pass 7 of 17 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.16594207, 0.47900248, 0.15186168, -0.38448718, -0.33396608, -0.12204449, -0.21397614, 0.22567725, 0.2399077, 0.16945037, 0.072409995, -0.015192162, -0.5004075, -0.10852234, 0.14456534, 0.36797065) * g_0;
    result += mat4(-0.03527082, -0.13062008, 0.2529196, 0.16799021, 0.2743078, 0.22924475, 0.4391596, -0.34473032, -0.08008852, 0.14463465, -0.30243787, 0.0352092, 0.49160767, 0.18479864, -0.13473135, -0.40414095) * g_1;
    result += mat4(0.14367065, 0.058683306, 0.091011606, 0.15336677, -0.119622074, 0.04199915, -0.19148684, -0.103310175, 0.116265774, -0.105254985, 0.6245667, -0.26108894, 0.18143174, -0.1839799, 0.048575178, -0.55331755) * g_2;
    result += mat4(0.35027766, 0.03997352, -0.023643266, -0.3330187, -0.10459313, -0.4023968, 0.07325048, -0.09424643, 0.06866858, 0.53465986, -0.44508684, 0.18428375, -0.23138772, 0.027757954, 0.17421234, 0.026670102) * g_3;
    result += mat4(-0.4365351, 0.22217907, -0.6871689, 0.045348447, 0.15043557, -0.48645085, -0.29547492, 0.057184387, -0.03682008, 0.3751258, -0.3201267, -0.17569698, 0.3118066, -0.3671979, 0.41987854, -0.122571744) * g_4;
    result += mat4(0.44111615, -0.40698248, 0.0016049108, -0.25277275, -0.28967234, 0.016609022, 0.5386827, 0.069790244, -0.51845384, 0.024502689, -0.026591584, 0.17351557, 0.12391694, 0.08250939, -0.08813545, 0.43510008) * g_5;
    result += mat4(-0.15770161, -0.27004284, -0.56035084, 0.15914616, 0.22454856, 0.3096621, 0.45845222, -0.008859915, 0.10483775, 0.14181131, 0.026368458, -0.0063670245, 0.24472655, -0.038785648, -0.14339298, -0.10899222) * g_6;
    result += mat4(-0.034405068, -0.2823658, 0.050728954, -0.08360402, -0.11867297, -0.20057304, -0.011291816, 0.08128843, 0.07198962, 0.41366118, -0.40760013, -0.05193347, -0.31802976, 0.11970909, 0.09838232, -0.08124989) * g_7;
    result += vec4(-0.04242169, -0.0033301958, -0.016717333, -0.0006306486);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, gxy, result);
}