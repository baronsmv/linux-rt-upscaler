// Anime4K_Upscale_GAN_x4_UUL - Pass 73 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_24_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_24_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_23_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 1038) uniform texture2DArray tex_conv2d_22_tf;
layout(set = 0, binding = 1039) uniform texture2DArray tex_conv2d_25_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv0ups1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_24_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_24_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_24_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_24_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_24_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_24_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_24_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_24_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_24_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_24_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_24_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_24_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_23_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_23_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_24 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_25 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_26 (max((texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_28 (max((texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_29 (max(-(texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_30 (max((texture(sampler2DArray(tex_conv2d_25_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_31 (max(-(texture(sampler2DArray(tex_conv2d_25_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.04541149, -0.0050366437, -0.015469368, 0.085441045, 0.00990414, 0.06771481, -0.037142653, 0.010778902, 0.0044673462, 0.051542062, 0.08994092, 0.13987154, -0.042845074, -0.16132447, 0.023451751, -0.22481805) * g_0;
    result += mat4(-0.09941504, 0.15387146, -0.051998027, -0.11480554, 0.062280208, -0.005401726, -0.17179395, -0.03911185, 0.0854519, 0.062706485, -0.019981606, 0.24536288, -0.030532219, 0.007958136, -0.13649222, -0.024381576) * g_1;
    result += mat4(0.03832889, 0.048103765, 0.12716842, 0.113495626, 0.0440496, 0.07310629, -0.0028000488, 0.17484048, 0.011438359, 0.07389019, 0.02776241, -0.069316044, -0.022972163, 0.10774051, -0.0938801, -0.046535835) * g_2;
    result += mat4(-0.19215232, 0.05232597, 0.10455481, 0.023444505, 0.10927069, 0.08145, -0.08996904, -0.04260127, -0.064315274, 0.026296314, -0.032755814, -0.03785644, 0.27563438, -0.07841699, -0.18636514, 0.12306294) * g_3;
    result += mat4(-0.048399806, 0.0760641, -0.05177265, 0.033973522, 0.067749225, -0.004380821, -0.0774159, -0.009233096, -0.16465154, -0.011200447, 0.21356043, -0.019024562, -0.20229931, -0.07075142, -0.15664288, 0.015643707) * g_4;
    result += mat4(-0.094351426, -0.12644641, 0.05531359, 0.056707513, 0.030638099, 0.07659976, -0.17997725, 0.19117208, -0.17829312, -0.12216621, 0.09648017, 0.14906263, -0.05786116, -0.07496384, 0.09830126, -0.014810007) * g_5;
    result += mat4(0.036279242, -0.06603527, 0.023111718, -0.02337117, 0.02710492, -0.006981581, -0.20071441, -0.1842067, -0.03716068, 0.04709737, 0.045576848, -0.06879641, 0.0679718, 0.23346439, 0.09709889, -0.057084534) * g_6;
    result += mat4(0.053583074, -0.14553311, -0.005482713, 0.12731002, -0.089931406, -0.07933109, 0.19270168, 0.11797083, -0.16010518, -0.060825907, 0.18154316, -0.20427613, -0.094507605, 0.02467587, 0.14440428, 0.039989635) * g_7;
    result += mat4(0.097599536, -0.09245783, -0.20063862, 0.06792256, -0.039978925, -0.05130527, 0.0061799865, -0.09635809, 0.042743832, -0.058897775, 0.0623141, 0.08815142, 0.00898274, -0.27158666, 0.18644404, 0.12572071) * g_8;
    result += mat4(0.13333327, -0.11141384, 0.0189257, 0.07486067, -0.1887069, -0.20007583, 0.13411185, 0.024675677, -0.06711045, -0.071214765, 0.14236219, 0.016948408, -0.17799276, -0.05374693, 0.15060847, 0.067363665) * g_9;
    result += mat4(0.038455024, -0.14224243, 0.100015596, 0.07427762, -0.09106503, 0.032443333, -0.14614339, 0.007896408, 0.022800734, 0.07946349, -0.16902667, -0.09839048, 0.14083186, 0.08481537, 0.011087685, 0.032849867) * g_10;
    result += mat4(0.085465506, -0.039180238, -0.057328876, 0.103486076, -0.019720137, -0.09047379, 0.08041987, -0.2419467, 0.15151846, -0.06660591, 0.08598306, -0.086127274, 0.15807416, 0.21837251, 0.14295265, -0.009427875) * g_11;
    result += mat4(-0.06841592, -0.047096353, 0.06594589, 0.04006714, 0.093568385, 0.11080303, -0.02862795, -0.24802656, 0.0015378788, 0.06396377, -0.06855018, -0.068710275, 0.072966084, -0.012504705, -0.065130696, -0.122934654) * g_12;
    result += mat4(0.12186286, 0.063676104, -0.029995052, -0.016781203, 0.019202778, -0.08175405, -0.10161839, 0.15557866, 0.05808489, -0.0065964856, 0.12905426, 0.20926952, 0.07859256, -0.008686442, 0.07933362, 0.027106019) * g_13;
    result += mat4(0.270541, -0.22690733, -0.1241414, 0.11304112, 0.31634018, -0.21323228, -0.18280524, 0.21687673, 0.0849898, -0.12234687, 0.21007027, -0.0402851, -0.12860335, 0.08126234, 0.08792168, 0.16685387) * g_14;
    result += mat4(-0.33927166, 0.29690525, -0.019686026, -0.25433338, -0.31825894, 0.14450845, 0.102088116, -0.07890628, 0.039674938, 0.30625406, -0.13709925, -0.10864652, 0.13764969, -0.11079243, -0.20283377, -0.121819116) * g_15;
    result += mat4(0.05846476, 0.25823107, 0.24806418, 0.055018846, 0.041051112, 0.14231546, 0.26531783, -0.13815305, -0.0347555, 0.0021447854, 0.035343073, 0.083788805, -0.009663775, -0.2863793, -0.09310482, -0.28089014) * g_16;
    result += mat4(0.0034832477, -0.1229684, -0.34263536, -0.2484542, -0.28131288, -0.22963811, 0.014533452, -0.059620526, 0.05972659, 0.0315117, -0.0146327, 0.0036656864, -0.16042776, 0.11570312, -0.13519408, 0.1524639) * g_17;
    result += mat4(-0.07282957, 0.022656137, 0.22041114, -0.08377895, 0.06489512, -0.036208138, 0.24620621, -0.3203503, -0.0572401, 0.13856757, 0.09503737, -0.18688709, 0.045257136, 0.08645792, 0.092612706, 0.0051408974) * g_18;
    result += mat4(0.15591198, -0.06501203, -0.066183835, 0.2039885, -0.041642334, 0.03326719, -0.1649146, 0.18826574, 0.041689713, 0.05594161, -0.21183926, 0.025191378, 0.041054897, -0.16157486, -0.17657453, 0.06918169) * g_19;
    result += mat4(0.017149586, -0.00056166644, 0.051872972, -0.032802667, -0.12568107, 0.039902873, 0.125781, 0.053033836, -0.03665155, 0.027094372, 0.02308107, -0.098191015, -0.018361865, 0.14320368, 0.01797281, 0.07521308) * g_20;
    result += mat4(0.033408675, 0.02283129, 0.02997752, -0.15788378, 0.07751225, -0.0834777, -0.1002591, -0.0842283, 0.004094495, -0.08941768, 0.015826201, 0.07211303, -0.007596218, 0.086126134, -0.016881859, -0.12621973) * g_21;
    result += mat4(0.09811428, 0.009112735, -0.03894858, -0.017335944, 0.059483584, -0.026246855, 0.1123727, 0.0808981, 0.1304059, 0.056278635, 0.1863773, 0.037938364, -0.09004633, -0.009749274, 0.152544, 0.067436) * g_22;
    result += mat4(-0.07445963, -0.08267445, 0.028935976, 0.07464005, -0.067380376, -0.08914155, 0.07307107, -0.080588445, -0.11806715, -0.08066856, -0.08647821, -0.049984932, -0.107150786, 0.0059908605, 0.014040852, -0.020190625) * g_23;
    result += mat4(-0.01459231, 0.059856355, -0.0875324, 0.027868854, 0.08657608, 0.06361718, -0.035373274, -0.0904787, 0.019741405, -0.018468766, 0.029145246, -0.05455427, -0.030421326, -0.009832721, 0.13064435, 0.12649667) * g_24;
    result += mat4(0.011868002, -0.07753596, 0.066872604, -0.04274739, -0.053444482, -0.005729885, -0.018525766, -0.00016065332, -0.058514312, 0.0052640345, -0.03733426, 0.0045842915, 0.011884783, 0.012894087, -0.072470754, -0.041928362) * g_25;
    result += mat4(0.018619414, 0.1113799, 0.022361143, 0.052643936, 0.046952497, 0.04414177, -0.20046502, -0.033954926, -0.05493111, 0.0051490664, 0.047908846, -0.10915426, -0.13786307, -0.011663383, 0.02886674, 0.029417193) * g_26;
    result += mat4(0.082477964, -0.122627676, -0.009119556, 0.00893143, -0.102564596, -0.012067043, 0.12668522, 0.049084503, 0.24883293, -0.14231145, -0.08492953, 0.056602266, 0.03987694, 0.015669636, -0.052809853, -0.04570298) * g_27;
    result += mat4(0.071245566, -0.0025086792, 0.16800047, -0.10551504, 0.029111952, 0.057431195, 0.07436777, -0.106048554, -0.111476324, -0.08960098, -0.056703247, 0.01733813, 0.017663429, 0.16780144, 0.088644154, -0.09442747) * g_28;
    result += mat4(-0.095035836, -0.060732454, -0.28546825, 0.04226247, -0.04221599, -0.07030749, -0.0042552785, 0.045604907, -0.028733522, 0.0071931393, 0.03753302, -0.018106647, 0.026788713, -0.0751185, -0.090948716, 0.09595944) * g_29;
    result += mat4(-0.20686343, -0.15346256, -0.023360955, 0.19853018, -0.0714482, -0.061878093, -0.12700674, -0.16375071, -0.11983135, 0.04651, -0.03974687, -0.01663389, 0.20360872, 0.103487924, -0.07434735, 0.20740858) * g_30;
    result += mat4(0.18442543, 0.05037994, 0.02335825, -0.12077025, 0.045586806, 0.13201606, 0.11823723, -0.17146091, -0.10422535, -0.12337711, 0.088312276, -0.059173893, -0.1398436, -0.11372023, 0.0055838027, -0.105238646) * g_31;
    result += vec4(-0.03529498, -0.032170508, -0.021623377, -0.0031779222);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups1, ivec3(valid_xy, tile.inputLayer), result);
}