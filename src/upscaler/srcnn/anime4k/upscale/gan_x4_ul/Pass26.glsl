// Anime4K_Upscale_GAN_x4_UL - Pass 26 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_9_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_9_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_9_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.29876372, 0.016366975, 0.21096407, -0.020094471, -0.1900656, -0.072851926, 0.26933378, 0.2965162, 0.047404896, -0.07100038, 0.36576727, -0.1726564, -0.09022945, -0.045195863, 0.054235443, 0.05129035) * g_0;
    result += mat4(-0.17622513, 0.029871318, 0.1261812, 0.2222432, -0.13800889, 0.07485947, 0.18132168, -0.07646577, 0.35130787, 0.025769712, -0.08360745, 0.1823751, 0.2580671, 0.17893296, -0.2970342, 0.2615672) * g_1;
    result += mat4(-0.09122936, 0.041544963, 0.11103348, -0.32509488, 0.11889552, -0.15459736, -0.14604495, 0.13639185, 0.25519374, -0.09549251, 0.027490158, -0.22870867, 0.15262592, -0.05271851, 0.07649719, -0.14544797) * g_2;
    result += mat4(-0.07842013, -0.07909847, 0.16719495, 0.060775355, 0.039721165, -0.11024404, 0.15099376, 0.017221982, 0.03604949, -0.00044745833, 0.09993808, 0.016347472, -0.1123219, 0.12352075, 0.0055856355, -0.038503457) * g_3;
    result += mat4(0.04749609, -0.011603198, -0.11631744, 0.29501718, 0.21616888, 0.076152876, 0.008262415, -0.17586538, -0.025060087, -0.06677992, -0.05253498, 0.20535102, 0.14948508, -0.16102068, 0.06183411, 0.12077816) * g_4;
    result += mat4(-0.0036952377, 0.15648776, -0.2770151, -0.26803473, -0.12806855, 0.21423273, 0.10177632, -0.010165392, 0.059501424, -0.16206288, -0.0119383745, -0.09637166, 0.016029779, -0.107704446, -0.066519134, -0.039579522) * g_5;
    result += mat4(-0.025284212, -0.11085338, -0.10921526, 0.19486162, 0.002627237, -0.24155024, -0.22131649, -0.008362887, -0.17378221, 0.254153, 0.14457825, 0.1237066, 0.1588314, 0.034734476, -0.32959384, 0.18392745) * g_6;
    result += mat4(-0.23717919, 0.032724388, -0.2579177, 0.032373153, 0.19237953, 0.18673407, -0.032884978, 0.34017587, 0.3633359, 0.22996293, 0.05866704, -0.051001176, 0.10989479, 0.15821928, 0.03814914, 0.18687908) * g_7;
    result += mat4(0.18111174, -0.045572106, 0.28947538, 0.028062606, 0.017460342, -0.11182857, -0.02323663, 0.22442394, -0.09908654, -0.1892071, -0.16361217, 0.23111914, -0.4034355, -0.160105, 0.124996185, 0.16111071) * g_8;
    result += mat4(-0.24601339, 0.16504896, -0.50432545, 0.17059588, -0.05622342, 0.03449165, 0.19813967, -0.23526217, 0.027649945, -0.091902114, 0.24123852, -0.27897063, 0.092255116, 0.46413165, 0.24431442, -0.28772914) * g_9;
    result += mat4(-0.10406283, 0.011556308, -0.28718328, 0.089035675, -0.34427065, -0.14430703, -0.05688551, 0.0073183607, -0.09622162, 0.11313123, 0.05555725, 0.14841734, 0.1549386, -0.17246638, 0.20873484, -0.03606831) * g_10;
    result += mat4(0.026205625, 0.20152962, -0.06303816, -0.3621029, -8.37066e-05, 0.022963323, 0.1556007, -0.010206023, -0.03585696, 0.013210482, 0.08844526, 0.08085807, 0.0154804215, 0.01674602, -0.22619575, -0.20517838) * g_11;
    result += mat4(-0.14771776, -0.087712936, 0.26490626, 0.13074578, -0.15972485, -0.17711553, -0.023439731, -0.35535946, 0.033503015, -0.04976214, 0.18148364, -0.25102466, 0.1015065, -0.17691332, -0.117089726, 0.2718636) * g_12;
    result += mat4(0.021445429, -0.2229151, 0.04363617, -0.01848845, 0.19044793, 0.12978733, 0.1401384, -0.051114038, -0.16472392, -0.059583012, -0.002701528, -0.12270173, -0.18227173, 0.03988044, 0.3377543, -0.18024927) * g_13;
    result += mat4(0.38426477, -0.09308802, -0.11083124, 0.21756104, -0.055889897, 0.100914784, 0.051462848, 0.1997221, 0.16923136, -0.0040037725, 0.21070997, -0.035059523, -0.0740145, -0.42558807, -0.020239443, -0.06474659) * g_14;
    result += mat4(-0.020568244, 0.08227015, -0.053252015, 0.01569164, -0.109781235, 0.06688285, 0.2620034, -0.18460485, -0.13735083, 0.0030442013, -0.21416521, -0.054695573, 0.047963038, 0.10726088, 0.034117166, 0.21801902) * g_15;
    result += mat4(0.520728, 0.06186967, -0.30889672, 0.0150618, -0.014702558, -0.2076953, -0.13387786, 0.101004966, -0.16997512, 0.14452092, -0.018287892, -0.14064445, 0.10045448, 0.33445045, 0.12254727, 0.033601977) * g_16;
    result += mat4(-0.08978202, 0.015013341, 0.11111453, 0.05192639, 0.18055484, 0.123284765, -0.1554275, 0.09262196, 0.057058904, -0.080403194, -0.163374, 0.046445247, -7.656726e-05, 0.23957397, -0.24086528, -0.04172887) * g_17;
    result += vec4(0.0030341349, -0.028386809, -0.0693459, -0.021886);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf1, gxy, result);
}