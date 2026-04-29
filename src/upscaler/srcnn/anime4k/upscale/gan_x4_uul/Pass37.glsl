// Anime4K_Upscale_GAN_x4_UUL - Pass 37 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_9_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_9_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf4;
#define g_0 (max((texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_9_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_9_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_9_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_9_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_9_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_9_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_9_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_9_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_9_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.085369416, -0.15684304, -0.13306437, -0.090675324, 0.07001203, 0.042601265, -0.045776606, 0.038092162, 0.3352239, 0.1771388, -0.18876538, -0.006706726, 0.16373621, 0.25545865, -0.16266474, 0.24038056) * g_0;
    result += mat4(-0.14294663, -0.26456648, 0.25277606, 0.060462173, -0.078849405, -0.09209792, -0.1693239, -0.18630522, -0.014867209, 0.103692755, 0.14898701, 0.046629176, 0.024372628, 0.16875252, -0.15838362, -0.040581323) * g_1;
    result += mat4(-0.14351358, 0.18334064, -0.10826993, 0.18453784, 0.11304891, -0.03537591, -0.0066316077, -0.0013244748, -0.078686886, 0.12878294, -0.032346953, 0.09220158, 0.17955816, 0.18110012, -0.022541158, -0.056274466) * g_2;
    result += mat4(-0.051650286, -0.098697364, 0.08296607, -0.0024960893, -0.093507074, -0.066408254, 0.17999014, 0.14308663, -0.0108735245, -0.13364671, -0.02929436, -0.23579551, 0.046282418, -0.131284, 0.052697252, -0.0419363) * g_3;
    result += mat4(0.1754224, -0.11919244, -0.1885955, -0.19994752, -0.14402874, -0.17087972, -0.09000405, 0.0018777894, -0.05090923, -0.07121361, 0.10294247, 0.026922463, 0.014392331, -0.03248051, 0.009739078, 0.31159627) * g_4;
    result += mat4(0.13837712, 0.15520355, -0.14125966, 0.09480141, -0.067623354, -0.02482682, 0.15788238, 0.3214408, -0.2643569, -0.040410206, -0.051892046, -0.057043463, 0.18232885, 0.19971256, -0.0956208, 0.23722707) * g_5;
    result += mat4(0.016028238, -0.08332774, -0.11755386, 0.21787633, -0.22682859, -0.019670114, 0.04961192, 0.23987772, 0.15335025, 0.13612296, -0.01693323, 0.011952209, -0.3059259, 0.017340606, -0.07829871, 0.089332424) * g_6;
    result += mat4(-0.37531942, -0.045622103, -0.20052142, 0.025810266, 0.09413211, 0.056469247, 0.0033650927, 0.20752242, 0.077076204, -0.10665101, 0.12946871, 0.11152074, -0.0077144187, 0.050461795, 0.09886446, 0.08139971) * g_7;
    result += mat4(-0.03805296, -0.3470507, 0.28351876, 0.121408775, 0.119826116, 0.50992435, -0.06502164, 0.15930907, 0.10803227, 0.16217098, 0.032394126, 0.08210439, 0.039388526, 0.123406455, 0.08190563, 0.29731047) * g_8;
    result += mat4(0.036232114, 0.098707214, 0.08512323, 0.28130695, -0.34401244, -0.16329831, 0.04697471, -0.32552102, 0.16708755, -0.0027450684, 0.22314417, -0.034509923, -0.23747928, 0.13334718, -0.20790295, -0.13229762) * g_9;
    result += mat4(-0.09985405, 0.1217619, -0.15892437, 0.0896462, -0.19392657, -0.23446624, -0.14154576, -0.041264284, 0.0042809956, 0.06508634, -0.01017789, 0.015765704, 0.059713606, -0.08648103, -0.14761575, -0.078500696) * g_10;
    result += mat4(-0.23650993, 0.6093473, -0.21706295, -0.07720968, 0.20827857, 0.44513646, -0.107045025, -0.033600613, 0.014263266, -0.10306615, -0.026285734, 0.014794844, -0.11126778, -0.28632736, 0.18140377, -0.026450366) * g_11;
    result += mat4(-0.11553207, -0.22439374, 0.31865847, -0.18898615, -0.13782051, -0.16033193, -0.021633865, -0.27643433, 0.22693352, -0.29244474, -0.015831951, 0.0687026, 0.102418706, -0.33087376, 0.2023287, -0.105282284) * g_12;
    result += mat4(-0.034931872, 0.09946529, -0.13103552, -0.062213715, -0.15901782, -0.38695586, 0.22993153, -0.028414402, 0.2567039, 0.3477113, 0.021467375, 0.18368858, 0.31393996, 0.0592541, 0.20478922, 0.2784516) * g_13;
    result += mat4(0.01799271, 0.19488642, 0.11242015, -0.22955132, -0.23888321, -0.22094306, 0.09417609, 0.11446179, -0.0079179555, -0.018179458, -0.042231873, -0.058901574, 0.1643617, 0.09013122, -0.11941602, 0.07102288) * g_14;
    result += mat4(-0.11062226, -0.12371038, -0.20077015, -0.00089137297, 0.23280777, 0.20893154, 0.058997855, 0.05910376, 0.10964983, 0.08948893, -0.10008929, -0.09328607, -0.16772552, -0.0853413, -0.14602263, -0.10898542) * g_15;
    result += mat4(0.195481, -0.27274716, 0.019802367, 0.090690926, 0.24005474, 0.10449332, 0.038418755, 0.08757919, -0.1915846, 0.13781285, -0.08271653, 0.048500787, -0.35495785, 0.2332735, -0.089916445, -0.045998074) * g_16;
    result += mat4(-0.18144973, 0.035474263, 0.07927232, -0.02095586, -0.04264259, -0.0010760617, -0.09657631, -0.009819116, 0.075253725, -0.043196574, -0.107321955, 0.13470802, -0.026763562, -0.23883738, -0.22906674, 0.010300531) * g_17;
    result += mat4(-0.04512939, 0.2671829, -0.33687657, 0.087930106, 0.29693905, 0.11120111, -0.10967137, -0.072849795, -0.04814717, 0.17015213, -0.12041813, 0.034130402, 0.08712948, -0.018699426, -0.103492275, 0.051607467) * g_18;
    result += mat4(0.066338874, -0.11700618, 0.20888169, -0.00036208666, -0.0027271865, -0.0078573795, -0.18614855, 0.039184168, 0.15719953, -0.011559825, -0.042109553, 0.01807291, 0.11502362, -0.03629767, 0.021261917, -0.11922495) * g_19;
    result += mat4(-0.5144418, 0.059783865, -0.25726122, -0.46498007, 0.042682044, 0.10820562, -0.057476927, 0.01971749, -0.10208486, -0.17488515, 0.20830333, 0.09561035, -0.066455886, 0.0572077, -0.062440347, 0.047606003) * g_20;
    result += mat4(0.4270871, 0.3251775, 0.33070606, 0.21848439, 0.032633763, -0.4511691, 0.21410948, -0.12868443, 0.030835679, 0.054710764, 0.1886484, -0.2683438, -0.0776137, 0.24714139, 0.17632207, 0.097902626) * g_21;
    result += vec4(-0.12784827, 0.05878478, -0.019919237, 0.06345429);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf4, gxy, result);
}