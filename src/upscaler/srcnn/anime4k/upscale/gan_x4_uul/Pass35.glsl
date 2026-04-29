// Anime4K_Upscale_GAN_x4_UUL - Pass 35 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_12_tf2;
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
vec4 result = mat4(-0.08458906, -0.045548566, -0.10978095, -0.047000825, -0.009786269, -0.011293472, 0.105108716, 0.2910591, -0.013156543, -0.27344525, -0.023291195, 0.07908779, -0.027045839, 0.071613476, -0.3137018, 0.13338767) * g_0;
    result += mat4(-0.28876805, 0.22697273, -0.20825712, -0.16558835, 0.07140026, -0.111653306, -0.18168612, 0.08566776, 0.017613843, 0.1612815, 0.30276966, -0.20298769, 0.09009318, -0.034424078, 0.06065636, 0.16040413) * g_1;
    result += mat4(0.05867395, -0.06784011, 0.124088526, -0.10969516, -0.11331259, -0.002973524, 0.11179402, 0.0051524965, -0.08812763, 0.13521312, 0.21501167, 0.07731858, 0.012728372, -0.10567223, 0.22674152, -0.27934498) * g_2;
    result += mat4(-0.02090283, -0.022435555, -0.032363184, 0.1468986, 0.02465703, -0.1274767, -0.13416417, 0.09719175, 0.028444616, 0.43590242, -0.0026427982, -0.14670907, 0.06547671, -0.0364002, -0.3601176, -0.12617487) * g_3;
    result += mat4(-0.001833205, -0.25144672, 0.2733562, 0.1314548, 0.2404573, -0.08306562, -0.051376957, -0.22175321, 0.059513494, 0.08910989, 0.13955326, 0.17420472, -0.12255514, 0.10941854, 0.33097896, 0.42308313) * g_4;
    result += mat4(0.28040674, -0.08416738, -0.096258685, 0.028955044, -0.080570556, -0.05523723, -0.114000015, -0.23623861, 0.2672264, -0.050743762, -0.047196355, -0.20179898, 0.23441824, 0.2783142, 0.05851139, 0.13421243) * g_5;
    result += mat4(0.035536747, -0.0678093, 0.31716034, -0.0426406, 0.21573278, -0.27805597, -0.1303578, -0.0040549343, 0.36113667, 0.23618573, 0.08076673, -0.09356886, 0.16183415, -0.07026038, -0.042547043, -0.09353161) * g_6;
    result += mat4(0.17357092, 0.15503445, 0.09806117, 0.029178388, -0.104631364, -0.041340955, -0.0138095915, -0.18791881, -0.012838156, -0.07531211, -0.047425177, 0.032766186, -0.17878921, 0.044547506, 0.020943025, -0.14078479) * g_7;
    result += mat4(-0.20356365, 0.30711046, -0.09476413, 0.039315, -0.09745359, 0.06334827, -0.040607564, -0.18709438, 0.041945547, -0.007845949, 0.046563085, 0.1600018, 0.051986653, -0.15268685, 0.05963624, 0.32689095) * g_8;
    result += mat4(0.15796256, 0.119560085, -0.097539894, -0.2437361, -0.22178903, 0.12989672, -0.03343675, -0.10420719, 0.123599604, 0.07092632, -0.10071645, 0.10339369, 0.19539836, 0.06069522, -0.016500194, 0.119013496) * g_9;
    result += mat4(0.04409632, -0.24597782, 0.17819872, 0.013527225, 0.095, 0.10927752, -0.057812016, -0.021960432, -0.090907395, -0.11064963, 0.24494053, -0.21103893, 0.103177205, 0.030693118, -0.17225249, 0.07037569) * g_10;
    result += mat4(0.118446834, -0.24679066, -0.14558293, 0.043784406, 0.3350531, -0.18761784, -0.102111734, 0.25430822, -0.0646614, -0.0583482, -0.08839935, 0.3168981, 0.0494778, -0.20223978, -0.2115357, -0.22018467) * g_11;
    result += mat4(-0.2534852, 0.32339612, 0.07270645, -0.011030359, 0.08920039, 0.017263435, -0.01874008, 0.07719922, -0.020826634, -0.14347431, 0.27981552, 0.03904678, -0.42448956, -0.064080186, 0.09288264, -0.027479073) * g_12;
    result += mat4(0.039590076, 0.07196033, -0.31280693, 0.24355434, -0.17980134, 0.15838742, 0.25616613, -0.057677414, -0.10442752, -0.020222804, 0.11435109, 0.20502312, 0.26433223, -0.00088657736, 0.46070856, 0.07778242) * g_13;
    result += mat4(-0.11134918, 0.042227045, -0.2372263, 0.0036231377, 0.038029823, -0.059270848, -0.17764676, 0.029884227, 0.105741605, -0.09559035, -0.15077686, 0.050598737, 0.09693952, 0.041702244, 0.18962328, 0.088337086) * g_14;
    result += mat4(-0.11884088, 0.028897036, 0.16024508, -0.105453186, 0.074528895, 0.0020912525, 0.10682421, 0.0020874685, -0.116808906, -0.19607912, 0.027745381, 0.08307784, 0.01938885, 0.086835325, 0.054351103, -0.034016903) * g_15;
    result += mat4(0.18121108, -0.06029793, 0.21373494, -0.007983294, -0.1457712, -0.056918383, 0.19265617, -0.04419998, -0.23829523, -0.04557198, -0.13232914, 0.15803981, 0.22176561, -0.115885, -0.0022589006, -0.04921306) * g_16;
    result += mat4(-0.033309873, -0.013707254, -0.14320348, -0.1340651, -0.1276264, -0.20742168, -0.15771109, -0.04302339, 0.2474691, -0.0071554068, 0.19327043, 0.0034425415, -0.12281466, 0.08008345, -0.16869386, 0.11770986) * g_17;
    result += mat4(0.022218548, 0.12861203, -0.11477767, 0.033912715, -0.083030604, 0.025131695, 0.12323128, -0.15532357, -0.03170147, 0.1692707, -0.28667265, -0.27277988, 0.07428763, -0.10514385, 0.120484896, -0.24011889) * g_18;
    result += mat4(-0.07960741, -0.21583335, -0.06945787, -0.043556266, -0.24026866, 0.081503086, -0.035037458, -0.066688865, 0.17150764, -0.020859774, -0.09971474, 0.19070682, 0.11626562, 0.26741263, 0.21771777, 0.08071578) * g_19;
    result += mat4(-0.20892513, -0.11934624, -0.27238977, -0.25402215, -0.1657022, -0.025967792, -0.18414563, -0.10561174, -0.24274185, 0.04068036, -0.12646407, 0.14470865, -0.14468817, 0.0036746184, 0.18668495, -0.010208388) * g_20;
    result += mat4(0.27423638, -0.1557262, 0.23233625, 0.29515898, 0.016182564, 0.33365154, 0.00833455, -0.008295928, 0.2103007, 0.38919896, 0.17985278, 0.20100696, 0.41522792, -0.20303713, -0.017147776, -0.0649312) * g_21;
    result += vec4(0.007557919, -0.015767513, -0.037968982, -0.034609392);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf2, gxy, result);
}