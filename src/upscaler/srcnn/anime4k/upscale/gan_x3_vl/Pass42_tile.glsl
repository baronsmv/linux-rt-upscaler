// Anime4K_Upscale_GAN_x3_VL - Pass 42 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_20_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv0ups2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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
#define g_22 (max((texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.29116806, 0.0051992643, -0.06692716, 0.28666902, -0.10336563, -0.19727555, 0.11084616, 0.025079565, 0.20502086, 0.0099646095, 0.009126803, 0.17547005, 0.058746554, 0.30771896, -0.0902547, 0.028172184) * g_0;
    result += mat4(-0.28205237, -0.036779154, 0.17233336, -0.13251382, 0.07100408, -0.051303998, 0.012103571, -0.121839024, -0.14955266, -0.011649629, 0.08549354, 0.18840949, -0.022462592, 0.021153163, 0.08049452, -0.15091342) * g_1;
    result += mat4(-0.2800372, 0.0042544575, -0.22374953, 0.201632, 0.22182395, 0.3408344, 0.03178537, -0.15618719, 0.0068062274, 0.14605409, 0.09106621, 0.05914199, 0.19480406, 0.044590045, -0.13806386, -0.14847448) * g_2;
    result += mat4(0.1505132, -0.027588725, 0.04962834, -0.11202418, 0.00049648335, -0.010397765, -0.08091891, -0.01213487, -0.24162677, -0.08179791, -0.037871603, 0.014869897, 0.21078886, -0.10133107, -0.11659543, 0.017790101) * g_3;
    result += mat4(0.41658482, -0.040856514, -0.054670364, -0.24993257, -0.007376621, -0.100203015, -0.19632444, 0.16588823, 0.11921404, 0.13566074, 0.1355261, 0.18513525, -0.03692965, 0.019232113, 0.021070294, -0.09910185) * g_4;
    result += mat4(-0.11130964, 0.068555534, -0.022549039, 0.20459346, 0.08735778, -0.2480742, 0.26074892, -0.06515858, -0.15426315, -0.20087741, 0.066354685, 0.16262609, 0.094984494, -0.09765662, 0.17054209, -0.25639787) * g_5;
    result += mat4(-0.088716365, -0.15923837, 0.07887449, 0.029613947, -0.07766362, 0.20016782, 0.07279328, 0.1514442, -0.051125146, 0.008917033, 0.15708658, 0.24593906, 0.1713729, 0.22876453, -0.06126321, 0.080008015) * g_6;
    result += mat4(0.10178238, 0.17811838, 0.14818382, 0.17277409, 0.120473444, -0.1943933, -0.07498233, -0.11512788, -0.06924987, 0.04548284, -0.008307158, 0.017101327, -0.038810693, -0.12316993, -0.34380746, 0.053759247) * g_7;
    result += mat4(-0.046007603, 0.26564816, -0.06891516, 3.1265055e-05, 0.061298724, 0.1925087, -0.15881963, 0.06479692, -0.1409332, 0.12286923, -0.053091913, -0.07207155, -0.11055874, 0.21104714, 0.094566196, 0.23457485) * g_8;
    result += mat4(-0.10533191, 0.09174932, -0.19229935, -0.26465586, 0.024089642, -0.353841, 0.032621946, 0.1661062, -0.091028884, 0.026411142, 0.23693994, 0.08054671, 0.13986488, -0.20758727, -0.15448147, -0.03494388) * g_9;
    result += mat4(-0.17668007, -0.02661902, 0.270635, 0.06442596, 0.053869188, -0.0075128167, -0.12906162, 0.1310764, -0.05808231, 0.14813021, -0.061848663, 0.16322616, 0.16354714, -0.1766021, 0.034994338, -0.365292) * g_10;
    result += mat4(0.2769774, 0.0903162, -0.153144, -0.0714264, -0.15604417, -0.02184839, -0.14195657, -0.0299081, 0.030514874, -0.13219188, 0.07739793, -0.094843924, -0.15415892, 0.08821149, -0.09969291, 0.11553133) * g_11;
    result += mat4(-0.024756059, 0.02924473, -0.11059422, -0.23357926, -0.14310671, -0.039102048, -0.14977954, 0.15673035, -0.2435825, -0.05197057, -0.075606585, -0.014227886, -0.15609197, 0.033796865, -0.11727036, 0.21573412) * g_12;
    result += mat4(-0.0034791795, -0.015750842, 0.21795836, 0.06755854, 0.21003358, 0.18348697, 0.007344055, 0.007894167, -0.031829726, -0.13820398, -0.024139944, -0.06376093, 0.16212739, -0.14601658, 0.011433787, -0.21962811) * g_13;
    result += mat4(-0.19470121, 0.07634093, 0.084294625, -0.1930676, -0.04052925, -0.07640723, 0.048489477, -0.067031436, 0.018694758, -0.051234454, -0.09647271, -0.05313391, -0.033016447, -0.30730128, 0.05531499, 0.24194908) * g_14;
    result += mat4(0.11188614, -0.0942737, 0.045266267, 0.02038586, 0.09011196, 0.15573163, -0.066437334, 0.09889085, -0.080061264, 0.037342984, 0.16573298, 0.12220635, -0.026486188, 0.25633007, 0.11129816, -0.2026236) * g_15;
    result += mat4(0.04242307, 0.112535976, -0.19269057, -0.23816746, -0.052621387, 0.0633971, -0.19528675, -0.042162407, 0.199502, 0.05493077, -0.088709444, 0.08472976, 0.054185133, 0.06422858, -0.039366808, -0.18133119) * g_16;
    result += mat4(-0.0053883283, 0.07370045, 0.17995751, 0.10520973, 0.06260075, -0.124870464, 0.071332276, 0.14470188, -0.038855236, 0.09279109, 0.10985604, -0.12241432, -0.20250633, 0.072249405, 0.06563947, 0.25110915) * g_17;
    result += mat4(-0.037988666, -0.02077325, 0.12789832, 0.03384976, -0.014303905, -0.087816834, -0.056331955, -0.1313604, 0.09380784, -0.14247838, 0.10469246, -0.122811496, 0.18130052, 0.04213147, -0.012292052, -0.19898601) * g_18;
    result += mat4(-0.12018575, 0.09009986, 0.025285363, -0.115545176, 0.1733185, 0.13020052, -0.057739727, 0.2317158, -0.012717598, -0.045057297, -0.23039842, 0.02120572, -0.047350824, -0.09068979, -0.029076718, 0.019612556) * g_19;
    result += mat4(0.13583413, -0.009503754, 0.02945625, 0.13004698, 0.20902146, -0.066765055, -0.016790587, -0.022145504, 0.115125865, 0.062911294, 0.009492768, -0.17444436, -0.06236797, -0.015372606, 0.11708899, -0.012473567) * g_20;
    result += mat4(0.03781474, -0.037127525, 0.0018324303, -0.025154835, -0.1573021, -0.094748974, 0.2049456, -0.0011915033, -0.27289516, -0.13360178, -0.19483006, 0.028352307, -0.16590592, -0.24364805, -0.17105217, -0.09763515) * g_21;
    result += mat4(-0.085604936, 0.1410735, 0.006653563, 0.1621681, -0.007415839, -0.13190715, 0.0072195483, 0.011567912, -0.23232964, -0.0045645055, -0.4088787, 0.15016212, 0.11169541, -0.024033517, 0.33648142, -0.05467641) * g_22;
    result += mat4(0.19473903, -0.41680276, -0.06333307, -0.39555615, 0.12667467, 0.323478, -0.08860081, 0.0018358243, 0.18223375, -0.040291768, -0.12997696, 0.011956389, 0.07855676, -0.04246141, -0.18503502, -0.2871073) * g_23;
    result += vec4(-0.0067077694, 0.046750613, -0.02120649, 0.0037727654);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups2, ivec3(valid_xy, tile.inputLayer), result);
}