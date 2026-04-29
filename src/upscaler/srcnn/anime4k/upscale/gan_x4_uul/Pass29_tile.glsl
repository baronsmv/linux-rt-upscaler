// Anime4K_Upscale_GAN_x4_UUL - Pass 29 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_6_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_6_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_6_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_8_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_9_tf4;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.09465223, -0.10873596, -0.35955498, -0.17102978, -0.07865758, 0.03300757, -0.040852863, 0.20757945, -0.0925244, -0.12299689, 0.0736371, -0.09471192, -0.3779846, 0.009169354, 0.11503113, -0.20957986) * g_0;
    result += mat4(-0.058279574, -0.22219251, -0.020915214, 0.0945366, 0.025918057, 0.057270855, -0.09852459, 0.14113797, -0.10049611, 0.03105915, 0.072065726, -0.056170464, 0.07183245, 0.24152692, 0.0058397814, -0.03508323) * g_1;
    result += mat4(0.15363896, 0.4238941, 0.123930104, -0.09307702, -0.1192144, -0.16101883, 0.005986172, -0.058577128, -0.19313446, -0.10295509, 0.20574117, 0.06833371, -0.0012903785, 0.29995304, -0.13213697, -0.1254232) * g_2;
    result += mat4(-0.2903937, 0.124987245, -0.024089197, -0.052240573, -0.024258995, 0.030661397, -0.010137248, -0.1609303, -0.10407328, -0.10629749, 0.04671163, -0.02009596, -0.07435262, -0.14072737, 0.2149428, 0.018486146) * g_3;
    result += mat4(-0.21417011, 0.2847672, -0.029020585, -0.10139499, -0.07400215, 0.10372491, 0.15485775, 0.12855476, 0.12904498, -0.08895321, -0.05515003, -0.20980029, 0.062432468, -0.038182955, -0.1816266, 0.355782) * g_4;
    result += mat4(-0.027595734, 0.12219175, -0.19319062, 0.035706658, -0.022891225, -0.085733496, -0.036004573, 0.051092744, -0.054424077, -0.030906882, -0.024611901, 0.08716703, 0.22153278, 0.13969363, -0.09846757, 0.016469453) * g_5;
    result += mat4(0.09095948, -0.03645167, 0.27152961, -1.7102455e-05, -0.007632466, -0.15666215, -0.26401493, -0.1549594, 0.050031006, 0.06181179, 0.07006888, -0.04870327, 0.3641525, -0.008073426, 0.16188, -0.091207646) * g_6;
    result += mat4(0.11283634, -0.005790793, -0.013517275, -0.16165686, -0.08701689, 0.033309393, 0.0010972739, 0.1642712, 0.04757619, -0.21329707, -0.04592619, 0.08010882, -0.10787384, 0.059010185, 0.05669982, 0.05839971) * g_7;
    result += mat4(-0.0017897426, 0.096831605, -0.10264635, -0.0007392807, 0.042224903, -0.07351851, 0.16442567, -0.10968471, 0.056543402, 0.38061613, -0.3234678, 0.22569597, -0.077230684, -0.3087383, 0.081054784, 0.087633185) * g_8;
    result += mat4(0.080605924, 0.06986007, 0.28359544, -0.3324396, 0.032405134, 0.011231502, 0.10453376, 0.15081415, 0.23304632, 0.01282744, -0.110539354, 0.119230196, -0.08274707, 0.79631245, -0.0049962257, -0.06853797) * g_9;
    result += mat4(0.24957526, -0.35100362, 0.14683032, 0.11050717, -0.08336315, 0.04131765, -0.19087222, -0.101899385, 0.122537844, -0.059581943, 0.11842144, -0.17657922, -0.017872468, -0.20183705, -0.08783171, -0.0649328) * g_10;
    result += mat4(0.1166889, -0.23226629, 0.12511998, -0.15160328, -0.035666835, -0.091406055, 0.064867236, 0.04495807, 0.014363706, 0.13465384, 0.012661851, -0.007246858, -0.08463122, -0.1826089, 0.008594106, 0.05406961) * g_11;
    result += mat4(-0.044576548, 0.03944883, 0.02922514, 0.04857608, 0.07982457, 0.28547665, -0.2580222, 0.27174193, -0.009301607, -0.15731618, 0.27248174, 0.111558996, 0.016642686, -0.070072554, -0.25297874, -0.13660255) * g_12;
    result += mat4(0.0619904, 0.027571948, -0.20821859, -0.075592734, -0.047970783, -0.16417085, -0.23739098, -0.43939596, 0.028930046, 0.0899, -0.24729219, -0.18904929, 0.04907895, 0.13355176, -0.032109547, -0.029098922) * g_13;
    result += mat4(-0.075305015, -0.004550873, 0.079111785, 0.0367624, -0.28268716, 0.034016214, 0.061273348, -0.29881823, 0.346599, 0.10867586, 0.1497806, 0.092778146, -0.26263794, 0.061326664, 0.15384254, 0.13936105) * g_14;
    result += mat4(0.2143571, 0.04833282, 0.018522646, -0.12657177, 0.2562043, 0.19504175, 0.07278834, -0.05239313, -0.46725237, -0.117593594, 0.021978024, -0.2434228, 0.25235966, -0.06409148, 0.0025807568, 0.06643222) * g_15;
    result += mat4(-0.38482606, 0.0037258423, -0.024128545, 0.050342213, -0.17996104, -0.12157712, 0.028484367, -0.11472539, 0.17927656, 0.043731786, 0.08844086, -0.013330732, 0.05990761, 0.2168297, 0.09100677, -0.0008136453) * g_16;
    result += mat4(0.50347346, 0.1341378, 0.023524579, -0.1837871, 0.145017, -0.06573727, 0.02377743, -0.03617753, -0.07013405, -0.21561088, 0.1574615, 0.17621611, -0.000903247, -0.19177268, -0.013945821, 0.0014927404) * g_17;
    result += mat4(0.024711724, 0.3515622, 0.47648275, 0.07185405, 0.20586282, 0.17289369, 0.042327203, 0.34730917, 0.03348624, 0.008369107, 0.24884492, -0.019298946, 0.02819896, -0.087031476, -0.002446221, -0.18767828) * g_18;
    result += mat4(-0.0786536, 0.13503742, 0.3140287, -0.21691471, -0.1240609, 0.106962465, 0.039765242, -0.09525154, -0.11635654, -0.025509981, -0.09417984, 0.27709702, -0.050951984, 0.012091699, 0.0031243872, 0.17191774) * g_19;
    result += vec4(0.009157748, 0.0064318995, 0.070232585, 0.055942155);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf4, ivec3(valid_xy, tile.inputLayer), result);
}