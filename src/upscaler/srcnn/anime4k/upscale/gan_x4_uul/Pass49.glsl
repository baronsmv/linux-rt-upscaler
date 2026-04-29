// Anime4K_Upscale_GAN_x4_UUL - Pass 49 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_15_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_15_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_15_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_15_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_15_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_15_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_17_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_18_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_15_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_15_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_15_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_15_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_15_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_15_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_15_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_15_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_15_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_15_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_15_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_15_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_17_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_17_tf, pointSampler), pos)), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.33416227, 0.09829885, -0.14215165, 0.047257327, -0.25676978, 0.06477231, 0.18437357, -0.09317491, 0.14196362, -0.09833729, -0.05023742, 0.30286238, -0.095891505, -0.05642394, -0.04279076, -0.20932348) * g_0;
    result += mat4(0.05250283, 0.097802795, -0.10851134, -0.034588467, 0.08729734, -0.13947372, 0.14574417, 0.15165779, 0.15822525, -0.09741342, -0.29856458, 0.101639755, -0.17390165, 0.20864505, -0.23063898, -0.069147386) * g_1;
    result += mat4(0.2346171, -0.12033308, -0.10432819, -0.028732711, -0.22354195, -0.09041756, -0.10091414, 0.004025042, -0.01537579, -0.11316728, -0.09128845, -0.10836599, 0.098449625, 0.021946304, -0.0559169, -0.027388508) * g_2;
    result += mat4(0.16285792, -0.2265136, -0.10871404, -0.116897024, 0.120534234, 0.047987677, -0.004379848, 0.055190843, -0.16359152, 0.1373434, 0.2990455, 0.013323317, -0.113601066, -0.28977937, 0.2619728, 0.17309852) * g_3;
    result += mat4(-0.16532536, -0.004392614, 0.094332375, -0.07948231, 0.0965218, 0.094979055, -0.16280106, 0.037660465, 0.11163236, 0.09897609, 0.084096566, -0.1494275, -0.016781123, -0.062385462, -0.26847538, 0.1566464) * g_4;
    result += mat4(-0.09193836, -0.035500966, 0.19209282, 0.30185416, -0.102988094, 0.03829289, -0.37286982, -0.08325574, -0.21487275, 0.0675388, -0.2152679, -0.15988335, -0.14248285, 0.033678766, 0.26234034, -0.113209285) * g_5;
    result += mat4(-0.22717316, -0.0009200798, 0.003287377, -0.002284066, -0.034983475, 0.15027894, -0.13538387, 0.0062207277, 0.00039265986, -0.007900346, -0.18446177, -0.13124779, 0.37357095, -0.039655972, 0.18370372, -0.13613242) * g_6;
    result += mat4(-0.008904987, 0.22167958, 0.022735478, -0.10282882, 0.009706884, 0.10853093, -0.11238819, 0.07017576, 0.08412395, 0.09763671, 0.092221156, -0.20290114, 0.12376833, 0.062525444, 0.13981692, -0.15654904) * g_7;
    result += mat4(0.2202994, -0.05487525, 0.11625077, 0.35435417, -0.0033555152, -0.03066193, 0.04199444, -0.06022421, -0.046327718, -0.04349393, -0.017858896, -0.29926088, -0.026567936, 0.0232344, 0.031930014, -0.16508788) * g_8;
    result += mat4(-0.014044821, -0.105468035, 0.16994655, 0.09042197, 0.02509403, 0.043242466, 0.007714088, -0.014514478, 0.12195026, -0.14864756, -0.17863454, 0.021342438, 0.05473602, 0.03023287, -0.04338681, 0.25018957) * g_9;
    result += mat4(0.11178171, -0.031541932, -0.022311704, 0.06927876, -0.118677296, -0.07876712, 0.2573275, -0.16963796, -0.09918738, -0.09615811, 0.18225491, 0.18405153, 0.28958827, 0.10559797, 0.23273212, -0.23836672) * g_10;
    result += mat4(0.17404434, 0.006543903, -0.04151141, 0.08504442, -0.036097426, 0.102214396, 0.18505338, -0.121599965, 0.05311446, 0.067163326, 0.03339468, -0.10639028, -0.08318937, 0.03591386, -0.096980564, 0.16911677) * g_11;
    result += mat4(0.05569724, -0.24573782, -0.08229295, -0.015653128, -0.088948324, 0.06831632, -0.0009226177, 0.20754391, -0.08485601, 0.27108276, -0.18006897, -0.14416619, 0.014280893, -0.20544566, 0.06332818, -0.18700986) * g_12;
    result += mat4(-0.014061824, 0.2738249, 0.13395612, 0.1722393, 0.1108353, 0.14290176, -0.19484134, -0.14986867, -0.00047288154, -0.3510016, 0.13103095, 0.10223549, 0.32832077, 0.19840792, 0.118998185, -0.028437005) * g_13;
    result += mat4(-0.15725374, 0.17122267, 0.114801794, 0.2099415, 0.12080525, 0.059072934, -0.023651272, -0.13910551, -0.036585454, -0.47406256, 0.055988673, 0.24299833, 0.05235501, -0.12523869, -0.00253683, 0.11640101) * g_14;
    result += mat4(-0.081746235, -0.22889271, 0.053322088, -0.08665787, 0.24643211, 0.027273338, 0.09500774, -0.115398645, 0.040935457, 0.0883963, 0.18543912, -0.098223954, -0.029414238, 0.024577033, 0.33146027, 0.038923774) * g_15;
    result += mat4(0.06752596, -0.25002465, -0.22013777, -0.11161415, -0.07435017, -0.06942425, -0.02743294, 0.108842425, -0.0013048031, 0.108312085, 0.10029556, 0.21221648, -0.26489133, 0.24258105, -0.073929526, 0.12577781) * g_16;
    result += mat4(-0.05739181, 0.23090334, 0.006777456, 0.036732256, 0.060325738, 0.0047021233, -0.016167793, -0.0797981, -0.06797836, -0.022108275, 0.09807591, -0.07017568, 0.1110942, 0.009747667, -0.06542803, 0.14152472) * g_17;
    result += mat4(0.07776711, -0.098150186, -0.16863117, 0.0073495065, 0.05722358, -0.34379464, 0.026611788, 0.158512, 0.17978796, -0.0070248432, 0.08746297, 0.0050373445, 0.06347449, -0.5033429, 0.04252335, -0.21747608) * g_18;
    result += mat4(-0.07743927, 0.010540148, 0.16479133, -0.0024370546, 0.18661375, -0.020397237, 0.016077021, 0.051072516, -0.037119925, -0.06755068, 0.12466155, -0.056955684, -0.36593297, 0.23062328, 0.22472279, -0.054084912) * g_19;
    result += mat4(-0.011354759, 0.093901664, -0.20744812, -0.072959766, -0.18470302, 0.028048197, -0.24052349, 0.12828217, -0.040006574, -0.067410275, -0.03315965, 0.06631403, -0.28481728, 0.005110992, 0.20470636, -0.009981321) * g_20;
    result += mat4(-0.03354525, -0.059142444, -0.15623446, 0.015744166, 0.08541153, -0.072278626, -0.04104654, -0.046746574, 0.11032013, -0.04839051, 0.029939886, -0.04404479, -0.050214116, -0.12854907, -0.187336, -0.09875316) * g_21;
    result += mat4(0.09276934, 0.1589921, -0.14998227, 0.15918075, -0.10429563, 0.14331265, -0.028513614, -0.29926082, 0.14870556, 0.14363697, 0.03612754, -0.34358153, 0.007659696, 0.03472827, 0.24480377, 0.25565132) * g_22;
    result += mat4(-0.058360998, -0.041696765, -0.025950164, -0.086585455, 0.059222456, -0.13592203, 0.12421702, 0.25911456, -0.30712909, -0.32777423, -0.065243766, -0.18262905, 0.2039587, 0.052910935, -0.08447836, 0.093383566) * g_23;
    result += mat4(-0.17947456, -0.107932284, 0.11335294, 0.16742402, -0.123715445, -0.27323994, 0.15531261, 0.22766086, 0.16263995, -0.2014767, -0.40492374, -0.15713632, -0.26240152, 0.018007467, 0.0621857, -0.2819687) * g_24;
    result += mat4(-0.26559585, 0.014900249, 0.16911738, -0.17638609, 0.22711746, -0.16094574, 0.03393967, 0.1899959, -0.1117433, -0.023160132, 0.054320656, 0.047609437, -0.0006658183, -0.020135878, 0.21770352, 0.6265344) * g_25;
    result += vec4(0.004939347, -0.026483338, -0.056496214, -0.07306347);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf, gxy, result);
}