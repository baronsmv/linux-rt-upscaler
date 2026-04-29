// Anime4K_Upscale_GAN_x4_UUL - Pass 68 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_24_tf3;
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
vec4 result = mat4(-0.011141579, 0.09674723, -0.13645004, -0.10970149, -0.04369547, 0.08311355, 0.021767681, -0.08375845, 0.022200847, 0.05360177, 0.16593163, -0.15328388, 0.08149341, -0.09137854, -0.040580057, 0.08350056) * g_0;
    result += mat4(-0.0026481631, -0.004045956, 0.012659179, 0.09567999, -0.04221551, 0.10712957, -0.056656756, -0.27661186, -0.053574864, -0.089751564, -0.17745095, 0.16676143, 0.34287563, -0.13643502, 0.33259082, 0.27071705) * g_1;
    result += mat4(0.18119478, -0.11287872, 0.24201767, -0.009600413, 0.048217695, 0.062931724, -0.06455807, 0.0013528515, 0.1764802, -0.08022894, 0.01977552, 0.014862132, -0.119611226, 0.06065237, -0.2003538, 0.057908155) * g_2;
    result += mat4(0.10390714, 0.03061146, 0.07345203, 0.020925567, -0.03771494, -0.055771235, -0.10182023, -0.0453298, 0.030018989, 0.020321988, -0.13780262, -0.10419699, -0.1531079, 0.08695891, -0.10523552, 0.0031262166) * g_3;
    result += mat4(0.013357037, 0.11706443, 0.02651922, 0.12551948, -0.03562916, 0.07041351, -0.22412951, 0.19341606, -0.06120095, 0.1594309, -0.25910634, 0.03911061, -0.030200286, 0.039532397, -0.04693854, 0.107756086) * g_4;
    result += mat4(0.26856127, -0.062083863, 0.26156938, -0.06557537, -0.06786968, 0.061135814, -0.18566874, -0.11154961, 0.06399305, 0.068129785, -0.0010524218, 0.039409623, 0.0527229, 0.16223872, 0.11896118, 0.13470948) * g_5;
    result += mat4(-0.09019031, -0.11750688, 0.08919765, 0.06305572, -0.110997446, -0.09387827, -0.024580022, -0.1923812, -0.011291289, -0.06320932, 0.15289676, -0.14364418, 0.041966986, 0.25329712, -0.19619554, 0.035929594) * g_6;
    result += mat4(-0.06743388, -0.08509898, -0.07433386, -0.025805349, 0.01812382, -0.02492702, -0.2482932, 0.28510815, 0.119341426, 0.2147701, 0.06835619, -0.07081952, -0.038794495, 0.10975482, -0.2239901, -0.124213785) * g_7;
    result += mat4(-0.026220966, 0.14319815, -0.1700538, -0.0335693, 0.07769912, 0.12722708, -0.26494396, -0.10431099, -0.08059116, 0.12723474, -0.15197968, 0.0060984325, -0.013070423, -0.25334156, 0.2920123, 0.110061795) * g_8;
    result += mat4(-0.25060546, 0.057933453, 0.041256662, -0.11589921, 0.3209416, 0.12978804, -0.017460592, 0.19088507, 0.08740428, 0.038495142, 0.26864913, -0.08148351, 0.05588537, -0.027696, 0.47028908, -0.08718974) * g_9;
    result += mat4(-0.028379083, -0.16510524, -0.0720884, 0.024243379, 0.030889094, -0.09380263, 0.10451546, -0.21832433, 0.20901899, -0.055639133, -0.051839713, 0.033683445, -0.029481068, 0.048284974, -0.08840896, 0.17702715) * g_10;
    result += mat4(-0.13655269, -0.009485257, -0.27257246, -0.027732212, 0.11677922, -0.08578314, 0.1272782, -0.033684663, -0.070519574, 0.01601166, 0.11166362, -0.2742834, 0.17340335, -0.19997278, -0.040465057, -0.2970155) * g_11;
    result += mat4(-0.20593609, 0.07950713, 0.05642528, 0.19129497, 0.3180778, -0.07194427, -0.19385284, -0.09050803, 0.23494293, 0.02127147, -0.014160815, 0.16873649, -0.045696944, -0.025910616, 0.10135493, -0.07330387) * g_12;
    result += mat4(0.11845643, -0.06579577, -0.10600301, 0.12729774, -0.30510858, 0.0974965, 0.114875704, 0.06391382, 0.14807853, 0.22989006, -0.072495855, 0.1800837, 0.028062822, 0.044472497, 0.27929953, -0.037439365) * g_13;
    result += mat4(-0.29070517, 0.2584094, -0.12230044, 0.29064023, -0.23902515, 0.29584745, 0.20774792, 0.41733524, 0.06608569, -0.04484478, 0.15128273, -0.3068231, 0.22654179, -0.080022156, -0.48213294, -0.037669115) * g_14;
    result += mat4(0.17929457, -0.073897004, 0.033858683, -0.24681814, 0.38705662, -0.31330046, -0.3057931, -0.30628645, 0.06434401, -0.040364057, -0.30331135, 0.09151124, -0.15681383, 0.29307282, 0.28045842, -0.06732098) * g_15;
    result += mat4(0.024120888, 0.06291463, -0.39767843, -0.199806, -0.18294619, 0.44507617, -0.20719141, 0.022910457, -0.04779181, 0.07508541, 0.12258552, 0.019429758, -0.10943762, -0.20337181, 0.072106324, -0.18230085) * g_16;
    result += mat4(-0.010640077, -0.15392596, 0.042594627, -0.0009270454, 0.3621191, -0.28109482, 0.080440365, -0.2073678, 0.052669737, 0.01759761, -0.0909907, -0.0051524066, 0.025632787, 0.15993036, -0.04525641, 0.05836689) * g_17;
    result += mat4(0.20725772, 0.05976848, 0.15562478, -0.22970834, -0.006273422, -0.0024398018, -0.15024984, -0.06983079, 0.037917525, -0.06959094, -0.30672732, 0.11463107, -0.103878215, 0.16795799, 0.123742215, -0.076316774) * g_18;
    result += mat4(-0.041884482, -0.048946526, -0.040261485, 0.145805, 0.18649343, -0.0044576614, -0.2316234, 0.08005378, 0.13540603, -0.13486005, -0.048867103, -0.039551396, 0.015187719, -0.113004565, -0.09270747, 0.053628337) * g_19;
    result += mat4(0.026232086, -0.05916773, 0.09088294, 0.059865057, -0.08295995, 0.04218031, 0.0016741708, 0.08783662, 0.12226684, -0.0601888, 0.14152455, -0.15758237, -0.118071996, -0.053882107, 0.22713134, -0.08549201) * g_20;
    result += mat4(0.030266033, 0.08861499, 0.04543061, -0.09845329, 0.29042727, -0.1387298, -0.27544942, 0.06959186, -0.06818984, -0.07793028, -0.26279172, 0.051999256, 0.13853306, -0.028943995, -0.1616878, 0.0055545145) * g_21;
    result += mat4(0.06571001, -0.15409341, -0.10983791, -0.10024373, 0.06786836, -0.034203686, 0.06702562, -0.13785091, 0.014078426, -0.118333764, 0.10679032, -0.11793583, -0.17936374, 0.08035579, -0.065410405, 0.012682481) * g_22;
    result += mat4(-0.08627442, 0.09910777, 0.06451081, -0.032909464, 0.016304161, 0.11485424, 0.075068, 0.17560685, -0.21859545, 0.03553843, -0.029545823, 0.0020583326, -0.09749895, 0.10549555, -0.13807511, 0.04073702) * g_23;
    result += mat4(0.013445668, -0.106096625, -0.14386144, -0.047453087, 0.030295242, -0.07128061, 0.18820919, -0.14116964, -0.08358127, 0.017694646, -0.22504877, -0.0870977, 0.159292, 0.1511803, 0.13363734, 0.059592243) * g_24;
    result += mat4(0.09585648, 0.13820451, -0.025589576, 0.14250357, -0.098605, -0.033331417, -0.26585752, 0.046970017, 0.0064765653, 0.15291844, 0.2051226, -0.033412863, -0.15486592, -0.10399778, -0.11634391, 0.00032476272) * g_25;
    result += mat4(0.09576212, -0.052482244, -0.11748363, -0.022807717, 0.18996853, -0.119998, -0.11650178, 0.15346055, -0.056865185, 0.17039599, 0.019453784, -0.15516305, -0.07541472, 0.05255179, -0.18442616, 0.13752738) * g_26;
    result += mat4(0.08866666, -0.037314344, -0.08462723, 0.01123993, -0.048002165, 0.08966719, -0.008348263, 0.022855654, -0.13039067, -0.026170973, 0.22115219, 0.061224397, 0.16689171, 0.06845198, -0.08873581, -0.050191987) * g_27;
    result += mat4(-0.08112671, -0.1593253, 0.19252764, 0.060990997, 0.29255992, 0.2258008, 0.05192984, -0.22563158, -0.005943522, 0.092420675, 0.12934043, 0.1422232, 0.0047882204, 0.034547567, -0.03979875, -0.13211358) * g_28;
    result += mat4(0.19852357, -0.09415307, 0.18439335, 0.09917704, -0.0036918402, -0.11341272, 0.14594431, 0.036229003, -0.3779797, -0.1963225, -0.05158393, -0.286296, 0.09826625, -0.11089739, 0.08578653, 0.032530606) * g_29;
    result += vec4(0.044129565, -0.091767386, -0.075459845, 0.066399455);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_24_tf3, ivec3(valid_xy, tile.inputLayer), result);
}