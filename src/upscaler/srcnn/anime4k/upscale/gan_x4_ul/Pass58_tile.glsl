// Anime4K_Upscale_GAN_x4_UL - Pass 58 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_27_tf3;
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
vec4 result = mat4(-0.104180515, 0.21909867, -0.0016195358, -0.00827801, -0.17956465, 0.008882964, 0.095886044, -0.12801364, 0.24021642, 0.23698345, -0.17307688, 0.024737755, 0.24745077, -0.121220514, 0.00431543, 0.11270653) * g_0;
    result += mat4(0.15997665, 0.017852405, 0.05119178, -0.15482607, 0.0473513, 0.102561824, 0.10925874, -0.088492356, -0.07925148, -0.0009926077, -0.1836283, -0.027848043, 0.078280285, 0.007133711, 0.010975833, 0.06212348) * g_1;
    result += mat4(-0.05369238, -0.3801088, 0.6358423, 0.13610448, -0.17373526, -0.06838332, -0.026865637, -0.22185935, 0.031365998, -0.24836074, 0.07786585, 0.12845472, -0.10230717, -0.090312645, -0.12451369, 0.012365612) * g_2;
    result += mat4(-0.11176632, 0.1129991, 0.19114831, -0.02778793, 0.17413953, -0.07105402, 0.062856786, 0.03620729, -0.08253814, 0.18052185, -0.23623717, 0.00784666, 0.2294231, -0.0063698697, -0.007017217, 0.19971047) * g_3;
    result += mat4(0.053607754, 0.128326, -0.08556963, -0.3267408, 0.2113072, 0.04600726, -0.087273054, 0.043838777, -0.013094107, -0.07035021, 0.06061421, -0.042725533, -0.2515608, 0.05992034, -0.00080709986, 0.053383853) * g_4;
    result += mat4(-0.1296537, -0.028914798, 0.12485024, 0.32676205, -0.15098321, -0.050126188, -0.10485253, -0.22199424, 0.004325448, 0.11900305, 0.03579892, -0.06502462, 0.09748344, -0.23620753, -0.08606443, -0.12277768) * g_5;
    result += mat4(0.06351925, -0.09474517, -0.030183055, 0.26909778, 0.012661174, -0.12511827, 0.07635961, -0.16331388, -0.07982632, -0.012759043, 0.03974436, -0.07089404, 0.114191614, -0.1768194, 0.20276785, -0.20046876) * g_6;
    result += mat4(0.118645184, -0.015464144, -0.13408852, -0.031532094, -0.036670644, 0.25638598, -0.08346215, -0.16632739, 0.10724415, 0.031202447, 0.06494471, 0.080996215, -0.1531831, -0.049804404, 0.06983809, -0.18219711) * g_7;
    result += mat4(0.057444304, 0.06428333, -0.2427994, 0.06495019, -0.2475473, 0.051088843, 0.14431933, 0.04322744, -0.0065100784, -0.07879368, 0.27862424, -0.015107099, 0.48285982, 0.07512295, -0.13956147, -0.5293498) * g_8;
    result += mat4(-0.04977926, 0.057724383, 0.005400039, -0.07485926, 0.099736564, -0.19428918, 0.3085949, -0.09256943, -0.007471054, 0.15845904, 0.024014933, -0.22958547, 0.05363298, -0.2262346, -0.08504123, 0.010983667) * g_9;
    result += mat4(-0.0011897761, 0.01905553, -0.07040949, 0.13073099, 0.07718515, -0.00919502, 0.16790766, 0.15093194, 0.07811035, 0.59745634, -0.038061313, 0.33472347, -0.046432715, -0.042526003, -0.042819142, 0.015483182) * g_10;
    result += mat4(0.16497271, -0.1832641, -0.06919869, -0.0699354, 0.1622412, -0.009429784, -0.042264223, -0.5095821, -0.22293803, -0.22964719, -0.24294993, -0.2749919, -0.24561481, 0.03678232, -0.040695712, 0.04990986) * g_11;
    result += mat4(0.17668974, -0.14166051, 0.048939627, 0.054249138, -0.07022914, -0.008821423, -0.056008007, -0.21688782, -0.14373022, -0.10112909, -0.26707867, -0.27844477, -0.13381785, 0.024470683, -0.18647262, 0.07304338) * g_12;
    result += mat4(0.1254997, 0.3412491, -0.11075748, -0.044977497, -0.2579634, 0.19033371, -0.12924103, -0.10767467, -0.18661416, -0.006703569, 0.11859471, 0.011905839, -0.15832269, -0.09578297, -0.050546784, 0.05611259) * g_13;
    result += mat4(-0.031839076, 0.24811439, -0.048889633, -0.10886483, -0.021840971, 0.07242472, 0.07856694, 0.21579736, 0.24734874, 0.002823113, 0.20664278, 0.07515607, -0.035989497, 0.025168674, 0.012789844, 0.04219985) * g_14;
    result += mat4(-0.029561277, -0.027150908, -0.2285595, 0.0623451, -0.21524262, -0.0495648, -0.26751977, -0.099391095, -0.11575608, 0.18860719, -0.26475087, 0.10348319, 0.1349935, -0.22972155, 0.07882446, -0.018600948) * g_15;
    result += mat4(0.11091095, -0.19174413, 0.0066961353, -0.028952863, -0.07400654, -0.1074968, -0.09721747, 0.02431324, 0.028736848, 0.050277565, -0.0013741596, -0.031192824, -0.03777562, 0.05401314, -0.06783531, 0.19289261) * g_16;
    result += mat4(-0.23818627, 0.22782011, -0.168649, 0.0773027, -0.29677773, 0.028283251, -0.032741956, 0.22565849, -0.059789155, -0.08474369, 0.25028643, 0.051620036, 0.06692328, -0.14508602, -0.0667097, -0.14061047) * g_17;
    result += mat4(0.13310762, -0.12951846, 0.06509994, 0.040003385, 0.049557522, 0.18617095, -0.09436182, 0.059164654, 0.11599615, -0.004864734, -0.07653804, 0.00014459781, 0.13770443, -0.14924237, 0.07231551, -0.016222041) * g_18;
    result += mat4(0.10529918, 0.08091443, -0.11911098, 0.12648894, -0.12755243, -0.051939204, -0.14069635, 0.032026708, 0.00019522365, -0.0022558924, 0.21253237, -0.13399132, 0.1323077, 0.17119333, -0.12659132, 0.09258308) * g_19;
    result += mat4(-0.18063812, 0.06042027, 0.13172136, 0.17522804, 0.1790162, -0.32260424, 0.012049487, -0.29769227, 0.027918922, 0.07017221, -0.0750346, 0.014930939, -0.1885921, 0.26602972, 0.026115637, 0.3200164) * g_20;
    result += mat4(0.38229984, -0.054856207, -0.30004284, -0.096048094, -0.045444023, 0.12204156, 0.01020938, 0.05631701, 0.18008712, 0.08312059, 0.14788924, 0.04911914, -0.089370966, 0.072039425, -0.045207575, -0.06889737) * g_21;
    result += mat4(0.32740393, 0.1746514, -0.10657198, -0.021967173, -0.002292727, 0.15766911, -0.2148169, -0.024471002, 0.24356085, 0.039451532, 0.008314017, -0.09937661, 0.1613525, -0.2391406, -0.029003207, -0.0159854) * g_22;
    result += mat4(-0.16562004, 0.041117836, 0.19213973, -0.14429536, 0.30970034, -0.07554239, 0.029687773, -0.024070954, -0.08167974, -0.004404698, -0.03143552, 0.042981133, 0.06546435, 0.16990507, -0.21680567, 0.06390797) * g_23;
    result += mat4(-0.03591141, 0.020884542, 0.023933852, 0.022759074, -0.029971978, 0.11930571, -0.086772785, 0.19787759, 0.030405317, -0.13947894, 0.07441769, 0.00034632036, -0.07164358, 0.057664413, 0.37139198, 0.06278644) * g_24;
    result += mat4(-0.051113605, 0.05665, -0.020249806, 0.16835532, 0.05984608, -0.08224659, 0.12696908, 0.13570228, -0.068349294, -0.099196844, 0.120686345, 0.055186067, 0.07618209, -0.026192036, -0.14863594, 0.06333659) * g_25;
    result += mat4(0.058455057, -0.088729665, 0.15909332, -0.012666964, 0.10028206, 0.03833605, 0.13993295, 0.031959523, 0.096895166, -0.03811847, 0.13775149, 0.02438105, -0.2683284, 0.111006245, 0.10954929, 0.025493354) * g_26;
    result += mat4(-0.13692367, 0.14800175, 0.012824838, -0.071239576, 0.0888179, 0.22001815, -0.11865171, 0.069108665, -0.25402087, 0.10172734, 0.30485952, -0.067486994, 0.0008256393, 0.0869447, 0.22277334, 0.21455327) * g_27;
    result += vec4(0.028628629, 0.06234057, -0.040859535, 0.012304189);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_27_tf3, ivec3(valid_xy, tile.inputLayer), result);
}