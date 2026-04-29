// Anime4K_Upscale_GAN_x4_UUL - Pass 75 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_24_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_24_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_24_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_24_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_24_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_24_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_23_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 1039) uniform texture2D tex_conv2d_25_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups3;
#define g_0 (max((texture(sampler2D(tex_conv2d_24_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_24_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_24_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_24_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_24_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_24_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_24_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_24_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_24_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_24_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_24_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_24_tf5, pointSampler), pos)), 0.0))
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
#define g_30 (max((texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_31 (max(-(texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.1545368, -0.051471695, -0.16140307, 0.09652848, -0.090248555, -0.12066054, 0.1767361, -0.08471509, -0.0811788, -0.14072022, -0.04303012, -0.007702722, 0.13935736, -0.21132554, 0.097583875, -0.12626477) * g_0;
    result += mat4(-0.077009946, 0.11341266, -0.014190827, -0.05731186, 0.14598061, -0.08561752, -0.087692715, 0.024827115, 0.15067159, -0.031084314, -0.103702016, 0.16679642, -0.007304722, -0.05382251, -0.006476595, -0.034540307) * g_1;
    result += mat4(-0.12478302, 0.0998608, -0.020768842, 0.178967, -0.22397885, 0.17558582, 0.011471913, 0.098842315, -0.026981229, -0.073270254, 0.07100908, 0.06399087, -0.07116806, -0.08182064, -0.0014849032, 0.2541588) * g_2;
    result += mat4(0.028780911, -0.09417787, 0.045969326, 0.10704354, -0.052760195, 0.08555782, -0.12812418, 0.1158547, -0.17714353, -0.04976, 0.041316688, 0.11038423, -0.27241063, 0.1855846, 0.23411646, -0.095824756) * g_3;
    result += mat4(-0.062022362, 0.12351213, 0.01305296, 0.04862448, -0.1472528, 0.036500677, 0.03666005, -0.11136876, 0.05285479, -0.18208516, -0.1316372, 0.04148666, -0.18160903, 0.056404397, -0.12911144, 0.083729036) * g_4;
    result += mat4(-0.14088988, -0.025164073, -0.4434851, 0.14736041, 0.04358233, 0.044943232, -0.0739642, -0.018053154, -0.14036542, -0.21224444, 0.08923161, 0.09663615, -0.08434565, 0.09656238, 0.024680674, 0.02995749) * g_5;
    result += mat4(0.16193505, -0.15713358, 0.2953047, -0.1257473, 0.019233074, 0.15819971, -0.17022912, 0.085982986, 0.17535183, 0.0613968, -0.015774077, 0.12607461, 0.079570904, 0.08338391, -0.11603918, 0.011505312) * g_6;
    result += mat4(-0.23952027, -0.13513869, 0.13461575, 0.17394428, -0.12297233, 0.07278597, 0.0699106, -0.10590944, 0.035547413, -0.043262303, 0.0038226866, -0.084128775, -0.08980834, -0.14883213, 0.11605759, -0.041146316) * g_7;
    result += mat4(-0.018182833, -0.12238664, 0.029634932, -0.25285953, 0.11828485, -0.05314554, 0.12802395, -0.07008308, -0.039349154, 0.26426378, -0.0057150517, -0.07171924, 0.098983854, 0.077945545, 0.0065407343, -0.26814637) * g_8;
    result += mat4(-0.08471211, -0.00053506374, 0.038021266, -0.087428264, 0.11662403, -0.038277518, -0.005095678, -0.009521368, 0.123804964, 0.14995687, -0.010620397, -0.035754666, 0.086847916, 0.06264173, -0.16579615, 0.02262065) * g_9;
    result += mat4(-0.09577556, -0.07982795, 0.024376906, -0.119355425, -0.092210874, -0.010486195, -0.04363388, 0.16995241, -0.13924848, 0.055487193, 0.1950311, -0.06857552, 0.14275251, -0.012629571, 0.10879939, -0.085644074) * g_10;
    result += mat4(0.057831254, -0.16999005, 0.15140204, -0.0647146, -0.012351427, -0.041099787, -0.03375414, -0.045616575, 0.026101796, 0.08556994, 0.02738961, -0.18606578, 0.028242199, 0.03386683, -0.061823543, 0.03558579) * g_11;
    result += mat4(0.023425754, 0.13217138, 0.032228522, -0.0340593, 0.07340007, -0.0020185385, 0.082099736, -0.06587912, -0.073847964, 0.009864729, -0.020948, 0.02759752, -0.24116306, -0.04943008, -0.041696478, 0.0475257) * g_12;
    result += mat4(-0.056659773, 0.003150759, 0.01840173, -0.062517665, -0.0787802, 0.045061097, 0.05366462, 0.042851992, 0.17394984, 0.05068143, -0.068130635, 0.03182271, 0.11936796, 0.034630287, -0.030017216, 0.0371981) * g_13;
    result += mat4(-0.04782677, -0.13856164, 0.102476485, 0.3168497, -0.029490076, -0.25574568, -0.15335694, 0.17697816, 0.06968332, -0.064986385, -0.19446203, 0.35532042, -0.10142414, -0.098764315, -0.008530768, -0.22272345) * g_14;
    result += mat4(0.003918355, 0.11477308, -0.03541845, -0.060774248, 0.01986403, 0.053085316, 0.020022528, -0.18842602, -0.06607439, -0.117085874, 0.19558486, -0.15384434, 0.14042355, -0.0805339, -0.042012088, 0.16506344) * g_15;
    result += mat4(-0.054274496, -0.3048171, 0.15363297, -0.48028508, -0.17355531, 0.15534942, 0.2397687, -0.3212727, -0.0069116117, 0.07829633, -0.12942782, 0.08540519, -0.16048779, -0.045530356, -0.106820785, -0.02039107) * g_16;
    result += mat4(-0.17271078, 0.05973828, -0.13368936, 0.18137284, 0.14774464, 0.01207385, -0.48741424, 0.37316188, 0.12304343, 0.033921722, 0.013900458, -0.13834685, 0.00724766, -0.009822602, 0.0048219366, -0.1497808) * g_17;
    result += mat4(0.046022985, -0.12942328, 0.106665194, 0.05104162, 0.08260261, 0.037978876, 0.05067675, -0.2878266, -0.15604153, -0.019456798, -0.09279057, -0.023125123, 0.13392529, -0.06734104, 0.03425348, -0.26038775) * g_18;
    result += mat4(0.08024023, -0.026217932, -0.0866867, 0.060902715, 0.047891118, -0.18346305, -0.00030129295, 0.06640321, 0.09371082, 0.12981345, 0.1371371, 0.047095854, -0.08373677, -0.075474314, -0.050123196, 0.16816519) * g_19;
    result += mat4(-0.06669337, -0.07323153, -0.005088308, -0.022087181, -0.13836318, 0.047315314, -0.098298065, 0.024197588, 0.11019521, -0.049888365, -0.010593423, 0.03579472, 0.13806434, 0.06568386, 0.09670891, -0.13850671) * g_20;
    result += mat4(0.033669885, 0.053267747, 0.0055295937, 0.0054150443, -0.14349131, -0.07215267, 0.14743172, -0.08989396, -0.13482799, 0.21353206, -0.015100392, -0.15850681, -0.023853622, -0.081464685, -0.17575328, 0.22396886) * g_21;
    result += mat4(-0.013254256, 0.05835715, 0.026902638, -0.036534548, 0.012239494, 0.024609983, -0.011468827, -0.00601273, 0.25535154, 0.039145224, -0.14032148, 0.06934234, 0.078024134, 0.08141313, -0.053155545, 0.058907513) * g_22;
    result += mat4(0.09006769, 0.0061046197, -0.05551385, -0.07883374, 0.21045619, -0.071170084, 0.045874875, -0.05969718, -0.06051193, 0.032679733, 0.059326146, -0.11344708, 0.0516495, -0.044130474, 0.021864831, 0.01791737) * g_23;
    result += mat4(-0.149584, -0.034539673, 0.056925774, 0.01407683, -0.14341363, 0.07235219, 0.029278886, 0.1040686, 0.044569943, -0.095220655, 0.06324637, -0.11561818, 0.14884533, 0.04400451, 0.030963998, -0.0480698) * g_24;
    result += mat4(0.09445444, -0.07705517, -0.04044035, -0.067266196, 0.12994061, -0.08685293, -0.028491655, -0.06546642, -0.06588555, -0.035200167, -0.054667167, 0.12181174, -0.08149457, -0.11196082, 0.022286078, 0.0011389274) * g_25;
    result += mat4(0.037566386, -0.0863645, 0.10746364, -0.062283915, -0.0828546, -0.059049137, 0.049943667, -0.09679541, 0.05570479, 0.10147355, 0.09882042, -0.09511045, 0.013920045, -0.13209742, -0.0231511, -0.008779095) * g_26;
    result += mat4(-0.049381115, 0.05511609, -0.08505539, -0.011759351, -0.0037505692, 0.02891526, -0.08524465, 0.13446826, 0.066822246, -0.07883564, 0.03159159, -0.114850216, -0.15590072, 0.08861297, 0.049592584, -0.06742877) * g_27;
    result += mat4(0.14131398, -0.019512732, 0.07624492, 0.17723484, 0.06855258, -0.11992505, 0.17618321, 0.035750873, 0.19290908, 0.10616057, 0.05006961, -0.10286499, 0.086485304, 0.017133571, -0.059471656, 0.153928) * g_28;
    result += mat4(-0.19372323, 0.06717175, -0.17909515, -0.10981143, -0.091010526, -0.03731334, -0.10764653, -0.042411704, -0.25248966, -0.15291771, -0.11685329, 0.097305104, 0.012290167, -0.06666997, 0.06516673, -0.084403165) * g_29;
    result += mat4(-0.22607833, 0.05895028, 0.04708332, 0.0361819, -0.18047495, 0.02135859, -0.048527088, -0.09720482, 0.071364224, 0.16597964, 0.058581673, 0.013964815, -0.26778197, 0.16814141, 0.04136449, -0.026651997) * g_30;
    result += mat4(0.22577362, -0.13153969, -0.0812206, 0.014283776, 0.14782336, 0.070584215, 0.06939886, 0.07700839, -0.0880132, -0.06622987, -0.088982984, -0.23417433, 0.3470509, -0.03866589, -0.08971988, 0.072038345) * g_31;
    result += vec4(-0.083648406, -0.040792946, -0.0071813604, -0.0033592125);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups3, gxy, result);
}