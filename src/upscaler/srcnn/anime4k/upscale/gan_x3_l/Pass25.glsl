// Anime4K_Upscale_GAN_x3_L - Pass 25 of 30 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.13381699, 0.17966591, -0.0866034, -0.15282217, -0.2567282, -0.38080183, 0.10091161, 0.32172382, -0.064547606, -0.08161712, -0.033353675, -0.0019234467, 0.027740227, 0.2277078, 0.06759129, -0.22699283) * g_0;
    result += mat4(-0.122093834, 0.20621717, -0.08142724, 0.16477586, 0.4863212, -0.24032472, 0.00055996195, 0.50562304, 0.028121283, 0.56215876, 0.014577866, 0.06960302, -0.15964645, 0.14526807, -0.026474794, -0.02554081) * g_1;
    result += mat4(-0.101622745, 0.022395104, -0.14208415, 0.09508211, 0.20496333, 0.11371943, -0.024784304, 0.09519364, 0.09233463, 0.03117482, -0.15262024, -0.16956648, -0.2432608, -0.12877996, -0.13148616, 0.043081667) * g_2;
    result += mat4(-0.28086182, -0.15846887, -0.058738094, -0.181707, -0.018847898, 0.05197007, 0.09753647, -0.19714034, -0.062462445, -0.17604835, 0.1268098, 0.15334699, 0.05568127, 0.16867611, -0.1686486, 0.28579247) * g_3;
    result += mat4(0.20252296, -0.27393097, 0.06578763, -0.12628423, -0.10547165, 0.030740904, -0.19412865, -0.034658667, -0.09081653, -0.19958268, 0.16915733, 0.056093715, 0.10596871, -0.1742866, 0.004890009, 0.19515324) * g_4;
    result += mat4(0.32077652, -0.004434404, -0.12717858, -0.13544025, -0.450333, 0.04072708, 0.04316467, -0.2578049, -0.011932833, 0.18828999, 0.12326536, -0.016795376, -0.0054118615, 0.061453808, 0.28015187, 0.13463841) * g_5;
    result += mat4(0.08942177, -0.0021343376, 0.23693596, -0.15413974, -0.32839566, -0.010874302, 0.033822935, 0.038676813, 0.18920816, 0.019961799, -0.055697896, -0.042120066, 0.10387084, 0.047366753, 0.17899887, -0.071130194) * g_6;
    result += mat4(0.0010777018, -0.071475126, -0.16156957, -0.08781234, -0.08701292, 0.29084647, -0.34587428, 0.06969663, 0.036580127, 0.106745, -0.1534462, 0.106189206, -0.22758242, 0.20691736, -0.018554503, -0.056773946) * g_7;
    result += mat4(0.14826776, -0.03700497, 0.066144, 0.023859248, -0.16708666, -0.23908418, 0.062023632, -0.16278005, 0.06265635, -0.039846748, -0.13978398, -0.027952245, 0.099891245, 0.18235108, 0.00991435, 0.0423486) * g_8;
    result += mat4(-0.17948383, -0.082759954, 0.10543674, -0.18660031, 0.0664088, -0.06837087, 0.04300318, 0.011699623, -0.017162412, -0.030628186, 0.07547453, 0.20060332, -0.19182351, 0.04914753, 0.040280227, -0.12417484) * g_9;
    result += mat4(0.04074336, -0.041421015, -0.0372822, 0.1647266, -0.13993263, 0.0029407872, -0.39398977, -0.1778468, 0.21322449, 0.19134948, -0.02818874, 0.226251, 0.06352273, 0.12620094, 0.24221466, 0.20657893) * g_10;
    result += mat4(-0.094572894, -0.046852108, 0.21210444, -0.14082888, -0.050984625, -0.13443558, 0.24309658, 0.1573335, 0.21941295, 0.11642813, 0.09684106, -0.08597462, 0.15502413, -0.018070435, 0.1292023, -0.1557655) * g_11;
    result += mat4(0.025215387, 0.16676718, -0.068287216, 0.017648363, 0.2779579, 0.059142746, -0.096408874, 0.22609432, 0.20962398, 0.24879578, 0.023621194, -0.29692242, 0.02272032, -0.33367038, 0.15799981, -0.1699598) * g_12;
    result += mat4(0.08816878, 0.076234445, -0.06670541, 0.024926793, -0.12045598, 0.07443171, 0.22081238, -0.044906516, -0.02448027, -0.22067828, -0.016471038, 0.21801811, 0.16276583, 0.34590468, -0.18487914, 0.0554853) * g_13;
    result += mat4(-0.085593045, -0.002904318, 0.049969394, -0.06931361, -0.10722648, -0.08499641, -0.25997344, 0.22650665, 0.069008924, -0.23179024, 0.20058884, -0.20237185, -0.1606995, 0.0758858, -0.09946377, -0.21032207) * g_14;
    result += mat4(0.11210572, 0.055658836, 0.041539114, 0.078087114, -0.060435783, 0.08331363, 0.07356019, 0.0842336, -0.38098484, 0.020591227, -0.45916042, 0.06386686, -0.19348675, 0.041925576, -0.23489946, -0.06711732) * g_15;
    result += mat4(-0.13721304, 0.15404533, 0.102312036, -0.090253755, 0.08690545, 0.034154307, 0.07618604, -0.15844443, -0.10604342, 0.2646684, -0.08719668, 0.19331944, 0.10569642, -0.058054388, -0.0110980645, -0.08710107) * g_16;
    result += mat4(0.15567884, -0.11589786, 0.031855986, 0.005064268, 0.37850487, 0.30044487, -0.2604449, 0.061879188, -0.015081224, -0.30759993, -0.07571204, -0.0077929585, -0.08748009, 0.22546281, -0.06377379, 0.435342) * g_17;
    result += vec4(0.0053140894, -0.030208405, 0.04287835, -0.059097543);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups, gxy, result);
}