// Anime4K_Restore_CNN_Soft_S - Pass 2 of 4 - https://github.com/bloc97/Anime4K
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
//    glslc -fshader-stage=compute --target-env=vulkan1.2 \
//          <this_file> -o <output.spv>
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(set = 0, binding = 3) uniform texture2D tex_conv2d_tf;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_1_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.027102098, 0.2640691, 0.1169015, 0.030902913, 0.15404584, 0.1361459, -0.38066056, 0.096569136, -0.111836195, -0.0051853824, -0.0996669, -0.23538585, -0.07060754, -0.18889332, -0.10793357, -0.15154232) * go_0(-1.0, -1.0);
    result += mat4(0.1378689, 0.21024452, 0.010976513, 0.0179521, -0.05993059, -0.28364083, 0.24486947, 0.21347582, -0.12522404, -0.16091396, 0.15499291, 0.08353191, -0.03342411, -0.08964405, 0.25111282, -0.07550899) * go_0(-1.0, 0.0);
    result += mat4(-0.06398718, 0.05763278, 0.021394925, 0.14780094, -0.033050716, 0.03346528, -0.0846797, 0.0125302235, 0.18018652, 0.24586707, 0.050538495, 0.09879243, -0.100035876, 0.043505374, 0.042692907, -0.08768257) * go_0(-1.0, 1.0);
    result += mat4(-0.11572878, 0.0545887, 0.16437739, 0.2775331, 0.10323911, -0.18938646, -0.17097469, -0.188723, 0.085762165, 0.14605838, -0.15568069, -0.16947642, 0.09042493, -0.087587915, -0.041969277, 0.27252352) * go_0(0.0, -1.0);
    result += mat4(0.21475963, -0.018211678, -0.5711054, -0.09235345, -0.20367791, -0.23041399, 0.16346097, 0.007901888, 0.12542121, 0.16807431, 0.09862575, 0.16968751, 0.28490388, 0.40945014, -0.22364445, 0.14460565) * go_0(0.0, 0.0);
    result += mat4(0.27512726, 0.14046481, -0.17684339, 0.102218024, -0.10503195, 0.3080809, 0.03681373, 0.2668656, -0.093752496, -0.07476867, 0.19900662, 0.06028286, -0.19815882, -0.0584525, 0.027984729, -0.02143819) * go_0(0.0, 1.0);
    result += mat4(-0.16829525, -0.06818115, 0.0006509334, 0.01163159, 0.18918815, -0.10731989, -0.008126929, -0.47991323, -0.11022971, 0.19150843, 0.05272113, -0.34417602, 0.022882428, 0.1774031, 0.062597334, -0.09915319) * go_0(1.0, -1.0);
    result += mat4(0.32131585, 0.05668815, -0.34203658, 0.05542482, -0.008077225, 0.009148517, 0.10953332, -0.050969962, 0.09904077, 0.46938205, -0.5148919, -0.22275375, -0.10536104, -0.23662373, 0.002147416, -0.14256701) * go_0(1.0, 0.0);
    result += mat4(-0.19335353, -0.103732094, 0.17156832, 0.0059756916, -0.118641876, 0.14529023, -0.18662338, 0.0447326, 0.026719248, 0.042491894, 0.026437795, 0.05601309, 0.08645617, 0.08365193, -0.039582565, 0.16612953) * go_0(1.0, 1.0);
    result += mat4(-0.014315469, 0.012588422, 0.037587024, 0.08707526, -0.08064868, -0.28149533, 0.27326405, 0.21468583, -0.04278333, 0.29369017, 0.18653142, 0.035729136, 0.079363555, 0.30725953, 0.0147137, 0.08527481) * go_1(-1.0, -1.0);
    result += mat4(0.06659263, 0.03452449, -0.33752796, 0.0066543026, 0.48697233, 0.019602561, -0.32033685, -0.20538871, 0.3089118, 0.4315903, -0.13524854, -0.10791581, 0.3315688, 0.13135147, -0.26904663, 0.142365) * go_1(-1.0, 0.0);
    result += mat4(0.13619833, 0.045271892, -0.029841429, 0.010704955, -0.29257727, -0.10563375, 0.35345638, -0.06734038, -0.043791633, -0.0056891907, -0.078411415, 0.075443126, -0.05746597, -0.19959894, -0.12797245, 0.18837726) * go_1(-1.0, 1.0);
    result += mat4(0.25673476, 0.120482095, -0.23827696, -0.13557845, 0.300447, -0.3008584, -0.13834439, 0.5459493, -0.26155484, 0.06905137, 0.16247983, 0.039960653, -0.023218757, 0.07977591, -0.11354706, -0.25831422) * go_1(0.0, -1.0);
    result += mat4(0.0842605, 0.282916, 0.14062001, 0.06356874, 0.55912817, 0.1743876, -0.30324093, 0.052068707, -0.20756413, 0.27321506, -0.26560605, -0.27695876, -0.3927334, -0.5439608, 0.39293098, -0.001130203) * go_1(0.0, 0.0);
    result += mat4(-0.021890296, -0.12703396, 0.06660714, -0.03164527, 0.0018722567, -0.26552317, 0.06978973, -0.24030049, 0.46008193, 0.5595346, 0.081981994, -0.038414747, -0.010446991, -0.56102365, -0.079274766, -0.01851302) * go_1(0.0, 1.0);
    result += mat4(0.052988984, 0.030581746, -0.06868741, 0.21545182, -0.5706256, -0.0034910638, 0.48361364, 0.9020033, -0.02242781, -0.13256042, 0.08997955, 0.21001706, -0.059571438, -0.040119104, -0.05029196, -0.127414) * go_1(1.0, -1.0);
    result += mat4(-0.08275339, -0.05999088, 0.11068767, 0.014646892, -0.041986465, 0.1028236, -0.17218924, 0.026559748, -0.17412743, -0.38364175, 0.17410514, 0.13038695, 0.23155633, 0.2655843, 0.045085523, 0.13005458) * go_1(1.0, 0.0);
    result += mat4(-0.013383197, -0.064526096, 0.049046878, 0.015992291, 0.123987064, 0.0104690585, 0.07065378, -0.009824511, -0.036109775, 0.13384768, 0.29676288, -0.39475223, -0.009368096, -0.05666906, -0.09132696, -0.082638375) * go_1(1.0, 1.0);
    result += vec4(-0.106538564, -0.065693766, -0.03790106, 0.04776706);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_1_tf, gxy, result);
}