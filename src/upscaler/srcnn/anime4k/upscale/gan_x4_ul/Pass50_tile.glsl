// Anime4K_Upscale_GAN_x4_UL - Pass 50 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_23_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_24_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_21_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_21_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_23_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_23_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.08979697, -0.10504161, 0.16022556, 0.11341658, 0.061358813, -0.11527514, 0.104621656, 0.17846957, -0.21971604, -0.08296368, 0.059561037, -0.030467503, -0.18203235, -0.00489335, -0.13960212, -0.1846774) * g_0;
    result += mat4(-0.021587428, 0.13345426, 0.002885677, -0.10446278, 0.17950022, 0.029065073, -0.32806116, 0.11106503, 0.041467514, -0.28959805, -0.033284128, 0.031551834, 0.006884119, 0.09131054, 0.02568901, -0.11571497) * g_1;
    result += mat4(-0.061347164, -0.019125437, -0.14035773, 0.17835122, -0.18599916, 0.006040366, -0.10548407, 0.16857028, -0.12821414, -0.257687, 0.083109885, 0.033304747, -0.03638158, 0.089094125, -0.2121359, -0.16846325) * g_2;
    result += mat4(-0.19272862, -0.040250458, -0.025220647, -0.0130254505, 0.16971767, -0.1262595, -0.17335917, -0.06738606, 0.25743198, -0.07245476, 0.034572147, 0.36634898, 0.06062579, -0.08718957, -0.03222726, -0.2564149) * g_3;
    result += mat4(-0.19240691, 0.12406588, 0.3184258, -0.34774688, 0.14093249, 0.03706444, -0.111542135, 0.26256654, -0.1875004, 0.049010817, -0.28910252, -0.07044059, -0.061912216, 0.0849468, 0.044482302, -0.09588286) * g_4;
    result += mat4(0.15970096, -0.0030905118, 0.28313154, 0.027417777, -0.1538593, 0.21207502, 0.13121693, -0.30331814, 0.121317744, 0.042900104, -0.022242952, 0.10603051, -0.029436313, -0.06481103, 0.1403121, -0.052515112) * g_5;
    result += mat4(0.08658267, 0.1741316, -0.18155402, -0.10258272, 0.032190584, 0.066993676, 0.1354344, 0.027893255, -0.017966608, 0.23040892, 0.030393174, -0.07598643, 0.13171883, 0.18465646, 0.067950405, -0.089663) * g_6;
    result += mat4(0.122048914, 0.11810184, -0.11860061, -0.26858392, -0.209042, -0.16273905, -0.055165585, -0.005811152, -0.18738034, 0.058543697, -0.039830476, -0.16113137, -0.091200404, 0.2339841, -0.021218592, 0.26669285) * g_7;
    result += mat4(-0.014585638, -0.0032463232, 0.17495912, -0.08503565, -0.19564098, 0.22158442, -0.1867278, 0.0042652315, 0.03968311, 0.28752264, -0.28998294, -0.0029852116, -0.23554218, 0.16868985, 0.08550133, -0.1574371) * g_8;
    result += mat4(0.49997026, -0.016691396, -0.18841855, 0.30310807, 0.100790545, 0.038233314, 0.1611522, 0.13933793, -0.22570881, 0.12208755, 0.23460633, 0.15977637, -0.03795079, -0.30355585, 0.0011402427, -0.07599262) * g_9;
    result += mat4(0.1040602, 0.087594695, -0.27393925, 0.0418618, 0.06769233, 0.10341748, 0.03344078, 0.14392397, 0.19013835, -0.003081719, -0.2819769, 0.025617521, 0.09402475, -0.015399136, 0.04733618, -0.044959366) * g_10;
    result += mat4(-0.060594074, 0.015600568, 0.16962534, -0.00081952167, 0.2690884, 0.04898387, 0.23332061, 0.094616964, -0.08526234, -0.07512189, 0.04900841, -0.18874052, 0.09941649, -0.040419415, -0.13692108, 0.16164334) * g_11;
    result += mat4(-0.053954955, 0.28258643, -0.07396885, -0.29855832, -0.05407898, 0.014401148, -0.054173157, -0.15637222, 0.272353, -0.02170652, -0.015834406, 0.08651297, -0.11185562, -0.19492313, -0.024557848, 0.10485409) * g_12;
    result += mat4(-0.08333046, -0.06798886, -0.11723233, 0.2928367, -0.029574843, 0.2017853, -0.26673993, 0.1334675, 0.017647222, 0.011599432, 0.2609211, 0.16404016, 0.16160911, -0.13806355, -0.0770869, -0.12961225) * g_13;
    result += mat4(-0.19316232, 0.15813714, -0.077418946, -0.20926195, -0.16160491, -0.11846783, -0.026574116, 0.061050467, -0.18681675, -0.062164336, -0.18367381, 0.00018551799, 0.031343188, 0.2299072, -0.118061095, 0.2129531) * g_14;
    result += mat4(-0.002469605, -0.042093765, -0.10694342, 0.42083347, 0.0670906, 0.30298585, 0.09004686, -0.23083562, 0.14870504, 0.17281657, -0.20583957, 0.010098754, -0.033128325, -0.111837484, 0.14905591, -0.15318894) * g_15;
    result += mat4(0.036136966, 0.018714666, 0.04639626, -0.19534552, -0.10005012, -0.0117230825, -0.21940173, 0.04220659, -0.0032740128, 0.059329886, 0.14921357, -0.056334518, -0.15263896, -0.16852587, -0.044578124, 0.2628712) * g_16;
    result += mat4(0.100949906, 0.004228454, 0.06405682, -0.06885952, 0.24312544, -0.33124098, -0.24260363, 0.0024199567, 0.1508378, 0.086369656, -0.08181863, -0.4503699, 0.17878622, 0.11472353, 0.16728742, -0.13093603) * g_17;
    result += mat4(-0.06985756, -0.0019436302, 0.015692828, -0.013669101, -0.20771547, 0.067934655, 0.06843243, -0.09379625, -0.043609153, -0.0037825725, -0.10029127, -0.1315925, -0.079464234, -0.08471481, 0.07953321, -0.07559369) * g_18;
    result += mat4(0.09396738, -0.08508011, -0.15136994, -0.05033154, -0.13346456, 0.07239574, -0.14461002, 0.03597791, -0.064514555, 0.06253932, -0.17408507, 0.037559777, -0.15963385, 0.08210336, -0.24775903, -0.01580598) * g_19;
    result += mat4(0.084354095, 0.18890528, 0.07061357, 0.23486592, -0.15324847, 0.18526913, -0.34279072, -0.37405473, -0.09294527, 0.010385339, 0.19220817, -0.04336903, -0.38940063, 0.076640904, 0.17280221, -0.09818483) * g_20;
    result += mat4(0.038739417, -0.07602283, 0.003676506, -0.22913142, -0.08044049, -0.19263157, -0.18030334, 0.09494168, 0.156977, -0.27044684, -0.031590268, 0.20470932, 0.28102174, 0.16872606, -0.11217233, 0.24780095) * g_21;
    result += mat4(0.06689687, 0.08853936, 0.09184726, 0.22699554, -0.14092675, -0.02688781, 0.2646647, 0.026377598, 0.12483503, -0.06999643, 0.04486326, -0.0897168, -0.022117272, 0.14900659, -0.26331872, 0.104682565) * g_22;
    result += mat4(0.065322906, -0.11183809, -0.17946585, -0.20076565, 0.009464183, -0.123363525, -0.07686269, 0.083753645, -0.062136367, 0.17842509, 0.17349558, -0.10999101, -0.036272816, -0.016200582, 0.10451098, 0.19585742) * g_23;
    result += mat4(-0.19023383, 0.26640254, 0.26287216, 0.055038862, -0.3129526, -0.022839354, 0.009630041, 0.08733156, -0.2612418, -0.19251396, 0.058636077, -0.3330285, -0.078063555, -0.27609676, -0.020230204, -0.18260407) * g_24;
    result += mat4(0.14539486, -0.21613313, -0.3492072, -0.20886984, 0.25280094, 0.01690657, 0.117284745, -0.14519997, -0.5187426, -0.14994088, 0.18306793, -0.0025114815, 0.022995003, 0.11710601, -0.05377852, 0.11480645) * g_25;
    result += vec4(-0.0247107, 0.005474094, -0.09375405, -0.020514423);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf1, ivec3(valid_xy, tile.inputLayer), result);
}