// Anime4K_Upscale_GAN_x4_UL - Pass 60 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_27_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_27_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_27_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_27_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_26_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_25_tf;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_28_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups;
#define g_0 (max((texture(sampler2D(tex_conv2d_27_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_27_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_27_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_27_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_27_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_27_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_27_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_27_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_26_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_26_tf, pointSampler), pos)), 0.0))
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
#define g_20 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_25 (max(-(texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_28 (max((texture(sampler2D(tex_conv2d_28_tf, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_28_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.24869502, -0.09899225, -0.43790483, 0.20478724, -0.1164636, -0.064487524, 0.19679324, -0.1449572, -0.15371573, -0.3400212, -0.21963254, 0.20369855, -0.2367356, 0.2477112, 0.35358265, -0.10717059) * g_0;
    result += mat4(0.008394252, -0.07444383, -0.21260554, -0.0109387245, -0.12783004, -0.046684895, -0.09459239, 0.15685712, -0.0650475, -0.17689607, 0.28597033, -0.14768666, -0.24485432, 0.11102652, 0.0016650548, 0.0335556) * g_1;
    result += mat4(-0.15471542, -0.055397827, 0.031601153, 0.12807971, 0.098534405, -0.078548655, -0.07627781, -0.045002084, -0.1607132, 0.22467372, 0.05354091, 0.14046556, 0.08950414, -0.11074417, -0.18164189, -0.062829755) * g_2;
    result += mat4(0.23552504, 0.106547005, 0.06353197, -0.12771529, 0.063815214, 0.0037739186, 0.13750316, -0.15964629, -0.13540323, 0.03661145, 0.1579406, -0.04318756, -0.23223858, -0.019027008, 0.14158043, -0.0981457) * g_3;
    result += mat4(-0.20985286, 0.006259769, 0.22924383, -0.14908646, 0.10981303, 0.09701522, -0.138446, 0.098020315, 0.1012965, 0.17753434, 0.03191124, -0.009315684, 0.15640236, -0.18660188, -0.108241856, 0.28092933) * g_4;
    result += mat4(-0.18514358, 0.020193081, 0.074342795, -0.20483983, 0.07773761, -0.0021120405, 0.1360036, -0.03176111, -0.032519307, 0.23044188, -0.0123683, 0.1398906, -0.057560008, 0.054931078, -0.09207622, -0.10482956) * g_5;
    result += mat4(0.042022258, 0.08705893, 0.04855544, -0.0702546, 0.09140309, -0.20014158, 0.08858101, 0.10530784, -0.17869075, -0.18289891, -0.06009552, -0.017472578, -0.12561706, 0.1241771, 0.10055958, 0.06711715) * g_6;
    result += mat4(0.11081939, 0.14038336, 0.086475745, 0.008545714, -0.09676236, 0.10120412, 0.018717231, 0.083903596, -0.010204144, 0.19445705, 0.08198393, -0.07868833, 0.16800411, 0.24233866, -0.14174843, 0.0127538135) * g_7;
    result += mat4(-0.07677055, -0.08069778, -0.19520187, 0.0811833, 0.16050573, 0.04002321, -0.062625214, 0.066150546, -0.0071385102, 0.15346812, 0.22585835, 0.017887173, 0.10958369, -0.27262884, -0.07289562, -0.13642263) * g_8;
    result += mat4(-0.20320824, 0.04060682, -0.045050982, -0.08530543, -0.15681775, 0.029664317, 0.040110916, -0.110328145, -0.115784444, -0.0010324386, -0.14814855, -0.05750071, -0.09158797, -0.05191994, -0.010077932, 0.010735767) * g_9;
    result += mat4(0.013956532, 0.10945481, 0.17186755, 0.085150324, -0.041226313, 0.12950367, 0.06430863, -0.13105504, 0.10078111, -0.25535673, 0.20490831, -0.18107158, 0.08253922, -0.2122405, 0.03085494, 0.046983067) * g_10;
    result += mat4(0.13400763, -0.33241597, -0.14590304, -0.07548988, -0.025087558, -0.09831733, -0.12063487, 0.12294168, -0.04194301, 0.5016058, -0.19878705, 0.2325771, -0.025853388, -0.113362834, 0.03071806, -0.043046314) * g_11;
    result += mat4(-0.24234526, 0.099842645, -0.123794004, 0.029319491, -0.06591831, 0.06859657, -0.04656591, 0.035922993, -0.15371624, -0.16684091, -0.13712381, -0.13332178, -0.012874865, -0.07265817, -0.13294667, 0.068372235) * g_12;
    result += mat4(0.337884, -0.053065576, 0.039201297, -0.3255975, -0.09653937, -0.08532608, 0.004564532, -0.064255305, -0.09196097, -0.064501986, 0.05946096, -0.065822385, 0.04373292, 0.18320732, 0.17107227, -0.09376649) * g_13;
    result += mat4(-0.1266736, -0.110596545, 0.06749142, 0.18791346, 0.3654019, 0.112833284, 0.05675392, -0.19131362, -0.05568984, 0.19247374, 0.102835864, 0.14997408, 0.31664333, -0.10273057, 0.1727324, 0.15486372) * g_14;
    result += mat4(0.3434959, 0.023886908, 0.031930014, 0.03582181, 0.005240771, 0.111360535, -0.19078243, 0.0100272475, 0.09107635, -0.008016216, -0.12759027, 0.10675808, -0.08348867, -0.09646617, -0.2607706, 0.018178092) * g_15;
    result += mat4(0.079807304, -0.05459316, 0.14646025, 0.044402126, 0.18155368, 0.030484838, -0.23650324, 0.050629415, -0.054936387, 0.24929616, -0.026216682, -0.027678574, 0.14901243, 0.00799581, -0.056854505, -0.2847785) * g_16;
    result += mat4(0.07668182, -0.090308845, 0.1426231, -0.076727286, 0.04532857, 0.41972977, 0.045198783, -0.2889559, 0.09463711, -0.115024, 0.12064761, -0.078441106, -0.0979431, 0.16587363, 0.034756947, 0.0819575) * g_17;
    result += mat4(0.02658691, 0.018619051, 0.10987584, -0.11632582, -0.097673975, -0.060380448, -0.048393946, -0.12066081, -0.08383298, 0.07522811, 0.00046106262, 0.056841437, 0.18688548, 0.2500605, 0.067883015, -0.0678706) * g_18;
    result += mat4(0.1660567, -0.18025756, -0.054567352, 0.06485854, 0.04710402, 0.10155829, -0.02514125, 0.18412691, 0.11272706, -0.078927964, 0.06751576, -0.10286652, -0.13830543, -0.117058784, 0.005188935, -0.06942043) * g_19;
    result += mat4(0.23703721, 0.10277758, 0.000754122, -0.029695567, -0.21699485, -0.20323198, 0.052537125, -0.23201968, -0.08901256, 0.14734636, -0.034757435, -0.0005979487, 0.44525814, 0.19301082, 0.6464728, -0.08360051) * g_20;
    result += mat4(-0.016849566, -0.17056245, -0.15224437, 0.09874574, 0.2365518, 0.13848515, -0.06262627, 0.030512452, 0.13390404, -0.17578915, 0.052553993, -0.0754797, 0.13499588, -0.091364816, -0.14214903, 0.012343283) * g_21;
    result += mat4(0.0444748, -0.120922156, -0.102585696, -0.029410962, 0.16525646, -0.003036487, 0.019754846, 0.10904324, -0.2154087, -0.08718995, 0.018755833, 0.03948844, -0.14803186, -0.2644333, 0.038109586, 0.16415441) * g_22;
    result += mat4(-0.11955258, 0.12032012, -0.0071599633, -0.08183172, 0.07993607, 0.15545094, -0.13790582, -0.12963726, 0.03992126, 0.013114452, -0.021836942, 0.06938646, 0.05713335, -0.14334689, 0.065875866, -0.15222839) * g_23;
    result += mat4(0.09515674, -0.28844547, 0.053185515, 0.03400144, 0.046243384, 0.06073404, -0.028122557, -0.14269671, 0.076097876, -0.25685546, -0.11053011, 0.0016753314, -0.061829623, 0.17545372, -0.073774636, 0.14134389) * g_24;
    result += mat4(0.09274064, 0.008774846, 0.01753719, 0.055378035, 0.070933565, -0.07643164, -0.03130691, 0.010624368, 0.08057614, 0.15103199, 0.16212596, -0.043121286, 0.024918344, 0.022077331, 0.12973905, -0.047122702) * g_25;
    result += mat4(-0.039035242, -0.05109422, 0.04064944, 0.046009026, -0.10690486, -0.072981425, -0.06059992, 0.16443883, 0.053239647, -0.049664095, -0.008035011, -0.047280237, -0.09541798, 0.044453926, -0.05769298, -0.054406438) * g_26;
    result += mat4(-0.07007281, 0.020636436, 0.21988238, 0.063351706, 0.23330332, 0.06405405, 0.09269646, 0.0076492154, -0.2956097, 0.04427142, 0.13951525, -0.0067400783, 0.094238706, -0.065390944, 0.11663461, 0.16150263) * g_27;
    result += mat4(-0.03655699, -0.066461764, 0.34125957, 0.0070882593, -0.051099982, -0.12373787, 0.05673152, 0.23672515, 0.0058079516, -0.0047331564, 0.17873889, 0.16574454, -0.17263038, 0.057122417, 0.21407363, -0.25284353) * g_28;
    result += mat4(-0.023008676, 0.11895382, -0.19360733, -0.11461752, -0.20733164, 0.068803884, -0.17845476, -0.10232586, -0.17705148, -0.021452963, -0.11692596, -0.02887165, 0.07515101, -0.049837537, 0.0055611697, -0.04965812) * g_29;
    result += vec4(0.046915848, 0.0039697043, 0.017740238, 0.02036365);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups, gxy, result);
}