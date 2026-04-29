// Anime4K_Upscale_GAN_x4_UL - Pass 39 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_17_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_18_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.12408465, -0.16741575, 0.06765819, -0.15944858, -0.19950457, -0.1716973, 0.048808597, 0.043000113, 0.007647513, 0.13003102, 0.06868207, -0.0016408832, -0.24698295, 0.033724148, 0.26656294, -0.04168408) * g_0;
    result += mat4(0.025299544, -0.2481157, -0.07735063, 0.07958534, 0.04743938, 0.123626634, 0.14503284, -0.200222, 0.20223439, 0.08858626, -0.37553144, 0.02513245, 0.09171499, 0.08145674, -0.028931713, 0.04081231) * g_1;
    result += mat4(-0.04600147, 0.14647272, 0.18308495, 0.06990148, -0.06455617, 0.09861496, -0.13262698, 0.16287735, 0.06737012, 0.03652816, -0.22811131, -0.064241834, -0.035340827, 0.29290062, -0.022302201, -0.19858247) * g_2;
    result += mat4(-0.11037198, 0.12009516, -0.14232409, 0.2716094, -0.04082168, -0.10308978, -0.18808627, -0.017621756, -0.031254657, -0.26940623, 0.24271232, -0.1467802, 0.10700058, -0.18850107, -0.08067445, -0.017454604) * g_3;
    result += mat4(-0.090594314, -0.019169644, -0.029233063, 0.34922495, -0.22969832, 0.04161748, 0.0016718027, -0.13671273, 0.20134616, -0.01069757, -0.41116753, 0.011301641, -0.093161866, -0.0598387, -0.20625715, -0.04319863) * g_4;
    result += mat4(0.1400459, -0.08488729, -0.14534405, 0.13608801, 0.054499432, 0.013480982, -0.115060575, -0.051957313, -0.11556034, -0.06907556, 0.2383428, -0.0032338845, -0.015882459, 0.24332793, -0.29487756, -0.31111467) * g_5;
    result += mat4(0.0035557884, -0.10662409, -0.167661, -0.038467426, 0.0067648925, -0.14742504, -0.15988947, -0.18424144, -0.015692392, 0.024426097, 0.18659574, -0.06826323, -0.098989435, -0.120715715, -0.012542293, -0.012921739) * g_6;
    result += mat4(-0.22045317, -0.039446186, 0.02062722, 0.04877487, 0.057328302, 0.107455134, -0.24580365, 0.084131025, 0.028729152, 0.4286281, -0.05177413, 0.23257121, 0.08110685, -0.22814348, -0.041566104, 0.2465172) * g_7;
    result += mat4(0.37156427, 0.26804617, 0.20049824, -0.021026293, 0.13211878, 0.040705554, 0.002239553, 0.20452338, -0.030344317, 0.099040724, 0.3838666, 0.055573136, 0.27482164, 0.23077035, -0.017845538, -0.26252562) * g_8;
    result += mat4(-0.25934902, 0.04962634, -0.11156898, -0.07086993, 0.12231552, -0.040678304, 0.16707222, -0.068827145, -0.20247164, 0.16845146, 0.21900423, -0.40101337, -0.20267262, 0.012057886, -0.16219872, 0.042600926) * g_9;
    result += mat4(0.076830566, 0.07031241, 0.23169716, -0.028218819, 0.12506121, -0.19878168, 0.14684094, 0.0931965, 0.20331647, -0.12333559, 0.22961548, -0.15381584, 0.08874619, 0.14223523, 0.16359226, -0.28227505) * g_10;
    result += mat4(-0.052383065, -0.078102276, 0.065739855, 0.0415868, -0.07094788, 0.16164882, 0.043656457, -0.0960344, -0.22771464, 0.13144033, -0.1159355, 0.046441697, -0.24606496, -0.25741673, 0.004535607, -0.0065205614) * g_11;
    result += mat4(0.23244801, -0.31457657, -0.10946917, -0.3663475, 0.17705315, 0.05067217, -0.1933483, 0.027725892, 0.03238109, 0.16744693, -0.057594296, -0.07276957, 0.03234641, -0.1372411, -0.08171865, -0.12950452) * g_12;
    result += mat4(-0.15673116, 0.19919762, -0.10481654, 0.10979371, 0.04279017, 0.022970842, 0.041732438, 0.043996546, 0.010470399, 0.040505856, -0.03274834, 0.0009573305, 0.08111623, 0.047052007, -0.15586549, 0.04683318) * g_13;
    result += mat4(-0.24751675, -0.08296508, 0.11407727, -0.2166629, 0.26892385, 0.24061169, 0.13039055, -0.025301076, 0.112557106, 0.33924893, -0.26320595, -0.3333313, -0.18867135, -0.15030354, -0.41406167, 0.049163118) * g_14;
    result += mat4(0.1665652, -0.21874574, 0.028786177, 0.2146646, -0.015547626, -0.012667473, 0.10428667, 0.14486806, -0.03420849, -0.012048649, 0.2303649, 0.17137095, -0.16784278, 0.08330269, 0.15572217, -0.08734928) * g_15;
    result += mat4(-0.191288, -0.2011081, -0.16282842, -0.16686897, 0.11942609, -0.14166519, 0.01405599, 0.18117349, -0.096682444, 0.010184171, -0.023849446, 0.17224887, 0.30125615, -0.06356407, 0.103124686, 0.014888768) * g_16;
    result += mat4(0.25378457, 0.075565144, -0.19106098, -0.14747557, -0.15002617, 0.028056031, -0.0025413758, 0.07962606, -0.015789257, -0.17432348, 0.12131772, -0.055529855, -0.041077815, -0.19829613, 0.13878337, -0.24223712) * g_17;
    result += mat4(-0.29446965, 0.15235735, 0.06717627, -0.015626365, 0.014169811, 0.07045108, 0.10471683, -0.05982132, -0.13769852, 0.12853971, 0.1119684, -0.14485933, -0.075092256, 0.24838834, 0.0017574847, -0.0804142) * g_18;
    result += mat4(0.24836873, 0.00066609884, -0.13763703, 0.14340822, -0.14462134, -0.038759258, -0.09077153, -0.0441944, 0.10637402, -0.18241063, 0.0067824926, 0.13309585, 0.07101235, -0.051455706, 0.06795849, 0.31597748) * g_19;
    result += mat4(0.25393802, 0.19519086, -0.18530098, 0.049162578, -0.008795799, 0.36194384, -0.00040475396, -0.27478936, 0.22377892, -0.18955742, 0.30927923, -0.21051413, 0.36050028, 0.028015982, 0.050072942, 0.5546838) * g_20;
    result += mat4(0.075164825, -0.044605773, -0.14191186, 0.21589251, -0.18884787, 0.011185897, 0.17542075, 0.1676064, -0.2930037, 0.21933044, -0.035698287, 0.070793465, -0.16923343, -0.09259949, -0.11534973, 0.060004164) * g_21;
    result += vec4(-0.0090077715, -0.014536999, 0.043094933, -0.0062093455);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf2, ivec3(valid_xy, tile.inputLayer), result);
}