// Anime4K_Upscale_GAN_x3_L - Pass 13 of 30 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_3_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.21563801, -0.12204513, 0.31932783, 0.28290224, -0.17011476, -0.06448831, 0.004365267, -0.07169507, 0.21165244, -0.07712424, 0.14979824, 0.2240992, 0.48357385, -0.015724417, -0.3836641, 0.07599027) * g_0;
    result += mat4(-0.20743755, -0.119118474, 0.1009234, -0.2842955, -0.24531132, 0.062108602, 0.11733637, 0.06687575, -0.065953426, 0.15715389, 0.21475503, -0.1019138, 0.08085453, -0.24522887, -0.108375534, 0.29179853) * g_1;
    result += mat4(0.16713834, 0.030504826, -0.2423963, -0.41885766, -0.20249867, -0.061683156, -0.14999944, 0.54505223, 0.16486095, -0.023248592, -0.17566164, 0.089543514, -0.1884646, 0.15263423, 0.14438081, -0.21730141) * g_2;
    result += mat4(0.37399703, 0.2731133, 0.11279373, 0.004775496, -0.19443156, -0.071899086, 0.17512012, -0.11265631, 0.01926881, -0.31321192, -0.32160205, -0.23714963, 0.097321026, 0.13937393, -0.28038052, -0.046872586) * g_3;
    result += mat4(0.124041334, 0.083966166, 0.13945055, 0.087915726, 0.11154068, -0.09223973, -0.012948238, 0.16114026, 0.13717382, 0.11968761, 0.076536775, -0.15866219, -0.19017774, -0.11172013, 0.024816172, 0.096302085) * g_4;
    result += mat4(0.081017025, -0.1537902, 0.193927, 0.22226687, 0.441012, 0.18478638, 0.30040395, 0.032401927, -0.13839063, 0.017778423, -0.42750338, -0.19760555, -0.21953818, -0.2148397, -0.084683254, 0.20916465) * g_5;
    result += mat4(-0.3921892, 0.2123992, 0.14027761, 0.10175143, -0.11134986, -0.16432697, -0.1097465, -0.21807413, -0.09732297, -0.11108596, -0.39636138, -0.06654249, 0.18766358, -0.0061503067, 0.1286225, 0.2418667) * g_6;
    result += mat4(-0.0039234986, 0.17088562, 0.12906016, -0.13476452, -0.09124947, 0.3098052, 0.09895542, 0.18631962, -0.06776231, 0.19485205, 0.14722902, 0.32147923, -0.1811334, 0.15313488, 0.0796922, 0.0012897709) * g_7;
    result += mat4(0.032229863, 0.025498863, 0.06695979, 0.019412167, -0.16543043, -0.12314033, 0.112201385, 0.16554663, 0.13644108, 0.3098045, 0.081390016, -0.006008416, -0.016406069, 0.22883923, 0.22282913, -0.13947442) * g_8;
    result += mat4(0.010251363, 0.08210024, -0.33465254, -0.012109372, 0.027115503, 0.1481351, -0.081793204, -0.20716506, 0.0056828605, -0.30995828, 0.11498873, 0.15678942, -0.061227474, -0.14681229, 0.1498136, 0.11219651) * g_9;
    result += mat4(0.21796124, -0.12195326, 0.44734144, -0.124715045, -0.05986958, -0.25252253, -0.13802508, 0.16756216, 0.28327593, 0.38355786, -0.27178785, -0.19969118, -0.26010805, -0.074593216, 0.10679648, 0.15610766) * g_10;
    result += mat4(-0.07648412, -0.18866923, -0.2592641, 0.32486007, -0.6200149, 0.09312683, 0.42827863, -0.2703639, 0.08144911, -0.054994784, -0.24911343, 0.41974616, 0.036914464, -0.32325324, 0.012920313, -0.48379797) * g_11;
    result += vec4(-0.013587518, 0.049618572, -0.065549955, -0.007242324);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf2, gxy, result);
}