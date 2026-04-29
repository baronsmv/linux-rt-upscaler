// Anime4K_Upscale_GAN_x3_VL - Pass 27 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_14_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_15_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_14_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_14_tf, pointSampler), pos)), 0.0))
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
vec4 result = mat4(-0.016565321, 0.16086368, 0.16377108, 0.06516585, 0.08774041, -0.15408382, 0.08090872, 0.044837043, 0.118495755, -0.145867, -0.0830602, 0.021258313, -0.083069436, 0.1438954, 0.3145759, -0.021647993) * g_0;
    result += mat4(-0.120379515, -0.24860992, -0.015166592, -0.12202178, 0.06496186, 0.0744854, 0.1485615, -0.109343, 0.19879182, -0.3081023, 0.21677417, -0.22301331, -0.011651633, -0.19334914, 0.15160677, 0.047521867) * g_1;
    result += mat4(-0.018556662, -0.38472578, 0.41192028, 0.43185833, -0.046080858, 0.04489752, -0.20783445, -0.1610854, -0.309501, -0.273866, 0.060515694, -0.12974882, -0.0759038, 0.19965601, -0.19319372, -0.11006917) * g_2;
    result += mat4(0.10012627, 0.13247557, -0.13383594, 0.13269171, -0.07811828, -0.22248991, -0.015335469, 0.000673531, 0.29827982, 0.06373573, 0.04488941, -0.013616235, 0.007511088, -0.33727455, 0.0019768223, 0.2379881) * g_3;
    result += mat4(0.14306581, 0.085049756, 0.047580484, -0.057794355, -0.043503262, -0.105414085, -0.1606061, -0.23061153, -0.11303711, 0.16984846, -0.068943, 0.28954068, 0.063482575, 0.047116138, 0.08716241, -0.12745613) * g_4;
    result += mat4(0.0020036818, 0.090957165, 0.015798112, 0.23128921, 0.1914184, 0.19120963, -0.06399709, -0.0788507, 0.07272036, -0.0119575225, 0.11690162, -0.1501703, -0.019269818, -0.42832217, -0.12736018, -0.06600497) * g_5;
    result += mat4(-0.2329279, 0.056115344, -0.0057740537, -0.2990719, -0.17836936, 0.27681816, 0.37309527, -0.15801883, -0.063524134, 0.099096715, -0.06648651, -0.28727666, 0.293816, 0.07798524, 0.048862323, -0.115539655) * g_6;
    result += mat4(0.3703411, -0.09810904, -0.09486779, 0.0014081999, 0.14049709, 0.21120222, -0.40097466, -0.34167844, 0.23002532, 0.028405711, -0.019445082, 0.034988888, -0.50940406, 0.08899147, 0.05107509, -0.00382772) * g_7;
    result += mat4(0.11272419, -0.033249535, 0.27027267, 0.17533688, 0.08927961, -0.0018240041, 0.16140664, -0.046008278, -0.15334447, -0.15343803, 0.091045976, -0.19814257, 0.04322423, -0.17734216, -0.2798295, -0.08573132) * g_8;
    result += mat4(0.12554517, -0.037913572, -0.07749419, -0.25204238, -0.24223939, 0.18784638, -0.20372832, 0.4048194, 0.25830784, 0.0051259343, -0.032063078, 0.28017554, -0.12499362, -0.26364753, 0.05812282, -0.18392684) * g_9;
    result += mat4(0.26486975, 0.061957724, 0.07971466, 0.046751168, -0.31778535, 0.4381787, -0.07035851, 0.23263998, -0.052127257, -0.12611173, -0.18760382, 0.14079882, 0.22377297, -0.05741558, 0.031250857, 0.16233918) * g_10;
    result += mat4(0.05335076, -0.34464896, 0.3002586, -0.24760664, -0.14003357, -0.09159649, -0.18697475, -0.14623205, -0.13852511, -0.04981257, -0.19454202, -0.09108177, -0.015734429, 0.13033359, -0.18407115, 0.10902568) * g_11;
    result += mat4(-0.02813337, 0.09047474, 0.017847307, 0.09261004, -0.21497558, -0.14598191, 0.19712229, -0.10600094, -0.13380432, 0.11108035, -0.004200233, -0.13140516, -0.015072323, -0.20674899, -0.007258648, -0.18661419) * g_12;
    result += mat4(-0.075342774, -0.15346074, 0.08983637, 0.26993182, -0.14880064, -0.25546706, -0.055426415, 0.082991235, 0.11674955, 0.02243115, 0.1323313, -0.16614287, -0.12463222, -0.021946859, -0.109896004, -0.18907025) * g_13;
    result += mat4(-0.13882166, 0.2001865, 0.0011639959, 0.194607, 0.10369673, 0.11537449, -0.20017526, 0.08001218, 0.2717005, 0.03861079, 0.21795402, 0.13731115, -0.28959844, -0.026275165, -0.13865054, -0.032054946) * g_14;
    result += mat4(0.056745965, -0.0028218296, -0.1637033, -0.10748185, -0.008221024, -0.012517368, -0.21787529, 0.24229775, 0.21705846, -0.31918925, -0.10432461, -0.020117749, 0.48566294, -0.0764948, 0.11959202, -0.21828687) * g_15;
    result += mat4(-0.08911589, 0.0019316651, 0.3447702, -0.28325114, -0.0017365502, 0.066785716, 0.057680055, 0.10159895, 0.028087914, 0.03835387, -0.09806545, -0.088825025, -0.016581869, -0.19346818, -0.068037614, 0.071174935) * g_16;
    result += mat4(-0.11981757, 0.11738665, -0.15907699, 0.15687436, -0.060289837, -0.0068618194, 0.10179951, 0.30881542, -0.010891428, -0.17345384, -0.4455766, -0.007086927, -0.08359593, -0.1598503, 0.012697522, 0.4165511) * g_17;
    result += vec4(0.03556714, 0.06747606, -0.010788525, 0.0018122225);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf1, gxy, result);
}