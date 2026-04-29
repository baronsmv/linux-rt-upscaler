// Anime4K_Upscale_GAN_x4_UUL - Pass 67 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_21_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_21_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_21_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_21_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_21_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_21_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_23_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 1038) uniform texture2DArray tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_24_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_21_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_21_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_21_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_21_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_21_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_21_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(-0.092858694, -0.05931229, 0.08649155, -0.19388752, 0.09477594, -0.22718045, -0.1061536, -0.1075417, 0.070740245, -0.06802919, 0.011984387, 0.04561339, -0.123741224, 0.108184166, 0.08394222, -0.14939074) * g_0;
    result += mat4(0.058254354, -0.0013696381, 0.016420096, -0.13577567, -0.08013081, -0.32121193, 0.10837322, -0.027337125, 0.006335759, -0.022232484, 0.08410539, -0.19057351, 0.124672756, 0.07544909, 0.25975785, -0.12386142) * g_1;
    result += mat4(0.124638155, -0.047200475, 0.18284287, -0.066423684, -0.013056071, -0.10780445, -0.046076063, 0.16543722, 0.011813712, 0.18919142, -0.054241043, -0.14428662, -0.072056115, 0.22149223, 0.020946557, -0.19635367) * g_2;
    result += mat4(-0.011655322, -0.02780763, -0.041065313, 0.07305037, 0.065463156, -0.055100318, 0.053504564, 0.12533133, 0.1791797, 0.07803201, 0.14791118, -0.17383428, -0.13258645, -0.057591084, -0.06590273, 0.24618948) * g_3;
    result += mat4(-0.076750286, 0.16913669, -0.041372858, -0.04987621, -0.09025659, 0.04717571, 0.17061087, -0.0018001683, 0.088723816, -0.1515349, -0.09417965, 0.025807919, 0.10298056, -0.07137411, 0.0913601, -0.0032140615) * g_4;
    result += mat4(0.076089844, -0.18487781, -0.031016396, 0.04298503, -0.07412648, -0.05946974, -0.029923726, -0.17263255, 0.044034805, 0.07122984, -0.022364214, -0.16337745, -0.3163445, 0.20027465, 0.006309955, -0.25441465) * g_5;
    result += mat4(-0.05660039, -0.03776745, -0.062613666, 0.1953333, 0.027620526, -0.081940845, 0.13821705, -0.030160451, 0.30174896, -0.063806735, -0.21273777, -0.23096886, 0.028107658, -0.035367317, 0.06729705, 0.18349262) * g_6;
    result += mat4(-0.024347452, -0.10386407, -0.0013563661, 0.09973845, 0.07293425, -0.04880119, -0.05229062, -0.18888217, 0.11884971, 0.05060733, -0.0013016739, 0.18116015, -0.038804606, 0.022207338, -0.043657467, 0.10695812) * g_7;
    result += mat4(-0.16758966, 0.15170631, 0.12204208, 0.1287092, -0.032021195, -0.1063502, -0.08161841, -0.2446335, -0.02391331, -0.061028045, 0.13008249, 0.10459833, -0.04717144, 0.05381585, -0.33450723, 0.291269) * g_8;
    result += mat4(0.07273305, 0.13187234, 0.04062448, 0.081797674, 0.00045577955, 0.09757571, -0.37391075, -0.17263971, 0.021420933, -0.07653126, 0.055799145, 0.04442693, 0.11818517, -0.044239108, 0.044269893, -0.41765675) * g_9;
    result += mat4(0.018076504, -0.085451566, 0.09415942, 0.12273072, 0.41912425, -0.2747585, -0.07259103, 0.08299482, -0.20763668, 0.14662866, 0.026512189, -0.10415019, -0.09460718, 0.17926225, -0.1907316, -0.058848727) * g_10;
    result += mat4(-0.13229714, 0.2401772, 0.08083883, 0.008972119, 0.090474635, 0.18910415, 0.14324625, 0.15242074, 0.16881411, -0.18706103, 0.1793161, -0.10074233, 0.2067493, -0.3289337, 0.13461551, 0.20269714) * g_11;
    result += mat4(0.07219379, -0.11565219, 0.028837852, 0.26118317, -0.13906774, 0.10994847, 0.1192699, 0.097068354, -0.10574048, -0.010274859, -0.041781224, -0.0022481561, 0.12714253, -0.41399276, 0.19635102, -0.23090687) * g_12;
    result += mat4(-0.100183904, -0.18720408, -0.13301018, 0.03502532, 0.031246057, -0.06721582, -0.17222083, -0.063806996, -0.08393857, -0.19553204, -0.05699341, -0.20882502, 0.048502672, -0.015325282, -0.14586648, 0.07136885) * g_13;
    result += mat4(-0.09550682, -0.09559199, 0.0093339095, 0.20071933, -0.07908767, 0.19251561, -0.13115655, 0.0072511537, 0.14562629, -0.20998305, -0.2212794, 0.061366275, -0.10772557, 0.29247293, 0.25483248, -0.06853779) * g_14;
    result += mat4(0.19130619, -0.08254158, -0.41616592, -0.12058406, 0.26799643, 0.018203866, 0.02795237, -0.026012532, -0.24163988, 0.27320904, 0.075838536, -0.43140167, 0.14748523, 0.2741325, 0.0313845, 0.0612638) * g_15;
    result += mat4(0.32383236, -0.05585864, 0.087669775, -0.15189308, -0.07285363, -0.10978753, 0.038074855, -0.20369512, 0.0534748, 0.09033383, -0.3636552, 0.2022929, 0.1410257, 0.0006435122, 0.31075886, 0.09591187) * g_16;
    result += mat4(-0.056077003, 0.22655378, -0.3908979, 0.3520772, 0.27514228, 0.028264234, -0.33393502, 0.12211863, -0.12077039, 0.3201821, 0.15064837, -0.2715489, 0.2161978, 0.2011329, -0.15005851, -0.19502445) * g_17;
    result += mat4(-0.006493266, -0.067167185, 0.1981182, -0.2185078, -0.098532386, 0.0012275389, 0.014535081, 0.022241963, -0.065986834, -0.13995624, -0.08640626, -0.036836196, -0.24935777, -0.12563467, -0.22868343, -0.043145802) * g_18;
    result += mat4(-0.24015582, -0.1428461, -0.10846771, -0.03822917, 0.25849542, 0.21787684, -0.10540706, -0.15437967, 0.09093761, 0.16064538, -0.040830817, 0.03802804, 0.07929484, 0.22184348, 0.17115451, -0.020434693) * g_19;
    result += mat4(-0.16424751, 0.18149984, -0.08263852, 0.10497438, -0.0057385676, -0.18649873, 0.1049834, 0.0753644, 0.07605413, -0.024556413, 0.16013342, 0.006168524, 0.14073265, 0.02001347, -0.08537071, -0.24739261) * g_20;
    result += mat4(0.014010803, -0.057850603, 0.0732021, -0.1718671, 0.024967216, 0.19706325, -0.14325745, -0.0021808648, -0.039533336, 0.058277003, -0.09344739, -0.004221897, 0.13857067, 0.081996195, 0.030180087, -0.013901144) * g_21;
    result += mat4(0.024102923, 0.056380466, 0.008602807, 0.09951257, 0.04897817, 0.045386482, 0.13025592, -0.21351977, -0.11473196, 0.1844349, 0.07928108, 0.1533404, 0.07377011, -0.1464216, 0.096964546, -0.007197212) * g_22;
    result += mat4(0.22597581, -0.13459527, 0.22883248, 0.14732298, -0.063105844, -0.034603957, -0.07247968, 0.19268765, 0.10675177, 0.0975782, 0.00033931955, 0.08774923, -0.12306441, 0.025208015, 0.04571016, 0.13542841) * g_23;
    result += mat4(0.013317153, -0.09033908, 0.033545654, -0.054263383, 0.1317443, -0.05465494, -0.074301384, -0.30426916, -0.007050128, 0.12030467, -0.11348823, 0.19741662, -0.04095728, -0.017503742, 0.0642433, -0.28208658) * g_24;
    result += mat4(0.02021165, 0.17795627, 0.043012455, 0.053738635, -0.017870188, 0.15490524, 0.040613562, 0.15851468, -0.12762383, 0.10450818, -0.0020172964, -0.25615835, -0.012736579, 0.06002046, -0.04626082, 0.019401643) * g_25;
    result += mat4(-0.0025097467, -0.02072768, 0.034803562, -0.08400342, -0.14013165, 0.2091311, -0.03782157, 0.0023983517, 0.19771661, 0.04676574, -0.03392009, 0.20773077, 0.076976426, 0.04612587, 0.22233194, -0.13806564) * g_26;
    result += mat4(-0.032217447, 0.073498376, -0.07565292, 0.05969695, 0.16941096, -0.3131595, 0.07141137, -0.15926841, 0.108835146, -0.0040562055, 0.15678787, -0.0012778786, -0.13674988, 0.034171615, -0.19931208, -0.13748777) * g_27;
    result += mat4(-0.18563417, 0.106456436, 0.078709476, -0.1308007, -0.1398474, 0.11156628, -0.33099747, -0.19933923, -0.12798372, 0.04342623, 0.074146606, 0.21212427, 0.09915748, -0.09082417, 0.3366307, -0.23036873) * g_28;
    result += mat4(0.14234035, -0.072425894, -0.18067764, 0.1100069, 0.10129257, 0.10165853, 0.18862309, -0.04466708, -0.037151866, 0.011230992, -0.013572791, 0.20083474, -0.18335798, 0.13396202, -0.2539405, 0.1323329) * g_29;
    result += vec4(-0.02703924, 0.18005958, -0.12375494, 0.031321514);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf2, ivec3(valid_xy, tile.inputLayer), result);
}