// Anime4K_Upscale_GAN_x4_UL - Pass 37 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_18_tf;
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
vec4 result = mat4(0.06333993, 0.09488723, -0.08568035, 0.05200572, -0.1472294, -0.044452854, 0.14845347, 0.21513753, -0.15652965, 0.10840373, -0.056219988, -0.030637205, 0.04253709, 0.055037092, 0.0414908, -0.1892757) * g_0;
    result += mat4(0.0787534, -0.04241309, -0.28714868, -0.046900865, 0.21437375, -0.24278513, -0.20257188, 0.022188142, -0.019003864, 0.15094592, -0.01814459, -0.1872464, 0.059750058, 0.07614743, -0.0521617, 0.17934658) * g_1;
    result += mat4(-0.00019216978, -0.15454617, -0.12794366, 0.044536293, 0.21249126, 0.32045737, -0.147422, -0.09734236, -0.12062187, -0.16607423, 0.09816451, -0.06590071, -0.19728394, -0.14778756, 0.017338278, -0.23659901) * g_2;
    result += mat4(0.074417666, -0.08059618, 0.07767349, -0.03693259, -0.15096827, -0.17373516, -0.20327133, 0.049108338, 0.054858647, 0.015723148, -0.2328269, -0.16492803, 0.12288839, -0.037010916, -0.16224542, -0.19452086) * g_3;
    result += mat4(-0.1915939, -0.15707129, -0.1509893, 0.28097305, 0.03221469, -0.18564048, -0.27148914, -0.084917046, 0.0059148185, 0.06549851, 0.19273312, -0.20762756, 0.011551308, 0.18630835, 0.07567006, 0.046911348) * g_4;
    result += mat4(0.01897941, 0.026447995, 0.30203855, -0.10592397, 0.05870943, 0.1054224, 0.14929043, 0.050682828, 0.0028596125, -0.15138957, -0.03117043, -0.06962448, 0.10460237, 0.30631867, 0.15475252, -0.082159385) * g_5;
    result += mat4(0.056030374, 0.16605477, -0.2011969, 0.0581226, -0.16144355, -0.02808077, 0.010258871, 0.17102659, -0.054532573, 0.3242664, 0.010550339, -0.05370968, -0.014814065, -0.13152799, 0.30049798, 0.122068055) * g_6;
    result += mat4(0.17697391, 0.074868776, -0.16765091, -0.14493272, 0.21677482, 0.07529925, 0.3344087, -0.35831642, -0.12440452, 0.15675198, -0.01240608, 0.21036354, -0.21215741, 0.18817489, 0.072722636, -0.07215567) * g_7;
    result += mat4(-0.29419374, 0.043863285, -0.083936326, 0.3729109, 0.18776, -0.16754451, -0.35357738, 0.045188952, -0.23892207, 0.060875878, 0.046727493, 0.39672953, -0.009434926, 0.0181569, -0.12958461, 0.09870838) * g_8;
    result += mat4(-0.12987071, -0.09597688, 0.2408095, -0.26320508, -0.09014934, -0.1188552, 0.16146885, 0.07402836, 0.35367203, 0.1402623, 0.18618205, -0.25213316, -0.10277592, -0.24674612, -0.32700107, 0.14396617) * g_9;
    result += mat4(-0.3089205, 0.16185652, 0.27521953, 0.041868176, -0.0022332487, 0.12922727, 0.18001151, 0.027498085, -0.110244, -0.044742703, -0.18411714, -0.06564328, 0.07164282, 0.08585003, 0.106629394, -0.054929875) * g_10;
    result += mat4(0.16139935, 0.03240059, 0.082769506, -0.18399146, 0.050481632, 0.018776342, -0.111956954, -0.040583946, 0.08147097, -0.04110496, -0.15557489, 0.05611198, -0.25277153, -0.048391934, -0.10089335, 0.12622349) * g_11;
    result += mat4(-0.2730474, 0.11085952, -0.075156026, -0.14303921, 0.0447421, -0.121895775, -0.35013795, 0.14995758, -0.016281242, 0.033779178, -0.15126662, -0.015176784, 0.040082585, 0.006450913, -0.030723661, -0.058004852) * g_12;
    result += mat4(0.0403051, 0.20903297, 0.067333676, -0.14318345, 0.16834565, 0.0948365, -0.17433995, 0.07182994, 0.06342598, -0.32021528, 0.048930682, -0.051184237, -0.057208735, -0.16286889, -0.12637149, 0.10992653) * g_13;
    result += mat4(-0.14312495, -0.049565334, 0.013813875, 0.070963, 0.26302704, -0.0026512244, 0.33206236, -0.16186446, 0.030595824, 0.119594894, 0.3493397, 0.12651123, 0.04868717, 0.15870047, -0.17626017, 0.053944312) * g_14;
    result += mat4(0.017788881, -0.08985951, 0.0063696383, 0.19405968, 0.06445815, -0.024619186, -0.18900226, -0.030232785, -0.08246631, 0.041897133, 0.089627616, -0.23452254, 0.08906869, 0.09038576, -0.12202178, 0.032400858) * g_15;
    result += mat4(0.23806943, -0.20720927, -0.19059941, -0.08068674, -0.035527237, -0.15776922, -0.024618277, -0.2444429, 0.05044065, 0.024451984, -0.14015712, 0.16094929, 0.03076579, -0.020462647, -0.20250656, 0.1029075) * g_16;
    result += mat4(0.047954805, 0.04713052, -0.014320014, 0.11667167, 0.45120004, -0.12177823, -0.11391618, 0.18149075, 0.08473487, 0.14073594, -0.07025125, 0.19289283, 0.083399035, 0.15313184, -0.2289391, -0.27340987) * g_17;
    result += mat4(-0.031021187, -0.056889966, -0.089950375, 0.08566341, -0.093087964, -0.114104606, 0.20981134, 0.20004368, 0.36221287, 0.09415981, 0.1761312, -0.07357187, 0.15133485, 0.18167816, 0.13953826, -0.108503394) * g_18;
    result += mat4(-0.04393188, 0.25963497, -0.0330857, 0.050094042, 0.0015226522, 0.09266069, -0.15832978, -0.22114822, 0.063840784, -0.33367425, -0.103081174, 0.01706331, 0.007467705, -0.3628944, -0.10182942, 0.1942455) * g_19;
    result += mat4(0.23547105, 0.03324374, 0.13732544, -0.18675572, 0.2536437, -0.024418214, 0.1405745, -0.08798336, -0.09310729, -0.088432625, -0.16199891, -0.07790996, -0.16207652, -0.057468604, -0.6186605, 0.84914094) * g_20;
    result += mat4(-0.10194844, 0.25304326, -0.13665953, -0.042847656, -0.030379621, 0.104918376, 0.07079868, 0.044213004, 0.032054633, 0.11013307, -0.10676529, -0.06577438, -0.0136965765, 0.076344326, 0.2286907, 0.17813052) * g_21;
    result += vec4(-0.077900425, -0.00413413, 0.020021616, 0.012168936);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf, ivec3(valid_xy, tile.inputLayer), result);
}