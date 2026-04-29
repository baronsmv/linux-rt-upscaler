// Anime4K_Upscale_GAN_x4_UUL - Pass 22 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_3_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_3_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_3_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_3_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf5;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_3_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_3_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_3_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_3_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_3_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_3_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.3184051, -0.13755248, -0.23732315, -0.023162326, 0.01720298, -0.13192378, 0.016757166, -0.11769522, -0.09113053, 0.045006696, 0.11998161, 0.22151577, -0.09237514, 0.25612727, 0.031724155, 0.03275836) * g_0;
    result += mat4(0.16658157, 0.09904747, 0.12178111, -0.21332578, -0.084959686, 0.25737628, -0.07269974, -0.0044502337, -0.16059934, 0.14796074, -0.2408073, -0.283023, -0.02290089, -0.12150798, 0.122527674, 0.33295074) * g_1;
    result += mat4(-0.13768205, -0.032166574, 0.10757663, -0.19916943, 0.22137393, 0.097398534, -0.028636161, 0.057976738, 0.021234423, 0.16993561, -0.006663144, 0.056026485, -0.17463136, 0.011491455, -0.34180948, -0.052859932) * g_2;
    result += mat4(0.2173205, -0.025248244, -0.24675395, -0.23414998, -0.062658116, 0.18439959, -0.050601244, -0.11459134, -0.22184677, -0.18934494, 0.20033342, -0.028426873, -0.12788561, 0.09256763, 0.04540186, -0.041159313) * g_3;
    result += mat4(-0.0993446, -0.04936769, -0.092339985, -0.36057615, -0.07563136, 0.16411334, 0.18075173, 0.06588899, 0.020508798, 0.06469463, 0.070499524, -0.032993205, 0.02209328, -0.03959476, 0.2591428, -0.31618914) * g_4;
    result += mat4(0.18500368, -0.27579078, 0.15843801, -0.19448781, 0.066866614, 0.00010545493, 0.15846692, 0.15597339, 0.2097692, 0.047041208, -0.16916004, -0.112265535, -0.31957072, -0.039543174, 0.27903298, 0.238342) * g_5;
    result += mat4(-0.24176823, 0.004759584, 0.30377442, -0.28161818, -0.01639163, 0.28049424, 0.15209472, -0.13002338, -0.034997053, 0.14607708, -0.16109394, -0.3709857, 0.06600745, -0.06402065, 0.09106263, -0.08173308) * g_6;
    result += mat4(0.00085082283, -0.1385803, -0.096698835, -0.018731076, -0.13685198, -0.066617444, -0.021327814, 0.047615487, -0.0067158537, -0.305055, -0.030938676, 0.103631414, -0.10505161, 0.1377772, -0.21578938, -0.08955101) * g_7;
    result += mat4(-0.012543417, 0.14635363, -0.34157932, 0.13002996, -0.08412303, -0.035678063, -0.018591393, -0.07879708, 0.052513346, -0.2033995, -0.2095011, 0.09329585, -0.10069142, 0.06845934, 0.34163034, 0.08352417) * g_8;
    result += mat4(-0.22950074, -0.028784348, 0.19254303, -0.08938541, 0.15025762, -0.28843135, 0.032744445, 0.31275362, 0.013827366, -0.0037322342, -0.20390843, 0.18030973, 0.014234129, 0.12213843, -0.021821825, 0.04274312) * g_9;
    result += mat4(0.14702202, 0.14780809, -0.050316352, 0.008637546, -0.018341271, -0.18107755, -0.034195397, -0.016785527, 0.01823875, -0.04468439, 0.11064914, -0.05889276, -0.052540354, 0.072073415, -0.2706125, 0.21487243) * g_10;
    result += mat4(0.5024447, 0.058864042, -0.257565, 0.1780413, -0.065261215, 0.03483217, 0.46696317, -0.055783324, 0.13675097, -0.0388672, 0.22358736, -0.019960344, 0.11402829, 0.040916674, 0.042867694, -0.19926277) * g_11;
    result += mat4(0.00014269089, 0.03286679, -0.024311759, -0.10549739, -0.21425818, 0.06221074, 0.040516183, -0.107838914, 0.14727353, 0.17660016, -0.20832092, -0.23476245, -0.09223368, 0.09435899, -0.06876976, -0.032683436) * g_12;
    result += mat4(-0.061027218, 0.0023568163, 0.03251149, 0.120799825, 0.18775438, -0.022180539, -0.23275055, -0.10154802, -0.078680724, -0.23514764, 0.15737699, 0.1601879, 0.124354616, 0.038517214, 0.14103456, 0.0208124) * g_13;
    result += mat4(0.22970279, 0.021356303, -0.11624362, -0.20197557, -0.12733872, 0.20742093, 0.35425633, -0.1574453, 0.045965664, -0.23022245, 0.16394545, -0.15241143, 0.24514204, 0.22437558, 0.113987625, -0.0011856258) * g_14;
    result += mat4(-0.35714933, -0.31235123, 0.12664467, 0.15167892, 0.16453564, -0.010062876, -0.0831791, 0.19339912, -0.1188241, -0.056378998, -0.22127298, -0.15548877, -0.24432793, -0.034023006, 0.041227486, -0.2873007) * g_15;
    result += mat4(-0.032629743, -0.27882102, 0.1215572, -0.017597208, 0.116811305, 0.14217746, 0.015951436, -0.5205457, -0.038023748, -0.14943328, -0.15468231, 0.074514836, 0.16636418, -0.062607236, -0.032341167, -0.11533553) * g_16;
    result += mat4(-0.08205011, 0.16940303, 0.18777788, 0.16565365, 0.1837101, 0.18085457, 0.018884834, 0.3717715, 0.083659224, 0.25785285, -0.21427527, -0.057258263, 0.07784925, 0.29109064, 0.23607136, 0.21052702) * g_17;
    result += vec4(-0.04224999, -0.02424048, 0.054364916, -0.013123425);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf5, ivec3(valid_xy, tile.inputLayer), result);
}