// Anime4K_Upscale_GAN_x2_S - Pass 10 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.09644354, -0.12061228, -0.15139145, 0.010084075, 0.19283041, -0.15289722, 0.0028078665, 0.15971705, -0.03884288, -0.06906346, -0.04772131, 0.32280502, -0.42069855, 0.21643022, -0.8389786, -0.50325495) * g_0;
    result += mat4(0.18034904, 0.037142154, 0.41413367, 0.08413125, -0.14397736, -0.4820656, 0.32794252, 0.2589487, 0.46948192, 0.26964813, -0.07420985, -0.16767345, 0.086358115, -0.10306444, 0.36070088, 0.1681583) * g_1;
    result += mat4(0.35362276, 0.012461055, -0.77784586, 0.09078976, 0.19976044, 0.17758635, -0.37238386, -0.03503108, 0.13998942, -0.37809366, 0.016560063, 0.3934089, -0.25227416, -0.123653956, -0.05106222, 0.005900442) * g_2;
    result += mat4(0.057956465, -0.049570814, 0.0606723, -0.20321843, -0.26415482, -0.27723017, 0.116116256, 0.091267794, -0.14814565, 0.25946814, 0.17341542, 0.14638402, 0.2880723, 0.10809813, 0.025261842, -0.34984475) * g_3;
    result += mat4(0.05510083, 0.17530598, -0.20630372, -0.027601322, 0.017287979, 0.1857018, -0.41756013, -0.14747128, 0.36301833, 0.13361412, 0.021245379, 0.08700895, -0.15968269, -0.32113054, 0.019964505, -0.15953153) * g_4;
    result += mat4(-0.12913038, -0.21853726, -0.14845535, -0.2878481, 0.060428645, -0.12468173, -0.0068141054, 0.044517014, -0.3603185, -0.21329117, -0.029232644, 0.033500195, 0.4367195, -0.048263986, 0.36913735, -0.015526651) * g_5;
    result += mat4(0.15424874, 0.09803074, -0.4081566, -0.24807191, -0.21617292, -0.26116055, -0.19488858, 0.13665622, -0.23223704, 0.13516016, -0.19990326, -0.09589857, 0.2877168, -0.18335378, -0.12726076, -0.01706245) * g_6;
    result += mat4(0.17850566, 0.11283147, 0.0941847, 0.07064274, 0.23485339, 0.053585358, 0.038221374, -0.052291602, -0.085393615, -0.43200582, -0.3899717, -3.6526293e-05, -0.1805902, 0.15160961, -0.25388122, -0.10506431) * g_7;
    result += mat4(0.10518986, 0.4441116, -0.16333202, -0.15620118, -0.025791602, -0.2971725, 0.27621722, 0.15761738, 0.008179799, 0.4354704, 0.8792617, 0.98227674, 0.27862114, -0.28962052, 0.08527341, 0.06820025) * g_8;
    result += mat4(-0.002976883, -0.220515, -0.2764896, 0.03840775, 0.09852327, 0.09890841, 0.6333531, 0.05949176, -0.12757486, 0.12711844, -0.103355624, -0.2612116, -0.92972547, 0.20546664, 0.43557793, 0.14573197) * g_9;
    result += vec4(-0.048349448, -0.027946962, -0.014499015, -0.017825816);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf, gxy, result);
}