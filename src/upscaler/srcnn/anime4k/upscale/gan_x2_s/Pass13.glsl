// Anime4K_Upscale_GAN_x2_S - Pass 13 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_1 (max(-(texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.2967133, -0.18581349, -0.03749059, 0.30880052, -0.11064016, -0.23309472, 0.05572459, 0.04502667, -0.12098995, 0.1875494, 0.17095889, 0.008563628, -0.16092524, 0.03845401, 0.1908294, 0.10556762) * g_0;
    result += mat4(0.23697758, 0.11629349, 0.19466121, -0.41413772, -0.20402254, 0.0062864223, -0.13700421, -0.10543815, -0.03498975, 0.02710536, -0.32383642, 0.12299909, -0.06849518, -0.005379719, 0.15714374, -0.15514039) * g_1;
    result += mat4(-0.17502604, -0.24644612, -0.13557185, -0.16728596, -0.024457034, -0.28457522, 0.13460088, -0.21639405, 0.057475664, 0.1473123, 0.19220911, -0.12668033, 0.67518485, -0.36505973, -0.16904399, -0.010216019) * g_2;
    result += mat4(-0.15164074, 0.2532923, -0.13278177, -0.11557631, -0.23019886, 0.115244605, 0.010407434, 0.044481948, -0.36745974, 0.6252675, -0.7489445, 0.31991, 0.04725299, 0.32507753, 0.3035176, -0.18355042) * g_3;
    result += mat4(0.11328097, -0.09094802, -0.03745151, 0.12965176, 0.0051720524, 0.028558291, -0.047848992, 0.23055501, 0.18047509, -0.07151716, 0.05670166, -0.008592144, -0.092078224, -0.013172229, -0.017855234, -0.07338865) * g_4;
    result += mat4(0.123723745, -0.06312486, 0.0427355, -0.11981472, 0.028110307, 0.2275076, -0.019800344, -0.10352946, -0.23628815, 0.24896589, -0.07624697, -0.21491022, -0.13148311, 0.27282125, -0.053250857, -0.15992334) * g_5;
    result += mat4(-0.23408101, 0.20139061, 0.0035646914, 0.16009186, -0.1912387, -0.0066828816, -0.13681525, -0.22325766, -0.056139376, -0.0638933, 0.0681208, 0.041838214, -0.016192758, 0.19360517, -0.21080317, 0.113634475) * g_6;
    result += mat4(0.1369719, 0.18950021, 0.019468868, -0.08180063, -0.31615034, 0.028354429, -0.1489749, -0.096815735, 0.22448029, 0.16501611, -0.11709639, -0.047612794, 0.10514418, -0.07882259, 0.2664075, 0.19011621) * g_7;
    result += mat4(0.13804765, 0.01748137, 0.18502045, 0.058146507, -0.5661739, 0.14128609, -0.25875592, -0.6150388, -0.031642724, 0.3204696, -0.021026978, -0.3983191, 0.08609409, 0.0042772954, -0.3754959, -0.19454613) * g_8;
    result += mat4(0.09550674, 0.26413566, -0.15292425, -0.13285659, 0.14078279, 0.08191184, 0.066060774, -0.02605145, -0.08946464, 0.11715431, 0.05521046, -0.03218011, -0.31606913, -0.011917866, 0.11926112, 0.145299) * g_9;
    result += mat4(0.71071726, -0.8614542, -0.050295915, 0.41341305, -0.38318273, 0.1269644, 0.46467987, -0.15950991, -0.75483114, 0.6358254, -0.19257315, -0.5991311, 0.10807353, 0.083646335, 0.032484207, -0.20280145) * g_10;
    result += mat4(-0.21395132, 0.37320906, 0.30284703, 0.054482624, 0.10859697, 0.21301107, -0.09715497, -0.047609363, 0.40013343, -0.22015318, 0.09944949, 0.4283713, 0.1767619, 0.15653327, -0.01787549, 0.22862214) * g_11;
    result += vec4(0.06043013, -0.057747327, -0.0260778, 0.034383494);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf, gxy, result);
}