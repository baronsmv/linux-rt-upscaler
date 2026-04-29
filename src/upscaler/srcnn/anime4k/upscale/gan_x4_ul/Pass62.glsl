// Anime4K_Upscale_GAN_x4_UL - Pass 62 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_27_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_27_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_27_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_27_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_26_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_25_tf;
layout(set = 0, binding = 1038) uniform texture2D tex_conv2d_28_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups2;
#define g_0 (max((texture(sampler2D(tex_conv2d_27_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_27_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_27_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_27_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_27_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_27_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_27_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_27_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_26_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_26_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_25 (max(-(texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_28 (max((texture(sampler2D(tex_conv2d_28_tf, pointSampler), pos)), 0.0))
#define g_29 (max(-(texture(sampler2D(tex_conv2d_28_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.023159716, -0.06445511, -0.13444243, -0.3029728, 0.09424871, 0.046222795, 0.1665773, 0.0054540136, 0.108596064, -0.034167033, 0.09486344, -0.06652879, -0.12501813, 0.29003936, -0.001826413, 0.4086747) * g_0;
    result += mat4(0.17339195, -0.12188165, -0.11409943, -0.08955709, 0.08390357, 0.15925337, 0.10573395, -0.044203065, -0.1956127, 0.062437166, -0.055394087, 0.21211234, -0.05303983, 0.08320662, 0.03260874, 0.085122004) * g_1;
    result += mat4(0.050840195, -0.0882688, -0.37795234, -0.21878824, 0.0823033, 0.001571019, -0.086516365, -0.032059066, 0.031085746, -0.26207578, 0.03567986, -0.15979347, -0.123573, -0.041428905, -0.07892891, 0.111200064) * g_2;
    result += mat4(0.118134536, 0.0017017128, 0.06084789, 0.13862696, -0.004776377, -0.022721525, -0.12781031, 0.023450686, -0.20167245, -0.014491597, -0.32268152, 0.041146316, -0.08904564, 0.13891083, 0.026140563, 0.053664643) * g_3;
    result += mat4(-0.014918813, -0.11442104, 0.0741294, 0.20350552, -0.024969127, -0.04713554, -0.09463233, -0.06777642, -0.15385136, 0.09367639, -0.18212073, -0.12458825, -0.11280945, -0.12408857, 0.056655087, -0.097056136) * g_4;
    result += mat4(-0.09134359, 0.42729822, 0.13041808, 0.22597447, -0.06003689, -0.017370071, -0.12883402, 0.027216416, 0.029739086, -0.0060472586, 0.00443273, -0.07316318, -0.046336673, -0.21877831, 0.020554282, 0.1732762) * g_5;
    result += mat4(0.12951167, 0.05868595, 0.23511209, -0.06839014, -0.13673079, -0.11585807, -0.17553164, -0.1661913, 0.03966464, 0.17386018, -0.11228396, -0.050033193, 0.13843036, 0.03351075, 0.14025663, -0.25514498) * g_6;
    result += mat4(-0.038775686, -0.04935347, -0.038891345, -0.019735469, 0.07429314, -0.0223186, 0.077693924, 0.15711477, 0.2130033, 0.19355707, 0.16412027, 0.06635085, 0.038207706, 0.06053999, -0.12567896, -0.007636511) * g_7;
    result += mat4(0.09569034, -0.010271957, 0.03721736, -0.15505005, -0.0838559, 0.0016339924, -0.05316335, 0.063593015, -0.20762952, -0.17041244, 0.046337787, 0.042274795, 0.10624157, 0.110793, 0.13401565, 0.17065364) * g_8;
    result += mat4(-0.11632263, -0.12953088, 0.001185442, 0.10271505, 0.063425556, 0.20457491, 0.035240173, -0.016209599, 0.18448795, 0.28286663, 0.047897473, -0.03594525, 0.12672062, 0.02626917, -0.017910505, -0.023291295) * g_9;
    result += mat4(0.15155636, 0.34159487, -0.14385378, 0.1202715, 0.08488496, -0.14626624, -0.15154605, 0.033907797, -0.4028903, 0.009578373, 0.20309076, 0.03162836, 0.0046819323, 0.12714009, -0.013452622, -0.027946994) * g_10;
    result += mat4(-0.023553226, 0.012964108, 0.2615834, -0.18088982, 0.16396646, -0.1555898, 0.062380422, -0.13156545, 0.11771863, 0.11465695, 0.15540528, 0.05780806, 0.162502, -0.15075624, -0.081975155, 0.08368184) * g_11;
    result += mat4(0.21025248, 0.19884978, -0.12959355, 0.12049732, 0.22328858, 0.13621397, -0.14099576, -0.12470971, -0.09525357, -0.3020424, 0.06765223, 0.11113628, -0.06416074, -0.19985223, -0.16019244, -0.11679983) * g_12;
    result += mat4(-0.09884801, -0.19851618, 0.09546932, 0.16984892, -0.23047769, -0.19711624, 0.075863495, 0.0017955381, 0.015505981, -0.18864273, 0.078835726, 0.045279432, -0.008318564, 0.22265139, 0.24933302, 0.012418065) * g_13;
    result += mat4(-0.12885031, 0.07197899, 0.034894828, -0.027127236, -0.15808247, -0.090660565, -0.032682374, 0.04424032, -0.02021023, 0.23655033, 0.2861916, 0.1077876, -0.00029343172, 0.14406225, -0.12042908, -0.05617217) * g_14;
    result += mat4(0.06726449, -0.13338274, 0.13298374, 0.1509329, 0.0012467351, 0.10550558, -0.11021875, -0.089391366, -0.121223524, -0.18981695, -0.30600676, -0.17530401, 0.035590086, -0.19236173, -0.00065066793, -0.14428075) * g_15;
    result += mat4(-0.07112659, -0.020882819, -0.1465499, 0.096829794, 0.20048432, 0.104522765, -0.26555765, -0.097862296, -0.030852538, 0.105224766, 0.08888586, 0.17757314, 0.16541813, -0.23302473, 0.2233853, -0.010632784) * g_16;
    result += mat4(0.014658764, -0.0334598, 0.3128382, 0.077815466, -0.22126053, -0.04505339, 0.061955534, 0.021540016, 0.010367894, -0.051611926, 0.07533717, -0.056219503, -0.2093322, 0.03568594, -0.17417803, -0.10428233) * g_17;
    result += mat4(0.2191052, 0.11557848, -0.012550732, 0.17574733, -0.029502312, -0.032267477, -0.07563763, -0.07457431, -0.038292985, -0.09042212, 0.08027953, 0.19520667, -0.083191395, 0.12538701, -0.09176717, 0.011189392) * g_18;
    result += mat4(-0.16427885, -0.10249853, -0.17418809, -0.17851928, -0.02198882, -0.016383043, -0.056685332, 0.054567203, 0.085425794, 0.07624397, 0.029935993, -0.11497607, 0.09389378, -0.113407105, -0.037462458, 0.05798364) * g_19;
    result += mat4(-0.11592955, -0.0355327, 0.02012006, 0.08628437, 0.18852545, 0.04429939, 0.2095552, 0.11321021, -0.10715762, -0.06410171, 0.07349654, -0.10263874, -0.25958562, -0.0065148305, 0.05395847, 0.23721853) * g_20;
    result += mat4(0.08934432, -0.018261336, -0.1469809, -0.1230833, -0.03024807, -0.108250126, -0.1356501, -0.19411466, 0.12480876, -0.056631427, -0.14539632, -0.011234567, -0.108617164, -0.0075640143, 0.016628174, -0.031951398) * g_21;
    result += mat4(-0.030735651, -0.25655523, 0.07889343, 0.072985075, -0.14274006, -0.0726582, -0.17257299, 0.04806954, 0.20640111, 0.09091482, -0.02442191, -0.056154832, -0.0973647, -0.15620042, 0.062126547, -0.27619773) * g_22;
    result += mat4(0.019488974, 0.09159406, 0.050291736, 0.05484099, 0.007813524, 0.031137392, 0.008452417, -0.06525648, -0.024203332, -0.04843337, 0.0056339726, -0.08692725, 0.12216992, -0.1479449, -0.11445307, 0.14418265) * g_23;
    result += mat4(-0.092634715, -0.12256442, -0.03266669, -0.13706104, -0.028364131, -0.16320482, 0.025872277, 0.0038799648, -0.038322225, 0.07213509, -0.08575004, 0.00078005146, -0.19118088, 0.13901393, -0.07466347, -0.15850773) * g_24;
    result += mat4(-0.10358112, 0.23026147, -0.17026868, 0.22740762, -0.073265195, 0.20872793, -0.1305692, 0.041578945, -0.14450042, 0.074723445, -0.19840808, -0.31698796, -0.13111241, 0.039627273, 0.20071575, 0.18766841) * g_25;
    result += mat4(0.083393425, 0.0077654063, -0.024181146, -0.23965842, -0.015347993, 0.06553551, -0.075003184, -0.12717652, 0.24724984, -0.2618065, 0.00016140452, -0.030394942, -0.09804706, -0.05339126, 0.13838013, -0.11934897) * g_26;
    result += mat4(-0.15981214, 0.099963255, 0.020670403, 0.055687193, 0.098974116, 0.09318632, -0.0020179797, 0.069629736, -0.18775915, 0.06435833, -0.054918338, 0.073864214, -0.004390631, 0.017190594, -0.099290535, 0.23170115) * g_27;
    result += mat4(-0.025526501, 0.06180454, 0.02409264, 0.067765474, -0.25856894, 0.056929503, -0.23243466, -0.29785407, -0.057924725, -0.18965043, -0.19148564, -0.08055246, 0.123928405, -0.12250164, -0.050594267, 0.03553811) * g_28;
    result += mat4(-0.0960669, -0.06418567, -0.15908502, 0.032472476, 0.17400779, -0.1997357, 0.23960195, 0.17217276, -0.17098325, 0.07912132, 0.15839973, 0.09257917, -0.11821401, 0.18548669, -0.04553704, 0.14563085) * g_29;
    result += vec4(-0.020268483, -0.020570418, 0.013189642, -0.023046626);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups2, gxy, result);
}