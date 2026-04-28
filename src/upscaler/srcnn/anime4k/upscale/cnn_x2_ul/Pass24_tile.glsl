// Anime4K_Upscale_CNN_x2_UL - Pass 24 of 25 - https://github.com/bloc97/Anime4K
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
//    glslc -fshader-stage=compute --target-env=vulkan1.2 \
//          <this_file> -o <output.spv>
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
//        uint  inputLayer;      // array slice to read (0-based)
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  margin;          // context margin (pixels in feature-map space)
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(push_constant) uniform TileParams {
    uint inputLayer;
    uvec2 dstOffset;
    uint fullOutWidth;
    uint fullOutHeight;
    uint margin;
    uvec2 tileOutExtent;
} tile;

layout(set = 0, binding = 3) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 4) uniform texture2DArray tex_conv2d_2_tf1;
layout(set = 0, binding = 5) uniform texture2DArray tex_conv2d_2_tf2;
layout(set = 0, binding = 6) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 7) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 8) uniform texture2DArray tex_conv2d_3_tf2;
layout(set = 0, binding = 9) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 10) uniform texture2DArray tex_conv2d_4_tf1;
layout(set = 0, binding = 11) uniform texture2DArray tex_conv2d_4_tf2;
layout(set = 0, binding = 12) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 13) uniform texture2DArray tex_conv2d_5_tf1;
layout(set = 0, binding = 14) uniform texture2DArray tex_conv2d_5_tf2;
layout(set = 0, binding = 15) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 16) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 17) uniform texture2DArray tex_conv2d_6_tf2;
layout(set = 0, binding = 18, rgba8) uniform image2DArray img_conv2d_last_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_2_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_2_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max((texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_4_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max(-(texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max((texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_5_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max(-(texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_5_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_24 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_25 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_26 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_28 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_29 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.20584391, 0.22176251, 0.12817344, 0.16349226, 0.24339934, 0.17479841, 0.23518398, 0.19196586, 0.10900553, 0.080384456, 0.049235467, 0.027794728, -0.05141681, 0.0007015638, -0.010815038, 0.0042753317) * g_0;
    result += mat4(0.0714463, 0.026722606, -0.01580307, -0.036710627, 0.13722661, 0.1325067, 0.12155393, 0.092651665, -0.21974826, -0.22233371, -0.16056158, -0.16607761, -0.10291634, -0.19475317, -0.117747545, -0.18824245) * g_1;
    result += mat4(0.0385657, 0.12090414, 0.09484494, 0.18811698, 0.015320313, 0.0051719607, -0.016927784, -0.03450855, -0.06506198, 0.05625437, -0.02982918, 0.06270707, -0.13614634, -0.16412087, -0.1319045, -0.1733402) * g_2;
    result += mat4(-0.2033194, -0.2067332, -0.16234529, -0.13661149, -0.22975448, -0.1841141, -0.26185742, -0.23617432, -0.058616254, -0.11470092, -0.064833924, -0.082624085, 0.0018012474, 0.010971402, -0.0015926235, -0.056720145) * g_3;
    result += mat4(0.012773226, -0.013976976, 0.007706423, -0.022663448, -0.13764867, -0.121803656, -0.12158649, -0.090470046, 0.22548035, 0.22929274, 0.19819829, 0.16713546, 0.15709636, 0.16574621, 0.17671035, 0.18283793) * g_4;
    result += mat4(-0.042175665, -0.07863977, -0.1209475, -0.14067635, 0.0041970555, 0.03598768, 0.009632853, 0.040009186, -0.014479617, -0.060088724, 0.041292075, -0.004627034, 0.09958161, 0.120460846, 0.15672928, 0.18279101) * g_5;
    result += mat4(-0.03370265, -0.07010845, 0.04648067, -0.007877368, -0.11963536, -0.014810524, -0.01556151, 0.11850641, -0.0021221144, -0.050126694, 0.03193186, -0.012815193, -0.019450104, 0.017504638, -0.007544723, 0.0028710878) * g_6;
    result += mat4(-0.018643383, -0.04445287, 0.07541755, 0.043240048, 0.027209729, 0.06499946, -0.018240616, 0.014570308, -0.058010563, 0.019799259, 0.0030194358, 0.06929909, -0.0056114118, 0.009093819, 0.03223382, 0.053046633) * g_7;
    result += mat4(-0.0133113945, 0.019222038, -0.019711712, 0.03676041, -0.040668692, -0.09569124, 0.053240422, 0.02388429, -0.12218938, -0.08086858, -0.043406986, 0.009516919, -0.04289723, 0.056066234, -0.035658766, 0.061961327) * g_8;
    result += mat4(0.023964832, 0.07624368, -0.020873679, 0.0256053, 0.12444348, 0.017517762, 0.0049669463, -0.13534403, 0.0061981925, 0.052108612, -0.02908856, 0.0135363275, -0.030678025, -0.015180554, -0.003328521, 0.021289025) * g_9;
    result += mat4(-0.02231607, 0.09188703, -0.13311718, -0.009214322, -0.021628553, -0.047853045, 0.014602204, 0.00086198986, 0.06729613, -0.04228859, -0.0030271288, -0.066696614, -0.0071333526, -0.019973027, -0.036203787, -0.056756962) * g_10;
    result += mat4(0.05850421, -0.0047896104, -0.0036014696, -0.05261781, 0.020924669, 0.093680315, -0.061118666, -0.020405825, 0.100053616, 0.061513033, 0.018219335, -0.02082051, 0.039510462, -0.08404035, 0.050883695, -0.052642383) * g_11;
    result += mat4(0.0018722751, 0.020684525, -0.02356179, 0.009360695, 0.0036660347, -0.006931955, -0.015446396, -0.02027952, 0.006836204, 0.00341897, -0.020235445, -0.029695021, -0.0053638928, -0.003108307, 0.016338514, -0.0058539147) * g_12;
    result += mat4(0.021255454, 0.036906153, 0.019704418, -0.009486708, -0.009084271, -0.012694315, 0.012314602, -0.002121502, -0.0047310013, 0.0051953527, 0.005284111, 0.019026738, -0.0082058, 0.0032704875, -0.02295881, 0.009902225) * g_13;
    result += mat4(0.01866446, -0.012482591, 0.011301323, -0.011294572, 0.035305023, -0.002237504, 0.010679519, -0.000508338, 8.54808e-05, -0.02033275, -0.008063064, 0.013109392, 0.0002144853, -0.007573196, 0.015446864, 0.0023629267) * g_14;
    result += mat4(-0.00978586, -0.025148384, 0.024103062, -0.009535831, -0.002879648, 0.0012579657, 0.018271701, 0.02113783, -0.03735869, -0.02581921, 0.005823926, 0.04087479, -0.0077521144, -0.012728182, 0.0067631016, 0.012669306) * g_15;
    result += mat4(0.018013993, 0.026847519, 0.0021338093, -0.010125906, -0.07225123, -0.0025745684, -0.012799456, 0.056836564, 0.011377961, 0.017062144, -0.007494936, 0.010489539, 0.012431433, -0.019703059, 0.007082196, -0.031403106) * g_16;
    result += mat4(-0.027560756, -0.030534893, 0.019047359, -0.0068690516, -0.0069791237, 0.0081298705, 0.0028945836, 0.009644792, 0.023117492, 0.020431874, -0.0056545194, -0.02480413, -0.07047867, -0.037890248, 0.025276575, 0.049277883) * g_17;
    result += mat4(0.015748044, 0.086017504, -0.051286206, -0.003599236, -0.023193073, -0.023733998, 0.002799065, 0.005258185, 0.010922322, -0.17615142, 0.14165695, -0.029909663, -0.017889502, -0.046552524, 0.03964598, 0.049426638) * g_18;
    result += mat4(-0.0073433192, -0.011656557, -0.0068763834, 0.014078096, 0.018000547, -0.053453963, 0.00786442, -0.050999343, 0.04133596, 0.079854034, -0.038685665, -0.053702615, -0.0019746814, -0.07859513, -0.0076702842, -0.067455895) * g_19;
    result += mat4(0.009444058, 0.043747634, 0.018948376, 0.05009854, -0.011580162, -0.0065071583, -0.013997229, -0.011439345, 0.023656886, 0.030394329, 0.02134696, 0.009440647, -0.048070773, 0.007841886, -0.05323206, 0.013742174) * g_20;
    result += mat4(-0.019898156, 0.000818382, 0.0010332671, 0.01928002, 0.013191405, 0.029638033, -0.02320344, 0.007421591, -0.02833562, -0.033782348, -0.04978492, -0.020176657, -0.0138621945, -0.013926801, -0.021230116, -0.058447562) * g_21;
    result += mat4(-0.08644919, 0.073316105, 0.017838318, -0.049475558, -0.007295481, -0.025924034, -0.0068463665, 0.024905838, 0.016891189, 0.041490942, 0.011466327, 0.029829478, 0.034047317, 0.036229853, 0.04733451, 0.062059373) * g_22;
    result += mat4(0.008540078, -0.09782984, 0.037032314, -0.063398704, 0.028395759, 0.12369336, -0.03458798, 0.012534729, -0.02110072, -0.007954169, -0.002136603, -0.019739889, -0.01087704, -0.004243762, -0.019832188, -0.03347458) * g_23;
    result += mat4(0.054272063, 0.053247515, 0.025393743, -0.043571323, 0.05035569, -0.0042993715, -0.08645438, 0.07723826, 0.009475109, -0.026420964, 0.06111581, 0.03551816, -0.040812302, 0.07295332, -0.07636345, 0.059867676) * g_24;
    result += mat4(-0.103165455, 0.07943813, -0.04935193, 0.0776962, 0.0149123045, 0.056066703, 0.028792242, -0.051936194, 0.015754307, 0.004817783, 0.011213326, -0.018288456, 0.004715879, 0.02536934, -0.015915168, -0.0008426239) * g_25;
    result += mat4(0.0723322, 0.054040924, -0.0476729, -0.08399067, 0.024805048, 0.0118207345, 0.022066418, 0.006886721, 0.031156952, -0.07442044, -0.06636254, -0.023382878, -0.051537152, -0.06360144, 0.045075376, 0.050795015) * g_26;
    result += mat4(-0.013090917, -0.0783513, 0.014832963, 0.0033018794, -0.014636453, -0.020164138, 0.043610837, -0.04028102, -0.024922965, 0.017962486, -0.045353472, -0.065985985, -0.020156763, -0.019561546, 0.01627726, -0.0065625296) * g_27;
    result += mat4(0.038890418, -0.007016582, -0.01374995, -0.01861392, -0.03940205, 0.019309007, -0.026372327, 0.0079260105, 0.05348645, -0.087648585, 0.057326347, -0.055338904, -0.07803935, -0.09048593, 0.09173596, 0.05747143) * g_28;
    result += mat4(0.001742558, 0.010703091, -0.021057613, 0.006859906, -0.086059436, 0.008977797, 0.021366948, -0.0043655075, 0.005885378, 0.042646274, 0.028150525, 0.037941158, -0.014817959, -0.016695084, -0.0056764153, 0.019049013) * g_29;
    result += vec4(0.0113136405, -0.0063769994, 0.010973808, -0.011560247);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_last_tf2, ivec3(valid_xy, 0), result);
}