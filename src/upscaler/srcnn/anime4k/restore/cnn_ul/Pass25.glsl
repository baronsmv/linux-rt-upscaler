// Anime4K_Restore_CNN_UL - Pass 25 of 25 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_MAIN;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_3_tf1;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_3_tf2;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf1;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf2;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_5_tf1;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_5_tf2;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_7_tf1;
layout(set = 0, binding = 1039) uniform texture2D tex_conv2d_7_tf2;
layout(set = 0, binding = 2048, rgba8) uniform image2D img_output;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_7 (max((texture(sampler2D(tex_conv2d_4_tf1, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_4_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_4_tf1, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf2, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_13 (max((texture(sampler2D(tex_conv2d_5_tf1, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_5_tf2, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_16 (max(-(texture(sampler2D(tex_conv2d_5_tf1, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_5_tf2, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_19 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_22 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_25 (max((texture(sampler2D(tex_conv2d_7_tf1, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_7_tf2, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_28 (max(-(texture(sampler2D(tex_conv2d_7_tf1, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_7_tf2, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.068483055, 0.036389243, 0.04961808, 0.0, 0.05059915, 0.033048775, 0.029426659, 0.0, 0.07465462, -0.012659731, -0.024048671, 0.0, 0.02224484, 0.012289658, 0.008910066, 0.0) * g_0;
    result += mat4(-0.10449372, 0.019832065, 0.035194747, 0.0, 0.039656557, -0.028246421, -0.032626413, 0.0, 0.10093569, 0.021039873, -0.0120673925, 0.0, -0.047074273, -0.041248, -0.019464392, 0.0) * g_1;
    result += mat4(-0.05256942, 0.0127243735, 0.012813261, 0.0, -0.03551604, 0.040801138, 0.04893271, 0.0, -0.0016839011, -0.018044796, -0.027161835, 0.0, -0.060873054, 0.012360936, 0.020700796, 0.0) * g_2;
    result += mat4(-0.116182, -0.04271438, -0.046686683, 0.0, -0.09575506, -0.030078743, -0.024359861, 0.0, -0.04794246, 0.0044337297, 0.013972317, 0.0, -0.023228236, 0.015726948, 0.0070847897, 0.0) * g_3;
    result += mat4(0.13986528, -0.016787121, -0.015848925, 0.0, -0.04900687, -0.027417973, -0.027077334, 0.0, -0.047319725, -0.021533312, -0.018427303, 0.0, -0.06136185, -0.0051562944, -0.032072, 0.0) * g_4;
    result += mat4(0.070715815, 0.012814227, -0.0003389576, 0.0, 0.012182037, -0.014952754, -0.019349998, 0.0, -0.03254603, 0.012881403, 0.016392775, 0.0, 0.059158217, 0.0055793705, -0.003696545, 0.0) * g_5;
    result += mat4(0.022627862, -0.020713277, -0.009454221, 0.0, -0.04352193, 0.058409747, 0.07186154, 0.0, -0.009326966, 0.034919802, 0.04204233, 0.0, 0.025182368, -0.039986387, -0.04990386, 0.0) * g_6;
    result += mat4(0.0116241425, -0.039915055, -0.050241623, 0.0, -0.0076204035, 0.050215762, 0.059038218, 0.0, -0.006659752, -0.0054298495, -0.003807067, 0.0, 0.011085346, -0.009443587, -0.009128077, 0.0) * g_7;
    result += mat4(0.0453952, 0.004603456, 0.006256434, 0.0, -0.104142666, 0.05726496, 0.069169044, 0.0, -0.10102446, -0.034291938, -0.013720296, 0.0, -0.035107866, -0.008388971, -0.0068969135, 0.0) * g_8;
    result += mat4(-0.038070124, -0.015017457, -0.015852718, 0.0, 0.0607464, -0.052079927, -0.07268223, 0.0, 0.008773512, -0.026051786, -0.027285712, 0.0, -0.022916751, 0.048140153, 0.064897746, 0.0) * g_9;
    result += mat4(-0.01670857, 0.012646949, 0.03353705, 0.0, 0.038032394, -0.044542246, -0.06310885, 0.0, 0.002600519, -0.00824961, -0.008912322, 0.0, 0.023435717, 0.021788329, 0.008603494, 0.0) * g_10;
    result += mat4(-0.02889454, -0.0058613745, -0.010699256, 0.0, 0.12959917, -0.046572708, -0.06832117, 0.0, 0.028117642, 0.020422146, 0.00869695, 0.0, 0.035915125, 0.009355984, 0.005175107, 0.0) * g_11;
    result += mat4(0.037913825, -0.0099191405, -0.018130798, 0.0, -0.0065440857, 0.004536478, -0.0019739012, 0.0, -0.014918686, -0.00011652434, 0.0007071924, 0.0, -0.0033633227, -0.018028691, -0.014883887, 0.0) * g_12;
    result += mat4(-0.021300001, -0.039009467, -0.043097164, 0.0, -0.008222791, 0.057612088, 0.063239105, 0.0, 0.023676023, -0.0119777955, -0.020785704, 0.0, 0.03422571, -0.009187399, -0.016286165, 0.0) * g_13;
    result += mat4(0.031610258, -0.022373654, -0.04004249, 0.0, 0.015456217, -0.014708875, -0.017118618, 0.0, -0.0235428, 0.0103508085, 0.020143243, 0.0, 0.0044788374, -0.017377898, -0.023227183, 0.0) * g_14;
    result += mat4(-0.036366682, 0.007874863, 0.016618004, 0.0, 0.0022973057, -0.010600425, -0.012978575, 0.0, 0.0070587453, 0.005480104, 0.0052379463, 0.0, -0.02330911, -0.002091681, -0.0004570695, 0.0) * g_15;
    result += mat4(0.0011265673, 0.017461559, 0.01678395, 0.0, 0.019458788, -0.032603145, -0.042017594, 0.0, -0.026735391, 0.007520235, 0.01661426, 0.0, -0.023014631, 0.027602635, 0.040214695, 0.0) * g_16;
    result += mat4(-0.05236764, 0.007274719, 0.023289332, 0.0, -0.033428065, 0.0054935357, 0.014490033, 0.0, 0.016193395, -0.012767524, -0.022695007, 0.0, -0.01161452, 0.015592775, 0.017280621, 0.0) * g_17;
    result += mat4(0.0075503755, 0.014264192, 0.014350495, 0.0, 0.013990636, -0.0011566521, -0.005510977, 0.0, -0.021975616, -0.013216436, -0.012400287, 0.0, 0.018202957, 0.010433842, 0.007529786, 0.0) * g_18;
    result += mat4(0.012649671, 0.016378459, 0.009756208, 0.0, 0.0023225206, -0.0038671023, -0.005242471, 0.0, 0.023699954, 0.015248626, 0.011651197, 0.0, 0.014677953, 0.014319745, 0.012088228, 0.0) * g_19;
    result += mat4(-0.0030005479, 0.0052323043, 0.007744717, 0.0, -0.0077438625, -0.00072459516, -0.001971826, 0.0, -0.01263717, -0.009226968, -0.005661945, 0.0, 0.0046659256, 0.0014185858, 0.0038442858, 0.0) * g_20;
    result += mat4(-0.0053241113, -0.010728358, -0.013345879, 0.0, -0.000893072, 0.015531841, 0.015812417, 0.0, 0.021348871, 0.015751695, 0.016067913, 0.0, 0.014817982, 0.03233685, 0.031598262, 0.0) * g_21;
    result += mat4(0.0038391522, 0.0027406036, 0.0063517806, 0.0, 0.0021543978, 0.0065204683, 0.009420363, 0.0, -0.022383714, -0.012619449, -0.008763167, 0.0, -0.009436604, -0.012201518, -0.0103548, 0.0) * g_22;
    result += mat4(-0.005432008, -0.013701671, -0.021388102, 0.0, -0.001045599, -0.0032160715, -0.0036216215, 0.0, 0.031028647, 0.022415614, 0.01880324, 0.0, -0.004328173, -0.004780637, -0.005459752, 0.0) * g_23;
    result += mat4(-0.007300146, -0.0076159053, -0.0080059795, 0.0, 0.005996225, 0.0057377047, 0.0059788194, 0.0, -0.021563234, -0.020394823, -0.020401813, 0.0, -0.030919729, -0.03150251, -0.029059272, 0.0) * g_24;
    result += mat4(-0.002826552, -0.0042917025, -0.0025527687, 0.0, -0.0074001094, -0.006878869, -0.0062073106, 0.0, 0.010867636, 0.010852139, 0.008577537, 0.0, -0.01606024, -0.0143771265, -0.013291837, 0.0) * g_25;
    result += mat4(0.012113326, 0.014259359, 0.011284172, 0.0, -3.851684e-05, -0.003696042, -0.0020337042, 0.0, 0.003427011, 0.006911378, 0.008471347, 0.0, 0.0063997298, 0.004651406, 0.0075980425, 0.0) * g_26;
    result += mat4(-0.026621016, -0.027831081, -0.025364956, 0.0, 0.022336917, 0.023742557, 0.023516335, 0.0, -0.01619396, -0.01820708, -0.015288538, 0.0, 0.0045815264, 0.0022230193, 0.0017512285, 0.0) * g_27;
    result += mat4(0.043799683, 0.046862658, 0.041910093, 0.0, -0.027854608, -0.02948632, -0.02927831, 0.0, -0.051899213, -0.04971418, -0.04712937, 0.0, -0.017539004, -0.0245854, -0.023040624, 0.0) * g_28;
    result += mat4(0.022317344, 0.021462968, 0.02187171, 0.0, 0.0530127, 0.054741293, 0.052202478, 0.0, 0.029963326, 0.0298772, 0.025601966, 0.0, 0.027699472, 0.031187871, 0.02950236, 0.0) * g_29;
    result += vec4(-0.0071146404, 0.005606682, 0.010180816, 0.0);
    return result + texture(sampler2D(tex_MAIN, pointSampler), pos);
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_output, gxy, result);
}