// Anime4K_Upscale_GAN_x4_UL - Pass 55 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_27_tf;
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
vec4 result = mat4(-0.11443151, -0.108713426, 0.276695, 0.07989307, 0.04647579, 0.009262729, 0.1685192, 0.06342496, 3.7802124e-06, 0.11471419, 0.21862917, -0.14714405, 0.07615697, 0.008696574, 0.12699789, -0.19018881) * g_0;
    result += mat4(0.12515754, 0.31493005, -0.09689205, 0.03547315, 0.014907384, -0.16497225, -0.13919856, -0.11483534, 0.12144794, -0.16309711, -0.32288572, -0.12443185, 0.069901936, 0.087048694, -0.10706947, -0.17567441) * g_1;
    result += mat4(0.39898342, -0.22792721, 0.14832391, 0.2717282, -0.020610651, 0.23566288, 0.010850474, -0.17099889, -0.016039778, -0.0020831313, -0.12241154, 0.12688214, 0.0036613182, 0.036608845, 0.014307337, -0.11151725) * g_2;
    result += mat4(-0.10309775, 0.13672508, -0.14171574, 0.0008346642, 0.009146607, 0.08628462, -0.08052912, -0.017026344, 0.15191628, -0.057887327, -0.19557409, 0.051096447, -0.08008495, -0.107524894, 0.2823684, -0.08889756) * g_3;
    result += mat4(-0.016564824, -0.24989256, -0.2249194, -0.0651977, -0.06807716, -0.025363477, -0.027399465, -0.07455227, 0.06599263, 0.26438046, -0.051439926, 0.06316548, 0.022916218, -0.046988536, 0.029912783, 0.022940762) * g_4;
    result += mat4(-0.12251786, -0.06948682, 0.22916022, -0.024786122, -0.00439896, 0.083174594, 0.036550373, -0.006298349, -0.11279929, -0.093094416, -0.034991793, 0.046064105, 0.11115092, -0.082963385, 0.05877601, -0.06852534) * g_5;
    result += mat4(0.07373158, 0.09035215, 0.07685686, -0.00512534, 0.16249287, -0.30190566, -0.17152359, -0.021798678, -0.036162075, -0.14855996, 0.06671937, 0.040752716, 0.038710788, -0.05742677, -0.15890189, -0.065827206) * g_6;
    result += mat4(0.08283188, -0.07847956, -0.1273862, 0.06317435, -0.045053452, -0.07436303, -0.21195294, 0.03413814, 0.0180427, -0.08224744, 0.19969232, -0.10173545, -0.0985865, 0.13246737, -0.22761853, -0.052478615) * g_7;
    result += mat4(0.058520608, -0.08817867, 0.23608765, -0.073843844, 0.052322935, 0.02629083, 0.13331904, 0.06627578, 0.041870154, 0.0606517, -0.26620305, 0.09230404, 0.027014492, 0.14735153, -0.16004741, 0.09812545) * g_8;
    result += mat4(0.047826007, 0.1634714, 0.11705604, 0.0708394, -0.009366613, -0.03155836, 0.077331886, -0.0031559314, 0.097498395, 0.04192316, 0.17008877, -0.2166131, 0.20248255, 0.010872594, 0.06436194, -0.13117972) * g_9;
    result += mat4(0.02341538, -0.083836935, -0.3000272, -0.13124003, -0.019327922, 0.04084534, 0.1415715, -0.032898612, 0.12683785, 0.2175736, -0.18110937, 0.16924378, 0.15692717, 0.2107051, -0.11289415, 0.024807237) * g_10;
    result += mat4(-0.0038417198, -0.023462469, 0.29741266, 0.41617903, -0.07855188, -0.10439054, 0.029460225, 0.19564202, -0.039808284, 0.1763466, -0.090184964, -0.34782696, -0.02403701, 0.074582, -0.12709166, 0.08750199) * g_11;
    result += mat4(-0.005616591, 0.06304182, -0.040408023, -0.09645956, 0.06324051, 0.20628944, -0.3098933, 0.02254578, 0.029077038, 0.053340837, 0.063302726, 0.16661525, 0.03846741, -0.009219741, 0.116365075, -0.10009024) * g_12;
    result += mat4(-0.05268469, -0.00017071658, -0.07163157, -0.21923296, -0.16725844, -0.03701403, -0.14504927, 0.014916945, 0.0009528244, -0.15782906, 0.12831807, 0.29388857, -0.016132563, 0.017562412, -0.25679052, -0.034620695) * g_13;
    result += mat4(0.22927792, -0.06749382, -0.009661854, 0.17025727, 0.0079777455, -0.041601792, -0.11932827, 0.03387773, -0.09392308, 0.3402342, 0.14215328, -0.39847612, -0.1305392, -0.15584923, 0.045079015, 0.01645792) * g_14;
    result += mat4(-0.04562495, 0.16534929, -0.046228826, -0.16118683, -0.14846939, 0.18226776, 0.0052598384, -0.23458757, 0.094621554, -0.10582074, 0.10714222, 0.05594153, -0.09598537, 0.113479495, -0.12497368, 0.023943413) * g_15;
    result += mat4(-0.02769864, -0.26299968, 0.14559303, 0.0944326, 0.17896965, 0.10208632, -0.013210181, -0.044628892, -0.05891498, -0.026696851, -0.22334224, 0.06637618, -0.18068133, -0.25608513, -0.17188187, 0.011999808) * g_16;
    result += mat4(-0.058387913, 0.0218284, -0.23960036, 0.022659982, -0.14655428, -0.2565323, 0.108330764, 0.13125636, 0.124482006, 0.16533256, -0.022780979, -0.09548541, 0.08578177, -0.006597655, -0.14589092, -0.12073695) * g_17;
    result += mat4(0.056324802, 0.0128009105, -0.025639247, 0.01001398, -0.17908664, -0.06784469, -0.2604881, -0.18153118, -0.063292824, -0.051646266, -0.06044485, 0.07686661, -0.082505025, 0.22550054, -0.037884668, -0.053193748) * g_18;
    result += mat4(-0.069400966, 0.0617642, 0.010582028, 0.09696695, 0.0014224951, -0.04151362, -0.12185871, 0.0012915661, 0.14637092, -0.006555717, -0.05938257, 0.13994268, -0.0066529186, -0.19960605, 0.15346165, -0.0865367) * g_19;
    result += mat4(-0.2611735, -0.022063201, -0.038368087, 0.09316622, -0.038465716, -0.18126398, -0.08461157, 0.067109436, 0.057539497, -0.20445953, 0.0928182, 0.04585181, -0.24495333, 0.0065940707, -0.37708935, 0.2060806) * g_20;
    result += mat4(-0.0027922213, 0.22430198, -0.14358118, 0.12783276, -0.11639961, -0.037831385, 0.13331455, 0.19188458, 0.053073954, -0.07114653, -0.058150347, 0.1569289, 0.124720514, -0.12141831, 0.1242011, 0.114829615) * g_21;
    result += mat4(-0.30982205, -0.037789118, -0.023584012, -0.108513854, -0.29589918, 0.23338793, -0.053462632, 0.14759938, 0.10133443, 0.11237711, 0.055803254, -0.12062855, 0.19252913, -0.08096047, 0.07718558, 0.008393711) * g_22;
    result += mat4(-0.050342154, 0.0074422276, 0.06969367, 0.08940038, -0.017735183, -0.18851873, 0.16643041, -0.3227906, -0.022566125, -0.14224024, -0.34606192, 0.046124987, -0.04396818, 0.0072183185, -0.15278862, -0.06988554) * g_23;
    result += mat4(0.034391437, -0.074430875, 0.20160396, -0.072047606, 0.2027079, -0.28531456, 0.10542997, -0.03773651, -0.055301867, -0.0936597, -0.21673253, 0.07367847, -0.02038547, -0.14456849, 0.22297329, 0.35531262) * g_24;
    result += mat4(-0.18277335, -0.08059337, -0.09400133, 0.15901576, 0.16223545, 0.2021658, 0.047907606, 0.056792736, 0.06719305, 0.0033384864, -0.06851851, 0.051555436, -0.040477566, 0.2388465, -0.020530254, -0.24586761) * g_25;
    result += mat4(0.11648392, -0.20024611, -0.07978261, -0.24872676, 0.24125583, 0.03680705, 0.044125002, -0.14167546, 0.18336643, 0.090984896, 0.07496362, -0.17672206, 0.16514459, -0.102161184, -0.030927394, 0.08411755) * g_26;
    result += mat4(-0.14201398, -0.31110483, -0.42112264, -0.11100327, -0.20474254, 0.027765524, 0.0070005557, -0.08926027, 0.044591606, -0.20539887, 0.08815937, 0.15499651, -0.15112466, 0.017493293, -0.12526624, 0.14187813) * g_27;
    result += vec4(-0.04274619, -0.027823832, -0.0074941483, 0.045495618);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_27_tf, ivec3(valid_xy, tile.inputLayer), result);
}