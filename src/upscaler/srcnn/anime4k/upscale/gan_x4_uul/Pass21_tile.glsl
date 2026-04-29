// Anime4K_Upscale_GAN_x4_UUL - Pass 21 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf4;
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
vec4 result = mat4(-0.21972683, 0.075138226, 0.10989088, 0.15510671, -0.1459443, -0.0016620584, 0.061098658, 0.31031737, 0.066652276, -0.028504146, -0.2547878, 0.05934589, -0.097173244, -0.02434052, 0.00775221, -0.1422285) * g_0;
    result += mat4(0.107364714, -0.04124382, 0.15790261, -0.06481956, 0.17907274, -0.060845222, 0.12766309, -0.00051298866, -0.102316536, -0.15852973, -0.08159873, -0.044251855, 0.27320522, -0.058971684, 0.10957703, 0.11716146) * g_1;
    result += mat4(-0.013670836, 0.24698958, -0.22751978, -0.0073335706, 0.056770742, -0.030483782, 0.02582211, 0.08631351, 0.037981253, -0.19984269, -0.0027441583, -0.0624548, -0.0073825894, 0.19920917, 0.025273615, 0.08608597) * g_2;
    result += mat4(-0.0662924, -0.07036538, 0.18532504, -0.2299518, -0.17168434, 0.10680291, -0.32843417, 0.18283479, -0.014981234, -0.3074193, 0.25829783, 0.13314934, -0.29796004, -0.24784647, 0.107523575, -0.06354826) * g_3;
    result += mat4(-0.27304897, 0.021216365, 0.19145995, -0.08837303, 0.002489904, -0.14517735, -0.11758484, 0.017706083, 0.11964576, 0.07262963, -0.02875841, 0.058490552, 0.36016595, -0.17619327, -0.14238013, -0.06569956) * g_4;
    result += mat4(-0.17569791, 0.018018663, -0.06937724, -0.19693184, 0.005096431, 0.24887225, -0.26054552, -0.08146536, 0.31367835, 0.3301311, 0.32667178, 0.28089377, 0.1244409, -0.031515893, 0.036075663, 0.19611663) * g_5;
    result += mat4(0.17254318, 0.2789707, -0.023289531, 0.0384691, 0.056068007, -0.21530272, -0.12280407, -0.27022615, 0.0869075, -0.005402115, 0.31068063, -0.28706273, -0.055334765, 0.08997763, 0.16977838, -0.050881755) * g_6;
    result += mat4(0.038418837, -0.016408218, 0.08852962, -0.014304706, -0.12245269, 0.32564455, 0.008428901, -0.12942936, 0.014469481, 0.19589558, 0.05143627, 0.015018481, -0.18424125, 0.31541458, 0.15289177, -0.015950657) * g_7;
    result += mat4(-0.24448341, -0.12913765, 0.14086853, 0.23801136, 0.053969346, -0.00888275, -0.16412334, 0.12726937, -0.16968949, 0.23890501, 0.00017258813, -0.009174681, 0.16712539, -0.24415763, 0.15660262, -0.065232545) * g_8;
    result += mat4(-0.050856017, 0.202047, -0.18741634, -0.046839286, 0.10381434, -0.18508428, 0.2024435, -0.058891546, -0.06494971, -0.13396326, -0.0043475446, 0.080295786, -0.03888818, 0.20266065, -0.11657034, -0.044489022) * g_9;
    result += mat4(-0.072022684, 0.03736022, -0.18028143, 0.084992565, 0.071270995, 0.17529677, 0.21173926, -0.04662527, -0.114107236, -0.0499027, -0.023457017, -0.14902714, -0.16848294, 0.29582912, -0.031783022, -0.21024497) * g_10;
    result += mat4(0.12895544, 0.031505328, 0.07695562, 0.345239, -0.23573573, -0.35058022, 0.16588537, -0.37892917, -0.25666252, 0.04829329, 0.015923034, -0.06639003, -0.19299003, 0.19805184, 0.062723555, -0.16471659) * g_11;
    result += mat4(-0.0048171217, -0.3616856, 0.10861591, -0.112293005, 0.22894251, 0.007305623, -0.15964155, -0.11533153, -0.04575267, -0.054644916, 0.102498904, -0.10909718, 0.06384877, 0.03547178, 0.036990482, 0.11729651) * g_12;
    result += mat4(0.12198726, 0.049392004, 0.030775595, -0.0439167, 0.05127687, 0.006836142, 0.25043175, 0.41561976, 0.18109778, 0.036204416, -0.18115522, -0.11104906, -0.13888827, -0.030574424, -0.15439117, -0.023217283) * g_13;
    result += mat4(0.037748005, 0.115257904, 0.0013052573, -0.08927453, 0.15113032, 0.0036705493, -0.036586095, 0.082375705, -0.14908089, 0.19808415, 0.10144146, -0.13911691, 0.18034998, -0.09426868, -0.28695896, -0.07120951) * g_14;
    result += mat4(-0.15097517, -0.23736724, -0.011011207, 0.15136749, -0.1099934, -0.054979928, 0.19652224, 0.18154691, -0.104135856, 0.14703101, 0.10374482, -0.14010042, -0.08321475, -0.15499261, 0.12135948, -0.09310376) * g_15;
    result += mat4(0.1298599, 0.09743068, -0.13728131, 0.15002461, 0.16739184, 0.1680788, -0.13828343, -0.0080054095, 0.10013758, -0.123607814, 0.045337323, -0.09940934, -0.13998291, -0.012435486, -0.2050455, 0.40441212) * g_16;
    result += mat4(-0.4145493, -0.041918173, -0.029234748, -0.04663795, 0.068999134, -0.13911937, -0.10113266, -0.004217848, 0.049335115, 0.26279005, -0.1096574, -0.009956439, -0.18413721, 0.25698513, 0.03403163, 0.050992493) * g_17;
    result += vec4(-0.03271656, -0.03322799, 0.033719946, -0.039838646);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf4, ivec3(valid_xy, tile.inputLayer), result);
}