// Anime4K_Upscale_GAN_x4_UUL - Pass 54 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_15_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_15_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_15_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_15_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_15_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_15_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_17_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_18_tf5;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_15_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_15_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_15_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_15_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(0.056246072, -0.16367151, 0.09586773, -0.09557277, -0.10967658, 0.29330617, -0.13319509, 0.1583132, -0.03072026, -0.13287482, 0.08872677, 0.01658334, -0.030632658, 0.23216708, -0.04874622, -0.19615364) * g_0;
    result += mat4(0.28258148, 0.23039894, -0.022433521, -0.076286666, -0.013763674, -0.011372233, 0.06338799, -0.14605698, 0.14725849, 0.04564273, -0.29587668, -0.06550259, 0.07033988, 0.056368083, -0.11388523, 0.22788034) * g_1;
    result += mat4(-0.078506514, 0.050773215, -0.05056612, 0.03687288, -0.06774274, 0.346275, 0.22509691, 0.14400601, 0.053844824, -0.032543994, -0.065815195, 0.05659026, 0.30160823, 0.21798158, -0.13396002, -0.070808604) * g_2;
    result += mat4(0.1414282, -0.14827503, 0.1398485, -0.07609034, -0.25334343, 0.14950044, -0.23095194, 0.20794556, 0.13395849, -0.016921503, -0.019526243, 0.03422955, -0.12746096, 0.051038973, 0.30596954, 0.08058667) * g_3;
    result += mat4(-0.16881044, -0.14647691, 0.005999665, -0.2447768, 0.01649153, 0.062070012, -0.046544943, -0.17421006, -0.1569363, -0.13780028, 0.06486153, 0.083640814, 0.10214361, 0.33934087, -0.10050735, 0.101777904) * g_4;
    result += mat4(0.290694, -0.21645689, 0.051882863, -0.17417477, 0.10914349, 0.08146335, -0.098452374, -0.19601184, 0.12863407, 0.1486865, -0.081353866, 0.041731454, -0.22860748, -0.2768738, 0.22779721, 0.17970768) * g_5;
    result += mat4(-0.010292755, 0.30307126, 0.070744984, 0.018192705, 0.059022196, -0.2962268, 0.32906732, -0.32876432, -0.21463345, 0.31662, -0.16954084, -0.117625155, -0.10809974, -0.23279764, 0.15617515, -0.12067889) * g_6;
    result += mat4(-0.09392243, -0.09030095, -0.0074743694, 0.18182948, 0.066194676, -0.06895621, -0.083494544, -0.11739724, -0.025220301, -0.07014885, 0.08474903, -0.15182392, 0.3104019, 0.1361944, -0.07185112, -0.30538258) * g_7;
    result += mat4(-0.04256853, -0.27519822, 0.4612011, 0.024868855, -0.017590877, 0.029131817, -0.032747604, -0.046608966, 0.047107942, -0.06539844, -0.1362288, 0.016851274, -0.19554174, -0.09681737, -0.09754212, -0.10524043) * g_8;
    result += mat4(-0.08256224, -0.061173473, -0.0003020941, 0.1565923, -0.003615149, 0.1686191, 0.25915742, -0.1551164, 0.010245293, 0.09092833, 0.0010728717, 0.12982604, -0.13078149, -0.079463206, -0.25684637, 0.022832563) * g_9;
    result += mat4(0.20522995, 0.088086136, 0.14705934, 0.1724673, 0.21438526, 0.069160245, 0.06703898, 0.06735102, 0.2414119, 0.23313762, -0.14652516, -0.2308932, 0.11138083, -0.35780203, 0.18798493, 0.079498045) * g_10;
    result += mat4(-0.053529646, 0.05224867, -0.021422606, 0.10177944, 0.2462833, 0.22917953, 0.09228497, -0.017690439, -0.0007594463, 0.08885728, 0.06285097, -0.006133101, 0.35480046, 0.094339065, 0.0025798874, -0.03436115) * g_11;
    result += mat4(0.29142246, -0.20571099, 0.039097242, 0.16419578, 0.33381957, 0.059117097, 0.3232492, 0.3207798, -0.17321022, 0.28149655, -0.37212068, -0.091761135, -0.29647976, -0.09786893, -0.012315099, -0.098530225) * g_12;
    result += mat4(-0.08517171, 0.29922923, -0.3016026, 0.18986404, -0.4725503, 0.21458124, -0.019785719, -0.22997737, -0.1803405, -0.3505279, 0.1441317, 0.123748966, 0.16901205, 0.0853246, 0.056168083, -0.12500733) * g_13;
    result += mat4(-0.05538139, 0.32405415, -0.07422156, 0.11243641, -0.12328553, 0.19872831, 0.11609064, 0.044187672, -0.03900837, 0.14938031, -0.26779997, -0.014325914, 0.08516605, 0.15472183, -0.008160691, -0.1546734) * g_14;
    result += mat4(0.10224539, 0.05463571, -0.10349991, -0.13967137, 0.013825501, -0.19771369, 0.022759158, -0.02061224, -0.14596504, -0.1389487, -0.023805464, 0.3357339, 0.053674806, -0.29536068, -0.030129524, -0.23420021) * g_15;
    result += mat4(0.00525935, -0.06187332, -0.21343656, 0.08685601, 0.1973513, 0.023780117, 0.10964963, 0.29554302, 0.23034461, -0.1638336, 0.052997477, -0.09746816, 0.3240945, 0.40397635, 0.14546403, 0.23516071) * g_16;
    result += mat4(0.12398506, 0.071972124, -0.041258276, 0.039724182, 0.2652426, 0.27666694, 0.23635465, -0.019449247, -0.1527029, -0.22316225, 0.10210884, -0.07005887, -0.30646923, 0.041887626, -0.009516569, 0.036413055) * g_17;
    result += mat4(0.028276786, 0.16043751, -0.2239881, -0.37586385, 0.31563812, -0.026203927, -0.19180797, 0.10412318, 0.26220286, 0.12667432, 0.23287152, -0.13779306, -0.08798421, -0.08690371, -0.13741593, 0.17836761) * g_18;
    result += mat4(0.287815, 0.14447291, -0.045042984, 0.29542264, 0.058183044, -0.23302315, 0.21404788, 0.02194636, -0.07718152, 0.013391173, 0.095230855, 0.057383515, 0.034200735, -0.02018772, -0.009704874, 0.022752954) * g_19;
    result += mat4(-0.21204911, -0.014358223, -0.04669444, 0.07340455, -0.34677908, 0.06096447, 0.07148003, -0.068913, -0.007976721, 0.23779279, -0.13419056, -0.19720857, -0.33705205, 0.044584982, -0.08765776, 0.19233592) * g_20;
    result += mat4(-0.1133937, 0.17952245, -0.21029858, 0.18934067, 0.09819281, 0.096423194, -0.11639172, -0.018819679, 0.010464611, -0.093951285, -0.014759534, 0.020049462, 0.18295068, 0.19702181, 0.020996286, 0.14536497) * g_21;
    result += mat4(-0.3783169, 0.33286926, -0.19929482, 0.15028305, 0.065908626, 0.041621454, -0.18216579, 0.043525103, 0.17919035, -0.12875584, 0.065998, -0.21985063, 0.13770798, -0.115711726, -0.088645585, 0.13645406) * g_22;
    result += mat4(0.1653456, -0.2774588, -0.012783554, 0.29001617, -0.2319765, -0.05957548, 0.13937134, 0.09561029, -0.18725371, 0.19096635, 0.23249848, -0.19607106, 0.11286404, -0.30301368, 0.00872854, -0.11348953) * g_23;
    result += mat4(0.2649749, -0.110655166, -0.014622274, -0.012837707, -0.25394395, -0.116608076, -0.13025038, 0.24080041, -0.29346582, -0.27480447, -0.14941107, 0.22009355, -0.028492803, -0.55209374, 0.09375013, -0.07632931) * g_24;
    result += mat4(-0.2204565, -0.20641033, -0.16525632, -0.024253568, 0.22351857, 0.014136642, 0.096259035, 0.011398014, -0.0904076, 0.3691236, 0.34148008, -0.18941431, -0.06418756, 0.16660745, -0.0032392892, 0.18603528) * g_25;
    result += vec4(0.107388094, -0.010368161, -0.030843422, -0.045815416);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf5, ivec3(valid_xy, tile.inputLayer), result);
}