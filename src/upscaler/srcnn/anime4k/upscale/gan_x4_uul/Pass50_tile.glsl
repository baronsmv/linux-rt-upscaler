// Anime4K_Upscale_GAN_x4_UUL - Pass 50 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_15_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_15_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_15_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_15_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_15_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_15_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_17_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_18_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_15_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_15_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_15_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_15_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(-0.03043192, -0.11382309, 0.15258959, 0.0018671904, -0.07262079, -0.15530646, 0.088956885, 0.0068843844, 0.18098354, -0.13130096, 0.019414594, 0.021504048, 0.12169795, 0.15837122, 0.09828637, -0.47963795) * g_0;
    result += mat4(0.14249554, -0.022084357, 0.06666183, -0.043699186, 0.014650524, 0.1188985, 0.0454781, -0.050885927, -0.20757285, 0.5144112, -0.48320413, -0.14140959, -0.13466966, 0.22992888, -0.005597194, -0.06725975) * g_1;
    result += mat4(0.06208693, -0.112261705, -0.1686331, 0.018273335, -0.09682144, 0.068702586, 0.045484196, 0.08813325, -0.11541148, -0.008004347, 0.036507435, 0.06754519, 0.011923774, -0.03168652, 0.015487991, 0.10111531) * g_2;
    result += mat4(-0.008023328, 0.1137135, -0.07264171, -0.120196424, -0.043222312, -0.22171052, 0.102924, -0.11386958, 0.21182953, -0.072151154, 0.04207932, 0.04245426, 0.074935004, -0.042641435, -0.098739915, -0.13941646) * g_3;
    result += mat4(-0.010649323, 0.009664776, 0.041474525, -0.06732602, -0.18728773, -0.14357336, -0.2223795, 0.22192913, -0.0651367, -0.11535945, -0.19640021, 0.116560034, -0.025604805, 0.019647487, 0.25854686, -0.1392261) * g_4;
    result += mat4(0.1567528, 0.10124439, -0.06609058, 0.11552276, 0.057271544, -0.065696426, 0.12358736, 0.15948243, -0.032239728, 0.011985731, 0.18371308, -0.08555982, -0.06528452, 0.11953871, 0.11031671, -0.029863868) * g_5;
    result += mat4(0.1311102, -0.1305194, -0.18688914, 0.05448602, -0.06396861, -0.12188008, 0.121559285, 0.088412315, -0.09227041, 0.35888135, -0.21576284, -0.09567888, -0.1135963, -0.30975553, -0.019740306, 0.23325934) * g_6;
    result += mat4(0.013327147, 0.069052495, 0.0853812, 0.13866353, 0.060591422, 0.1950111, 0.063291125, 0.06301278, 0.16034324, -0.03186552, -0.015433267, 0.21410994, 0.017428825, -0.095040835, -2.532167e-06, -0.19249855) * g_7;
    result += mat4(-0.10042209, 0.051823184, 0.06878474, 0.039450742, -0.02151693, -0.125688, -0.080015615, 0.101158395, -0.023944302, -0.3210737, 0.19029768, -0.080297835, 0.03199306, 0.0999303, 0.22268118, 0.08898154) * g_8;
    result += mat4(-0.06613979, -0.10264432, 0.06768314, 0.16863261, 0.23254016, 0.049546715, -0.22763276, 0.042342335, -0.20712924, 0.092378855, -0.022331564, -0.04691188, -0.027093714, 0.098690435, -0.19893834, -0.04930573) * g_9;
    result += mat4(-0.122772284, -0.11104652, -0.018459626, 0.115983605, 0.12493899, 0.16507398, 0.21478258, -0.15713362, 0.055545174, 0.05634718, 0.1609001, 0.046624824, 0.08476838, 0.024616027, -0.0030971076, 0.040258918) * g_10;
    result += mat4(-0.030780645, 0.10763727, 0.2205602, -0.22281945, 0.08244692, -0.12237726, -0.26415175, -0.16127835, -0.01633197, -0.12299418, -0.012012627, -0.084443405, 0.012664263, 0.07389567, 0.01104131, 0.01305866) * g_11;
    result += mat4(-0.28838482, 0.15918796, -0.119311474, -0.053310875, -0.07448111, -0.13836008, -0.22057253, 0.2299248, 0.009213285, 0.0044759554, -0.058288343, 0.19605552, -0.062922835, 0.081783056, -0.20190218, 0.008294941) * g_12;
    result += mat4(0.16755526, 0.08699512, -0.18997741, -0.0014094117, -0.06733589, -0.15045306, 0.25367445, -0.17017934, 0.017913489, -0.015539376, 0.088074, -0.05331681, 0.04171007, 0.14498031, 0.06460646, -0.00037390782) * g_13;
    result += mat4(0.04930183, 0.12424497, -0.0722411, 0.09628479, -0.043124642, 0.04497056, 0.18794456, -0.03480863, -0.09988751, 0.053120367, -0.1482433, -0.145739, 0.09281689, 0.026481925, -0.10084, -0.15488812) * g_14;
    result += mat4(-0.004074055, 0.04565656, -0.015633525, 0.035065204, 0.11478302, 0.020277338, -0.048027817, -0.010702974, -0.083617836, 0.010090728, -0.22310819, 0.15971296, 0.06781031, -0.16845126, 0.39758167, 0.22460622) * g_15;
    result += mat4(-0.09374665, -0.042104498, -0.033132017, 0.08122814, -0.08190475, 0.27325064, -0.08330755, -0.3144509, -0.12476947, 0.07372691, -0.005574465, 0.19122915, 0.03066927, -0.018531645, 0.19734049, 0.002256408) * g_16;
    result += mat4(0.013257584, -0.10722849, 0.03737538, -0.12670442, 0.07042824, 0.0074753985, 0.061389714, -0.3798834, 0.012847999, 0.08157751, 0.015498391, -0.06905376, -0.27448237, 0.002926611, -0.0022811508, -0.1625364) * g_17;
    result += mat4(0.07984379, 0.16429926, -0.08719054, 0.084147796, -0.08544172, 0.049447432, -0.3133747, -0.024927497, -0.003863256, 0.18635638, -0.059786454, -0.052997295, -0.07169392, 0.11241022, -0.19898133, -0.007140295) * g_18;
    result += mat4(-0.108855434, -0.09246034, 0.04956623, 0.028047003, -0.039407548, 0.031223932, 0.015852997, -0.050448515, -0.04515231, -0.1598301, -0.08276407, 0.17720093, 0.2920873, -0.021305554, 0.028241735, -0.18086697) * g_19;
    result += mat4(0.047492385, -0.1599947, -0.20104182, 0.16174223, -0.071828544, -0.12785994, -0.12311588, 0.012565137, 0.016804317, -0.03577294, -0.09488874, 0.06645059, -0.00015702203, 0.16082056, 0.03234071, -0.08351094) * g_20;
    result += mat4(-0.032639805, -0.010861794, 0.030566638, 0.014637599, 0.120822355, 0.12297292, -0.05141305, -0.016473597, -0.048908286, 0.07600826, -0.0022954363, -0.113686286, -0.20952684, 0.09235576, -0.15726195, -0.2348195) * g_21;
    result += mat4(0.13191621, -0.002480696, -0.14792813, 0.15621583, 0.100709975, -0.21280108, 0.045120943, -0.02165414, -0.1447397, 0.24282482, -0.1569735, 0.11792232, 0.012485835, 0.0029504807, 0.067921594, -0.25737903) * g_22;
    result += mat4(-0.11145241, 0.27000552, -0.19557719, -0.16048421, 0.012310486, 0.07280107, -0.13137956, 0.27061656, -0.25022137, 0.07077271, 0.3398045, -0.10735134, 0.124004506, -0.03584192, -0.042106874, 0.13895391) * g_23;
    result += mat4(0.11946389, 0.10225672, -0.057140473, 0.09698616, 0.13223277, -0.19595279, -0.15960483, -0.017795812, 0.120322645, -0.0914318, -0.2300714, 0.14489214, 0.2006262, -0.0036377236, 0.14416055, 0.247531) * g_24;
    result += mat4(0.2734717, -0.26736638, -0.06574077, -0.041792296, -0.13349292, 0.23770794, -0.0032957396, 0.07614033, -0.11995782, 0.25061053, -0.017311087, -0.3048492, -0.07940496, 0.166133, -0.2777709, 0.0010628162) * g_25;
    result += vec4(0.015130698, -0.049747583, 0.006816977, -0.09670764);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf1, ivec3(valid_xy, tile.inputLayer), result);
}