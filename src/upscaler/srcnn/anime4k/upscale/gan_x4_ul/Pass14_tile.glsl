// Anime4K_Upscale_GAN_x4_UL - Pass 14 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_3_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_3_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.3210504, -0.13668466, 0.20637684, 0.0037060305, -0.2674051, -0.11230086, 0.29947895, 0.093965776, -0.08801977, 0.23411755, -0.00690265, 0.22540577, 0.3496324, -0.07614303, -0.2682172, -0.18024528) * g_0;
    result += mat4(-0.12103706, -0.061189037, 0.019804776, 0.31127328, -0.36069378, 0.213189, 0.22896592, 0.008048813, -0.021931307, 0.3776008, 0.04475082, 0.08132412, 0.12560965, -0.12159681, 0.012501785, -0.3363862) * g_1;
    result += mat4(-0.2294047, 0.038059004, 0.21087843, 0.037582193, -0.026122637, 0.28849372, 0.24839666, 0.13881797, -0.29496697, -0.17923991, 0.024531588, -0.06418792, 0.015839651, 0.12997966, 0.23888347, -0.1048919) * g_2;
    result += mat4(-0.18445078, 0.025115933, 0.08433517, -0.22597772, -0.12536137, 0.21140383, -0.030371241, 0.036926106, 0.19343626, -0.0041754777, 0.00244178, 0.021117657, 0.26237983, 0.22308359, 0.2492868, -0.24042289) * g_3;
    result += mat4(0.22000861, 0.08476075, 0.11643673, 0.15832588, 0.03325583, 0.24106406, 0.2292178, -0.2764258, -0.06348522, 0.17427239, 0.16678956, 0.17231269, -0.0872214, -0.0135706505, -0.06671483, -0.07503989) * g_4;
    result += mat4(-0.30087617, 0.3176826, -0.31664857, -0.101466715, 0.073069066, 0.0038022113, -0.13776854, 0.10784852, 0.02954845, -0.24216515, -0.19634016, 0.022595271, -0.17444247, 0.17016955, -0.07563684, 0.20474768) * g_5;
    result += mat4(-0.27660307, -0.07230632, -0.09617381, 0.21262856, 0.11049351, 0.050447285, -0.3273503, 0.05641904, -0.042776052, -0.17620195, -0.06274188, 0.039536018, -0.070038274, 0.20343757, 0.08803773, 0.009139854) * g_6;
    result += mat4(0.24007742, -0.13485539, -0.3781107, 0.027324034, 0.010332106, 0.08556457, -0.2392748, -0.13601078, -0.19836703, 0.022715727, -0.016411083, -0.17756946, -0.14373688, 0.020681657, 0.05082997, -0.14939624) * g_7;
    result += mat4(0.28352678, 0.20785898, -0.15538763, 0.04196249, 0.19792412, -0.24451323, 0.04824567, -0.1365707, 0.19390641, -0.061393958, -0.25272602, 0.0045554833, -0.21719287, -0.08406589, -0.048988152, 0.05259591) * g_8;
    result += mat4(-0.10792345, -0.29639974, 0.21581274, 0.029042492, -0.28554165, 0.10910743, 0.07680131, -0.13153972, 0.14755669, 0.0854899, 0.24539046, 0.08502808, 0.22990887, 0.15149027, 0.23587988, -0.09517703) * g_9;
    result += mat4(0.15912442, -0.34394726, 0.34174097, 0.25116822, -0.24741888, 0.37633938, -0.08430594, 0.2769256, -0.03159722, 0.05234807, 0.029541405, -0.1266574, -0.122047566, -0.16540837, 0.2679574, -0.23974617) * g_10;
    result += mat4(-0.10200111, -0.11974673, -0.0079962695, -0.39264813, -0.006873918, -0.23566915, 0.13980511, -0.070295505, 0.12384241, 0.09101257, -0.04413333, -0.112293474, -0.27065778, 0.03445708, 0.16511594, 0.37050763) * g_11;
    result += mat4(-0.096395366, 0.06278703, -0.09479416, -0.488774, -0.09141473, 0.12217416, -0.11785924, -0.22766003, 0.16063516, 0.00020897393, 0.3078544, 0.18561389, -0.15621823, -0.13971844, 0.020068014, 0.013216665) * g_12;
    result += mat4(0.12522821, 0.0046115327, -0.007866688, -0.22109744, 0.2225005, -0.051918246, 0.11966214, -0.119629785, 0.2925202, -0.26889777, -0.3189588, -0.24831142, -0.036346573, 0.047227684, 0.1266368, 0.1058624) * g_13;
    result += vec4(0.020081282, -0.013928095, 0.0059036794, 0.08544713);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf1, ivec3(valid_xy, tile.inputLayer), result);
}