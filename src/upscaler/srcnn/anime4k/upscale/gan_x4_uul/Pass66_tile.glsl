// Anime4K_Upscale_GAN_x4_UUL - Pass 66 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_21_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_21_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_21_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_23_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 1038) uniform texture2DArray tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_24_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_21_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_21_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_21_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_21_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_21_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_21_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_23_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_23_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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
#define g_26 (max((texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_28 (max((texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_29 (max(-(texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.071940355, 0.2520996, 0.09685728, -0.0401572, -0.020982517, -0.04016773, 0.1032851, 0.15116775, -0.1194921, -0.13441806, -0.15435277, 0.00857813, 0.117160164, -0.013084895, -0.12161744, 0.044572134) * g_0;
    result += mat4(0.082026035, -0.16376685, 0.045928918, -0.04447462, 0.10981917, 0.054794677, 0.07120542, 0.084866405, 0.045389425, -0.021687545, 0.028005822, -0.210078, 0.04063033, 0.115505874, -0.27422935, 0.21725571) * g_1;
    result += mat4(0.22438343, 0.29941106, -0.012607681, 0.058178894, -0.08457912, -0.20864323, -0.07985059, 0.22438551, -0.06932785, 0.03345395, 0.28202337, 0.034280214, -0.1215527, 0.07437099, 0.20735577, -0.15139194) * g_2;
    result += mat4(-0.14662248, 0.022648463, -0.005571487, -0.07256508, 0.06747346, 0.0043868935, 0.094813496, 0.10695963, -0.14902529, 0.063808665, -0.08206709, -0.060363546, -0.0005435626, -0.15917943, 0.061691567, 0.09855836) * g_3;
    result += mat4(0.017799556, -0.009981281, -0.10833081, -0.13543043, -0.14525245, -0.06271629, 0.0726242, 0.07933559, -0.064622484, 0.08688535, -0.08111695, 0.013164932, 0.08823724, 0.006742534, -0.101684675, 0.017604306) * g_4;
    result += mat4(-0.031298436, -0.08050973, -0.18454958, -0.07897026, -0.0374373, -0.23446067, 0.038722772, 0.014162436, -0.15375976, -0.2147507, -0.095423505, 0.20034626, 0.028895382, 0.039372966, 0.06964464, 0.10350529) * g_5;
    result += mat4(0.21796271, -0.25407016, -0.098337315, -0.023319852, 0.030746967, 0.018345634, -0.010781914, -0.11792986, 0.28487346, 0.00467481, -0.040187147, 0.050997503, -0.060900237, 0.17249253, 0.055063184, -0.025005285) * g_6;
    result += mat4(0.049115237, 0.09444041, 0.07742757, -0.004662866, -0.14920074, -0.15653574, 0.14555736, -0.07487493, 0.08641984, -0.06845398, -0.15090026, 0.14357427, -0.07476173, 0.009871881, 0.19720715, -0.08900054) * g_7;
    result += mat4(-0.1306777, -0.12845808, 0.11419963, -0.006885182, 0.008033006, 0.06334985, -0.0060840836, -0.006333369, -0.02772289, -0.07669655, -0.07227849, 0.014051398, 0.111269996, -0.11380638, -0.10760507, -0.08484392) * g_8;
    result += mat4(0.2309008, 0.0027662152, -0.036648475, -0.02116145, -0.052217614, -0.19290513, -0.08249262, 0.060923748, 0.1697141, 0.04970059, 0.11332741, -0.02550202, -0.055906452, 0.3661976, -0.09877092, 0.1200653) * g_9;
    result += mat4(0.021928959, -0.050234713, 0.018235236, -0.050222646, 0.09582609, 0.021217717, -0.085548654, 0.10058183, -0.053230625, -0.082145125, 0.11671694, -0.07539133, -0.14239438, -0.13499749, -0.119287185, 0.11536136) * g_10;
    result += mat4(0.14766274, 0.016457219, 0.14650516, -0.17780317, -0.0026669295, 0.25558603, 0.09041751, -0.0301739, 0.03781546, 0.31132954, 0.080671474, -0.066909626, 0.022474205, 0.031319484, -0.22102872, 0.18719581) * g_11;
    result += mat4(0.08785325, 0.012904848, -0.16835691, -0.09674578, -0.25299898, 0.080151744, -0.04051892, -0.020169353, -0.16149361, 0.020387627, 0.12841122, -0.22339927, -0.18225776, 0.13121991, -0.094190426, -0.0002138417) * g_12;
    result += mat4(-0.36095276, -0.21171942, 0.17676146, -0.022404185, 0.4154611, -0.19463924, -0.10602125, 0.2693611, 0.10176359, -0.150534, 0.018383717, 0.19981897, 0.14625713, -0.13406813, -0.16022418, 0.2644558) * g_13;
    result += mat4(-0.06377917, 0.008183962, -0.006316106, -0.21600586, -0.26798826, -0.11782882, 0.06906469, -0.12426933, -0.27595305, 0.10574508, 0.3301182, -0.1685902, 0.17062853, 0.09983599, -0.08783116, 0.02585788) * g_14;
    result += mat4(0.18317774, -0.12538116, -0.28490618, 0.08996663, 0.42957532, 0.26287696, 0.10370257, 0.14557624, 0.70839125, 0.28065285, 0.009297889, -0.080495015, -0.14877662, 0.15308489, 0.07313569, 0.1318443) * g_15;
    result += mat4(0.08888086, -0.23179686, 0.17731842, 0.2988673, 0.021801222, -0.19859089, 0.011203003, -0.010040333, -0.054594494, -0.12354569, -0.21615268, 0.2763243, -0.099458195, -0.020375904, -0.13495544, 0.11390239) * g_16;
    result += mat4(-0.09784923, 0.1944123, 0.2601614, -0.28403583, -0.12053281, 0.028450225, 0.35481617, -0.027033992, 0.12224312, 0.12257788, -0.03696105, -0.050443426, 0.19214073, -0.035758987, 0.17233865, -0.21286553) * g_17;
    result += mat4(0.19778739, 0.19405492, 0.08939406, -0.06725612, 0.00286375, -0.071152225, 0.11470776, 0.1390715, -0.15622304, 0.06087436, 0.13643411, -0.046493623, 0.13816592, -0.13400874, -0.066770785, 0.09377127) * g_18;
    result += mat4(0.093480326, 0.11511413, -0.014940799, -0.300682, -0.07999973, 0.03399139, 0.122863345, -0.21434176, 0.10897804, 0.0074770562, -0.007341148, -0.11243166, -0.030653583, 0.11616559, 0.018601365, -0.23593631) * g_19;
    result += mat4(-0.07589857, -0.02816285, 0.10634287, -0.018159848, 0.10259108, 0.09316107, 0.114035785, 0.1632097, -0.16202134, 0.014525685, -0.057170212, 0.038775932, 0.18918377, 0.096198745, -0.26848194, 0.18337348) * g_20;
    result += mat4(-0.2151602, 0.1066596, 0.14015315, -0.16308795, 0.11991323, 0.043978903, 0.0656563, 0.03562853, 0.1823667, 0.22206141, 0.09851152, 0.10862079, -0.1730631, 0.07102773, 0.17776415, -0.24044661) * g_21;
    result += mat4(0.0060158237, -0.19177158, 0.10502828, -0.013080114, -0.08032154, 0.13057697, -0.076577656, 0.03263069, -0.11365605, -0.026887862, -0.09828686, -0.05051089, 0.04763855, 0.062761344, 0.013665174, 0.013192335) * g_22;
    result += mat4(-0.024832191, 0.054555204, 0.04472656, 0.015691593, 0.042494036, 0.06770802, -0.016350098, -0.1738042, 0.18029715, 0.08776134, 0.1073352, -0.0917886, -0.083804026, 0.0037783678, 0.018796401, 0.011723983) * g_23;
    result += mat4(-0.22104199, 0.046134423, -0.06569704, -0.19891003, 0.16334966, 0.3763836, -0.019122118, -0.19262604, 0.007953619, 0.035609093, -0.023634747, 0.05284935, 0.14042082, 0.012188833, -0.090246305, 0.09179504) * g_24;
    result += mat4(0.03651659, 0.024162583, 0.04007273, 0.2573568, -0.09408693, -0.15685976, -0.052655444, 0.07787627, -0.052549917, 0.012946145, -0.17698365, 0.016063817, 0.09167271, -0.024874488, 0.07187681, 0.033850722) * g_25;
    result += mat4(0.004172805, 0.022183372, -0.11286437, 0.08598362, -0.13067168, 0.16070427, 0.05422221, -0.029724583, -0.030735672, -0.00447319, 0.23366688, -0.016390052, 0.12756462, 0.24891639, 0.024162434, 0.080731995) * g_26;
    result += mat4(0.089021474, -0.06563795, 0.27291998, -0.13451853, 0.122246146, 0.34007818, -0.18697657, 0.009945519, 0.05180866, -0.12638813, -0.1173521, -0.05986753, -0.0337749, 0.064504266, 0.0034679365, -0.1219767) * g_27;
    result += mat4(-0.06837359, -0.07258382, 0.0140398, -0.07469804, 0.18686692, 0.19984262, -0.22008726, 0.26256636, -0.10768354, -0.18561411, 0.1427139, -0.030018665, 0.09759611, 0.103011966, 0.05294409, -0.016820678) * g_28;
    result += mat4(-0.11673777, 0.051226504, -0.034002636, -0.2731483, -0.08450124, 0.31373835, 0.22628455, 0.03579624, 0.08832027, 0.11600223, -0.03500645, -0.23789707, -0.18811859, -0.2895229, -0.31334436, -0.09072995) * g_29;
    result += vec4(0.028765388, 0.015914816, -0.010572618, -0.046241153);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf1, ivec3(valid_xy, tile.inputLayer), result);
}