// Anime4K_Upscale_Denoise_CNN_x2_UL - Pass 22 of 25 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_2_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_2_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_3_tf1;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_3_tf2;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_4_tf1;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf2;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_5_tf1;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_5_tf2;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_last_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_2_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_2_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_2_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_2_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_7 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max((texture(sampler2D(tex_conv2d_4_tf1, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_4_tf2, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_16 (max(-(texture(sampler2D(tex_conv2d_4_tf1, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf2, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_19 (max((texture(sampler2D(tex_conv2d_5_tf1, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_5_tf2, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_22 (max(-(texture(sampler2D(tex_conv2d_5_tf1, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_5_tf2, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_25 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_28 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.06761509, 0.0010596798, 0.118115634, 0.14935187, -0.05466623, 0.091785856, -0.03665047, 0.076207176, -0.15206745, -0.074811794, -0.041557387, 0.020541618, -0.037649132, -0.07627772, -0.10156735, -0.07498991) * g_0;
    result += mat4(-0.0541389, 0.007155582, -0.06095953, -0.016313383, -0.13457695, -0.03827954, -0.034835886, 0.04974308, 0.008285558, -0.06611796, -0.067563675, -0.11533022, -0.08719109, 0.042913426, -0.083873115, 0.027492668) * g_1;
    result += mat4(0.17322378, -0.07721062, 0.076297946, -0.1325289, 0.00692486, 0.019282155, 0.038707003, 0.056305885, -0.037604675, -0.17109787, 0.052209407, -0.11086336, 0.0052244705, 0.056766637, -0.017374612, 0.06740667) * g_2;
    result += mat4(0.053550255, 0.07344529, -0.10690144, -0.08243465, 0.028142922, -0.07358604, 0.070248306, 0.0053416835, 0.009705257, 0.09426246, 0.05850371, 0.08341002, 0.06166079, 0.102394834, 0.058707405, 0.19911417) * g_3;
    result += mat4(-0.009806288, 0.061949313, 0.011325549, 0.031676874, 0.113277406, 0.07123387, -0.0022331094, -0.05520811, -0.021068804, 0.0073448666, 0.031778157, 0.06381251, -0.022977686, -0.0044090333, -0.028826792, -0.005600321) * g_4;
    result += mat4(-0.13628425, -0.107186474, 0.010461016, 0.045646533, 0.010563035, 0.0005640543, 0.002957052, -0.01454462, 0.106655054, 0.13992403, -0.01641908, 0.0264948, 0.014378123, 0.024764376, -0.06435794, -0.076860085) * g_5;
    result += mat4(0.031931117, 0.062713124, -0.049225837, -0.02620178, 0.20593183, 0.03311921, -0.02824421, -0.19422682, -0.017965427, 0.05093508, -0.07729694, -0.013976707, -0.054889455, -0.008431357, -0.00865999, 0.05323866) * g_6;
    result += mat4(-0.07898102, 0.13033123, -0.24963257, -0.046712235, -0.017762529, -0.07267942, 0.039491024, -0.034781307, 0.02270499, -0.12520099, -0.02714401, -0.13284011, 0.014340563, -0.007257448, -0.07413879, -0.12837824) * g_7;
    result += mat4(0.09598721, -0.006008832, 0.051995635, -0.07847789, 0.109905876, 0.18126504, -0.086034976, -0.0360382, 0.19074084, 0.054656357, 0.06871617, -0.041497722, 0.064660124, -0.10478427, 0.052080367, -0.1518587) * g_8;
    result += mat4(-0.044614766, -0.08404386, 0.06729217, 0.03758003, -0.23567544, -0.0450765, 0.014905518, 0.19749434, 0.0070031853, -0.068472505, 0.04280405, -0.009026482, 0.03368337, 0.037044305, 0.014582284, -0.015817456) * g_9;
    result += mat4(0.05070276, -0.13125883, 0.24694905, 0.049511425, 0.021699967, 0.080548055, -0.03720478, 0.032441437, -0.01215519, 0.09360713, 0.024676912, 0.11170701, -0.024200387, 0.0021200276, 0.06300166, 0.10979445) * g_10;
    result += mat4(-0.1055991, 0.007073368, -0.07666124, 0.06573558, -0.10762247, -0.16527167, 0.09825201, 0.051373113, -0.1926851, -0.046607103, -0.07601954, 0.05199459, -0.06756806, 0.092222616, -0.026166819, 0.1535803) * g_11;
    result += mat4(0.0067429054, 0.014872415, -0.019792963, 0.0014269215, 0.041500363, 0.018643422, 0.04487991, 0.031431414, -0.0278133, -0.028131608, -0.019798402, -0.041768856, -0.0063227355, 0.007656633, 0.0019235855, 0.00076331315) * g_12;
    result += mat4(0.025489544, 0.023983652, 0.029175067, 0.0075372118, -0.010194142, -0.014977182, 0.011589661, 0.00036903258, -0.012841702, -0.010945794, -0.012143497, -0.0069256728, 0.007313037, 0.007576904, -0.016960602, 0.009170305) * g_13;
    result += mat4(0.004188971, 0.017998729, -0.0046976185, -0.0034182668, 0.021841675, 0.012860078, 0.009202975, -0.0071324864, -0.0037808695, 0.01139587, -0.016267903, 0.007991299, 0.008879691, 0.007677154, 0.016209174, 0.011406443) * g_14;
    result += mat4(-0.008698401, -0.017972758, 0.026514322, -0.0024080887, 0.00012845756, 0.021530064, 0.0014967524, 0.0060274163, 0.017589558, 0.031043446, 0.014386793, 0.051733218, -0.013435874, -0.020567564, 0.011874828, 0.0030195254) * g_15;
    result += mat4(0.008565417, 0.0073839244, -0.012248247, -0.019089373, -0.04383907, 0.01000193, -0.003246391, 0.0502051, 0.012343873, 0.027492827, -0.011591099, 0.010474208, -0.009317595, -0.009244615, -0.00889853, -0.015167559) * g_16;
    result += mat4(-0.0149119655, -0.05737016, 0.027463723, 0.0013402153, 0.0012228708, 4.653676e-05, 5.3374144e-05, 0.010701133, 0.011828213, -0.012499855, -0.009720743, -0.035716657, -0.06976149, -0.05596556, 0.0028440042, 0.013388718) * g_17;
    result += mat4(-0.010236228, 0.08551208, -0.060067203, 0.012999882, -0.0060008806, 0.003534564, 0.009385839, 0.010742909, 0.02672157, -0.17606625, 0.13504161, -0.035290483, -0.014812689, -0.0236554, 0.031493064, 0.01800991) * g_18;
    result += mat4(0.0005283657, -0.032297328, 0.023884023, 0.024165852, 0.0017424148, -0.015371204, 0.0058860597, -0.04624227, 0.04947679, 0.09081732, -0.04592456, -0.03128466, 0.00023743653, -0.032846384, -0.0013158394, 0.0037953698) * g_19;
    result += mat4(0.0034766623, -0.006661828, 0.027227342, 0.033958994, -0.007990619, 0.0025515554, -0.016197672, -0.0010064896, 0.022598108, 0.014734878, 0.021482255, -0.0059315437, -0.038538814, 0.03478085, -0.05926627, 0.012918195) * g_20;
    result += mat4(-0.023291608, -0.013129155, 0.0032865414, 0.026531553, -0.004495095, 0.0043812403, -0.027177097, -0.009125319, -0.006041235, -0.0031154896, -0.030664662, 0.005782464, -0.008880747, 0.015690446, -0.0108247, -0.022403536) * g_21;
    result += mat4(-0.07639219, 0.05440532, 0.016447276, -0.055569574, 0.0014948049, -0.03464865, -0.006925237, 0.024131197, 0.009468209, -0.011771851, 0.013548103, 0.004704814, 0.063868396, 0.04857746, 0.08745972, 0.0690927) * g_22;
    result += mat4(0.021505289, -0.06289818, 0.031038022, -0.047952045, 0.014759762, 0.10819852, -0.044093642, -0.020913709, -0.017672667, 0.007322798, -0.0030338434, -0.015471056, 0.017840479, -0.052742675, 0.044256743, -0.014589662) * g_23;
    result += mat4(0.037849434, 0.04017271, 0.01840757, -0.05590355, 0.041468013, -0.015397055, -0.059170194, 0.08708615, 0.021914955, -0.0045240326, 0.03308673, 0.0141805615, -0.045770008, 0.048188016, -0.08913234, 0.046581928) * g_24;
    result += mat4(-0.09374169, 0.07681035, -0.032266654, 0.066911325, 0.0071584303, 0.06599442, -0.0031403983, -0.062489454, 0.013248783, 0.018261025, -0.00095267413, -0.026741864, -0.0059258267, 0.03542517, -0.033440042, -0.0007421821) * g_25;
    result += mat4(0.06491965, 0.0354909, -0.035559855, -0.07943817, 0.028543673, 0.026842002, -0.0029009457, -0.0022229373, 0.045988, -0.08896797, -0.04740724, 0.002011393, -0.067833476, -0.048432026, 0.025755037, 0.042066928) * g_26;
    result += mat4(-0.0011515832, -0.067060925, 0.02632549, 0.019017957, -0.0021755556, 0.004405696, 0.03028079, -0.043944478, -0.06373467, -0.032911435, -0.07619137, -0.055402283, -0.014293524, -0.009286333, 0.032950103, 0.0020192636) * g_27;
    result += mat4(0.033251163, -0.012636667, -0.019736348, -0.02221555, -0.035174683, -0.0024467881, -0.0020635366, 0.021488743, 0.054788366, -0.085087426, 0.06572526, -0.037050918, -0.06467607, -0.1047945, 0.10937466, 0.058931317) * g_28;
    result += mat4(-0.0015108787, 0.016789518, -0.02054971, 0.014368727, -0.083879344, -0.0024550394, 0.047329154, 0.018185811, -0.008528356, 0.04782707, 0.0019893225, 0.0095295245, -0.0024202724, -0.022640519, 0.0033455987, 0.010862984) * g_29;
    result += vec4(-0.00339168, 0.022745693, -0.021186745, 0.007273877);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_last_tf, gxy, result);
}