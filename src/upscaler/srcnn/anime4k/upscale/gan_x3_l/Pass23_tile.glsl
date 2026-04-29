// Anime4K_Upscale_GAN_x3_L - Pass 23 of 30 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_9_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.06816948, 0.34817252, -0.046539452, 0.0051957658, -0.1393289, -0.123660676, -0.28295487, -0.09683893, -0.3166085, 0.112649016, 0.016630042, 0.12213537, 0.048850413, 0.10865108, 0.36645818, -0.1570077) * g_0;
    result += mat4(0.16992034, 0.15695556, 0.23111318, -0.07952356, 0.008467285, -0.11592582, -0.18852152, 0.11257074, 0.24210866, 0.1062648, -0.101493195, 0.04611632, -0.13289067, -0.07632904, 0.012860103, -0.08678244) * g_1;
    result += mat4(0.19332299, -0.06392618, -0.18013911, 0.23211008, -0.0025107847, 0.4468814, -0.15807462, -0.27148855, 0.24238719, 0.16024797, -0.22240195, 0.2425211, 0.008685379, -0.43995225, 0.28782377, -0.04508348) * g_2;
    result += mat4(-0.038411126, -0.0034189979, -0.10616163, -0.22397435, 0.005768774, 0.13181472, 0.091235116, 0.07068676, 0.08932033, 0.025967117, -0.053367026, -0.22340903, -0.13413511, 0.24192514, -0.011392121, -0.09885669) * g_3;
    result += mat4(-0.13691483, 0.058308467, 0.14866434, 0.005773672, -0.16254735, -0.03150588, 0.16304344, 0.31798756, -0.22399272, 0.033883456, -0.09658691, -0.12437203, -0.117079385, 0.21686973, -0.037619635, -0.085622996) * g_4;
    result += mat4(-0.24666454, -0.06097481, -0.08042751, -0.09151835, -0.09213628, 0.06706758, -0.12596707, 0.05328458, 0.25016794, -0.21868211, 0.22890028, -0.16557315, 0.036212686, 0.13603954, -0.20226133, -0.22868301) * g_5;
    result += mat4(0.022882584, -0.023618432, 0.08065757, 0.33173925, 0.07162631, -0.010860303, 0.15222527, -0.21064946, 0.023574507, 0.06347729, -0.2955436, 0.31633475, -0.3643237, -0.087610714, -0.089636534, 0.13809934) * g_6;
    result += mat4(-0.22458415, -0.01961852, -0.014363966, -0.2820657, -0.20567393, 0.106780864, -0.43547606, 0.3259588, 0.42431846, -0.30789465, -0.053756483, 0.18392731, -0.43784657, 0.23359884, 0.25319567, -0.1464313) * g_7;
    result += mat4(0.06667747, 0.011182004, 0.26176485, -0.15575507, -0.017922953, 0.0014675539, -0.13763407, -0.086996995, -0.00082739035, 0.03939667, -0.09286956, 0.29952076, 0.014103506, 0.10058367, 0.16165632, 0.23478027) * g_8;
    result += mat4(-0.1966405, 0.11404606, -0.12005759, -0.22895505, -0.0848272, 0.021871557, 0.044186037, -0.111861885, -0.16986093, -0.24633476, 0.07282808, -0.26975635, 0.34241816, 0.030470898, -0.09903839, -0.22579415) * g_9;
    result += mat4(0.10059369, 0.010142443, 0.061046213, 0.6807189, 0.005402132, -0.21700516, 0.16900781, -0.09973772, -0.025505878, 0.14216411, 0.14366129, -0.02743741, 0.09240224, 0.055595424, -0.22342968, 0.32391673) * g_10;
    result += mat4(-0.24940865, -0.042881966, -0.19815244, -0.05011009, 0.32227826, 0.07563262, -0.22649106, 0.10700333, -0.14117172, 0.1359497, -0.14451554, 0.34859756, 0.060239617, 0.09917812, 0.13169186, 0.077682465) * g_11;
    result += mat4(-0.0714192, 0.12607583, -0.3341241, 0.18375745, -0.18943295, 0.11634349, 0.06633747, -0.13485552, 0.045528308, 0.2432545, 0.26417813, 0.0074096527, 0.004411052, -0.5647283, 0.021793056, -0.1910634) * g_12;
    result += mat4(0.04678379, 0.15781826, -0.14137928, -0.065010436, 0.1379615, -0.07252597, -0.05457498, 0.049137864, 0.054244712, -0.24069838, -0.11444052, 0.27642834, 0.19889133, 0.31845504, -0.102143094, 0.088378325) * g_13;
    result += mat4(-0.1163185, 0.19226453, -0.1896929, -0.30681732, -0.013604632, -0.12468549, 0.018667353, 0.09807849, 0.030277459, 0.18578297, 0.14520812, 0.43598676, 0.24981564, 0.22188906, -0.12707953, 0.35956743) * g_14;
    result += mat4(-0.1817424, 0.27081814, -0.16284765, 0.033412658, -0.29831278, -0.1345311, 0.27491164, 0.14552177, -0.054520354, -0.2996891, -0.1279112, -0.64904505, 0.049450837, -0.021562194, -0.6366078, 0.15545636) * g_15;
    result += vec4(0.019361967, -0.009793055, 0.03647491, -0.010136049);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf2, ivec3(valid_xy, tile.inputLayer), result);
}