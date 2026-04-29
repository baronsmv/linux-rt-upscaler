// Anime4K_Upscale_GAN_x3_VL - Pass 16 of 47 - https://github.com/bloc97/Anime4K
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
vec4 result = mat4(-0.1517466, 0.08653111, -0.12849529, -0.0145909265, -0.20225123, -0.25598082, -0.27031836, -0.11011148, 0.023438375, 0.11201232, 0.46751308, -0.11576917, -0.29880443, 0.04816672, 0.21560355, -0.11404305) * g_0;
    result += mat4(-0.12978144, 0.100125104, -0.06335867, -0.06317281, 0.054012444, 0.018025735, -0.09827809, -0.09725046, 0.005299584, -0.098031715, -0.22854897, 0.17967635, 0.12765448, 0.045635063, 0.0012192138, -0.34536725) * g_1;
    result += mat4(0.011804178, -0.06590833, -0.031301893, -0.1775461, -0.41570944, 0.087449126, -0.02128947, -0.27094513, -0.060209982, -0.18076003, -0.17616534, -0.1265182, 0.05190358, -0.16350612, 0.13440031, -0.02040334) * g_2;
    result += mat4(-0.08296803, -0.28662565, -0.088028625, -0.04346711, 0.17134765, -0.057956398, -0.27708423, -0.11509851, 0.0017504691, -0.1335092, -0.40999198, -0.17734398, 0.32179204, -0.14760494, 0.0014923187, -0.40818754) * g_3;
    result += mat4(-0.06289323, 0.18344052, -0.030397955, 0.26505098, -0.20116702, 0.19888414, 0.22849302, 0.39404854, -0.028509716, 0.108586155, 0.18787633, 0.08936724, 0.2189794, 0.008488558, -0.10159572, 0.28290325) * g_4;
    result += mat4(-0.04573871, -0.110110976, -0.10133858, -0.12086325, -0.2474638, -0.031180179, -0.34253988, 0.15010545, -0.0040049986, -0.019926922, 0.26064172, -0.19498073, -0.1095731, 0.09029125, -0.108377635, -0.0038560093) * g_5;
    result += mat4(-0.121560805, 0.020504333, -0.0597182, -0.09707394, 0.17374295, -0.20030156, 0.10344341, 0.3244939, -0.18901767, -0.020843312, 0.132772, 0.08054658, 0.13611425, -0.29363188, -0.34134823, -0.38264117) * g_6;
    result += mat4(0.16559608, 0.16367547, 0.29445526, 0.22651257, 0.06375283, 0.39584106, 0.006053162, 0.055495188, 0.22115736, -0.22024626, 0.14978565, -0.083540656, -0.14054725, 0.10124253, 0.0061804047, 0.17122638) * g_7;
    result += mat4(-0.14379624, 0.22831523, -0.15875602, -0.019427398, 0.08650438, 0.12258277, -0.0355665, -0.044720147, 0.25487396, -0.26249576, 0.021001643, 0.09981675, -0.039034113, 0.043660853, -0.15347818, -0.16691351) * g_8;
    result += mat4(0.07939632, -0.05486855, 0.2904414, -0.074339755, -0.08656439, -0.20840298, -0.20732778, 0.1029268, -0.20539123, 0.040745974, -0.10717815, -0.25687888, 0.20816644, 0.129532, -0.16312623, -0.14453101) * g_9;
    result += mat4(-0.27986488, -0.23781885, 0.3357808, 0.022635408, -0.23463887, 0.08829273, -0.104331024, 0.059385765, -0.008988081, 0.08307928, -0.10422426, -0.06952313, -0.063950576, -0.39974853, 0.2428403, -0.15027511) * g_10;
    result += mat4(0.073085204, -0.10948135, 0.056989595, 0.18264382, 0.3548214, -0.12389114, 0.08049114, -0.39152363, 0.27634555, 0.13423951, 0.2994666, 0.121581756, -0.3245417, -0.11582107, -0.12750253, 0.17907634) * g_11;
    result += mat4(0.23503982, -0.17774986, 0.14940716, 0.111273095, -0.05475033, -0.17823237, 0.19284964, 0.15520798, 0.1600294, 0.025111979, 0.034554236, -0.22638519, 0.44020715, -0.2762028, 0.111869164, 0.16672193) * g_12;
    result += mat4(-0.25770104, 0.011573565, -0.065385014, 0.036166515, 0.34582734, -0.018427689, -0.06642216, 0.08775443, -0.1237332, -0.102610715, 0.22667718, 0.101304494, 0.53382784, 0.123501934, 0.16460274, -0.048920505) * g_13;
    result += vec4(-0.03949794, 0.0395381, -0.024099527, 0.0041297916);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf, gxy, result);
}