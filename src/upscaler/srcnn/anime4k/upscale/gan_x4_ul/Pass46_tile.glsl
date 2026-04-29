// Anime4K_Upscale_GAN_x4_UL - Pass 46 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_18_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_18_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_18_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_18_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_20_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_21_tf3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_18_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_18_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_18_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_18_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_18_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_18_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_18_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_18_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.099412, 0.018248364, -0.13228352, 0.4672803, 0.034476146, -0.1978014, -0.11049704, -0.27439678, -0.060605004, 0.110746264, -0.051524, -0.1361938, 0.009921265, 0.23397371, -0.07823562, 0.012807971) * g_0;
    result += mat4(-0.057887197, -0.16899316, -0.097910166, 0.27173346, 0.048372928, -0.09819956, 0.2760085, 0.09113153, -0.25055817, 0.10803364, -0.32569218, 0.018657776, 0.10861732, 0.25150824, -0.12217984, 0.14836118) * g_1;
    result += mat4(-0.23982282, 0.16482148, 0.042845722, 0.26944172, 0.03479865, 0.26460785, 0.29936558, 0.26309288, -0.03825185, 0.16846797, 0.11344883, 0.097732104, 0.011267582, 0.06025005, -0.017220326, -0.14788473) * g_2;
    result += mat4(-0.07698723, 0.31528163, 0.018389257, 0.32013643, -0.17028578, 0.10416205, 0.14160097, 0.07994368, -0.21445467, 0.065764554, -0.010799837, 0.12783599, 0.16091037, -0.041146606, 0.06914886, 0.23852104) * g_3;
    result += mat4(-0.21730243, 0.0005364685, -0.06843196, -0.18304375, -0.0838743, 0.06591937, -0.119132325, -0.12775517, -0.14532626, 0.035126243, -0.014109256, 0.11822324, 0.08915501, -0.048738454, 0.017610341, -0.17118132) * g_4;
    result += mat4(0.066193976, -0.08082204, -0.119381346, -0.38606662, -0.018930387, 0.08734439, -0.080338374, -0.10179199, 0.28592992, -0.038777832, -0.02912025, -0.13968153, 0.1751963, -0.10257253, -0.02308871, 0.103588775) * g_5;
    result += mat4(-0.015369136, 0.043419622, -0.09212257, -0.09099887, 0.17050241, 0.017557086, -0.09919063, 0.2121736, 0.13851827, -0.09521062, 0.31105414, -0.21121062, -0.16483651, -0.05569374, 0.15418938, -0.046936) * g_6;
    result += mat4(0.1726453, 0.32175332, -0.2238786, -0.038357526, -0.057416882, 0.1856948, -0.15019979, -0.07717308, -0.05847253, -0.05986613, -0.09415613, 0.06858027, -0.4783783, -0.024743836, -0.039746255, 0.030463157) * g_7;
    result += mat4(-0.13700408, -0.021685323, -0.1302628, -0.08178966, 0.050457038, 0.052361347, -0.3721997, 0.1799716, -0.33779272, -0.2478128, -0.11195146, 0.03438403, -0.0769632, -0.01370984, 0.358675, -0.016251782) * g_8;
    result += mat4(0.18463574, -0.32811102, 0.09035979, -0.15944754, -0.01858092, -0.12055925, 0.11789398, -0.24762204, 0.19556394, 0.3658605, 0.0063217054, 0.13560002, -0.0031609968, -0.092887774, -0.11317696, 0.1688745) * g_9;
    result += mat4(-0.18825243, -0.057770394, 0.13403799, 0.15150245, -0.0184938, -0.16399476, -0.20233853, -0.15256546, -0.012932695, -0.006998052, -0.27886555, -0.1801957, 0.005736763, -0.16826138, -0.11622382, 0.009515264) * g_10;
    result += mat4(0.21212149, 0.025956135, -0.076748274, 0.081390835, 0.10770965, 0.14706889, -0.03222262, 0.02229013, 0.111733, 0.27851826, -0.06712574, 0.14247932, -0.21986732, -0.04752835, 0.18228333, -0.13603105) * g_11;
    result += mat4(-0.09660765, 0.1315258, 0.17911027, 0.11740451, -0.097255416, 0.060639273, -0.093187824, 0.02105227, -0.07707017, 0.089799285, -0.015904067, 0.1251983, 0.0164978, 0.12589863, 0.10049757, -0.2215788) * g_12;
    result += mat4(-0.019633045, 0.08128165, -0.21685003, 0.12429716, 0.21384989, 0.28713462, 0.36082667, 0.066602774, -0.20333257, -0.22721171, -0.272673, -0.0440037, -0.22458526, -0.100124046, 0.042302642, -0.10875494) * g_13;
    result += mat4(0.12793371, -0.019439168, 0.16232544, -0.27688906, 0.072149724, -0.2702213, 0.10965313, -0.23709685, -0.024219394, -0.17060119, -0.09893195, -0.06776005, 0.2715758, -0.03232274, -0.04255475, -0.37065327) * g_14;
    result += mat4(-0.32041374, -0.074793965, -0.036865823, -0.02918251, -0.017197197, 0.16684239, 0.025243908, -0.07547195, 0.13938503, 0.055163417, -0.011429674, -0.13055529, -0.20067081, -0.18778045, -0.11177742, 0.092909254) * g_15;
    result += mat4(0.14335759, -0.074887894, -0.097555235, 0.20072718, 0.026916051, 0.074796274, -0.040159326, 0.13532946, -0.074374124, -0.1852574, -0.26057327, -0.13128847, -0.08296219, -0.14694557, 0.110786796, 0.013070258) * g_16;
    result += mat4(-0.32044858, -0.063347876, -0.23396221, -0.21997774, 0.26588383, 0.028225997, 0.01708149, -0.24854802, -0.05019675, 0.18214068, 0.13636373, 0.25459006, 0.03579004, -0.13517296, 0.018898118, -0.16877192) * g_17;
    result += mat4(-0.07525496, 0.14939371, 0.17912684, -0.08323159, 0.10446684, -0.04631436, -0.02372887, -0.033120833, -0.04439999, 0.26327297, -0.0050649103, 0.0598028, 0.24129944, 0.042389676, 0.014767951, 0.005455403) * g_18;
    result += mat4(0.20534733, -0.04825815, -0.16734582, 0.12407057, 0.12095892, 0.113786094, -0.031531718, 0.09064296, 0.23715405, 0.12641983, 0.25125253, 0.13647586, 0.05642747, 0.21420534, -0.021030078, 0.0067664357) * g_19;
    result += mat4(-0.19284865, 0.016823744, 0.035537027, 0.08619851, -0.4948977, 0.34391722, -0.22931114, 0.14890936, 0.052512612, 0.037328973, -0.09397819, 0.04763624, -0.14281563, -0.07775558, 0.041917272, -0.24072154) * g_20;
    result += mat4(-0.016150191, -0.27570885, -0.043972906, -0.15360864, 0.12333279, -0.16048594, 0.19867133, -0.11443874, 0.0046046698, -0.08360428, -0.14277548, 0.09461427, 0.20481633, -0.07163476, -0.110096864, -0.2062863) * g_21;
    result += mat4(0.013339331, 0.039179143, -0.18245237, -0.29612786, -0.25390434, 0.06809853, 0.003070957, -0.11978623, -0.26271898, -0.18589073, 0.14316171, 0.1990445, 0.17755853, 0.056225445, -0.06782714, 0.29821777) * g_22;
    result += mat4(0.020388031, -0.09590241, 0.006317689, -0.17690729, 0.30927724, -0.3388045, -0.31306866, 0.027354693, 0.4423801, -0.16751811, -0.008609924, -0.08048698, 0.20227478, 0.0663151, 0.07970592, 0.055658944) * g_23;
    result += vec4(0.008592977, -0.044200934, -0.05895498, -0.02388236);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf3, ivec3(valid_xy, tile.inputLayer), result);
}