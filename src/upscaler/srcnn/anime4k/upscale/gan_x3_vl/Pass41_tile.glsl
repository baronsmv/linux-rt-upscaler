// Anime4K_Upscale_GAN_x3_VL - Pass 41 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv0ups1;
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
vec4 result = mat4(0.19633518, 0.06885309, -0.20043527, 0.035509795, -0.10401743, -0.21588884, -0.102477305, 0.011876971, -0.056948267, 0.25264382, -0.15101993, -0.15266001, 0.010933664, 0.09011232, 0.09345315, 0.006623116) * g_0;
    result += mat4(0.27567336, 0.032350313, -0.19810209, -0.21658543, -0.0659062, -0.3352386, 0.07164577, -0.012328946, -0.17325617, -0.10731732, -0.0677151, -0.09058453, -0.044920623, 0.13278453, 0.218302, 0.06825565) * g_1;
    result += mat4(0.028230175, 0.0018616526, -0.21906042, -0.07338764, -0.023010844, -0.014972394, -0.020508962, 0.058636636, 0.12617883, -0.19870517, 0.11696488, 0.065536946, -0.03026256, 0.023291413, 0.14201568, 0.06143288) * g_2;
    result += mat4(0.025846066, -0.090636976, -0.07404494, -0.090020634, 0.008514354, 0.109184064, 0.05742023, 0.12586315, 0.083378665, -0.13951068, 0.045261055, 0.345901, 0.02675545, 0.095778815, 0.076500334, 0.14780305) * g_3;
    result += mat4(0.00470463, 0.018870084, -0.32943425, 0.16893233, 0.019939557, 0.21623498, -0.18504573, 0.10291846, 0.091479525, -0.16171393, -0.07914371, -0.12615843, 0.06589903, 0.15675966, -0.10883045, 0.02186343) * g_4;
    result += mat4(0.20796785, 0.009986704, 0.057757147, 0.030481182, -0.0036845834, -0.11120154, 0.15609682, -0.038438197, 0.12596935, -0.06617715, -0.109660454, -0.07545557, 0.046646334, 0.08662475, -0.14833032, -0.13950638) * g_5;
    result += mat4(-0.060464397, -0.012758383, 0.02772358, -0.11097607, 0.046997264, -0.124745354, -0.24724343, -0.23114161, -0.09586756, -0.04930659, 0.2014008, 0.31652108, 0.074047916, -0.11001771, 0.019132676, 0.08412601) * g_6;
    result += mat4(0.050371062, 0.08204854, 0.039742008, 0.076570585, 0.05938661, -0.06386326, 0.09085278, 0.076653615, -0.07528917, 0.09379596, 0.021202901, 0.0059685786, 0.34758928, -0.26862696, -0.124089494, -0.13643466) * g_7;
    result += mat4(0.32158887, -0.34527287, 0.25377008, -0.13895594, 0.0054988973, -0.24181193, -0.40868145, -0.0022963625, -0.06266895, 0.0030860363, -0.020924645, -0.18905482, 0.141399, 0.008508758, 0.115678936, -0.43306655) * g_8;
    result += mat4(0.057700455, 0.17643234, -0.09683699, 0.0057190154, 0.07252213, 0.15004468, 0.37618238, 0.13903357, 0.218705, -0.060630042, 0.11694831, -0.00048630088, -0.0134587595, 0.076368295, -0.1325984, -0.10201561) * g_9;
    result += mat4(0.012976455, -0.29424316, -0.14308581, 0.049230546, -0.07200477, -0.13733308, 0.25564528, 0.08696407, 0.14173195, -0.4262995, 0.20581593, 0.22764574, -0.23969811, -0.021570327, 0.07481749, 0.1941362) * g_10;
    result += mat4(-0.17857735, 0.112538725, 0.19362856, -0.06760973, 0.06499711, -0.005863579, -0.30760095, 0.05362555, -0.08302696, 0.021682503, -0.09627604, -0.00945931, -0.07492733, -0.02935675, -0.10610068, -0.09772539) * g_11;
    result += mat4(0.06233666, 0.0509348, 0.006487371, -0.006774608, -0.04553992, 0.03091619, -0.023414508, 0.06836573, 0.072267964, -0.011354451, -0.0025099765, -0.23190095, -0.20676394, -0.061777104, 0.013524417, 0.21478185) * g_12;
    result += mat4(-0.008408447, 0.05689985, 0.16880135, 0.11134194, 0.0058967494, 0.28136337, 0.11531701, -0.15612614, 0.13670067, 0.06262395, -0.0943045, -0.0937771, -0.105943695, -0.13124335, -0.13190243, -0.0259559) * g_13;
    result += mat4(0.13609879, 0.1420789, -0.0102266455, 0.027917469, 0.18166769, -0.04157506, -0.17849353, -0.10579488, -0.016188206, -0.09247544, 0.115879655, -0.005531635, 0.123433806, -0.0477944, -0.118518375, -0.21525477) * g_14;
    result += mat4(0.09320673, 0.024231741, 0.14889163, -0.16015185, -0.051729757, -0.07560833, 0.032730922, 0.01543164, 0.007215127, 0.096069746, -0.13138555, -0.08324462, -0.14087589, -0.13676994, 0.040817242, 0.19880508) * g_15;
    result += mat4(0.08556744, 0.11995626, -0.12598105, 0.07094707, -0.030116409, -0.13692346, -0.10617047, 0.1170125, 0.0635618, 0.015630903, 0.033283047, 0.027908718, -0.16022116, 0.05379484, 0.1643671, 0.08461423) * g_16;
    result += mat4(0.027346484, -0.04373988, 0.14366151, 0.021193424, -0.020020869, 0.08702033, 0.067230165, -0.13468166, -0.06336041, 0.19826981, 0.09957918, 0.0019007461, 0.11597447, -0.11684592, -0.052715372, 0.009431231) * g_17;
    result += mat4(0.1160723, 0.13518505, -0.07323529, -0.102813244, -0.05717617, 0.22344513, -0.09574202, 0.030326243, -0.11634749, -0.09885759, -0.0041502435, -0.114238635, 0.05903762, -0.042631276, 0.07528514, 0.018450156) * g_18;
    result += mat4(-0.080062985, 0.12060534, 0.108948626, 0.2663645, 0.015359482, -0.18093999, 0.02191666, -0.019032517, 0.082503706, 0.0037899283, 0.0038726546, 0.06054277, 0.034015723, 0.07618506, -0.025927188, -0.10678223) * g_19;
    result += mat4(0.00035550856, -0.20764709, 0.013300498, -0.35849246, 0.12688975, -0.11437089, -0.02337497, -0.21238862, 0.46495908, -0.11521313, 0.049601704, 0.14637932, -0.25788313, -0.17036532, -0.020144291, -0.0016756164) * g_20;
    result += mat4(0.14395922, 0.029118493, -0.08014281, 0.094050094, -0.062834464, -0.025796665, 0.15015388, 0.28717938, -0.2570273, 0.10900227, -0.15873776, 0.13343036, 0.2544096, 0.32181814, -0.15404758, -0.22983788) * g_21;
    result += mat4(0.048919182, 0.26769882, 0.04733999, -0.016210597, 0.2571225, -0.19034678, -0.16507657, -0.033483442, 0.25795573, 0.09645708, -0.1332106, 0.077412024, -0.030721905, -0.19939502, 0.041621, -0.04823887) * g_22;
    result += mat4(0.3016378, -0.26046696, -0.10701948, -0.0042546196, -0.24555147, 0.10042819, 0.11718351, 0.13214561, 0.016662005, 0.15979412, 0.033659726, 0.06328732, 0.08410991, 0.17246136, 0.019442663, -0.08638967) * g_23;
    result += vec4(-0.017773768, 0.0060332157, 0.0007953922, -0.012296271);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups1, ivec3(valid_xy, tile.inputLayer), result);
}