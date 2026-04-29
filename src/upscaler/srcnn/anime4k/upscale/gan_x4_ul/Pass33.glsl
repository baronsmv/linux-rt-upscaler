// Anime4K_Upscale_GAN_x4_UL - Pass 33 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_15_tf2;
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
vec4 result = mat4(-0.29968667, -0.2054413, -0.42633036, 0.06540815, 0.25410962, -0.064704284, 0.15351892, 0.15098672, -0.060556993, 0.15943852, -0.2327252, -0.15252773, -0.27296653, -0.023351386, 0.01709797, 0.17157109) * g_0;
    result += mat4(0.21247834, 0.16731767, -0.23244476, 0.033929322, 0.12147452, 0.15835738, 0.20386045, 0.0099615855, 0.11954695, -0.0007262615, 0.25783026, 0.2163411, 0.2006933, -0.2897014, 0.22469328, -0.037531313) * g_1;
    result += mat4(-0.075687766, -0.0587827, -0.26173526, 0.014225498, -0.069109224, 0.19879107, 0.26262647, 0.1933589, 0.17341125, -0.075728156, 0.32497543, -0.12600474, -0.07275422, 0.032364674, 0.26471478, 0.18148176) * g_2;
    result += mat4(-0.19684902, -0.12419164, -0.15366356, 0.035451632, -0.1676133, 0.30628285, 0.013135715, 0.0828437, 0.24747711, 0.111026585, -0.3899608, 0.040306747, -0.14160432, 0.11833543, 0.07778105, 0.019718869) * g_3;
    result += mat4(-0.22168091, 0.27330446, 0.25358558, -0.13290156, -0.035276677, 0.0024858087, -0.055826478, -0.2468239, -0.008866367, -0.05784767, -0.01706684, 0.07295643, 0.1302385, -0.08386059, -0.02501015, 0.07468001) * g_4;
    result += mat4(0.042352963, 0.0657346, 0.13386852, 0.11897824, -0.12557411, -0.05947027, -0.16942193, -0.250491, 0.05414618, 0.28099364, -0.023707846, -0.40636906, -0.028787367, -0.13474262, 0.16070609, 0.31273147) * g_5;
    result += mat4(-0.13678479, 0.19962284, -0.26247823, -0.23762986, 0.06520537, -0.03368567, -0.16694795, -0.14713484, -0.01582234, -0.063183546, 0.24840857, 0.11376298, 0.0037960846, -0.16444042, 0.013803154, -0.030848777) * g_6;
    result += mat4(-0.06552558, 0.01993205, 0.18481286, -0.12726143, -0.23085758, -0.20116006, 0.10603243, -0.10200674, -0.16622123, 0.107850745, -0.19173287, 0.060454354, -0.0027331826, 0.20100433, 0.11314092, -0.05037935) * g_7;
    result += mat4(-0.14448921, 0.29943776, -0.020892464, 0.37468755, 0.122420244, 0.3393939, -0.15974823, -0.16213733, -0.21092644, -0.1603829, 0.197158, -0.008338081, 0.23865728, 0.03966763, 0.025320457, -0.1346732) * g_8;
    result += mat4(0.37890595, -0.121016815, 0.0532523, -0.513218, 0.039289672, -0.15242423, 0.043490604, -0.19230618, -0.07929196, -0.09307486, -0.034099534, -0.19038978, -0.20650864, 0.12007891, -0.103319936, 0.090364404) * g_9;
    result += mat4(-0.13087903, -0.26987913, -0.17999482, -0.08381556, 0.010039951, 0.0047134277, -0.11918671, -0.11301866, 0.2314213, 0.2650823, -0.039580453, -0.31289777, 0.07591129, -0.21344167, 0.031197479, 0.25037217) * g_10;
    result += mat4(0.07539192, -0.11289182, -0.035013635, -0.0049591977, -0.062005084, -0.016576197, 0.033936746, -0.09773915, -0.393588, 0.045551285, 0.049009543, 0.040800996, -0.08324719, -0.14489968, 0.03073572, -0.2191878) * g_11;
    result += mat4(0.19480848, 0.007287647, 0.10993567, -0.31089494, -0.23149367, -0.154109, -0.0038248543, -0.15359117, 0.051747542, 0.007752202, -0.12192655, 0.023507293, 0.017773356, -0.280811, 0.20664506, 0.020295167) * g_12;
    result += mat4(0.15923792, -0.023258807, 0.09257097, 0.08763583, -0.0037047588, 0.32919067, 0.22631034, 0.14352241, -0.05482676, 0.19056046, 0.017488375, 8.430863e-05, -0.021616697, -0.038389638, -0.22182924, -0.21699542) * g_13;
    result += mat4(0.010522319, -0.066425666, -0.12642634, 0.12129272, -0.022023065, -0.233132, 0.09775469, -0.027969204, -0.032578427, -0.20589033, 0.09356718, 0.08583383, 0.05210765, -0.07712435, 0.250104, 0.008439425) * g_14;
    result += mat4(0.06802483, -0.13343696, -0.047004845, 0.16506574, -0.091166094, -0.16346036, -0.13110496, -0.28389332, 0.035855703, 0.12646672, -0.099049605, -0.0008063162, -0.009684357, 0.010770653, -0.009783527, 0.11862203) * g_15;
    result += mat4(-0.010126488, -0.028762225, 0.18976927, -0.030415734, 0.12148659, 0.041320156, 0.0746818, 0.018062174, -0.30057785, -0.13369675, 0.122107536, 0.198235, -0.2140395, -0.024747701, -0.3379253, -0.21174349) * g_16;
    result += mat4(-0.016392622, 0.02029067, 0.11583286, -0.1268402, -0.19290908, 0.09967843, -0.12862396, 0.08984122, -0.003903114, -0.08975317, -0.18257642, -0.2447739, -0.13734268, -0.06588839, -0.039996687, 0.086118914) * g_17;
    result += mat4(0.15091965, 0.12736365, 0.13546066, 0.008318725, 0.028630871, -0.36270767, 0.24071144, -0.047721867, -0.0029238814, -0.299951, 0.16515507, 0.2045453, 0.23567834, -0.1644619, -0.18801829, 0.14953467) * g_18;
    result += mat4(-0.14868434, 0.023688158, -0.11039743, -0.18117934, 0.16662696, -0.17234206, -0.14898847, 0.16994476, -0.04968569, 0.19829328, -0.051957127, 0.11434248, -0.18070386, -0.114997305, 0.6586136, 0.21840969) * g_19;
    result += vec4(0.05267218, -0.01234981, -0.005742453, -0.0313311);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf2, gxy, result);
}