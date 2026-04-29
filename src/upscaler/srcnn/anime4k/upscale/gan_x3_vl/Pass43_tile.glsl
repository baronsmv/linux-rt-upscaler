// Anime4K_Upscale_GAN_x3_VL - Pass 43 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_20_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_22_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv0ups3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_21_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_21_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_21_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max((texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_22_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.19771652, 0.054560076, -0.018467195, 0.17260106, -0.04713744, 0.005960446, -0.15811634, 0.12638375, -0.20130037, -0.2361124, 0.15739627, 0.07660247, 0.008880481, 0.09471094, -0.1340188, -0.0603885) * g_0;
    result += mat4(0.018275172, 0.02949308, 0.16530277, -0.08129835, -0.017484661, 0.08206879, 0.05372496, 0.027559277, -0.07266388, 0.14723828, -0.019852815, -0.124051854, 0.19641098, -0.19842927, -0.02707376, 0.18565983) * g_1;
    result += mat4(0.0152915055, -0.025145184, -0.14171547, 0.11287294, 0.03981024, -0.283831, 0.08403579, -0.022620574, 0.097417176, -0.015617099, -0.0749846, 0.11501153, 0.07712399, -0.17645292, -0.18069206, 0.30625495) * g_2;
    result += mat4(0.11910245, -0.014835673, 0.016234221, -0.17016123, -0.12874368, 0.028920865, 0.0015389418, -0.0396468, 0.058122113, 0.06308889, -0.11089211, 0.07629556, 0.14638005, 0.15483578, -0.009679061, 0.028340086) * g_3;
    result += mat4(-0.18488705, -0.09046926, 0.3086096, 0.28608966, 0.07914294, -0.18663022, -0.18758698, -0.010628958, 0.11284831, -0.024477161, -0.34357247, -0.110528395, 0.11260746, -0.16653295, -0.333203, -0.028419986) * g_4;
    result += mat4(0.14164338, 0.0116197225, -0.09517204, 0.018433275, -0.11906503, 0.12618221, -0.14154993, 0.11922271, -0.25966203, 0.13593048, -0.12451744, -0.12732752, -0.17531879, -0.059646163, 0.08191489, -0.023034088) * g_5;
    result += mat4(0.060834974, -0.17094417, -0.12378968, 0.20129171, 0.10589014, 0.27925324, -0.0760502, -0.19307284, 0.1918753, 0.06295021, -0.117325544, -0.032219686, 0.08970859, 0.10133687, 0.07045942, -0.043928903) * g_6;
    result += mat4(0.06141528, -0.1155439, 0.07150852, -0.017323446, 0.14442965, -0.16464208, 0.053869866, -0.0066738073, -0.26015645, 0.25578022, -0.12132279, 0.15647876, 0.0766546, -0.08933414, 0.09379291, 0.06804614) * g_7;
    result += mat4(0.14762619, 0.052262735, 0.06740719, -0.029300386, -0.19549088, -0.21684435, -0.085099526, -0.055771094, 0.010171737, -0.14868538, 0.115141615, -0.051683053, -0.044367358, -0.18520084, -0.06393748, 0.0010731925) * g_8;
    result += mat4(-0.14650695, 0.08601589, 0.12697595, 0.13276917, 0.108520165, 0.1912617, 0.019971784, 0.14559254, -0.028546251, 0.08042131, -0.09087924, -0.02770981, 0.15391286, 0.05714011, 0.04471975, 0.037705023) * g_9;
    result += mat4(-0.12902713, 0.28093, -0.29668728, -0.09586236, 0.11485171, -0.06694571, 0.16276729, -0.2492834, 0.022340612, 0.09901862, -0.172989, 0.16625328, -0.10677142, -0.19990413, 0.16999872, 0.31516576) * g_10;
    result += mat4(0.05200403, -0.17484799, -0.09285037, 0.22709143, 0.14310056, 0.20167555, 0.07357741, 0.04894263, -0.18580721, 0.0037048862, 0.07984998, 0.109460205, -0.1658866, 0.0067397184, 0.10205478, -0.30009425) * g_11;
    result += mat4(0.01906955, -0.01307976, -0.054768458, 0.10404966, 0.023302928, 0.1506304, -0.24312226, 0.09407256, 0.14547575, -0.09326737, 0.05963468, -0.17096291, -0.03973353, -0.012859634, -0.011132303, -0.23727575) * g_12;
    result += mat4(0.018458707, -0.08093601, -0.084748484, -0.032792903, 0.023445344, 0.0038735385, -0.047041256, 0.031227939, 0.016863292, 0.022734966, 0.000798652, 0.20134626, 0.10911789, -0.2571384, 0.12569575, 0.12899989) * g_13;
    result += mat4(-0.02005358, -0.13560984, 0.16960412, 0.07813574, 0.14358784, 0.114273846, -0.06344754, -0.022004206, 0.048542615, -0.21317734, 0.06406535, -0.116627425, -0.016013943, -0.080993414, 0.15286861, -0.0021789172) * g_14;
    result += mat4(-0.051536534, 0.085252315, -0.12893482, 0.19260244, -0.087101154, -0.08621803, -0.0064267796, -0.013781654, -0.0952192, 0.11305202, -0.23815015, -0.033821765, -0.059584074, 0.1069189, -0.21070237, -0.034997597) * g_15;
    result += mat4(0.08561619, 0.0930155, 0.33753118, -0.031700823, 0.09551905, 0.080744945, 0.011288477, 0.061302166, 0.056226872, -0.10404533, -0.055435713, 0.004116961, -0.14561117, 0.17033315, 0.12503803, -0.07372825) * g_16;
    result += mat4(-0.09182204, -0.09104942, 0.041599516, 0.16590819, 0.00983582, 0.10518859, -0.113934346, -0.104463175, -0.00079954404, 0.034999546, 0.13909996, 0.0493524, 0.19881092, -0.096706204, 0.14631568, -0.008105569) * g_17;
    result += mat4(-0.00929841, 0.03932664, -0.054535374, 0.07319642, -0.09397188, 0.078899324, 0.1951339, -0.07413376, -0.0461229, -0.09307032, -0.039535936, 0.1277176, -0.1613869, 0.06263851, -0.19089746, 0.07733326) * g_18;
    result += mat4(-0.116017684, 0.17785975, -0.08255256, -0.017906634, 0.079656884, 0.1062068, -0.07560774, 0.05632323, 0.06347149, -0.0038651915, 0.18395548, -0.018724794, 0.06897179, -0.017391736, -0.09945868, 0.007462038) * g_19;
    result += mat4(0.09895682, 0.0008542192, 0.040768873, 0.0739274, 0.04401002, -0.17797345, 0.108511046, -0.1596793, -0.3202953, 0.25767303, 0.114281945, 0.10362787, -0.010467758, -0.040315267, 0.03151773, -0.18630013) * g_20;
    result += mat4(-0.16360605, -0.11041179, 0.08405035, 0.11882953, -0.061490558, -0.06537877, -0.039295603, -0.085139036, 0.13128738, 0.093954295, 0.17564337, 0.0050902218, 0.057772268, 0.03324601, 0.02978617, 0.045452252) * g_21;
    result += mat4(0.009214316, 0.2615397, -0.32527506, 0.0049241674, -0.12779853, -0.009896386, -0.063335165, 0.014920392, -0.012698124, 0.053253584, 0.21158943, 0.047342606, -0.0747987, 0.018429412, -0.09028407, -0.0753332) * g_22;
    result += mat4(-0.21073934, -0.39829832, 0.5173677, -0.016563633, 0.17195706, 0.13737291, 0.0993746, -0.019057626, -0.09700681, -0.05018698, 0.017614022, 0.22466557, -0.08776291, -0.41851798, 0.063330576, 0.15770285) * g_23;
    result += vec4(-0.00083234225, 0.029220644, -0.021711512, -0.010490012);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups3, ivec3(valid_xy, tile.inputLayer), result);
}