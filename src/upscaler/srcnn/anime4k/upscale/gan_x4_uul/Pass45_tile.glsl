// Anime4K_Upscale_GAN_x4_UUL - Pass 45 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_12_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_12_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_12_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_12_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_12_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_12_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_14_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_15_tf4;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_12_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_12_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_12_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_12_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.14196062, -0.02053057, -0.07263348, 0.22242844, -0.069366455, -0.07599116, -0.24256042, 0.054868866, -0.17625082, -0.007019716, -0.113896124, 0.06029265, -0.33038747, -0.24047355, -0.07707203, -0.12618175) * g_0;
    result += mat4(0.2641447, 0.20302898, 0.11049544, 0.06935479, 0.08874244, -0.11180222, 0.22703084, -0.037252616, 0.049151152, -0.26571065, 0.2566087, -0.19559465, 0.026178649, -0.09336953, -0.15396582, -0.060832605) * g_1;
    result += mat4(-0.14049934, 0.037963107, -0.21600282, -0.024867453, 0.23356499, 0.25709978, 0.20883206, 0.025470912, 0.081024416, 0.086439654, 0.039591312, 0.0703785, 0.08931542, -0.017118547, 0.08146628, -0.20914824) * g_2;
    result += mat4(0.16301146, 0.055098668, -0.17369606, 0.1285926, -0.21210109, -0.21506578, 0.2993681, -0.18734126, 0.10324259, -0.10892179, 0.16455299, -0.09379545, 0.07187383, 0.18076982, -0.19408746, -0.14634538) * g_3;
    result += mat4(-0.17136872, 0.18589741, -0.26261556, 0.27026632, -0.06397295, -0.19135362, -0.13612793, 0.04076611, -0.14749071, 0.0644836, 0.029172575, 0.14051709, 0.018954301, -0.17011856, 0.03518231, 0.14694777) * g_4;
    result += mat4(0.01462739, 0.16519663, -0.06963009, -0.26547143, 0.053700965, -0.07965579, 0.030911697, 0.08216649, -0.09090798, -0.14469762, 0.101480395, 0.2453987, 0.16511187, 0.09583153, -0.051365204, -0.31418574) * g_5;
    result += mat4(-0.14265122, 0.013500145, -0.27755547, -0.35044006, -0.28055587, 0.14820805, -0.07966734, 0.20943366, 0.3879986, 0.044507142, 0.28056288, 0.12725809, -0.043548014, 0.054243155, 0.053768754, -0.07648862) * g_6;
    result += mat4(-0.16118912, -0.15949926, 0.10161533, 0.22494748, -0.14213897, 0.012663654, 0.19885182, -0.15045607, -0.17744212, 0.15615463, -0.17122573, 0.041775905, 0.16900201, 0.09705761, -0.003141293, -0.031626303) * g_7;
    result += mat4(0.26178294, 0.13443723, -0.10966655, -0.025935082, 0.11178123, 0.10601803, 0.11125899, -0.04168405, 0.07152025, -0.12318109, 0.06391876, -0.26012185, -0.26537088, -0.01870863, -0.31110883, 0.072430775) * g_8;
    result += mat4(-0.11461679, -0.11115381, -0.11512802, -0.0849818, -0.19124708, -0.09565243, -0.31988642, -0.007379634, 0.13623501, -0.27210787, 0.20422134, 0.17212251, 0.20176752, -0.2088367, 0.057676136, 0.26400682) * g_9;
    result += mat4(0.06382013, -0.019412925, 0.11166499, -0.1167881, -0.071942225, 0.018743433, -0.14072515, -0.07148564, -0.10749998, 0.12237429, -0.10744663, 0.04025467, 0.26050708, 0.351076, -0.02934236, -0.22102655) * g_10;
    result += mat4(-0.10656222, -0.09071829, -0.34339997, -0.07646886, 0.02796594, 0.005340661, 0.115450874, 0.14969155, 0.03835863, -0.010790472, -0.05871064, 0.01423236, 0.22537707, 0.33385828, -0.15029915, 0.07367339) * g_11;
    result += mat4(0.30884805, -0.23663065, 0.031883277, -0.03320561, -0.050423212, -0.3281527, 0.10394608, -0.0749873, -0.064002484, -0.35469085, -0.2122367, 0.020249272, -0.27326742, 0.02000293, 0.20578866, -0.018839063) * g_12;
    result += mat4(-0.5473822, -0.10873662, -0.29810318, -0.07632667, 0.047157068, 0.06275736, -0.09811392, 0.24783231, -0.12046891, 0.41266727, 0.2436679, 0.024679149, -0.12600063, -0.17010899, -0.21425788, 0.07119708) * g_13;
    result += mat4(0.117677234, -0.054181933, 0.065846235, -0.04929893, 0.08533609, 0.04636543, 0.30038458, 0.02330411, 0.024728734, -0.09597387, 0.010447719, -0.20696889, -0.017916039, 0.079871304, 0.010056369, 0.06291176) * g_14;
    result += mat4(-0.0579763, 0.018944405, -0.14009921, 0.08765421, -0.029314717, -0.13179289, -0.009668318, -0.117530614, -0.0853067, 0.03650012, 0.0078530945, -0.19518211, -0.05920554, 0.19264583, 0.008880586, -0.03560413) * g_15;
    result += mat4(0.042966127, 0.025064057, 0.094821475, -0.016764855, -0.21325764, -0.060747217, -0.07825418, -0.1374183, 0.06629058, -0.093919374, 0.15805462, 0.1187494, 0.21715021, -0.09113653, 0.06076613, 0.1753257) * g_16;
    result += mat4(0.23275353, -0.045174975, 0.17990083, -0.03170214, -0.20888183, -0.050161786, -0.44225174, -0.07750995, 0.055791933, 0.1754295, 0.13890503, -0.087261945, 0.015942331, -0.002073752, 0.23700726, -0.1406417) * g_17;
    result += mat4(-0.17989896, 0.052198254, 0.09631692, -0.16038898, 0.03376904, -0.042175625, -0.039186575, -0.2520231, 0.04852203, 0.09647585, -0.011128373, 0.010953865, -0.1797949, -0.058203597, 0.06857295, 0.040861364) * g_18;
    result += mat4(-0.025050908, -0.1299404, 0.28858674, -0.017769823, 0.06310829, 0.086729944, 0.08149323, -0.055179875, 0.13012943, -0.07458519, 0.1382156, 0.051026117, -0.18673064, 0.086739376, 0.09040544, 0.0836127) * g_19;
    result += mat4(0.020357449, 0.22048305, 0.09739252, 0.24337311, 0.010595294, -0.11086683, 0.059038695, 0.05644574, -0.16103926, -0.035155784, -0.26436335, -0.06716334, 0.17485845, 0.16937979, -0.20187125, -0.038486667) * g_20;
    result += mat4(-0.0045594163, -0.21635443, 0.06031479, -0.19148222, -0.006656789, 0.08385509, -0.03819692, -0.17931695, 0.07232661, 0.23445003, -0.17640385, 0.16671506, -0.184719, -0.029015712, -0.022614706, 0.014873415) * g_21;
    result += mat4(0.32585597, -0.16295198, 0.04640218, 0.07696528, 0.069500424, 0.105702765, 0.1296909, 0.24009204, 0.14028086, 0.28418058, 0.11589889, -0.22921228, 0.010826454, -0.054120503, -0.25884682, -0.30648708) * g_22;
    result += mat4(0.07101887, -0.41187993, 0.31501228, -0.11794851, -0.20814322, -0.18655151, 0.14477637, -0.22380604, -0.058629174, -0.02504061, -0.09827353, 0.046498295, 0.18585126, 0.011712637, -0.10845518, -0.1348349) * g_23;
    result += vec4(0.04891512, -0.022042824, 0.015331318, -0.0034486696);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf4, ivec3(valid_xy, tile.inputLayer), result);
}