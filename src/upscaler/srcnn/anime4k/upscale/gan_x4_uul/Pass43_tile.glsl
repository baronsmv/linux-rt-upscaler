// Anime4K_Upscale_GAN_x4_UUL - Pass 43 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_12_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_12_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_12_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_12_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_12_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_12_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_14_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_15_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_12_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_12_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_12_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_12_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(-0.20167744, -0.157522, 0.17093335, -0.2046946, 0.2856094, -0.050556354, 0.007262048, 0.14952745, -0.04247257, 0.17190292, -0.09215134, 0.19234902, 0.11206616, -0.084574, -0.3175454, 0.042932633) * g_0;
    result += mat4(-0.07878131, 0.062472034, 0.018257348, -0.19074398, 0.13601506, 0.008776523, 0.267088, -0.012840031, 0.050926745, 0.3572716, 0.12923348, 0.46291292, -0.23700884, -0.15193067, 0.0856555, 0.40051663) * g_1;
    result += mat4(0.14584677, 0.013734126, -0.18150613, -0.012350994, 0.17582431, 0.4088792, 0.26603162, 0.091171645, -0.015379834, 0.0488545, 0.24532855, -0.051027495, 0.07409059, 0.08885718, 0.05520881, 0.015742032) * g_2;
    result += mat4(-0.06285555, 0.08400318, 0.06185944, -0.18929732, 0.13995175, -0.19606028, 0.010748447, -0.20088021, 0.17389578, -0.029055133, 0.082567476, 0.050448395, 0.035711713, -0.043132007, 0.024843518, -0.09793246) * g_3;
    result += mat4(-0.3586075, -0.3017418, -0.1681393, 0.22291918, 0.15187578, -0.19922642, -0.2057764, -0.27078348, 0.011819467, 0.17961735, -0.13120805, -0.088759094, 0.2551945, 0.047898185, 0.025353746, 0.060715955) * g_4;
    result += mat4(0.016972095, -0.37482634, -0.0943781, -0.031390063, -0.34399232, 0.029482381, -0.078299224, -0.009884333, 0.21471865, -0.24464053, -0.043118928, 0.031691045, -0.10749998, -0.0004123357, -0.12062625, -0.018974587) * g_5;
    result += mat4(0.16740109, 0.11503844, -0.249842, 0.37721476, -0.041268256, -0.047318432, -0.1646984, 0.050292853, -0.05445752, -0.13412616, -0.029601602, 0.05383983, -0.09787379, 0.1975832, -0.10428375, 0.04688707) * g_6;
    result += mat4(0.12610112, -0.06527068, -0.051615972, 0.019693172, -0.064654246, 0.18017481, -0.14940402, -0.18683234, 0.01930582, -0.3629499, 0.10711305, -0.38592446, 0.18264556, 0.21697325, 0.40637898, 0.11306176) * g_7;
    result += mat4(0.015629973, 0.09973684, -0.014146676, -0.032374937, -0.007512354, 0.03472241, -0.0057590734, -0.25632006, 0.24247666, -0.23546802, -0.09738896, -0.004368026, -0.2864425, 0.063916594, -0.0911149, 0.08962794) * g_8;
    result += mat4(0.20205286, -0.119944714, -0.22832054, 0.12242931, -0.16022639, -0.0038066695, 0.15136321, 0.15943359, -0.034349896, 0.20438096, -0.024260236, -0.0099594, 0.19143064, 0.020218, -0.16863364, -0.022940978) * g_9;
    result += mat4(0.2880043, 0.2553526, 0.2121158, 0.22303773, -0.35936388, -0.012881388, 0.16779672, 0.02153533, -0.13068561, -0.19650954, 0.19661143, -0.14305532, -0.03043471, -0.04733776, 0.3437708, -0.18667449) * g_10;
    result += mat4(-0.28560263, -0.017020063, -0.0050273836, 0.006250603, 0.17099115, 0.18850201, -0.22828178, 0.015579833, 0.014822471, 0.30457675, -0.038834136, -0.31266782, 0.15971808, -0.06438075, -0.009744115, -0.03306814) * g_11;
    result += mat4(-0.15123658, 0.2563589, -0.17504866, -0.01227597, 0.025134224, -0.15487325, 0.16592397, -0.26994568, 0.08195849, -0.059410386, -0.17071712, 0.43500945, 0.10446758, -0.124810636, 0.012390868, -0.0974764) * g_12;
    result += mat4(-0.058242775, -0.16383912, 0.081500575, -0.28807116, -0.11164024, 0.06807287, -0.16831931, -0.056299932, 0.19682515, 0.22347595, 0.19510195, -0.121536516, 0.09904918, -0.030608056, 0.06541719, 0.3754091) * g_13;
    result += mat4(0.14409892, -0.1411304, -0.0836665, 0.07335537, 0.13046919, -0.07286559, 0.045427103, 0.08125719, -0.06354604, -0.062673196, -0.18825212, 0.14445488, 0.0020812547, -0.03635817, -0.11814364, -0.13838975) * g_14;
    result += mat4(0.046461742, -0.041100018, -0.024416603, -0.038657367, -0.019944014, -0.2316368, -0.024327591, 0.045484517, -0.019521859, -0.25675112, -0.17842057, 0.12149841, -0.13795595, -0.31766632, -0.11135957, -0.10803858) * g_15;
    result += mat4(-0.16907722, 0.06126622, -0.06634626, 0.03341968, -0.060098544, -0.17163853, -0.10266564, 0.2723191, 0.19778359, 0.28850815, -0.34816468, 0.00064078096, 0.0035072854, 0.17807572, 0.12858596, -0.11537019) * g_16;
    result += mat4(0.051234458, -0.07300655, 0.12607743, 0.09331296, 0.12784722, -0.2357276, 0.2502991, 0.100865416, -0.067441724, -0.17176364, 0.19372036, -0.0036744007, 0.1729184, -0.28252605, 0.13410504, 0.10560959) * g_17;
    result += mat4(-0.16876727, -0.044162266, -0.04474033, -0.052215215, -0.16071874, 0.19163048, -0.0688657, -0.093865626, -0.033344444, 0.31560823, 0.087719224, -0.136447, -0.22141162, -0.009322204, -0.04754566, -0.10042662) * g_18;
    result += mat4(0.16383414, 0.017913472, 0.031216452, 0.043571133, 0.09270605, -0.38240147, -0.047052402, -0.17349271, 0.03210811, 0.032853756, 0.012647186, -0.013132529, 0.00427122, -0.11034066, -0.073932715, -0.10335922) * g_19;
    result += mat4(0.2385153, -0.14038697, -0.088857055, 0.00049609377, 0.14978889, 0.20203528, 0.23484455, 0.11428516, -0.06660778, 0.04556526, 0.025550742, -0.04666389, 0.29577836, 0.021924702, 0.029047322, -0.22408137) * g_20;
    result += mat4(-0.058507595, -0.0062844846, -0.1952249, -0.15763733, -0.13065399, -0.11990473, 0.052280486, 0.38537347, -0.14243399, 0.07946314, 0.09423048, 0.16778792, -0.26061493, 0.04655475, -0.13971363, 0.19715877) * g_21;
    result += mat4(0.20081937, 0.11324881, 0.059111953, 0.21300194, -0.19257958, -0.02915909, 0.14482126, -0.34046003, -0.44731438, -0.043879975, 0.41890976, 0.28744698, -0.18441407, 0.012571736, 0.18022124, 0.09692596) * g_22;
    result += mat4(-0.21155542, -0.16366267, 0.037170194, 0.082775876, 0.18969263, 0.28030342, 0.12968771, 0.33312726, 0.040552497, 0.12065949, -0.351312, -0.18901314, 0.013641883, -0.11387678, 0.07249402, -0.3379979) * g_23;
    result += vec4(0.03052825, 0.036824416, -0.025144452, 0.1161349);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf2, ivec3(valid_xy, tile.inputLayer), result);
}