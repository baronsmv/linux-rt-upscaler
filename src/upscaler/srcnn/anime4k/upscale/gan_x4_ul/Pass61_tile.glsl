// Anime4K_Upscale_GAN_x4_UL - Pass 61 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_27_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_27_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_27_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_27_tf3;
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
layout(set = 0, binding = 1038) uniform texture2DArray tex_conv2d_28_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv0ups1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_27_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_27_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_27_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_27_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_27_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_27_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_27_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_27_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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
#define g_28 (max((texture(sampler2DArray(tex_conv2d_28_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_29 (max(-(texture(sampler2DArray(tex_conv2d_28_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.20925894, 0.104857735, -0.40466902, 0.0584133, -0.14659958, -0.036843687, 0.13835002, -0.2415225, -0.17522843, 0.11434039, -0.20046623, 0.16023546, 0.2475015, 0.042058993, 0.002350279, -0.17032729) * g_0;
    result += mat4(0.11970422, -0.10322249, -0.070675366, 0.06804973, 0.079779394, -0.016731435, 0.04715111, 0.13588014, 0.14615758, 0.022396626, -0.18744521, 0.03337888, -0.048930615, 0.17753999, 0.08515489, -0.27303153) * g_1;
    result += mat4(-0.044238064, -0.044585355, -0.4703711, 0.17369467, -0.22562256, 0.003894716, 0.2256651, -0.103996016, 0.007853871, 0.14751841, -0.05668432, 0.07511469, 0.1619497, -0.020217957, -0.090126194, -0.16162491) * g_2;
    result += mat4(-0.12567434, -0.04298686, 0.12304879, -0.16227202, -0.008668434, 0.15376252, -0.1295699, -0.07683395, 0.046303485, -0.012221398, 0.0038834864, -0.09826842, 0.12768197, 0.18517894, -0.18903579, -0.19901276) * g_3;
    result += mat4(0.17195696, -0.17648453, 0.19818112, -0.023518814, 0.09163597, -0.0049098246, -0.11661733, 0.016902868, 0.060930923, -0.01878846, 0.11788164, -0.1353775, -0.08755757, 0.014184077, 0.16375954, -0.06450589) * g_4;
    result += mat4(-0.0034882906, 0.27027172, -0.08576453, -0.2118125, -0.086501405, 0.010157458, -0.2640269, -0.046359222, 0.028317366, -0.16451906, 0.12050226, -0.053686112, -0.10052837, 0.096894056, 0.16462097, 0.094494134) * g_5;
    result += mat4(-0.05727481, -0.013227722, 0.21700768, -0.07177067, 0.033377443, -0.0545755, 0.027782457, 0.2090808, 0.011714184, -0.010148169, -0.18692647, -0.2786883, 0.23827875, 0.0011900894, 0.08619064, 0.14836025) * g_6;
    result += mat4(0.16917573, 0.21033037, -0.0050825966, 0.18095241, -0.029595587, -0.32528213, 0.20749976, 0.15824726, 0.01744845, -0.18352279, -0.19498493, 0.024413247, -0.017869025, -0.12914586, 0.021449931, -0.019033303) * g_7;
    result += mat4(0.050177246, -0.023704303, 0.0017737169, 0.022661313, 0.007864253, 0.0176497, -0.16047522, 0.10303941, 0.2444177, 0.41632912, 0.00715035, -0.18481494, 0.05252633, 0.006689579, 0.13945661, -0.018428788) * g_8;
    result += mat4(-0.0941601, 0.048248548, 0.16638602, 0.041016433, 0.0026687274, 0.019066641, 0.08475801, -0.09578143, -0.10059114, -0.29335198, 0.017439498, 0.11830718, -0.054326836, -0.11888715, -0.04045584, 0.073335744) * g_9;
    result += mat4(-0.13832748, 0.21032946, 0.31014842, 0.17925423, -0.063551836, -0.1199703, 0.16982867, 0.016346592, -0.025109967, -0.022150239, -0.37054747, -0.49025953, 0.14235863, 0.06635017, 0.002241298, 0.0040627583) * g_10;
    result += mat4(-0.13018467, -0.0144080445, -0.16799062, -0.1249275, -0.12707768, 0.07865254, 0.038435075, 0.1667798, 0.09192991, -0.03252081, 0.7629332, 0.48081362, -0.00011961902, 0.058554083, 0.11982404, 0.1822051) * g_11;
    result += mat4(-0.06755234, -0.0075415038, -0.14266185, 0.12655805, -0.0045153988, 0.0048743295, -0.008591593, 0.056268115, 0.024279088, -0.0629758, -0.14188884, -0.025769057, 0.15646881, -0.14415343, -0.22970784, -0.037042253) * g_12;
    result += mat4(0.25852588, 0.017387692, 0.13789654, -0.019787727, -0.11308935, 0.16850404, -0.2373339, -0.04899185, 0.17354745, -0.09472497, -0.21602263, -0.21760805, -0.020826988, 0.16989823, 0.0741717, -0.10448863) * g_13;
    result += mat4(-0.18604822, 0.009787992, -0.06459633, 0.052285228, -0.14829153, 0.075823255, -0.111874774, -0.09117474, 0.03208986, 0.021619327, 0.30147213, 0.13760304, 0.12453839, -0.016333232, 0.094405904, 0.0878566) * g_14;
    result += mat4(0.14507103, 0.07554785, 0.03146559, 0.045327432, -0.051290758, 0.039846797, 0.114740096, 0.26464698, -0.1658753, -0.12688372, -0.179181, -0.0732476, -0.031645183, -0.02680665, -0.17883217, -0.061550755) * g_15;
    result += mat4(0.08742578, -0.14921658, -0.008039882, 0.032061443, -0.17833516, -0.23691227, -0.14369945, -0.017769985, 0.065309726, 0.038026232, 0.23837644, 0.005659167, -0.20681982, 0.061288934, 0.080895506, -0.067547865) * g_16;
    result += mat4(-0.19850676, -0.015734296, 0.018384686, 0.020779416, 0.1471408, 0.26202065, 0.05143831, -0.18096192, -0.14602786, 0.027607052, -0.22484896, -0.08151626, 0.11529563, 0.1390684, -0.16282271, -0.012490131) * g_17;
    result += mat4(-0.048379734, -0.041772716, -0.0041537993, 0.21717072, 0.10138077, -0.12603214, -0.18361042, 0.049941633, 0.1703956, 0.11111548, 0.12635674, 0.06445028, -0.08243661, 0.06709483, 0.046443917, 0.10167419) * g_18;
    result += mat4(-0.035105225, 0.06199828, 0.0020574334, -0.011254863, -0.047805354, 0.1722725, 0.08265051, 0.049911566, -0.17403728, 0.02808134, -0.16923027, -0.023735922, -0.008281012, -0.093713865, -0.07359882, 0.048530914) * g_19;
    result += mat4(0.020626063, 0.008559935, -0.023751533, 0.103401795, 0.17920512, 0.042976495, -0.12651409, -0.114272855, 0.0033929124, -0.031355213, 0.08776122, -0.22491921, 0.2031401, 0.2379429, 0.28060517, -0.0007719008) * g_20;
    result += mat4(0.026417585, 0.17757705, -0.043824922, 0.028119845, -0.04151611, 0.054795753, 0.0028165078, 0.00073246437, 0.1412875, 0.21982361, -0.087146886, 0.10897306, -0.11245943, -0.14196636, -0.052475058, 0.037263144) * g_21;
    result += mat4(0.18080506, 0.15489496, 0.022035526, 0.061552692, 0.090489246, 0.0372591, -0.076371096, 0.09855082, 0.12062604, -0.11851761, -0.091217645, -0.0456572, -0.15227035, 0.19842634, -0.25994444, 0.0014280345) * g_22;
    result += mat4(-0.004529129, 0.00022631227, 0.13502745, -0.062293727, 0.0070622144, 0.14676675, 0.053662084, 0.072721094, -0.02548614, -0.13910522, -0.042703785, 0.03434115, 0.14548635, 0.009612174, -0.101212025, 0.18954988) * g_23;
    result += mat4(0.0022483568, -0.08712446, 0.10486132, 0.26073435, -0.00852917, -0.09080537, 0.10038895, -0.105297185, 0.07585101, -0.17707159, -0.20059243, -0.0673406, 0.08531025, 0.13096005, 0.057341557, -0.13544896) * g_24;
    result += mat4(-0.0006035619, 0.09268198, -0.016875379, -0.14467251, 0.009340458, -0.101583, 0.057097267, 0.112552926, -0.07803109, 0.3324704, 0.033041988, 0.077711694, -0.037180506, 0.0757784, 0.081892945, 0.123966664) * g_25;
    result += mat4(-0.057247143, -0.03035935, -0.03899445, 0.19533473, 0.009087412, -0.075170524, 0.0023444563, -0.041517466, -0.037251793, 0.012194933, -0.073488355, 0.1223987, -0.18770866, 0.031678624, 0.015153505, -0.13081336) * g_26;
    result += mat4(0.052989263, -0.0714155, -0.12801231, -0.05954568, -0.02600527, 0.12803787, -0.019737625, 0.11588791, 0.13464773, -0.07630486, 0.054382257, -0.2291579, 0.042531025, -0.046213683, 0.09142889, -0.020872064) * g_27;
    result += mat4(0.14624128, -0.09307583, -0.18519302, -0.010523176, -0.042090297, -0.039113797, -0.17932849, 0.1574002, 0.042603053, 0.18812989, -0.061091296, 0.084948115, -0.11052512, 0.11764443, -0.13139613, 0.15068875) * g_28;
    result += mat4(-0.052416, 0.011094299, 0.13501611, -0.052369393, -0.02655924, -0.10207045, 0.02851461, -0.13901424, 0.034044232, -0.22422798, 0.006999936, 0.004138137, 0.15997367, -0.12716383, 0.025097579, -0.23885375) * g_29;
    result += vec4(0.02927894, 0.051008213, -0.011481529, -0.038922433);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups1, ivec3(valid_xy, tile.inputLayer), result);
}