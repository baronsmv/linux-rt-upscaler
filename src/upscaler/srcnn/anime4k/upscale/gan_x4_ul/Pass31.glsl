// Anime4K_Upscale_GAN_x4_UL - Pass 31 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_12_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_12_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_14_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_15_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_12_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_12_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_14_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_14_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.113152556, -0.17597556, -0.20193578, -0.16201825, -0.08261954, -0.09107908, 0.044691782, 0.096718885, -0.092856266, -0.32485804, 0.15855914, 0.107594654, -0.049829155, -0.39206952, -0.17158785, -0.23730572) * g_0;
    result += mat4(-0.071358085, 0.05543187, 0.22816211, -0.15256211, 0.001002783, -0.097697146, 0.1485318, 0.3147081, -0.015470234, 0.1159168, -0.087412134, 0.025953531, 0.10858151, 0.04679302, 0.0035066542, 0.080319606) * g_1;
    result += mat4(-0.093644544, 0.15760094, 0.13644949, 0.15050913, 0.010754489, 0.21110971, 0.11982236, -0.027942248, 0.07777082, -0.05871466, 0.18935864, 0.26278642, -0.17607118, -0.24569197, -0.17914876, 0.011594047) * g_2;
    result += mat4(0.07215027, 0.07955528, -0.1192735, -0.24221008, -0.16430855, 0.31650412, -0.23902535, -0.14772269, -0.18149576, 0.1425237, 0.19313167, -0.25584412, -0.116279155, -0.0810948, -0.06305671, 0.31891116) * g_3;
    result += mat4(0.06337334, -0.0032687138, -0.035707716, -0.28104553, 0.12251401, 0.14867608, -0.28116974, -0.2499687, 0.16777486, 0.27506724, 0.1349104, 0.21004717, 0.2722905, -0.10366932, -0.089448065, 0.054238733) * g_4;
    result += mat4(0.2623722, -0.06399301, 0.26491323, 0.09354902, -0.15800871, 0.11810623, 0.01566208, -0.026193254, -0.22059508, -0.09398052, -0.15558046, 0.1636607, -0.24724618, -0.025115723, -0.03819038, -0.089232855) * g_5;
    result += mat4(-0.049244456, -0.2812487, -0.15883873, -0.1873005, -0.12443533, 0.26619563, 0.006807127, -0.18589701, -0.23903847, -0.04840708, -0.19155607, -0.3244167, 0.029380817, -0.073488645, 0.04205761, 0.12826183) * g_6;
    result += mat4(0.060077637, 0.21867147, -0.08562434, 0.12142833, -0.103506744, 0.015023599, -0.012361518, 0.39705324, 0.20116816, -0.1352389, -0.08270523, 0.08666531, 0.03978398, 0.012456996, 0.16741525, -0.03339209) * g_7;
    result += mat4(0.27487412, -0.2183994, -0.22064212, -0.18507382, 0.09653221, -0.31412682, -0.020428544, 0.15572692, -0.1708959, -0.09906218, -0.24475281, -0.07649422, -0.06725418, -0.1632794, -0.042570926, 0.15362686) * g_8;
    result += mat4(0.25352266, 0.078569, -0.06491825, 0.0024975773, -0.2520004, -0.14971292, 0.2396663, -0.10596094, -0.16498, -0.1615543, 0.03212853, 0.022647707, 0.11449023, -0.12597407, -0.3845188, -0.6042289) * g_9;
    result += mat4(-0.09472388, 0.09383272, -0.113919444, 0.06324396, -0.18574698, -0.017954197, 0.102970116, -0.036133416, -0.14566462, 0.106732786, -0.1981579, 0.08657682, 0.023193007, -0.26844215, -0.044777893, 0.1802785) * g_10;
    result += mat4(0.11824268, 0.060186915, -0.09982153, 0.054944858, -0.06390667, -0.12343378, 0.06823325, -0.05481055, -0.160094, -0.041776497, -0.093563, -0.18349311, -0.014049265, 0.24608798, -0.022140604, -0.14207092) * g_11;
    result += mat4(0.13720459, 0.07687791, -0.060669206, 0.11711911, -0.19655584, -0.008325822, 0.28701362, -0.03874219, -0.080647625, 0.08374782, 0.08991399, 0.1254085, -0.06939809, 0.10815167, -0.07602521, 0.003993563) * g_12;
    result += mat4(0.050552983, 0.3398467, 0.21439157, 0.07090537, 0.003626732, -0.013387389, -0.16702957, -0.023790954, -0.22492494, -0.17196465, 0.020361913, 0.028113617, 0.08070967, 0.06335804, 0.1024209, -0.07302465) * g_13;
    result += mat4(-0.06452998, -0.19448164, 0.068943985, 0.26658177, 0.03672322, -0.042712092, -0.14239077, 0.026480686, -0.0026813857, 0.07805945, 0.10659483, 0.25577578, 0.14431271, 0.26420194, -0.057292048, 0.14447866) * g_14;
    result += mat4(0.17443675, -0.10127553, -0.08078197, -0.13357292, 0.080379255, -0.0743335, 0.15775783, 0.042903706, -0.2730787, 0.0143810455, -0.100053966, 0.04868161, -0.17388023, -0.27480134, 0.17716847, 0.09831684) * g_15;
    result += mat4(-0.009394652, 0.05770814, 0.12612171, -0.07125733, 0.039110083, 0.18584593, 0.34637934, 0.1997804, -0.034237277, -0.2637098, -0.2565544, 0.18495636, 0.16258357, 0.051936973, -0.2022921, 0.025638767) * g_16;
    result += mat4(0.0264838, 0.34137276, 0.05243436, 0.0092191165, -0.22356755, -0.06718224, -0.07905385, -0.10482739, 0.26888105, -0.0944922, 0.11656137, -0.025189193, -0.21240412, -0.0740068, 0.3606278, 0.117385626) * g_17;
    result += mat4(0.24394973, -0.33353502, -0.20044908, -0.047943193, 0.26528633, 0.18467769, -0.118773505, 0.19762191, 0.008643024, 0.27267835, 0.110893816, -0.097346835, 0.35045865, 0.27740118, 0.12889476, -0.013060394) * g_18;
    result += mat4(-0.0465528, 0.05087261, -0.12176598, -0.26143193, -0.012329495, 0.12112426, -0.25950795, -0.06628347, -0.18653181, -0.003041955, -0.093980595, 0.10332955, -0.29503638, -0.011706522, -0.37699062, 0.18755646) * g_19;
    result += vec4(-0.015548932, 0.0007181281, 0.032181147, 0.046147745);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf, gxy, result);
}