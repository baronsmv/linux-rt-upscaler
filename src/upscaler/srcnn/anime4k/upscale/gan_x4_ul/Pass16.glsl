// Anime4K_Upscale_GAN_x4_UL - Pass 16 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_3_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf3;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_3_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_3_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.014542811, -0.1261262, 0.17474864, -0.18425815, -0.3337646, 0.14748253, 0.09152566, 0.2310806, -0.06578738, -0.3566174, -0.22862534, 0.15323487, 0.01515519, 0.26764703, -0.13214609, 0.09887451) * g_0;
    result += mat4(0.19941364, 0.015275053, -0.022320624, 0.020372959, -0.10664179, -0.28493354, 0.014191545, 0.12122301, -0.045194257, -0.22491856, -0.071520865, -0.020854274, 0.13432617, 0.25484133, 0.018084215, -0.06713652) * g_1;
    result += mat4(0.017183261, -0.056154247, 0.13298456, -0.07631693, 0.18904336, -0.41949302, 0.14992298, 0.11840105, 0.13420148, 0.029390668, 0.017888589, -0.1975919, 0.22601372, -0.061724294, 0.12116033, -0.19753963) * g_2;
    result += mat4(0.020371309, 0.21103396, 0.034326386, -0.23044631, 0.12982637, -0.14810205, -0.23559897, -0.2222485, 0.18240234, -0.17697355, -0.11639408, -0.08132961, 0.039377302, 0.07299684, 0.094041504, -0.13445067) * g_3;
    result += mat4(-0.3512728, 0.09182307, -0.2731474, -0.20885572, 0.07993976, 0.23121795, 0.15620309, 0.3383141, -0.28460538, 0.12850872, 0.1916648, 0.13205391, 0.14932914, 0.041017998, -0.17976354, -0.0014468295) * g_4;
    result += mat4(-0.069909975, -0.23581205, 0.11732144, 0.35232806, 0.3549401, -0.2124837, 0.10403375, -0.09976183, 0.1178997, 0.09910817, 0.061140217, 0.18059346, -0.48723674, 0.037783384, 0.109662086, 0.15543982) * g_5;
    result += mat4(0.11262317, -0.12212692, -0.14394115, 0.15909098, 0.22035566, 0.06488609, -0.2719919, -0.05028129, -0.21462728, 0.17861556, -0.023895046, -0.060819868, -0.17524192, -0.042733762, 0.142835, 0.2747072) * g_6;
    result += mat4(-0.034566112, -0.18427409, 0.09579439, -0.16909808, 0.052964725, -0.058238853, 0.33444786, -0.20727915, -0.31497413, -0.11388015, 0.13721034, 0.19388893, -0.21066165, -0.14097935, 0.030426605, 0.110704474) * g_7;
    result += mat4(0.094303906, -0.23499818, -0.43609008, 0.21279193, 0.39544016, 0.19924188, -0.07611524, 0.012560389, -0.08812965, -0.13701713, 0.01677176, -0.29865423, -0.06948771, 0.14918856, 0.1985359, 0.3003729) * g_8;
    result += mat4(0.014332535, -0.021538176, 0.20930877, -0.029769948, -0.06551115, 0.11966418, -0.08329082, 0.049386136, 0.08940004, 0.16989197, 0.06084547, 0.13855645, -0.10395637, -0.27498555, -0.19077462, 0.043506) * g_9;
    result += mat4(-0.31060696, 0.047150746, 0.22204353, 0.31374148, 0.06301296, -0.007103609, -0.2580888, -0.07127509, 0.11478869, 0.094191864, 0.21567936, -0.06297016, 0.06925183, -0.023501558, 0.16371831, 0.2506513) * g_10;
    result += mat4(0.07425674, 0.012622665, 0.02251264, -0.0731929, -0.008055616, 0.09563007, 0.063964136, 0.24579796, -0.30710867, 0.13981472, 0.025152119, -0.11285761, -0.4419823, -0.026953885, 0.14130811, -0.22058487) * g_11;
    result += mat4(-0.04211301, -0.17002018, -0.13325875, 0.20184138, 0.09686255, 0.054461457, 0.16713423, -0.031002847, -0.26473212, 0.11992785, 0.04697473, 0.051042553, 0.17835025, -0.12469087, -0.3201284, -0.088562444) * g_12;
    result += mat4(0.13638292, -0.033149652, -0.19838256, -0.09581218, 0.0060164076, 0.42301872, -0.07126564, -0.10523957, 0.16030665, -0.20535246, -0.14773448, -0.015409135, -0.24350728, 0.23187117, 0.0220223, -0.039217964) * g_13;
    result += vec4(-0.011449135, -0.002830778, 0.09782809, -0.0067631872);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf3, gxy, result);
}