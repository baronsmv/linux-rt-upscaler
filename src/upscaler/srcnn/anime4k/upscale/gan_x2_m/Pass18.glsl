// Anime4K_Upscale_GAN_x2_M - Pass 18 of 23 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_9_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_2 (max(-(texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.22607668, 0.021170171, -0.06774968, -0.019062893, -0.029051676, 0.029224426, 0.097410545, 0.07505055, 0.17470665, -0.025774082, -0.041022647, 0.07615996, 0.031361237, -0.18075092, -0.01981288, 0.30251572) * g_0;
    result += mat4(-0.2228827, -0.18372375, 0.17952546, 0.031262513, 0.10978829, 0.095414534, -0.11202218, -0.017824037, 0.13419671, -0.056704585, 0.086960495, 0.089463, 0.0436869, 0.1987542, -0.24825421, -0.14668585) * g_1;
    result += mat4(-0.2848745, -0.09242928, 0.24002336, -0.06059541, -0.0066300016, 0.050746392, -0.26092768, -0.060129635, -0.2699064, -0.13927452, 0.3134039, -0.21668927, 0.0028670141, 0.044556674, 0.040246494, -0.26040232) * g_2;
    result += mat4(0.08408219, -0.038882803, -0.08522774, 0.1714629, -0.03067602, -0.10863579, 0.072058044, -0.012343554, -0.0076697394, 0.17840211, -0.2823912, 0.11976201, -0.05657313, 0.092938855, -0.060931504, 0.06991858) * g_3;
    result += mat4(0.09868284, 0.054261737, 0.13327791, -0.14897001, -0.06348394, 0.11385057, 0.09684055, -0.084950894, -0.3038146, -0.08645148, 0.035114545, -0.07148952, -0.15862693, 0.26620075, -0.018059343, 0.35772058) * g_4;
    result += mat4(-0.4964452, -0.32340884, 0.5129584, -0.090460144, 0.28658384, -0.117274396, 0.25311428, 0.119918026, 0.27442876, -0.19332558, -0.40261742, -0.0627285, -0.36318043, -0.07865861, -0.11114984, -0.1290027) * g_5;
    result += mat4(0.42158237, -0.032889403, 0.034080755, 0.25719455, -0.18799819, 0.0981468, 0.22785765, -0.07262642, 0.22532979, -0.09519116, -0.1005627, 0.1767603, -0.100850165, -0.06818755, 0.0059797456, -0.0718568) * g_6;
    result += mat4(0.12787001, -0.20670003, 0.0034799385, -0.024907416, 0.04423561, -0.13276835, -0.102332935, 0.14673741, 0.08700579, 0.08124997, -0.009865786, 0.041748982, -0.076119795, 0.09744985, 0.13542135, 0.12240728) * g_7;
    result += mat4(-0.1702021, 0.18497302, 0.06786661, -0.09040049, 0.15212716, 0.055503774, 0.020584844, 0.24927403, 0.23556694, -0.1571619, -0.02012801, 0.08423509, -0.114376806, -0.04171382, 0.040876187, -0.116261706) * g_8;
    result += mat4(-0.0854133, -0.023111762, 0.3320211, -0.21760856, -0.169973, 0.22671382, 0.4513697, 0.35962802, -0.1499719, 0.24696982, -0.29979527, 0.006662296, 0.20241787, -0.2276791, 0.059445832, 0.18853071) * g_9;
    result += mat4(-0.026398154, 0.124663144, 0.20381314, 0.2053697, 0.010302614, -0.050437275, 0.033807695, 0.014369258, -0.20720173, 0.05919782, 0.008449617, -0.31949872, 0.011598942, -0.0432789, 0.12732887, 0.049919438) * g_10;
    result += mat4(-0.06617085, 0.023928246, 0.1698239, 0.19584818, 0.022199618, -0.0040151025, -0.14364237, -0.06734091, 0.49634683, 0.40206975, -0.023004102, 0.16953272, 0.13243976, -0.47359994, 0.18358715, -0.15007599) * g_11;
    result += mat4(0.03754883, -0.84370553, -0.0057923268, -0.06449944, 0.09488198, -0.09577232, 0.31362334, -0.09768442, 0.15369056, -0.16346063, 0.41194627, 0.10364933, -0.2073915, -0.15944852, -0.57649344, 0.1580545) * g_12;
    result += mat4(-0.3224099, -0.17332473, 0.12429976, -0.12284861, 0.32270268, 0.2888736, -0.20192772, 0.15415959, -0.10240418, 0.09524166, -0.14117688, -0.1239787, 0.0015336396, 0.10390812, 0.20461708, -0.12672688) * g_13;
    result += vec4(0.01866206, -0.01430976, -0.04231479, 0.06331023);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf1, gxy, result);
}