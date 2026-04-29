// Anime4K_Upscale_GAN_x4_UUL - Pass 41 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_15_tf;
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
vec4 result = mat4(-0.009551103, -0.1578829, -0.023872105, 0.032085985, 0.027971271, 0.039934665, -0.28228688, -0.061062165, 0.100776665, -0.04452535, -0.006273476, -0.09813465, 0.004865175, 0.09403208, -0.20160039, 0.413236) * g_0;
    result += mat4(0.18565936, 0.035244744, -0.08872044, 0.022702076, -0.11219526, 0.050610166, -0.029482607, -0.15944795, 0.11747894, -0.034937173, -0.10601389, -0.07908995, -0.06948369, 0.078262895, -0.10566501, -0.0712045) * g_1;
    result += mat4(0.15651268, -0.051332787, -0.16583267, 0.04954766, 0.041720442, -0.14801401, -0.011037535, -0.05058025, 0.078457914, 0.042230852, -0.072076604, 0.22530177, 0.06007432, -0.00476048, 0.045151718, 0.21380138) * g_2;
    result += mat4(-0.24534833, -0.11603982, -0.18161574, -0.07407666, -0.19366856, 0.06265982, -0.13283755, -0.14593442, -0.13195409, -0.039278407, 0.08604219, 0.29780805, 0.008677809, 0.06479625, 0.015411021, 0.034155287) * g_3;
    result += mat4(0.05640475, 0.037920874, -0.09059915, -0.08817172, -0.27626717, 0.12396845, -0.13103396, 0.0026781796, 0.15049712, 0.07754007, -0.19105206, 0.17042683, 0.3114985, -0.09133819, -0.021938948, 0.254589) * g_4;
    result += mat4(-0.16998518, -0.20131175, 0.027466161, 0.11566531, 0.18034823, 0.072060615, -0.23353261, -0.11075216, 0.032076754, -0.021048, 0.012148336, 0.091040045, -0.18995504, 0.08408764, -0.1569736, 0.03552465) * g_5;
    result += mat4(-0.04162126, -0.057651754, -0.065363966, -0.18329124, 0.104769826, 0.089769594, 0.15653561, 0.09221142, 0.004628914, -0.057831094, -0.092486836, -0.052079238, 0.12100204, 0.18322322, 0.11601413, 0.0020635729) * g_6;
    result += mat4(0.15670863, -0.11881685, 0.2568278, -0.1839135, -0.04724428, 0.06305948, -0.039979734, 0.09861011, 0.03296062, -0.029781949, -0.25168973, 0.05086964, 0.035107438, 0.058550417, 0.03825196, -0.03621426) * g_7;
    result += mat4(-0.14257605, -0.18165039, -0.101343095, -0.1612177, -0.07650364, 0.07354628, 0.3225121, -0.0399608, 0.23337401, 0.09668289, 0.17832872, -0.19480577, -0.37638342, 0.009177453, 0.01430114, -0.06184679) * g_8;
    result += mat4(0.18150946, -0.17396615, 0.15020455, 0.11095252, -0.04938365, 0.13811995, 0.21872883, 0.1665478, 0.24408577, -0.25829598, -0.05333277, -0.09722728, -0.14163989, -0.2562132, -0.071317025, 0.23899561) * g_9;
    result += mat4(-0.06284202, 0.027760154, 0.11999594, 0.17721936, 0.084894985, -0.088369444, 0.017951638, 0.20490159, -0.059588224, 0.02880265, -0.026036453, -0.10354341, 0.10513227, 0.087837726, 0.2588742, -0.27092904) * g_10;
    result += mat4(-0.16925864, 0.08769487, -0.09762704, 0.0391378, 0.0035971864, 0.072891735, 0.09307799, 0.27171433, 0.07969811, -0.02832524, 0.018054279, -0.18448217, 0.008436939, -0.041673474, 0.09115246, 0.014632326) * g_11;
    result += mat4(0.25382346, 0.065921, -0.07871562, -0.25246596, -0.1803274, -0.12246585, 0.1921425, 0.18788809, -0.061109893, 0.09155593, -0.089252725, -0.27288997, 0.19322978, -0.20218955, 0.12605186, -0.2562263) * g_12;
    result += mat4(-0.2838705, -0.040187504, 0.07924205, -0.21460438, -0.12758467, 0.009960648, 0.14958748, -0.20346983, 0.0024511465, -0.0029784795, 0.03761442, 0.13831198, -0.024297677, 0.1012345, -0.084601626, 0.18076244) * g_13;
    result += mat4(0.06449929, 0.05275191, -0.12103874, 0.24089414, -0.20560616, -0.10341962, 0.1507051, 0.06430561, -0.13462862, 0.09508162, 0.1236627, -0.012525578, -0.09431966, 0.041634366, 0.08173197, -0.15510611) * g_14;
    result += mat4(0.027247978, 0.094439656, -0.03555053, -0.098382965, -0.12275858, 0.07966601, 0.011419914, 0.016940989, -0.059244152, 0.0141640995, 0.28897017, -0.23790632, 0.06870021, 0.065537006, 0.10910026, 0.068046376) * g_15;
    result += mat4(0.09527742, 0.07966788, 0.0065336, 0.00047729645, -0.22677961, -0.19132724, 0.038642567, -0.20873657, 0.22698054, -0.17566124, 0.0931999, -0.049740683, -0.13000306, -0.21351433, -0.057329457, -0.101816036) * g_16;
    result += mat4(0.009278632, 0.039469216, -0.085109934, 0.28698707, -0.14632075, -0.10635572, 0.08193169, -0.29346558, -0.13445924, 0.14408123, -0.020417368, -0.09325916, -0.20485316, -0.15253286, -0.03744777, -0.003730377) * g_17;
    result += mat4(-0.08470291, 0.003728395, 0.107398994, -0.16985098, 0.0072377436, 0.27434322, -0.17388123, 0.015298767, 0.040480837, 0.19347449, 0.077726595, 0.10207363, -0.1588992, -0.0074615697, 0.15348962, -0.2786934) * g_18;
    result += mat4(0.12293403, -0.031468052, -0.07419456, -0.039155077, -0.066696815, 0.12546724, 0.17678119, 0.16800387, 0.07157375, -0.06990396, 0.087699026, 0.012418362, -0.05796857, 0.08915443, -0.003907652, 0.024577782) * g_19;
    result += mat4(0.049035165, -0.007998411, -0.08784051, 0.05972267, 0.12698646, -0.06103241, -0.004091063, 0.054421507, 0.066380054, -0.17193739, 0.030281775, 0.012471225, 0.36877003, -0.22548924, -0.03885732, -0.18560503) * g_20;
    result += mat4(0.06274616, 0.080091685, 0.08087955, 0.07442669, 0.021437827, 0.08772858, 0.03468758, 0.03489351, -0.114316195, -0.1327461, -0.17319082, 0.05784275, -0.14492308, 0.13633093, 0.24737152, -0.17852335) * g_21;
    result += mat4(0.07352172, 0.12839572, -0.14603852, 0.038831383, -0.10336226, -0.008882389, 0.2233969, 0.014047068, -0.008017061, 0.0032474427, -0.03606961, 0.13068153, -0.079270124, 0.04567792, -0.11811478, -0.37396926) * g_22;
    result += mat4(-0.0875562, 0.0075374576, 0.24364722, 0.3135225, 0.059202157, 0.017321471, -0.44433868, 0.31329906, 0.2166983, 0.15394291, 0.16318081, -0.0053147315, -0.20274022, -0.33773518, -0.22899714, -0.4062436) * g_23;
    result += vec4(-0.035847142, 0.032481533, 0.0020201565, 0.07194935);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf, ivec3(valid_xy, tile.inputLayer), result);
}