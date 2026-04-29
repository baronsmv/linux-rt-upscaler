// Anime4K_Upscale_GAN_x2_M - Pass 20 of 23 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_12_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_12_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
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
#define g_14 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.3378193, 0.013861057, 0.19208853, -0.05050854, 0.08691835, 0.16724123, 0.10351982, -0.40157926, -0.055889476, -0.040115904, -0.13351472, -0.7937818, 0.18700145, 0.109559685, -0.119053595, -0.12651901) * g_0;
    result += mat4(0.05863214, -0.011048432, 0.22007701, -0.21624403, -0.06139813, -0.06766812, 0.022506371, 0.17585056, -0.37994936, -0.018394569, 0.5127985, -0.19700864, -0.07880973, 0.15687309, -0.12574019, -0.19570859) * g_1;
    result += mat4(0.5059051, -0.010676642, -0.47922808, -0.017590942, -0.20583269, -0.10777252, -0.33185184, -0.0025075034, -0.1518394, 0.14268444, 0.005011664, 0.09016961, -0.46011007, -0.09428751, 0.34915137, 0.13334215) * g_2;
    result += mat4(-0.15615676, 0.09427065, 0.006016912, -0.0003997069, 0.16170138, 0.09666374, 0.14158808, -0.23772424, 0.39373854, 0.004074768, -0.28073287, 0.0032489141, 0.23473479, -0.12678933, -0.24589436, -0.21988034) * g_3;
    result += mat4(-0.12682347, 0.033012364, 0.18928578, 0.12523666, 0.12809147, 0.008567846, -0.10653368, -0.03712133, 0.075765386, -0.042196997, 0.039182812, 0.17273012, 0.21258987, 0.039698593, -0.0018848967, -0.07930902) * g_4;
    result += mat4(0.013454855, -0.18023406, -0.49323913, -0.032017395, 0.11903338, -0.043025218, -0.46579728, 0.21894619, -0.21387324, -0.13455649, 0.30638975, 0.3472243, 0.09305909, -0.015791988, 0.071368046, -0.038680866) * g_5;
    result += mat4(0.012506262, 0.09754124, -0.092920735, 0.23061672, 0.08051618, -0.38472125, 0.17626029, 0.009075537, -0.18316247, -0.1338181, 0.2650675, 0.0516641, 0.080453254, 0.22033659, -0.13004474, -0.07781194) * g_6;
    result += mat4(-0.12412428, -0.11978811, 0.06780084, -0.1710261, -0.09355731, 0.31283846, -0.022725523, -0.16437142, -0.11865966, 0.10907317, 0.22463441, 0.017325362, 0.02512185, -0.49577957, 0.2016018, 0.14196795) * g_7;
    result += mat4(0.02570746, 0.22231244, -0.10168496, -0.21518417, -0.0054759895, -0.32655567, -0.34048972, 0.11826245, -0.002854444, -0.11257602, -0.09318273, -0.10332744, 0.078923725, -0.11612356, -0.030546617, -0.12474622) * g_8;
    result += mat4(-0.11420135, -0.24489257, 0.15446539, 0.12646616, -0.07092042, 0.110105604, 0.054362826, 0.07867222, -0.15557991, 0.071640015, 0.21894808, 0.24164975, 0.0062167975, 0.10681122, -0.32373384, 0.06931269) * g_9;
    result += mat4(0.0769479, -0.09528171, -0.38724712, 0.010703831, -0.016925508, -0.018486671, 0.035855293, -0.17932071, -0.078450575, -0.036463127, 0.20942347, 0.060895607, -0.16549253, -0.008952913, 0.20420915, -0.009001661) * g_10;
    result += mat4(0.074243605, 0.015648128, -0.05003613, 0.10121142, -0.0218682, 0.006933849, 0.101385176, 0.16132122, 0.0013466089, 0.14042993, -0.25816667, -0.040413387, -0.19570185, -0.08637437, 0.17934911, 0.24961887) * g_11;
    result += mat4(-0.40401492, -0.16131033, 0.454142, 0.56882274, -0.013024656, -0.04423676, -0.023137214, 0.36117804, -0.0901519, -0.03237353, 0.010538879, -0.033432953, 0.105834074, -0.0549062, 0.05576519, -0.092626475) * g_12;
    result += mat4(-0.0017419134, -0.022569131, 0.027351622, -0.1289159, -0.0823291, -0.020735232, -0.28244564, -0.21001048, -0.048950948, 0.022033915, 0.14678808, -0.010097721, -0.06839686, 0.031720705, 0.11333891, 0.05049834) * g_13;
    result += mat4(-0.2191025, -0.005935159, 0.24627906, 0.058490098, -0.011270337, -0.019233467, -0.17698613, -0.0052346545, 0.2288101, -2.5289672e-05, 0.267102, -0.026019678, -0.17386179, -0.017672652, -0.35420522, 0.2836498) * g_14;
    result += mat4(0.19294678, 0.011570707, -0.34666267, -0.09040537, 0.18127288, 0.10182209, 0.08549184, -0.48737645, -0.040560674, 0.20645715, -0.68665904, -1.3146902, 0.18629448, 0.09806124, 0.09953519, -0.5450951) * g_15;
    result += vec4(-0.24792486, -0.09899526, 0.3761066, 0.022595163);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups, gxy, result);
}