// Anime4K_Upscale_GAN_x4_UL - Pass 22 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_6_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf3;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_6_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_6_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.18489622, 0.01521825, -0.053398065, 0.077619, -0.08345202, 0.20407347, -0.11390942, 0.08462241, -0.1705865, 0.30955344, -0.08472498, -0.16442084, -0.22677645, 0.048857957, -0.057290807, -0.40370303) * g_0;
    result += mat4(-0.04026143, -0.020023338, -0.022386922, -0.1292272, 0.17330426, 0.13575786, 0.16291218, -0.14266899, -0.23032628, 0.11625899, 0.0062630204, -0.0012355708, 0.15870166, -0.035987332, 0.0871242, 0.085054055) * g_1;
    result += mat4(0.016969275, 0.054262232, -0.23052263, -0.19101018, 0.03396106, 0.0054336865, -0.0467761, 0.19085331, -0.106530495, -0.27656856, 0.015368871, 0.13383915, -0.08088739, -0.15458798, 0.01770847, 0.26224154) * g_2;
    result += mat4(-0.1710468, -0.010396238, -0.008604742, -0.27136776, -0.08490557, 0.016414553, -0.27219942, -0.2275841, -0.0020410966, -0.074557334, 0.32281566, -0.0358406, -0.07795256, 0.11081372, -0.34438163, 0.15058495) * g_3;
    result += mat4(-0.13303854, -0.054123223, -0.034091465, -0.08479921, -0.3663492, 0.047407333, -0.08467303, -0.015536085, 0.07641996, -0.08629571, -0.026073072, 0.05748389, 0.39037332, 0.017548965, 0.105086334, -0.08005681) * g_4;
    result += mat4(0.08531782, -0.06040872, -0.25501314, -0.15468454, -0.18607718, -0.045276865, -0.08727564, 0.101659656, -0.14160259, -0.011791499, -0.14346547, 0.16301742, -0.054622017, -0.028709898, -0.05332203, -0.23680754) * g_5;
    result += mat4(0.18716991, 0.12908773, -0.3459139, -0.054999888, -0.1764484, 0.04881557, 0.096896894, -0.011711037, 0.093170814, 0.1973141, -0.028869364, -0.052994333, -0.050567757, -0.052473217, -0.20334762, -0.29321235) * g_6;
    result += mat4(0.16290617, 0.070835315, -0.13578944, 0.049878098, 0.024889912, 0.0046419716, 0.17256121, 0.24758084, 0.33473715, -0.05304426, -0.031384464, 0.30393425, 0.06880461, 0.018678263, 0.40095538, -0.32181707) * g_7;
    result += mat4(-0.12459963, 0.0924927, 0.17442048, -0.015650576, -0.05587131, 0.21291989, 0.31195658, 0.07287886, 0.1531054, 0.022245308, 0.09070423, -0.090930104, 0.036900636, -0.062797755, -0.015801767, -0.06667231) * g_8;
    result += mat4(-0.22362942, 0.30185577, -0.0560174, -0.17768693, 0.14361233, -0.36686167, -0.108977124, -0.06692557, 0.046176855, 0.06899551, 0.19507368, 0.18504564, 0.2892618, 0.108308315, -0.32998815, 0.15013184) * g_9;
    result += mat4(-0.06166722, 0.03421678, 0.007097079, -0.06511754, -0.07503845, -0.097745866, 0.0767785, 0.12762466, 0.078295015, 0.15278883, -0.20041291, -0.15149453, 0.1359745, -0.055542946, -0.1351582, 0.04746136) * g_10;
    result += mat4(0.2754691, -0.045461576, 0.28655398, 0.066658214, 0.10664401, 0.019698175, 0.21868771, 0.010793508, -0.37068173, -0.22633933, 0.05709351, -0.015515003, -0.25028723, 0.07527501, -0.060320277, 0.11013715) * g_11;
    result += mat4(0.16451468, -0.048677545, -0.21968195, -0.024521982, 0.06710036, -0.00431936, -0.040931974, 0.14162326, 0.30826005, -0.19923253, 0.06730949, 0.33769038, -0.17198718, 0.060878154, -0.2895043, -0.029802436) * g_12;
    result += mat4(-0.10908404, -0.18938556, 0.11546769, 0.11317103, -0.096525446, -0.1143871, 0.095474064, -0.12509643, -0.20624343, -0.23595047, -0.11051539, 0.1230616, -0.047473382, -0.11819063, -0.1330644, -0.09428916) * g_13;
    result += mat4(0.099916406, -0.19375911, -0.08102031, 0.1239838, 0.27221766, 0.20148776, 0.19851638, 0.08333579, 0.086547665, -0.18228337, 0.022614995, -0.1385529, 0.35897738, 0.20353337, -0.051304217, 0.09238109) * g_14;
    result += mat4(-0.17090152, 0.34364688, 0.25943616, 0.04933595, -0.022766197, 0.33663043, 0.09173691, -0.040311158, -0.20550281, 0.17361137, -0.13678429, 0.07744437, -0.42078802, -0.2707222, 0.21051168, 0.2207691) * g_15;
    result += vec4(-0.00853374, 0.014111409, -0.018602863, 0.025112765);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf3, gxy, result);
}