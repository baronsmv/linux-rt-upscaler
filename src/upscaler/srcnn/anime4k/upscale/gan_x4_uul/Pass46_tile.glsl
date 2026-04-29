// Anime4K_Upscale_GAN_x4_UUL - Pass 46 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_15_tf5;
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
vec4 result = mat4(-0.1563384, -4.2348038e-05, 0.21088852, -0.10074043, -0.2737169, 0.19910938, -0.06523852, 0.08260719, 0.06681506, 0.08398279, 0.08112851, -0.06271677, 0.19443683, 0.3140938, 0.06358846, -0.24377517) * g_0;
    result += mat4(-0.07703153, -0.0842186, 0.01512419, 0.091211595, -0.11350783, 0.08426691, -0.028900454, 0.11823197, 0.04875585, 0.03750477, 0.19681686, -0.04269959, 0.036398802, 0.047569744, 0.12544703, -0.026172163) * g_1;
    result += mat4(0.29032633, 0.050980248, 0.058194604, -0.019475559, 0.17345822, -0.24062975, -0.21322982, 0.42244488, 0.06804174, -0.18426242, -0.10372379, -0.07140781, 0.18495008, -0.34838748, 0.12188065, -0.19211207) * g_2;
    result += mat4(-0.29782, 0.13921519, -0.08461761, -0.107774965, 0.08354831, 0.118166685, 0.1622595, 0.03740301, 0.08480873, 0.078856945, -0.037666395, 0.08779327, -0.041599847, -0.08245203, 0.1429502, 0.08010295) * g_3;
    result += mat4(0.1605823, 0.00014730562, 0.016887885, -0.040745202, 0.17265643, 0.29641476, -0.12986568, -0.05113458, 0.076540425, 0.15484014, -0.23496233, 0.19515266, -0.028631026, -0.038202707, -0.080664515, 0.12057771) * g_4;
    result += mat4(0.11460453, -0.050684724, 0.20615812, 0.01643888, -0.10416711, 0.100582175, 0.035920016, -0.025840579, 0.1103276, 0.2833988, 0.024743505, -0.10666319, 0.17747831, 0.21371357, 0.032975666, -0.04190704) * g_5;
    result += mat4(0.011197512, 0.16411427, -0.19208677, -0.17151442, 0.16737005, 0.027391635, -0.026951822, -0.016613541, 0.0032831782, -0.059412222, -0.066838935, -0.10225273, 0.0021287128, 0.023737555, 0.13474901, -0.04558329) * g_6;
    result += mat4(-0.19312629, -0.01058644, -0.21747608, -0.1474776, 0.042395744, -0.17641127, -0.16623084, 0.09171901, -0.21876743, 0.22580327, -0.084752835, -0.25452504, 0.07984656, -0.4423898, -0.22987825, -0.08352869) * g_7;
    result += mat4(0.0069102994, -0.110352114, -0.07521295, 0.099378504, 0.001659902, -0.0038716302, 0.037715383, -0.11712855, 0.12579428, 0.0017785282, -0.22036885, -0.019738209, -0.0034085102, 0.26078427, -0.12166613, 0.2008257) * g_8;
    result += mat4(-0.038544666, -0.07219808, 0.028675534, 0.099281736, -0.23815387, 0.03485132, 0.046542224, -0.3781598, 0.19114049, -0.08161937, 0.06317728, 0.20634823, 0.0802016, -0.1216539, 0.25130817, -0.13255747) * g_9;
    result += mat4(-0.05713687, -0.019339267, 0.066463225, 0.11161798, -0.21163659, 0.075951084, -0.029443193, -0.25528103, -0.2308967, -0.15222046, 0.04718688, 0.06978249, 0.12882593, -0.5987798, -0.12197535, 0.030687023) * g_10;
    result += mat4(-0.13764851, 0.15330292, 0.16018312, -0.49503544, -0.16520153, 0.13832116, -0.024153056, 0.027324235, -0.09427501, -0.040549293, -0.024912398, 0.08060826, 0.09142337, 0.00488734, -0.15568374, -0.0985281) * g_11;
    result += mat4(-0.10500595, 0.20050812, -0.01487173, 0.15295555, -0.04712123, 0.051116835, -0.302946, 0.12568721, -0.1681454, -0.07675961, -0.3161021, -0.12655284, -0.3167647, 0.09684754, -0.16133003, 0.15951052) * g_12;
    result += mat4(0.15607205, -0.25850067, 0.11871884, -0.31882218, 0.17650777, -0.019189376, 0.1073271, 0.0034152938, 0.10415428, 0.0054145185, 0.16176777, -0.10523716, 0.07847772, 0.040496692, 0.22647256, 0.04398088) * g_13;
    result += mat4(0.24400397, -0.0384044, -0.21188568, 0.27411124, 0.14313321, 0.072909415, 0.18460783, 0.14612274, 0.2838993, 0.140949, -0.21245211, 0.27844483, 0.14368927, 0.016486926, 0.1082019, -0.060620487) * g_14;
    result += mat4(-0.14134651, -7.1389e-05, -0.19200438, -0.053445943, -0.103280954, -0.20622449, 0.029827105, -0.2797714, 0.1552006, -0.26046538, -0.13706698, 0.083868355, -0.25775772, -0.20121866, -0.03605909, -0.069998674) * g_15;
    result += mat4(0.058855478, -0.1532865, 0.03206366, -0.005691445, -0.38566765, -0.16169494, 0.02574184, -0.054270905, -0.12126733, -0.057428207, 0.18522896, -0.16544363, -0.26917803, -0.12187415, 0.17564186, -0.14418602) * g_16;
    result += mat4(-0.05512333, 0.037456047, -0.04533679, 0.12092291, -0.19412133, -0.10732244, -0.26686874, 0.379613, 0.06616941, 0.21898451, -0.01444954, 0.12263187, -0.066122636, -0.0626703, -0.11018273, 0.16922808) * g_17;
    result += mat4(0.12281162, -0.00843568, -0.11958423, 0.03653139, 0.089102715, 0.07257941, -0.16025232, 0.012180051, -0.15409741, -0.11771615, -0.02216731, -0.1854874, -0.0236496, -0.055969007, -0.21524337, -0.13740915) * g_18;
    result += mat4(0.030042715, -0.06231122, -0.18729754, 0.21269098, -0.16715202, -0.29836708, 0.07573045, 0.13103722, 0.028832506, -0.027299328, -0.0870532, -0.025646947, -0.19446446, 0.0058135786, -0.1405455, 0.07491713) * g_19;
    result += mat4(-0.07880487, -0.13220546, 0.06522037, 0.121417455, 0.009829517, 0.06654325, 0.2568132, -0.20259766, 0.0007492223, -0.08141206, -0.24408619, 0.0041711377, 0.17885362, -0.018794749, -0.18738106, -0.20076036) * g_20;
    result += mat4(0.43662158, -0.073237136, 0.06410434, 0.0768924, -0.22872317, -0.07136076, 0.08949116, -0.020143397, 0.000121645106, -0.11288245, 0.33393764, 0.16950496, -0.11639818, 0.13381785, 0.023384197, 0.16942506) * g_21;
    result += mat4(0.020018844, -0.18646887, -0.0069234655, 0.09404709, 0.1482564, 0.039720826, -0.15250199, -0.010954307, -0.10006045, 0.024348486, 0.15170497, -0.19681026, -0.17672434, -0.040419213, -0.26169667, -0.20060538) * g_22;
    result += mat4(-0.15089865, -0.09773179, 0.13388306, -0.2330703, 0.20980428, 0.05050314, 0.26115113, 0.11146053, -0.10908558, 0.29291332, 0.08921834, -0.059216894, 0.14480549, 0.10386442, 0.28325698, -0.02240901) * g_23;
    result += vec4(0.009868551, -0.021667233, 0.06688179, -0.050735172);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf5, ivec3(valid_xy, tile.inputLayer), result);
}