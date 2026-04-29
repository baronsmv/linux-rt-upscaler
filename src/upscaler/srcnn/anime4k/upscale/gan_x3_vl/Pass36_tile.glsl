// Anime4K_Upscale_GAN_x3_VL - Pass 36 of 47 - https://github.com/bloc97/Anime4K
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
// -----------------------------------------------------------------------------
//  Push constants (only in tile-mode shaders)
//    layout(push_constant) uniform TileParams {
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  inputLayer;      // array slice to read (0-based)
//        uint  margin;          // context margin (pixels in feature-map space)
//    } tile;
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

layout(push_constant) uniform TileParams {
    uvec2 dstOffset;
    uvec2 tileOutExtent;
    uvec2 fullOut;
    uint inputLayer;
    uint margin;
} tile;

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_18_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_18_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_18_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_20_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_21_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_18_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_18_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_18_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_18_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_18_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_18_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.09549911, 0.37316352, -0.04671274, 0.022156661, -0.099851176, -0.016477318, -0.15647866, 0.3075032, -0.41206098, -0.10546171, 0.040359724, 0.13995685, -0.37928727, -0.017326128, 0.047914587, 0.14423256) * g_0;
    result += mat4(0.084515356, 0.006663507, -0.21146557, 0.26029226, -0.25549483, 0.06314179, 0.0009546878, 0.011714899, -0.20285705, -0.09633961, 0.044988878, 0.010919512, 0.11979154, -0.35923663, -0.33764264, 0.24825361) * g_1;
    result += mat4(-0.13476388, 0.20931306, 0.06758379, -0.24818432, -0.014518509, -0.19829272, 0.20000297, -0.22848319, -0.07284091, 0.14168872, -0.10349599, -0.038411904, -0.1296637, -0.033355676, -0.019598074, 0.037219126) * g_2;
    result += mat4(0.05446092, -0.15814775, -0.051778644, -0.04556046, -0.05707862, 0.05894901, 0.30567068, -0.34205344, 0.07921361, 0.018968029, -0.217382, 0.12733924, 0.16229834, 0.25780123, -0.095756724, -0.068911575) * g_3;
    result += mat4(-0.13599817, -0.11680487, 0.07268368, 0.21054786, -0.14810202, 0.12554282, 0.21146035, -0.023012314, 0.14020249, -0.1214641, -0.11742288, 0.062001504, 0.02912684, 0.008054588, 0.020715035, 0.115733996) * g_4;
    result += mat4(-0.10301303, -0.20502062, -0.020675663, 0.04069118, 0.27905715, 0.19296066, -0.16847864, -0.085301064, 0.20787837, 0.07654023, -0.05522329, -0.076257445, -0.25044343, -0.43387407, -0.068221375, 0.11907199) * g_5;
    result += mat4(0.066475466, -0.17091195, -0.013050041, 0.05297836, 0.37009987, -0.12823582, 0.19216327, 0.16380179, -0.058420453, -0.15365978, -0.14184836, 0.10372518, 0.124301985, 0.019163188, 0.0068595526, -0.14791846) * g_6;
    result += mat4(-0.17540008, -0.07897177, 0.031282343, 0.1203962, 0.1185166, -0.03167777, -0.07604457, -0.1384773, -0.4286709, -0.32054543, 0.17831656, 0.104549386, 0.13248782, -0.048322544, 0.23582847, -0.03182922) * g_7;
    result += mat4(0.16559057, 0.14952078, -0.153311, -0.14549127, 0.06029146, 0.13079861, -0.20099011, 0.111981146, 0.26113033, 0.16972302, 0.17616469, -0.06314989, 0.28278658, 0.039805803, -0.035618275, 0.029560173) * g_8;
    result += mat4(-0.07657932, -0.22380318, 0.2373389, 0.22987534, 0.23404339, 0.019233508, -0.2622599, -0.4245506, -0.050316285, -0.096794784, -0.22926746, 0.19520392, 0.05983981, 0.05918882, -0.023647195, -0.2528051) * g_9;
    result += mat4(-0.05170879, 0.036037747, -0.07416669, 0.0359808, -0.31013575, -0.05018038, 0.12777044, 0.00060244696, -0.08604466, 0.44220653, -0.13737565, -0.20205748, 0.26324764, 0.09860818, -0.124673955, 0.20514517) * g_10;
    result += mat4(-0.32772323, -0.106489114, 0.26368877, -0.14325057, 0.050906926, 0.34152874, 0.05805066, -0.036700435, -0.013218071, -0.048243362, 0.19560795, -0.18726018, 0.20994471, 0.11561842, -0.02017441, -0.0816956) * g_11;
    result += mat4(0.022519596, 0.13739026, 0.24774754, -0.060937256, 0.25772008, 0.28999618, -0.13695791, -0.088689476, 0.028487388, 0.07854702, 0.12198411, 0.016715651, 0.14221917, -0.035250396, -0.025666341, 0.10188678) * g_12;
    result += mat4(0.08483084, -0.046606388, 0.05214152, -0.0794586, -0.31594074, -0.18887727, 0.038710102, 0.07454813, 0.104813755, -0.011655456, -0.17008287, -0.17740634, -0.13157463, 0.15785204, 0.19256103, -0.14532489) * g_13;
    result += mat4(-0.20306674, 0.1292239, -0.28123298, -0.18613516, 0.24752474, 0.14401013, 0.06234358, 0.31490028, -0.071559936, 0.015407359, -0.009575451, -0.14955868, -0.084203295, -0.12973298, 0.007254705, 0.14774777) * g_14;
    result += mat4(0.08610954, -0.11005577, 0.31825662, 0.10915726, 0.021506164, -0.09548129, -0.0313006, 0.10486949, -0.19896136, -0.1046353, 0.026411569, 0.030561283, -0.07856321, -0.053018767, -0.056160312, 0.08518151) * g_15;
    result += mat4(0.056912024, -0.113755904, 0.21678402, 0.0047052423, 0.2992955, 0.0425172, 0.18385644, -0.112410665, -0.03510993, 0.05937854, -0.17551777, -0.0066648335, -0.20076093, 0.024946915, 0.15961152, 0.085359626) * g_16;
    result += mat4(-0.20451596, 0.15053003, -0.024022756, -0.14673562, 0.20152482, 0.073144756, -0.05883982, 0.09941695, -0.124058485, 0.2529782, 0.18737115, 0.057465617, 0.23198842, -0.03696399, -0.010907207, -0.019168029) * g_17;
    result += mat4(0.22507596, -0.031345993, -0.037750687, 0.25322357, 0.16381021, 0.059297476, -0.2563697, -0.002998937, -0.14249223, 0.008298676, 0.09520146, 0.2786267, 0.14549607, 0.067360066, 0.016998664, 0.046272833) * g_18;
    result += mat4(-0.13654792, 0.011035229, 0.20823318, -0.0048796176, -0.011389315, -0.25957406, -0.04244137, -0.03109198, 0.02487866, 0.18223195, 0.008499495, -0.25806475, 0.0005713295, 0.09914737, 0.104602136, 0.10642613) * g_19;
    result += mat4(0.08935836, -0.046523742, 0.028143274, 0.10530491, -0.2550387, 0.12701567, 0.044246152, 0.20321028, 0.015860397, -0.089859016, 0.24590254, -0.2112368, 0.16364408, 0.029709993, 0.13556595, -0.010670673) * g_20;
    result += mat4(-0.09306708, -0.038163673, 0.11326007, 0.04958378, 0.10383473, -0.12534077, 0.038890462, -0.2463075, -0.22917604, -0.20793879, -0.20209685, 0.056477755, -0.030611562, 0.44527152, -0.110011935, -0.27335247) * g_21;
    result += vec4(0.030681891, -0.017473118, -0.034582928, 0.0316943);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf, ivec3(valid_xy, tile.inputLayer), result);
}