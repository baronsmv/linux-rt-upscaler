// Anime4K_Upscale_GAN_x4_UUL - Pass 38 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_9_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_9_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_9_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_9_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf5;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_9_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_9_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_9_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_9_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_9_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_9_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.10146893, -0.06355417, -0.0066939867, -0.112247504, 0.15743892, 0.2661364, -0.24241701, -0.17822737, 0.11587934, -0.029756429, 0.0928847, -0.10046272, 0.14444917, 0.12547572, -0.2114753, 0.023556458) * g_0;
    result += mat4(-0.047596626, 0.09543128, 0.23701866, -0.08471554, 0.51885915, -0.1704686, -0.04001014, -0.054579906, -0.07877735, -0.09762826, -0.146179, 0.0787038, 0.22635859, -0.31619364, 0.073862836, 0.25550374) * g_1;
    result += mat4(0.27489266, 0.03828787, 0.1788482, -0.07628321, -0.007864044, -0.25208792, 0.37145224, -0.05436547, 0.17768216, 0.06377889, -0.029021077, 0.060763232, -0.020521913, 0.15733998, -0.10828051, 0.13728242) * g_2;
    result += mat4(-0.21597046, 0.021131428, 0.114165306, -0.017311715, -0.12344303, 0.048893873, -0.04941004, 0.06477217, 0.1573259, -0.07459121, 0.09720801, 0.12087764, -0.1889173, 0.15563762, 0.09565472, -0.16171652) * g_3;
    result += mat4(0.25529733, -0.030553222, 0.19627945, 0.21340033, -0.0357832, -0.14596821, -0.14145969, -0.17806748, -0.053110838, 0.20665482, 0.08333174, -0.02258432, 0.1662624, -0.14893246, 0.02501433, 0.21777983) * g_4;
    result += mat4(-0.09700643, 0.05642473, -0.29080915, -0.07261638, 0.08252391, 0.22238337, 0.008129421, -0.18302573, -0.4751298, 0.03521261, 0.16102098, 0.22523795, 0.106175326, 0.097425245, -0.056549445, -0.058554217) * g_5;
    result += mat4(0.2115773, 0.060346328, 0.07946409, -0.17166963, 0.0878238, 0.032195155, 0.053393956, 0.2399919, -0.03793802, -0.1799568, -0.14780137, -0.019833531, -0.060654577, 0.086268514, 0.2597936, 0.24647377) * g_6;
    result += mat4(-0.15642072, -0.14679217, -0.100522175, 0.11584608, 0.09088178, 0.13054077, 0.04432568, -0.118127726, -0.041004654, -0.06222515, -0.09301348, 0.046497803, 0.010794347, -0.015452295, -0.052613236, 0.06925519) * g_7;
    result += mat4(-0.19688836, -0.22052658, -0.16386695, 0.08732065, 0.111491896, 0.19614422, 0.0256523, 0.06947972, 0.03396227, -0.13961029, -0.008658522, 0.24620731, 0.13377586, -0.07979868, 0.36551273, 0.39424098) * g_8;
    result += mat4(-0.30495998, 0.2224925, 0.027218822, 0.04317854, -0.06996757, 0.048042685, 0.06731089, -0.23949164, 0.20741203, 0.08487502, 0.2277233, -0.08041561, 0.16487156, -0.25665572, 0.07448175, -0.19871257) * g_9;
    result += mat4(0.161757, -0.18321225, 0.006443096, -0.03942912, 0.30194885, 0.17840338, 0.089457296, -0.111660995, -0.25981718, -0.18808901, -0.008459478, 0.12424914, 0.38462314, 0.031231843, 0.055111516, -0.28973204) * g_10;
    result += mat4(0.104183905, -0.12262509, 0.15137221, -0.23025867, 0.040099107, -0.05383875, -0.04934622, 0.1180123, 0.10198143, 0.27173567, -0.15230067, -0.099421, -0.08984255, 0.11140736, -0.045036234, 0.18769833) * g_11;
    result += mat4(-0.07531492, -0.024759036, -0.03848608, -0.036268033, -0.03411223, 0.094500594, 0.00280404, 0.062361084, 0.03790362, 0.037668772, -0.0514829, 0.09995965, 0.283923, -0.5238069, -0.06496828, -0.0055070156) * g_12;
    result += mat4(0.28150153, 0.14254282, -0.05911421, -0.12254332, -0.022384, -0.14173482, 0.014685391, -0.18164866, -0.22542116, -0.19810574, -0.09996172, 0.10686331, -0.08414146, -0.025034428, 0.11224387, -0.0063977554) * g_13;
    result += mat4(-0.17710046, -0.17579278, 0.00020095073, -0.1109482, -0.020255143, 0.08271713, -0.10690405, 0.08052975, -0.062588565, 0.089410976, -0.13496846, 0.03015718, -0.22929737, 0.15872306, 0.2993516, 0.11859886) * g_14;
    result += mat4(-0.035919335, 0.19236436, -0.25442082, 0.021053115, -0.10868948, -0.015284599, 0.33936346, -0.008365188, 0.043490786, 0.13828352, 0.20429905, 0.28155825, 0.127419, 0.057945773, -0.06780165, -0.017564125) * g_15;
    result += mat4(-0.13482623, -0.065182775, 0.08911843, 0.2783017, 0.11952674, 0.06991993, 0.299208, -0.10903764, 0.18224056, 0.03948293, -0.21087712, -0.11832146, 0.10328364, -0.07665122, 0.18435805, -0.11931017) * g_16;
    result += mat4(0.034891166, -0.13113704, -0.17151785, -0.27690044, 0.11699234, -0.0034974716, -0.0656246, 0.07852395, 0.15545385, 0.0013671276, -0.046343226, 0.0034052336, 0.2453219, 0.13581915, -0.13983195, 0.007911855) * g_17;
    result += mat4(-0.011330336, 0.24790573, -0.15979306, 0.19069764, -0.40002748, 0.011870201, 0.0031194224, -0.17847504, -0.0150662465, 0.13579376, 0.0030671223, -0.11590648, 0.18090703, -0.08737256, 0.39159694, -0.22220485) * g_18;
    result += mat4(-0.11186643, 0.21464026, -0.09462943, -0.14211422, 0.36246783, -0.097312845, 0.21176222, -0.20439352, 0.08605301, -0.0007772716, -0.047504634, 0.035329465, 0.01759311, -0.042337477, -0.14740078, 0.28027928) * g_19;
    result += mat4(0.124633305, 0.49622107, -0.1905822, -0.032103766, -0.09118705, -0.071040735, -0.17103319, 0.21466342, -0.06857113, 0.030909235, 0.08125023, 0.2334075, 0.06821963, -0.21760683, 0.25531697, 0.15648827) * g_20;
    result += mat4(-0.12612516, 0.16043583, -0.049337797, 0.0980794, -0.17805529, 0.0054840203, 0.171222, -0.017960507, 0.33597863, -0.27860585, -0.08922912, -0.12972547, -0.16144331, -0.039900865, -0.263512, 0.089571014) * g_21;
    result += vec4(-0.06092896, 0.0026034676, -0.0045185564, -0.045552935);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf5, ivec3(valid_xy, tile.inputLayer), result);
}