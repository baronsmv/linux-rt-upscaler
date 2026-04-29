// Anime4K_Upscale_GAN_x4_UUL - Pass 76 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups4;
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
vec4 result = mat4(-0.02987822, -0.14156254, -0.006805638, -0.06491689, -0.023117961, -0.11864792, -0.020782726, 0.016718477, -0.12822492, -0.2627571, -0.10936498, -0.020479368, -0.08946875, -0.07078646, -0.14763172, 0.079474844) * g_0;
    result += mat4(-0.07517533, 0.14936899, 0.005200026, 0.15833679, -0.20985723, 0.015140312, 0.16891868, -0.12731305, 0.001276647, 0.10806773, 0.07292632, -0.0230428, 0.22559881, -0.024635307, 0.05207048, 0.016969835) * g_1;
    result += mat4(0.033257335, -0.004516727, 0.08077173, 0.07780093, 0.2343147, 0.16830377, -0.16836162, -0.008906441, -0.09850461, -0.08738698, -0.26028165, -0.029635794, -0.05397607, -0.25291416, 0.08932801, -0.17621125) * g_2;
    result += mat4(0.021441426, 0.089970976, 0.087451175, 0.01982307, -0.00534548, 0.0016146855, -0.32349735, 0.020162579, 0.0049562925, -0.065152735, 0.046657056, -0.15083495, 0.11233022, -0.04739685, -0.09070248, 0.17958602) * g_3;
    result += mat4(0.1273905, 0.007927681, 0.08298969, -0.022412037, 0.035267398, 0.07840721, 0.08048102, -0.03691808, 0.016431633, 0.012698254, -0.008662408, -0.13933934, 0.12972483, 0.21850783, 0.23307513, 0.000571898) * g_4;
    result += mat4(0.0100407, -0.39405826, 0.32025802, 0.2832041, 0.33294165, -0.05958231, -0.1577708, -0.028620213, -0.048587576, 0.039346397, -0.027196862, 0.025590241, 0.00061374693, -0.01180234, -0.018360002, 0.25070924) * g_5;
    result += mat4(0.22246312, -0.04815649, 0.08736281, 0.016199166, 0.077316865, 0.045456205, -0.07477754, 0.12618002, 0.07883082, 0.0686953, 0.06405744, 0.0009818063, -0.02092714, -0.030966131, 0.09841693, -0.10895756) * g_6;
    result += mat4(0.26012385, -0.10243986, -0.06322028, -0.09087655, 0.06912959, 0.07663046, -0.23804459, 0.053852726, 0.05078947, -0.109246224, -0.14178644, -0.052218866, -0.101676404, -0.023825765, 0.026447691, -0.14865609) * g_7;
    result += mat4(0.041431427, -0.015064366, -0.2236117, -0.030924913, -0.08685426, -0.13520546, 0.11651171, 0.053487726, 0.02606458, 0.24306768, 0.16120963, 0.051762126, 0.022511886, 0.081198335, -0.034219068, 0.0092173265) * g_8;
    result += mat4(0.19416513, -0.13046128, -0.09250759, 0.033059027, -0.15878743, 0.0041482826, 0.25107592, -0.04122384, -0.12977393, 0.08382433, -0.12364666, 0.10107232, -0.015173569, 0.103763856, 0.026309956, -0.09117284) * g_9;
    result += mat4(-0.05419911, 0.00058963, -0.12988667, 0.20055313, 0.030918771, -0.014228711, -0.16702838, 0.020387288, -0.027360002, 0.014445924, -0.022155182, 0.14796254, 0.020506943, -0.111637115, -0.15514074, 0.059505507) * g_10;
    result += mat4(0.13351838, 0.15389496, -0.16921681, -0.15721107, -0.23370336, 0.10680521, 0.0915842, 0.10845563, 0.13528366, -0.10152182, -0.023946082, 0.004758842, -0.0053138984, -0.039067965, 0.10247054, -0.2013928) * g_11;
    result += mat4(0.0940642, 0.18500984, -0.051960737, -0.007081406, -0.0057662693, -0.056610145, -0.08623894, 0.085122645, -0.0117327655, 0.09875138, -0.0043660044, 0.05047526, 0.04188438, 0.20341921, 0.04265216, 0.056258943) * g_12;
    result += mat4(-0.08604029, -0.05491035, 0.059321914, -0.052624896, 0.13617016, 0.11754236, 0.11821107, -0.09910127, 0.07241852, -0.120371416, 0.09970373, -0.17198959, -0.14523451, -0.03410314, 0.015047165, 0.029333182) * g_13;
    result += mat4(0.33456117, -0.1694432, -0.33715236, 0.10869151, -0.11678155, -0.12573223, -0.37280464, 0.08583611, -0.050305888, -0.10936392, -0.0093005, -0.16355872, -0.031578295, 0.019013532, 0.12860784, -0.105620846) * g_14;
    result += mat4(-0.32792798, 0.1792595, 0.1993371, -0.08149261, 0.046808135, 0.009618961, 0.24690527, 0.017353626, -0.21925704, 0.065837644, 0.29835764, 0.05139222, 0.12341928, -0.11190375, 0.170546, 0.056202386) * g_15;
    result += mat4(-0.31099838, -0.06758222, 0.06285113, -0.07353864, -0.047731224, 0.15535083, -0.64979374, 0.099978834, 0.089411214, -0.100012384, 0.08959716, -0.15088384, 0.059998848, -0.15229112, -0.17324549, -0.08506205) * g_16;
    result += mat4(0.19391792, -0.16036808, -0.11902212, 0.07436227, 0.10363112, -0.074310906, 0.91709113, 0.084803954, -0.082337715, -0.047767054, -0.04131998, 0.11194046, -0.083899155, 0.17141213, 0.29864565, -0.026448477) * g_17;
    result += mat4(0.05156777, -0.049753625, 0.015471171, 0.052691612, -0.02994984, -0.024420734, 0.11585649, -0.20938542, 0.018834207, -0.20320056, -0.13085459, -0.0086262915, -0.04427753, 0.13335848, -0.064420775, -0.04642022) * g_18;
    result += mat4(0.16542359, 0.058639698, -0.08314426, -0.14000902, -0.05393692, -0.028636307, 0.10156203, 0.073714875, 0.07786534, 0.08234555, -0.0094138095, 0.056138765, 0.12131325, -0.12354777, 0.073989555, -0.04605284) * g_19;
    result += mat4(-0.037727747, 0.018552719, -0.06636154, -0.01930026, 0.04758094, -0.034193367, -0.008783199, -0.07046236, -0.06284397, 0.14185563, 0.15161303, 0.019813264, -0.013503992, 0.10599879, -0.03256722, -0.033422105) * g_20;
    result += mat4(-0.065330975, 0.021591648, 0.079216816, 0.10628196, 0.12180891, 0.01777432, -0.00906628, -0.08466977, 0.024665624, -0.1072835, 0.03337738, 0.0034946792, -0.15655187, -0.054999005, 0.110962674, -0.07868374) * g_21;
    result += mat4(0.033571556, -0.117526256, 0.027212862, 0.025825463, -0.074807905, 0.05171015, 0.058270566, -0.03289996, -0.18173727, -0.14643425, 0.013240775, -0.054958276, -0.040303323, 0.10216123, -0.021644054, -0.08853978) * g_22;
    result += mat4(0.028159522, 0.053900108, 0.056507323, -0.04859119, 0.09431302, -0.027665535, -0.07907181, 0.13235402, 0.06084304, 0.07409592, -0.06193444, 0.04139512, 0.042664766, 0.019047534, 0.09258238, 0.05521245) * g_23;
    result += mat4(0.11870216, 0.055985536, 0.0019851802, -0.0021985958, 0.23987925, 0.013639941, -0.05615768, 0.09740685, -0.04664704, -0.07862708, 0.009283556, -0.022454312, 0.0049701035, 0.14134249, 0.0716289, -0.0737223) * g_24;
    result += mat4(-0.30323797, -0.09561487, 0.017899506, -0.048141718, -0.056937806, -0.04146931, 0.060856055, -0.09340158, -0.06772142, -0.060182527, 0.017792957, 0.06672238, -0.050410192, -0.07002814, 0.0774449, -0.02395373) * g_25;
    result += mat4(0.09439649, 0.008914242, -0.004399012, -0.06303121, 0.12567714, -0.052876584, -0.04600808, -0.03413656, 0.0473433, 0.027317489, -0.035305254, -0.0049644914, 0.0038185562, -0.019911442, 0.012968243, -0.088209115) * g_26;
    result += mat4(-0.05984137, -0.09097414, -0.07085692, -0.007414078, -0.059817106, 0.0005326131, 0.06701414, 0.093250066, -0.07503431, -0.048183344, 0.045087397, -0.022639273, 0.0227802, 0.14528684, 0.047489513, 0.032764312) * g_27;
    result += mat4(-0.0060594324, -0.08082185, -0.060745455, 0.11094361, -0.010657223, -0.1381517, 0.004693926, 0.09341289, 0.05251002, 0.19687954, 0.0047872537, 0.08393252, -0.10891673, -0.1535456, 0.031703554, -0.007602281) * g_28;
    result += mat4(0.1211426, 0.0037113805, 0.0053533735, 0.06705086, -0.0113079185, -0.14421159, -0.091448925, -0.00971443, 0.064816035, -0.1309255, -0.03377283, -0.054445747, -0.023829643, 0.11046322, -0.04438854, 0.027087016) * g_29;
    result += mat4(0.14089139, 0.061144315, 0.05492873, 0.08141859, 0.013321813, 0.11854551, -0.0523245, 0.02350885, 0.027290756, 0.20114194, -0.04875496, 0.1252922, 0.13713759, -0.055055924, 0.01316475, 0.061486248) * g_30;
    result += mat4(-0.084306486, -0.0730094, -0.02533989, -0.045629617, -0.1022427, -0.16021572, 0.06772375, -0.027088458, -0.24639171, 0.046187285, 0.08361509, -0.08620142, 0.00507411, 0.037024546, -0.11199879, 0.039523087) * g_31;
    result += vec4(0.055495262, -0.051167354, 0.028084511, -0.043321524);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups4, gxy, result);
}