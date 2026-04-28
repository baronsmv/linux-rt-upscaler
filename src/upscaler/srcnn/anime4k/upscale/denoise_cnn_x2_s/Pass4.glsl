// Anime4K_Upscale_Denoise_CNN_x2_S - Pass 4 of 5 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_last_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.04508749, 0.00222134, 0.013338363, -0.0067310617, 0.099346675, 0.05804196, 0.018694466, -0.008126048, 0.007771997, -0.0072556734, -0.008293339, 0.001518462, -0.06296499, -0.064195156, 0.0727399, 0.044078834) * go_0(-1.0, -1.0);
    result += mat4(0.20800652, -0.016071903, -0.08095607, -0.03472411, -0.20690396, 0.061331827, -0.10627648, 0.12838624, 0.036534917, -0.006113497, 0.029266752, -0.002263159, 0.2937966, -0.05544609, 0.14546311, -0.01290958) * go_0(-1.0, 0.0);
    result += mat4(0.07792222, -7.288649e-05, 0.2800036, 0.019709835, -0.010950291, 0.021879988, 0.037608813, 0.055267945, 0.018646395, -0.016691998, 0.03787624, -0.006547077, 0.03214097, -0.018541625, 0.12142825, -0.070806496) * go_0(-1.0, 1.0);
    result += mat4(-0.009798109, -0.06606263, 0.0010101331, 0.009924258, -0.10272075, -0.07983353, 0.028398676, 0.04967719, 0.12467993, 0.06775066, 0.017111637, 0.012814711, 0.0031143876, -0.0902014, 0.11242646, 0.076476306) * go_0(0.0, -1.0);
    result += mat4(0.07650971, 0.35096344, 0.0612814, 0.06036218, 0.253547, -0.0460987, -0.11145313, -0.48844674, -0.050644107, 0.038706005, 0.19390784, 0.035322774, -0.010191005, 0.58071, -0.2856661, -0.009533105) * go_0(0.0, 0.0);
    result += mat4(-0.071486905, -0.036179904, -0.07303894, 0.19301178, -0.11499898, -0.024847068, -0.0027055284, 0.20373714, -0.09671404, -0.020897992, -0.25572056, -0.008931707, -0.13582602, -0.006546881, -0.16154496, 0.26454738) * go_0(0.0, 1.0);
    result += mat4(0.005463064, 0.006769753, 0.0039625713, 0.014121269, -0.068200685, -0.057850275, 0.008622973, 0.061149873, 0.017436448, 0.11660872, -0.02994459, 0.008590145, -0.03223439, 0.052557915, -0.011846354, 0.03523357) * go_0(1.0, -1.0);
    result += mat4(-0.00015264735, 0.0012872831, 0.021878848, 0.022240406, 0.01822283, -0.008284247, -0.018443186, -0.04997753, -0.111760505, -0.20911667, 0.006166832, 0.14597091, 0.02305932, -0.16312876, 0.023375351, -0.028755601) * go_0(1.0, 0.0);
    result += mat4(0.013701143, 0.010794129, 0.0024321147, -0.018976321, 0.0365032, -0.006783485, 0.01046472, -0.08473902, 0.057523903, 0.029831914, 0.0040916028, -0.2046352, 0.03542, -0.034598, 0.0031058635, -0.20746285) * go_0(1.0, 1.0);
    result += mat4(0.09283864, -0.0035849356, 0.013190911, -0.035437535, 0.035798516, 0.022954805, -0.0029692063, -0.006633743, -0.13456796, -0.011448714, 0.011536131, 0.046695728, -0.0359048, -0.01144856, -0.0027279712, 0.0065755467) * go_1(-1.0, -1.0);
    result += mat4(-0.14295974, -0.0034393691, 0.0051469817, -0.021334402, -0.05882422, -0.003004241, 0.011182507, 0.0015169785, 0.08474255, 0.1255887, -0.23984577, 0.07119401, -0.12547183, 0.038449038, 0.007738907, 0.031506266) * go_1(-1.0, 0.0);
    result += mat4(-0.028237654, 0.010254326, -0.11843009, 0.03034298, -0.038323015, 0.0026470951, -0.060652684, 0.0022312272, -0.022539174, -0.01008126, 0.14868541, 0.02881852, -0.05327277, -0.012296453, -0.21280704, -0.021286633) * go_1(-1.0, 1.0);
    result += mat4(-0.034825645, 0.0877418, -0.009103147, 0.041650586, 0.0135769, -0.005229229, 0.00082947424, -0.0020421906, 0.12402267, 0.007698874, -0.056337915, -0.006580138, -0.018867968, -0.08487179, -0.020938644, -0.029210499) * go_1(0.0, -1.0);
    result += mat4(-0.37082648, -0.30321857, -0.22912364, -0.07368761, 0.15169628, 0.0013253551, 0.09232649, 0.011408914, 0.06347244, -0.377988, 0.13980117, -0.41065913, -0.00040237256, -0.23220152, -0.03643865, -0.10101427) * go_1(0.0, 0.0);
    result += mat4(0.10692653, 0.049867555, -0.011915118, -0.10688069, 0.042109665, -0.017163716, 0.10852331, -0.0088934945, 0.06780516, -0.017808875, 0.26564032, 0.0523693, 0.099033475, 0.042864073, 0.18299587, -0.13503626) * go_1(0.0, 1.0);
    result += mat4(0.07014404, 0.08841395, 0.01895322, 0.0036451078, -0.00933168, 0.044764042, -0.0034986525, 0.010701783, -0.043601245, -0.1375109, 0.0039965697, -0.054331, 0.018830067, 0.040386382, 0.007759782, -0.012478715) * go_1(1.0, -1.0);
    result += mat4(0.024152381, -0.11462646, 0.07005155, 0.0424638, -0.0048070764, 0.06089261, -0.036675487, 0.057459857, 0.02478629, 0.2926517, -0.08248396, -0.053960845, 0.013205341, 0.09851673, -0.04310949, -0.001428641) * go_1(1.0, 0.0);
    result += mat4(0.016168298, 0.009701502, 0.0064305146, -0.068672284, -0.044653386, -0.016051823, -0.015055443, 0.032019246, -0.0829852, -0.011304939, 0.0023902296, 0.30322486, -0.023831543, -0.0046928846, 0.026961725, 0.16314326) * go_1(1.0, 1.0);
    result += vec4(-0.0031417734, -0.002754766, -0.004053268, -0.003937834);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_last_tf, gxy, result);
}