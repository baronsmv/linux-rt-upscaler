// Anime4K_Upscale_GAN_x4_UL - Pass 56 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_24_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_24_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_24_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_24_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_26_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_22_tf;
layout(set = 0, binding = 1037) uniform texture2DArray tex_conv2d_25_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_27_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_24_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_24_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_24_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_24_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_24_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_24_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_24_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_24_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_26_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_26_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max((texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_24 (max((texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_25 (max(-(texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_26 (max((texture(sampler2DArray(tex_conv2d_25_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_25_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.12234858, -0.021024397, -0.008911491, 0.008654683, -0.261921, -0.08852813, -0.014769153, 0.07656934, -0.1312976, -0.0395526, -0.1335422, 0.16576755, -0.024820516, -0.050337326, -0.10896443, 0.033768054) * g_0;
    result += mat4(-0.018000448, 0.013071354, 0.049299564, -0.07042542, 0.3076099, -0.02068737, -0.18147635, 0.10448964, 0.07281318, 0.010307286, -0.18882285, -0.014645502, 0.0791774, -0.21212971, 0.026508024, -0.058461342) * g_1;
    result += mat4(-0.23666126, -0.018033542, 0.0024688705, 0.23144715, 0.0010496895, -0.021392277, 0.08807161, 0.026790189, 0.023468774, 0.011498715, 0.14476688, 0.18361224, 0.04218432, -0.22661938, 0.34774292, 0.113836944) * g_2;
    result += mat4(-0.029370226, -0.22133234, -0.066944055, -0.24185248, -0.09880753, -0.023189416, 0.006161905, -0.07948689, 0.012845118, -0.19781755, -0.1683098, -0.10058418, -0.018076612, -0.07924661, 0.08356604, -0.23357888) * g_3;
    result += mat4(0.022303218, 0.12761936, 0.022652805, -0.20914936, 0.17180137, 0.12143295, 0.09799191, -0.12665649, 0.034417123, -0.09280215, -0.0984246, -0.07475625, -0.0069865007, 0.17393745, -0.047097508, 0.086801045) * g_4;
    result += mat4(-0.009374213, 0.13395758, -0.037030727, 0.069092, -0.12193983, -0.06298433, 0.22348295, 0.051750474, -0.0943686, -0.045059983, 0.23618917, -0.15909736, 0.11566603, 0.07151492, 0.013066669, -0.04950254) * g_5;
    result += mat4(0.05421195, 0.1602265, 0.12650324, -0.017457927, -0.008281588, -0.09576464, -0.038360406, 0.023573698, -0.071081236, 0.18549033, -0.17457892, -0.06348481, 0.0057788654, -0.17015602, -0.2143573, -0.12245353) * g_6;
    result += mat4(-0.012059985, 0.034365635, 0.038933452, 0.15287007, 0.08915255, -0.09115187, 0.020236796, -0.030026728, 0.034153678, 0.14779243, -0.2252762, 0.18940309, -0.17914702, 0.04489441, -0.016465506, 0.19653367) * g_7;
    result += mat4(-0.24926579, 0.21237439, -0.07930057, 0.11889715, -0.02740544, -0.09377776, 0.039144963, 0.24697267, -0.0735153, 0.26344168, -0.15305813, -0.03005728, -0.36296624, -0.11677285, 0.08789561, 0.15614145) * g_8;
    result += mat4(0.21561594, 0.027871598, 0.11443511, -0.08989617, -0.15216057, 0.31315288, 0.07875693, 0.31678453, -0.05351552, 0.0603098, 0.098363675, -0.024522562, 0.32440776, 0.04057012, 0.020779671, -0.09102291) * g_9;
    result += mat4(0.030619625, 0.23956256, 0.12258182, -0.056125734, 0.047818817, 0.007024855, 0.005731205, -0.044608884, 0.14420183, -0.34504604, 0.37266588, 0.21600994, 0.14392853, 0.18355964, -0.16690119, -0.055878773) * g_10;
    result += mat4(0.08539339, -0.030770814, -0.20747332, -0.14294678, 0.06483853, 0.28473207, 0.17663138, -0.14832555, -0.09196593, 0.38663465, -0.4864812, 0.024431465, -0.024223857, -0.13960868, -0.19981948, -0.0046645487) * g_11;
    result += mat4(0.052366443, -0.11314741, 0.25294435, 0.12731439, 0.12228493, 0.31405678, 0.13434315, -0.124796845, -0.07093641, 0.24931367, 0.008088064, 0.057337996, 0.14562343, -0.1662442, -0.16025625, -0.008378218) * g_12;
    result += mat4(-0.107468806, 0.012494604, 0.13145463, 0.0044467025, -0.20689802, -0.008778631, 0.22577581, -0.083029106, 0.024620963, -0.025284542, 0.055661917, 0.1272626, -0.03796311, 0.1556227, 0.042157676, -0.08214739) * g_13;
    result += mat4(-0.04830007, 0.044968493, -0.0075896606, 0.10583585, -0.002229782, -0.061159782, -0.019315276, -0.08692975, -0.02174253, 0.10504436, -0.095099375, 0.10481533, -0.10043261, -0.103314795, 0.099944495, -0.005334155) * g_14;
    result += mat4(0.12740242, 0.17563054, 0.08312964, -0.067844905, -0.04208514, 0.1110867, -0.21594112, -0.23460679, -0.13176624, 0.1059882, 0.12894152, -0.11152399, 0.09752229, 0.014816284, -0.22325674, 0.09841326) * g_15;
    result += mat4(0.0653981, -0.022964995, -0.2938982, -0.0061169066, 0.03942006, 0.019700393, 0.08734106, -0.065434955, -0.067304276, 0.112637825, -0.05742705, 0.023384662, -0.2054386, 0.29436016, 0.0037892356, -0.22304635) * g_16;
    result += mat4(0.088354826, 0.23902883, 0.08372811, 0.0065366016, -0.07964651, 0.24419506, -0.3911946, -0.029087873, 0.090739176, -0.049014863, 0.06988132, 0.02258769, 0.10247047, 0.12518027, 0.0008728705, -0.056853645) * g_17;
    result += mat4(0.19367176, -0.041542146, -0.16576086, 0.07154839, 0.044061545, 0.16537209, 0.1270174, 0.041331172, -0.20587024, -0.065511934, -0.13275598, -0.07027002, 0.18806867, -0.03407952, 0.04837352, 0.045474067) * g_18;
    result += mat4(-0.2582355, 0.17942189, 0.12967736, 0.12031099, -0.14537609, -0.041969452, -0.043003123, 0.013001321, 0.12566818, 0.0038525918, -0.08360705, 0.02547348, -0.09314052, 0.052094415, -0.08657066, 0.014753045) * g_19;
    result += mat4(-0.044867773, -0.12017535, 0.06931032, 0.21013774, -0.17006443, -0.11134061, 0.052347653, 0.22170502, 0.0809573, -0.04026027, 0.058802795, 0.033606496, -0.69711787, -0.21366166, 0.32256404, 0.001037066) * g_20;
    result += mat4(-0.109290324, 0.12479354, -0.0016870967, -0.2105443, -0.12823416, 0.19568188, -0.01180512, -0.0901166, -0.113193884, 0.20936523, -0.26581213, 0.14669225, -0.03157429, 0.078640506, 0.1446152, -0.10513303) * g_21;
    result += mat4(-0.12432017, 0.09697878, -0.09566158, -0.1560019, -0.04478926, 0.08118913, -0.023159185, -0.08924593, 0.07948424, 0.13116947, 0.08267777, 0.041434366, 0.12660475, 0.21119997, 0.040758017, 0.010252911) * g_22;
    result += mat4(-0.07343955, -0.11137574, -0.20888542, -0.010525646, 0.08654566, -0.25162008, 0.0015843184, 0.2251664, -0.16099241, -0.05303513, -0.010290805, -0.19370262, -0.09699956, -0.021551458, -0.28225294, -0.012553028) * g_23;
    result += mat4(0.13522272, -0.037814137, -0.17619848, 0.059898973, -0.19553477, 0.17938456, -0.27291644, -0.0061011547, -0.010751843, -0.035017565, 0.03794967, 0.31951827, -0.18536541, 0.13390224, 0.0263642, 0.0029341222) * g_24;
    result += mat4(-0.12729633, -0.14954208, -0.12916204, 0.22230428, 0.11732888, 0.008057732, 0.07490304, 0.13995908, 0.061645962, -0.16856796, -0.03455527, -0.37620506, 0.22656745, -0.15411325, 0.131253, -0.03256949) * g_25;
    result += mat4(0.102106966, 0.16285823, 0.07355709, -0.06602972, 0.15325125, -0.16784416, 0.1471553, -0.14970179, 0.1314055, -0.036945526, -0.014696616, 0.06697295, 0.07670483, -0.013443979, 0.10073605, 0.114370696) * g_26;
    result += mat4(0.14675961, -0.21042137, -0.10476935, -0.003657964, 0.013142314, 0.025201753, -0.0875375, 0.17088741, -0.32458684, 0.23715518, 0.07397589, -0.028977808, 0.049964994, 0.03821004, -0.01645503, -0.16695203) * g_27;
    result += vec4(0.013880447, -0.06316735, -0.020679189, 0.0052526686);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_27_tf1, ivec3(valid_xy, tile.inputLayer), result);
}