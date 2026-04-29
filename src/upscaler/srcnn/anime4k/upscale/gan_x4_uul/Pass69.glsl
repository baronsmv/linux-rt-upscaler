// Anime4K_Upscale_GAN_x4_UUL - Pass 69 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_21_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_21_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_21_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_21_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_21_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_21_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_23_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_24_tf4;
#define g_0 (max((texture(sampler2D(tex_conv2d_21_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_21_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_21_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_21_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_21_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_21_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_21_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_21_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_21_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_21_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_21_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_21_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_23_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_23_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_25 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_28 (max((texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.064318754, -0.18948539, 0.15593126, -0.06304488, 0.06629931, -0.12705792, 0.06512428, 0.063008524, -0.14651999, 0.097759366, -0.23798478, -0.24931762, -0.08670739, -0.040990945, -0.114390776, 0.023151657) * g_0;
    result += mat4(0.016485719, -0.09634283, -0.14198488, -0.04438048, -0.21505983, -0.26128006, -0.04784944, -0.09402356, 0.06304391, -0.15288098, 0.00068967254, 0.068428546, 0.19094922, 0.26162505, 0.012422096, 0.0019210136) * g_1;
    result += mat4(0.09429176, 0.17532441, 0.04093382, 0.23090097, -0.039049014, -0.029371511, -0.22049028, 0.087878235, -0.16436112, -0.16126816, -0.13443045, 0.11702453, 0.011557647, 0.0860798, -0.13721867, 0.04339029) * g_2;
    result += mat4(-0.13857365, 0.07155365, -0.026300088, 0.030843856, -0.003029181, -0.16634469, 0.009277505, -0.0477318, 0.08176135, -0.025760109, -0.14980459, -0.23881069, 0.04395779, -0.020711109, -0.003765235, 0.16139714) * g_3;
    result += mat4(-0.029404152, -0.14717855, 0.08600079, 0.10087113, -0.0015481604, 0.12785077, -0.017091133, 0.11298956, 0.0135069, 0.048736177, -0.16933975, -0.010427592, -0.0710784, 0.035118822, -0.05988874, 0.05704193) * g_4;
    result += mat4(0.118158385, 0.05269367, 0.023569904, -0.1657988, 0.046414927, 0.192022, -0.038966145, -0.0991989, 0.052595813, 0.09601838, -0.09776323, -0.10896508, -0.03430822, 0.04195307, -0.03257825, -0.051419284) * g_5;
    result += mat4(-0.030581048, 0.17614278, 0.14005136, 0.25032252, -0.041909087, 0.03415134, 0.18558922, -0.013872336, 0.15255652, -0.21187684, 0.14342351, 0.03002535, 0.09936515, 0.07143285, 0.10832944, 0.07492966) * g_6;
    result += mat4(0.117437966, 0.20312095, 0.16551267, 0.036241867, 0.15959081, -0.15883422, 0.13650912, 0.13133384, -0.08531496, 0.22273071, -0.09418646, 0.16729115, 0.050657116, -0.15333027, 0.09318966, 0.038184803) * g_7;
    result += mat4(-0.18683884, -0.16802727, -0.01640892, -0.033356212, 0.13456257, -0.040969536, 0.12549457, -0.1290507, -0.04681963, 0.040288992, 0.05573994, -0.14020221, -0.08451734, 0.084726095, 0.027533028, -0.062352005) * g_8;
    result += mat4(0.16800499, 0.068888284, -0.06970656, -0.11694171, 0.027877143, 0.08590325, -0.41597658, 0.19020869, 0.18468907, 0.10396149, 0.2688539, -0.051384643, 0.082193665, -0.0061698114, 0.10528453, -0.039762035) * g_9;
    result += mat4(-0.13182193, 0.13022594, -0.04265935, -0.031845935, -0.031530503, 0.0028220103, -0.075633064, -0.038005225, 0.08944671, -0.038589507, 0.1264931, 0.04362325, -0.017746134, -0.074040845, 0.22195354, 0.02025781) * g_10;
    result += mat4(-0.010372041, -0.054928456, -0.11535243, -0.08789095, -0.25536317, -0.14206916, -0.18415648, 0.20086259, -0.08668259, -0.06832273, 0.00049483957, 0.0037794516, 0.022831686, 0.11659795, -0.06669702, -0.19588953) * g_11;
    result += mat4(-0.28961572, -0.4749287, -0.028464912, 0.052383482, -0.22320336, 0.24375547, -0.12413771, 0.13081387, -0.1111063, -0.07677365, -0.07474673, 0.13839811, 0.13673459, 0.008945309, -0.16129646, 0.083366215) * g_12;
    result += mat4(0.29712868, 0.29954886, 0.096922785, 0.16342036, 0.087328605, -0.31575698, 0.033533126, -0.01676748, -0.05085677, 0.10915346, -0.009143204, -0.08164666, 0.02106476, -0.08223177, -0.13560964, -0.06952909) * g_13;
    result += mat4(0.12253968, 0.10194223, -0.18962221, -0.019411137, -0.02967273, 0.07758143, 0.11593596, 0.0006656379, 0.4334612, -0.23675393, -0.10674996, 0.07835363, 0.10412569, 0.08455689, -0.036294702, -0.14943564) * g_14;
    result += mat4(-0.08402736, -0.19991463, 0.18588512, 0.07676709, 0.07191373, -0.07213601, -0.1128286, 0.053900886, 0.24843894, 0.15576254, 0.11854475, -0.26013455, 0.06444892, -0.105995424, -0.02662165, 0.23990677) * g_15;
    result += mat4(-0.048506703, -0.0874562, 0.09056293, 0.079049595, -0.27113122, 0.042350817, 0.08988192, -0.3137793, 0.0747184, 0.032512806, 0.017864892, 0.14460078, -0.03651161, 0.074389, 0.24303643, -0.099042624) * g_16;
    result += mat4(-0.007119913, 0.09615741, -0.03428203, 0.33762857, 0.065405674, -0.49520698, 0.13928282, 0.36657473, -0.023395495, -0.039354183, 0.11659457, -0.07508826, -0.086808786, 0.037178524, -0.08136895, 0.14095466) * g_17;
    result += mat4(0.13255325, 0.05039712, -0.1868099, -0.09327347, 0.24704066, 0.18458563, -0.096471004, -0.18579604, 0.01985749, -0.01758252, 0.3442843, 0.053911295, -0.048990734, 0.14512312, 0.068960086, -0.21552262) * g_18;
    result += mat4(-0.05009779, -0.07166913, -0.0064091743, 0.12607603, 0.22009291, -0.12833357, 0.07912463, 0.24400796, 0.07644523, -0.09144226, -0.04527602, 0.023284711, 0.14405306, 0.06575743, 0.02459841, -0.025973033) * g_19;
    result += mat4(0.008448822, 0.054047976, 0.0909093, 0.037993927, -0.05116312, -0.2986432, -0.07816385, 0.024441332, -0.14043695, 0.027960885, -0.14233884, -0.1725978, 0.048629027, -0.04404273, -0.3075077, 0.06929521) * g_20;
    result += mat4(0.093220495, -0.055684812, -0.055064965, 0.028901886, 0.19592312, 0.1363604, 0.076918535, -0.19113176, 0.36366606, -0.013933859, 0.03314929, -0.03575491, 0.07210199, 0.106656946, 0.15615965, -0.19988714) * g_21;
    result += mat4(0.12586692, -0.013626416, -0.02413242, 0.0756625, 0.09772758, -0.09996077, -0.008041489, 0.1159643, 0.1241683, 0.14317046, -0.0932358, 0.31132537, -0.0020806575, 0.020223314, -0.2438224, 0.06940367) * g_22;
    result += mat4(-0.0016025436, 0.060878396, 0.17611162, -0.100864336, 0.028983932, 0.09252143, 0.10481248, -0.06146908, -0.31934208, -0.13838133, 0.13185565, -0.035758033, -0.13044602, 0.10710358, 5.8081503e-05, -0.00454267) * g_23;
    result += mat4(-0.059576258, 0.06968948, -0.008232615, -0.06129336, -0.08833713, -0.054481387, -0.004371116, -0.1964046, 0.022765493, 0.025811723, 0.0067215296, 0.02305441, 0.10606636, -0.086005725, -0.21056533, 0.12253492) * g_24;
    result += mat4(-0.00835301, -0.15535109, 0.12221956, 0.19185501, 0.05132267, 0.16891663, -0.11666316, -0.03017235, -0.13267665, 0.046521697, 0.027762229, 0.059645366, 0.00027471577, -0.11043438, 0.10424315, -0.1086128) * g_25;
    result += mat4(0.05075079, 0.019918585, -0.031245248, 0.116343796, -0.15688774, 0.13276225, 0.043608118, 0.038603537, 0.09514637, -0.12972692, -0.15088506, -0.19487189, 0.12054755, 0.014158436, -0.017870666, 0.244829) * g_26;
    result += mat4(0.16140082, 0.12640321, 0.1969524, 0.14234789, -0.0387056, -0.16567732, 0.13261116, 0.13626204, -0.08689124, -0.13475373, 0.18032974, -0.034728065, 0.016112087, -0.07409384, 0.009190101, -0.13319102) * g_27;
    result += mat4(0.13840085, -0.1503008, -0.28004104, 0.0004458277, 0.085771725, 0.18693484, -0.38570777, -0.0015788627, -0.22876291, -0.05482633, -0.19387709, 0.065617, -0.015152447, 0.11920871, -0.10714691, 0.15455256) * g_28;
    result += mat4(-0.44118914, 0.15384102, 0.470851, -0.14082034, 0.30934575, 0.16286017, 0.23737209, 0.035161156, 0.035742745, 0.14005975, -0.103563346, -0.0142445285, 0.1746347, 0.13249661, 0.0984072, -0.23170716) * g_29;
    result += vec4(0.023260193, 0.094669305, 0.13180539, 0.011011345);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf4, gxy, result);
}