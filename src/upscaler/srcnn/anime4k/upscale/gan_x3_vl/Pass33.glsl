// Anime4K_Upscale_GAN_x3_VL - Pass 33 of 47 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_15_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_15_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_15_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_17_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_18_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_15_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_15_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_15_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_15_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_15_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_15_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_17_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_17_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.006507618, 0.35551, 0.10029036, 0.20938163, -0.27909538, 0.107799135, -0.117420286, 0.017393347, -0.07090822, 0.067006424, -0.025181938, 0.06960745, 0.050213918, 0.11024797, -0.06292335, -0.28821605) * g_0;
    result += mat4(-0.07828812, -0.24313068, -0.041977264, 0.28533673, -0.046961866, -0.0382004, -0.06722913, 0.046214554, -0.015937736, 0.2662867, -0.11650494, -0.03243863, 0.20631221, 0.01906351, 0.20938441, 0.063740134) * g_1;
    result += mat4(0.2477787, -0.15261632, -0.09109093, 0.16242526, 0.030849725, 0.36562842, -0.24916211, -0.2537, -0.0005451666, 0.040962283, -0.12698911, 0.1940532, -0.0031755446, 0.16081375, -0.31149757, 0.24105449) * g_2;
    result += mat4(0.15018864, -0.0975225, 0.16312592, -0.023348464, 0.025320804, 0.08907452, -0.20382877, 0.14941658, -0.025980422, 0.2518956, 0.37375775, 0.0670902, 0.21562299, 0.096583225, 0.24626857, -0.1689578) * g_3;
    result += mat4(0.032749493, 0.26481724, 0.16459878, -0.1093412, 0.35898176, -0.08814589, -0.19542596, 0.35450563, 0.34313765, 0.082954384, 0.06760144, -0.13203524, 0.08626903, -0.082864255, 0.3760177, -0.052356176) * g_4;
    result += mat4(-0.22347268, -0.23800248, 0.22216137, -0.1334753, -0.0019713258, -0.117614284, 0.2928468, -0.022849852, 0.09592314, -0.0526934, 0.07753605, -0.21934861, -0.1660914, -0.2673251, 0.032538224, 0.0033737908) * g_5;
    result += mat4(0.4056822, -0.22801818, -0.009285619, 0.20891581, -0.12555836, -0.1479676, -0.15377103, 0.091794685, 0.18693839, 0.029455252, -0.28683576, -0.01816607, 0.034140516, 0.21041095, -0.031228764, -0.20486769) * g_6;
    result += mat4(-0.016693812, -0.25051102, 0.250197, -0.143388, -0.012325928, 0.0013464197, -0.045613196, -0.13748543, -0.023561578, -0.03421223, 0.08587755, 0.36944443, 0.0090245735, -0.07692534, -0.21768387, 0.11940026) * g_7;
    result += mat4(0.14990924, -0.15969902, -0.24874954, 0.25423834, 0.047977734, -0.11828463, -0.07667344, -0.07940479, -0.033960067, -0.19987972, -0.07886391, -0.1691948, -0.059108987, 0.12546931, -0.09120288, -0.2301952) * g_8;
    result += mat4(0.07120231, 0.11496656, 0.11952848, 0.06014948, 0.07809767, 0.10536339, -0.11122203, 0.28110188, 0.014941528, -0.0792158, 0.23271102, 0.1513328, -0.14564197, -0.0053231698, 0.06846381, -0.05170115) * g_9;
    result += mat4(0.14952776, 0.1830435, 0.0693483, -0.12810285, -0.2411923, 0.02373353, 0.09710389, -0.00886689, -0.075813554, -0.15807281, 0.019722076, 0.122158974, -0.08879681, 0.1176225, 0.023886852, 0.009521271) * g_10;
    result += mat4(-0.12003659, 0.25038052, -0.09751039, -0.21425623, 0.05037122, -0.30314568, 0.056634273, 0.049238324, 0.06321857, 0.058443442, 0.067801915, 0.24130674, 0.10302721, -0.22205399, 0.008704116, -0.10264142) * g_11;
    result += mat4(-0.12898026, 0.09346042, 0.29941607, -0.04953118, -0.1304296, -0.0008984169, -0.04556631, -0.14597142, 0.063871995, 0.06488008, 0.08948201, 0.23473148, -0.20545703, 0.10851978, -0.025103066, -0.23575859) * g_12;
    result += mat4(0.13659224, 0.08942274, -0.20569776, 0.017678559, 0.09806826, 0.15677394, 0.15822731, 0.029734695, -0.08716191, -0.01778334, -0.13599, -0.16893873, -0.30254295, 0.18124272, 0.051892713, -0.18010335) * g_13;
    result += mat4(-0.002885469, 0.009502494, 0.12664194, 0.21007413, -0.08120904, 0.04213149, -0.19298813, -0.09197216, -0.11336129, 0.026870906, 0.11918877, -0.07471192, 0.07715422, -0.28567305, -0.0050871065, -0.0589191) * g_14;
    result += mat4(0.11605678, 0.017162867, -0.00952252, 0.12467068, 0.118510686, -0.186823, -0.13314165, 0.027390392, 0.19537403, 0.21234393, 0.3235463, -0.041289236, 0.07744967, 0.36400458, 0.25095546, 0.09901454) * g_15;
    result += mat4(-0.17919436, 0.1251613, -0.18175727, 0.021816947, -0.04216387, 0.10944426, 0.02161377, -0.0076910397, 0.03792699, 0.04829799, 0.16696233, 0.27722096, -0.15549976, -0.0015638673, -0.046067294, -0.21890913) * g_16;
    result += mat4(0.02248908, -0.25410384, 0.23302642, 0.013278944, 0.04128571, -0.1978489, -0.068986565, 0.06931732, 0.07257194, 0.10191749, -0.10704886, -0.07942535, 0.10373902, -0.33918902, -0.097765245, 0.35452053) * g_17;
    result += mat4(0.10310988, -0.36429033, -0.17563991, -0.33056924, 0.10157224, -0.26683134, 0.10698191, 0.09721982, -0.3825923, 0.011767701, 0.19865969, 0.22241755, -0.16556083, 0.021593302, -0.2107391, -0.20859967) * g_18;
    result += mat4(-0.16120493, 0.2403295, -0.25938925, 0.13073151, -0.11099456, -0.19550775, -0.21077448, -0.18629125, -0.082744755, -0.04692217, -0.2137643, 0.19053587, -0.11437479, 0.02856005, 0.3253954, 0.12590827) * g_19;
    result += vec4(-0.013902712, 0.006466277, -0.021404289, -0.029253915);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf2, gxy, result);
}