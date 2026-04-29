// Anime4K_Upscale_GAN_x4_UL - Pass 51 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_23_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_24_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_21_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_21_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_21_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_21_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_21_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_21_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_21_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_21_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_23_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_23_tf, pointSampler), pos)), 0.0))
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

vec4 hook() {
vec4 result = mat4(-0.14804654, -0.14173095, 0.16659345, -0.009385182, -0.020287529, -0.09633324, -0.30860174, 0.063476086, 0.01976211, -0.23352058, 0.09209867, 0.16206749, 0.08077074, -0.10959624, -0.12718476, 0.17011921) * g_0;
    result += mat4(-0.3140556, 0.12636565, 0.012903826, -0.08176523, 0.14805675, 0.23573041, 0.22436617, -0.04828265, 0.13404454, -0.016488977, 0.30504864, -0.0019838111, 0.14962101, -0.00575774, 0.19882312, 0.22259174) * g_1;
    result += mat4(0.16593869, 0.05078502, -0.12377358, 0.28647205, -0.10124151, 0.15258715, 0.027155356, -0.015847337, -0.054100014, 0.13954991, -0.095538475, -0.024002708, -0.12028006, 0.058690242, -0.32992294, -0.11747722) * g_2;
    result += mat4(0.18058912, 0.013726746, 0.14127955, 0.14231133, -0.08689764, -0.092697755, 0.17092462, -0.039948042, 0.1217311, -0.12693831, -0.19433555, -0.10920207, -0.07334007, 0.025639182, 0.032232128, 0.10318817) * g_3;
    result += mat4(-0.012409655, 0.055781372, -0.19240658, -0.23877834, -0.0960606, 0.17469998, -0.022961274, 0.063891776, 0.027615886, 0.067367285, -0.25862217, -0.29574084, -0.028999899, 0.17343716, -0.24148487, 0.1229659) * g_4;
    result += mat4(0.12804163, -0.23425618, -0.33593133, -0.040897377, 0.11306302, 0.065293916, -0.05870299, -0.15702757, -0.20557828, 0.037325155, -0.21109815, 0.05123402, -0.23969208, 0.053520784, -0.27755785, -0.11555018) * g_5;
    result += mat4(-0.13524376, -0.31770554, 0.0842197, 0.08805993, -0.07403083, -0.087194294, 0.012449786, 0.14015238, -0.09606474, -0.04868743, -0.011370155, 0.005927663, 0.028680688, -0.1429374, 0.27102706, 0.11689099) * g_6;
    result += mat4(0.15883644, 0.09540351, 0.10983531, -0.047686223, -0.026774509, 0.08621119, -0.06392311, -0.02266724, 0.20034596, -0.013704803, 0.28371832, 0.19092667, 0.10529074, -0.12145345, -0.10676546, -0.02673637) * g_7;
    result += mat4(0.0096095605, 0.03329556, 0.09830959, 0.1595078, -0.18308333, 0.14192823, -0.048857637, -0.06888825, 0.18871805, -0.061875697, -0.13133556, -0.17831984, -0.028223597, -0.16346388, 0.16018315, -0.006383535) * g_8;
    result += mat4(0.26071513, 0.09806688, -0.34068507, -0.3768804, 0.011374573, -0.2450996, 0.104056686, -0.20815447, -0.3442328, 0.35717773, -0.18200488, 0.21185465, 0.30605116, 0.17752215, 0.26911554, 0.101427086) * g_9;
    result += mat4(-0.041318867, 0.1009111, 0.2157564, -0.088500485, 0.07373474, -0.25785303, -0.004410731, -0.14463747, -0.1358761, 0.023295294, 0.113840915, 0.4273329, 0.05128152, 0.14215858, 0.19876923, -0.019440446) * g_10;
    result += mat4(-0.23231222, -0.14272551, 0.09846874, -0.06775076, 0.0059967814, 0.062043674, -0.2065345, -0.12056687, -0.024301382, -0.34733498, -0.2054398, -0.08064672, 0.118986174, -0.05259333, 0.09134329, 0.0941969) * g_11;
    result += mat4(-0.15081125, -0.03763831, -0.077403225, -0.014139531, 0.1599335, 0.043187547, -0.20010144, -0.12097138, 0.09763305, 0.103107266, 0.01814798, -0.11254244, -0.17597707, -0.05016406, -0.27989724, -0.031772614) * g_12;
    result += mat4(0.054545857, 0.03135118, 0.08629934, -0.12681678, -0.049472764, 0.13161416, 0.06408171, 0.09543149, 0.14036587, 0.10973382, 0.095143825, -0.18786812, -0.04433381, 0.04301664, 0.3060177, 0.18051994) * g_13;
    result += mat4(0.017087614, -0.09423588, 0.046461068, 0.0127245085, 0.16147164, 0.24400745, 0.08311569, 0.137946, -0.020603297, 0.26379335, -0.09492048, 0.16765113, 0.15279007, -0.111419536, -0.06080683, -0.10723545) * g_14;
    result += mat4(0.19078189, 0.050451245, 0.075727284, -0.007865759, -0.10067247, -0.32282433, -0.08889799, 0.025485834, -0.19373515, -0.22204797, -0.08299226, -0.28381655, -0.14620808, 0.08457609, -0.15491463, -0.07288427) * g_15;
    result += mat4(0.11656609, -0.14487429, -0.4425259, 0.021374635, 0.06596484, -0.12771748, -0.22535199, 0.028234273, 0.11496608, 0.019801984, -0.04632526, 0.20007893, 0.040895678, 0.083485365, 0.14834464, 0.08356117) * g_16;
    result += mat4(0.02211244, 0.08450315, 0.024438182, -0.0043306663, -0.1586669, 0.024556836, -0.0056188432, 0.19931546, -0.15735053, -0.16440377, -0.10889861, 0.06196059, 0.022048898, -0.037491623, -0.34702402, 0.20129041) * g_17;
    result += mat4(-0.33401018, -0.014858959, -0.08085903, -0.0008211832, 0.14658095, 0.028263792, 0.27077958, 0.0016592528, -0.025635215, 0.055104904, 0.22146593, 0.18182918, -0.06691726, -0.039572526, 0.14165977, -0.23499596) * g_18;
    result += mat4(-0.013547897, -0.025930658, 0.027264774, -0.1256101, -0.051624347, 0.33928105, -0.04096477, -0.04092852, 0.061986156, 0.07382448, -0.41080087, -0.093699835, -0.217555, -0.5191564, -0.30832314, 0.05686793) * g_19;
    result += mat4(-0.12603499, 0.011196643, -0.10582392, 0.120446354, 0.044026893, 0.26011583, -0.018695889, -0.12168744, -0.032591492, 0.0948056, -0.0015739531, 0.2480614, 0.16675782, 0.26526824, 0.34634092, 0.12777542) * g_20;
    result += mat4(0.09301084, -0.10419714, 0.06912984, -0.17989379, -0.15554993, 0.12535709, -0.017463861, -0.17737497, -0.008574159, 0.05409429, 0.14558169, -0.22812454, 0.03895372, 0.1275974, 0.22765099, 0.057943035) * g_21;
    result += mat4(-0.24794875, 0.10049649, 0.028166026, -0.23643738, -0.14107783, -0.010134537, -0.0795233, 0.04698603, 0.11822467, 0.21065955, 0.2251092, -0.19143367, -0.035236355, -0.13354316, 0.07519012, -0.003378642) * g_22;
    result += mat4(-0.08100237, -0.016064119, -0.17029656, 0.13301337, -0.44654125, 0.20930994, 0.053686365, 0.20886885, 0.008915734, 0.08018005, -0.14843301, -0.1306173, -0.28592983, 0.051150486, -0.098725766, -0.068406634) * g_23;
    result += mat4(-0.16141048, -0.18943654, -0.04775461, 0.08474171, -0.11267106, 0.035240255, -0.12966546, -0.0010696419, -0.0058098137, 0.13086191, -0.2514126, -0.1916487, 0.19768499, 0.046074815, 0.3501277, 0.07461552) * g_24;
    result += mat4(-0.03546506, -0.00097176316, -0.174551, -0.11048581, 0.17106281, 0.01978063, 0.19416088, 0.1295629, 0.28066772, 0.09117813, 0.3837941, 0.1571746, -0.21350138, -0.16293706, 0.01890914, -0.120004654) * g_25;
    result += vec4(0.0056376588, -0.032156657, 0.017695736, 0.04698144);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf2, gxy, result);
}