// Anime4K_Restore_CNN_VL - Pass 17 of 17 - https://github.com/bloc97/Anime4K
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
//        uint  inputLayer;      // array slice to read (0-based)
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  margin;          // context margin (pixels in feature-map space)
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
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
    uint inputLayer;
    uvec2 dstOffset;
    uint fullOutWidth;
    uint fullOutHeight;
    uint margin;
    uvec2 tileOutExtent;
} tile;

layout(set = 0, binding = 1024) uniform texture2DArray tex_MAIN;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_1_tf1;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_2_tf1;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf1;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_5_tf1;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 1037) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1038) uniform texture2DArray tex_conv2d_7_tf1;
layout(set = 0, binding = 2048, rgba8) uniform image2D img_output;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_1_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_1_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max((texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max((texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_24 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_25 (max((texture(sampler2DArray(tex_conv2d_7_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_26 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_7_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.09689336, 0.06046458, 0.072598994, 0.0, 0.11994565, 0.104477674, 0.09302802, 0.0, -0.05718302, 0.050438102, 0.08814741, 0.0, 0.0308889, 0.0033925986, -0.01715605, 0.0) * g_0;
    result += mat4(-0.028314235, 0.06597744, 0.0966897, 0.0, 0.035656154, 0.07770106, 0.075551905, 0.0, 0.0001793458, -0.000479495, -0.00297406, 0.0, -0.053916585, -0.016807461, -0.0057141334, 0.0) * g_1;
    result += mat4(-0.047189303, -0.0207, -0.020910334, 0.0, -0.07933196, -0.06961211, -0.086069845, 0.0, 0.0943727, 0.008463375, 0.010755166, 0.0, 0.062410597, 0.022625161, 0.04068433, 0.0) * g_2;
    result += mat4(0.10270994, -0.019080428, 0.0050091282, 0.0, -0.004672948, -0.013966742, -0.0063746064, 0.0, -2.5856789e-05, 0.03151499, -0.0023983798, 0.0, 0.113539025, 0.12381699, 0.100360274, 0.0) * g_3;
    result += mat4(0.07868885, -0.030913834, -0.009213676, 0.0, 0.04870991, 0.021467991, 0.038739506, 0.0, -0.042969644, -0.07122453, -0.08798675, 0.0, -0.09784122, 0.021434791, 0.02510374, 0.0) * g_4;
    result += mat4(0.050420716, 0.0729716, 0.076532185, 0.0, -0.019112485, -0.01037939, -0.026948035, 0.0, -0.02591423, 0.008927897, -0.00042541025, 0.0, 0.1043701, -0.0071186824, -0.041817162, 0.0) * g_5;
    result += mat4(-0.16143242, -0.0009298223, -0.01228508, 0.0, 0.07744052, -0.018313263, -0.0488145, 0.0, 0.09241393, 0.07128674, 0.055164956, 0.0, 0.054884013, -0.04834418, -0.06281626, 0.0) * g_6;
    result += mat4(-0.049036566, -0.05979936, -0.05594288, 0.0, -0.014564307, 0.031926468, 0.037857566, 0.0, 0.015474487, -0.11385003, -0.11527764, 0.0, -0.07076006, 0.057038613, 0.095983796, 0.0) * g_7;
    result += mat4(0.03094887, -0.008734403, 0.00042712069, 0.0, 0.053891554, 0.05837673, 0.06200635, 0.0, 0.09071558, -0.04202184, -0.046172567, 0.0, -0.0425916, 0.04905093, 0.020835675, 0.0) * g_8;
    result += mat4(0.096628904, -0.037792254, -0.043241944, 0.0, -0.011923947, -0.025950424, -0.031381752, 0.0, -0.060941868, -0.07859433, -0.07535451, 0.0, -0.026777223, 0.08604982, 0.07829908, 0.0) * g_9;
    result += mat4(-0.06435972, 0.0036599538, 0.00786578, 0.0, -0.061972067, -0.05681472, -0.06667608, 0.0, -0.106890626, 0.007406496, 0.029977169, 0.0, -0.20519382, -0.044860814, 0.0021225857, 0.0) * g_10;
    result += mat4(-0.16876474, 0.012789643, 0.026692612, 0.0, 0.017817136, 0.026935097, 0.02227043, 0.0, 0.01690181, 0.07716103, 0.086527, 0.0, 0.07923805, -0.10443151, -0.10859543, 0.0) * g_11;
    result += mat4(0.003730466, -0.024648283, -0.022169832, 0.0, -0.0062762927, 0.022062732, 0.032966793, 0.0, 0.016349113, 0.017197203, 0.020952817, 0.0, -0.1763789, 0.035497356, 0.053835396, 0.0) * g_12;
    result += mat4(0.020886675, -0.07054202, -0.079142675, 0.0, 0.06664387, 0.044960167, 0.042230908, 0.0, -0.095019594, 0.012421141, 0.0142890485, 0.0, 0.056814816, -0.012751135, -0.014684506, 0.0) * g_13;
    result += mat4(0.011765893, 0.0008920681, -0.0018258415, 0.0, -0.010473814, -0.023085753, -0.028783914, 0.0, -0.023034256, -0.0024786016, -0.0052162083, 0.0, 0.1643386, -0.06132718, -0.09289065, 0.0) * g_14;
    result += mat4(0.016597198, 0.09389637, 0.10833379, 0.0, -0.043163072, -0.04714812, -0.035274632, 0.0, 0.09634976, -0.009292612, -0.022424143, 0.0, -0.08765172, 0.0051558353, 0.010900356, 0.0) * g_15;
    result += mat4(0.030815786, 0.021069322, 0.01812191, 0.0, 0.084839165, -0.0080813095, -0.029270556, 0.0, -0.10456346, 0.062386703, 0.0665605, 0.0, 0.11926609, -0.1104228, -0.13291118, 0.0) * g_16;
    result += mat4(-0.07159541, -0.007267032, -0.010134558, 0.0, 0.008234213, 0.045609634, 0.040295456, 0.0, 0.018416971, 0.01308482, 0.014649557, 0.0, 0.035107512, -0.02140815, -0.030279048, 0.0) * g_17;
    result += mat4(0.01918586, 0.03875863, 0.03229402, 0.0, -0.07917104, 0.041135103, 0.057182517, 0.0, 0.08609541, 0.0079662455, 0.004327576, 0.0, -0.14332893, 0.03120354, 0.056732506, 0.0) * g_18;
    result += mat4(0.03200192, -0.0035752193, -0.0031064528, 0.0, -0.010902813, 0.014607456, 0.019431474, 0.0, -0.016461229, -0.004938204, -0.004655488, 0.0, -0.033470232, 0.0026075812, 0.005896968, 0.0) * g_19;
    result += mat4(0.037410006, 0.048742272, 0.04348088, 0.0, 0.037719514, 0.030768529, 0.03127472, 0.0, 0.056426726, 0.03066893, 0.016440205, 0.0, -0.010599352, 0.022832409, 0.023211194, 0.0) * g_20;
    result += mat4(-0.005733291, 0.06365659, 0.06663611, 0.0, -0.041917093, -0.016493445, -0.020438088, 0.0, -0.0014357592, -0.0022506563, -0.0045095007, 0.0, 0.029893145, -0.009129354, -0.015173116, 0.0) * g_21;
    result += mat4(0.013052085, 0.005108175, 0.0025906067, 0.0, -0.021950055, -0.036447693, -0.036141638, 0.0, -0.036296472, 0.0068928464, 0.013102313, 0.0, 0.0060471976, -0.024798103, -0.023548538, 0.0) * g_22;
    result += mat4(0.0067743887, -0.06191211, -0.062355213, 0.0, 0.0016080744, -0.020445071, -0.016840393, 0.0, 0.028264903, 0.01852915, 0.015891539, 0.0, -0.023877412, -0.013271666, -0.008158679, 0.0) * g_23;
    result += mat4(-0.04317466, -0.018953001, -0.020452993, 0.0, -0.009322576, -0.03022352, -0.030970376, 0.0, 0.05653658, 0.05430553, 0.046692245, 0.0, 0.05615359, 0.059338935, 0.056018773, 0.0) * g_24;
    result += mat4(0.022878079, 0.03392234, 0.033057988, 0.0, -0.017554542, -0.0141542535, -0.014122613, 0.0, -0.048634093, -0.05316463, -0.047988772, 0.0, -0.058002178, -0.040221967, -0.034025013, 0.0) * g_25;
    result += mat4(-0.018253656, -0.04197674, -0.040467236, 0.0, -0.04358929, -0.028309818, -0.025425073, 0.0, -0.008488672, -0.001727991, 0.00035808363, 0.0, -0.0011709273, 0.0052514165, 0.0059479307, 0.0) * g_26;
    result += mat4(-0.08333935, -0.09818201, -0.09476284, 0.0, -0.033692095, -0.046259012, -0.045797516, 0.0, -0.007577072, 0.0022402718, 0.0016200038, 0.0, 0.0029786075, -0.020728534, -0.018938033, 0.0) * g_27;
    result += vec4(0.047567394, -0.02504617, -0.028163986, 0.0);
    return result + texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos, tile.inputLayer));
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_output, ivec2(valid_xy) + ivec2(tile.dstOffset), result);
}