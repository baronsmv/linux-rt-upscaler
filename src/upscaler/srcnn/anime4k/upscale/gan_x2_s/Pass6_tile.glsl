// Anime4K_Upscale_GAN_x2_S - Pass 6 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_4_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.23653865, 0.034179572, 0.2680533, 0.03070888, -0.34707117, 0.05323393, 0.20052955, -0.09135351, 0.031460114, -0.23158966, 0.08698448, -0.120006196, -0.11532645, -0.08093671, 0.0037868635, 0.10042472) * go_0(-1.0, -1.0);
    result += mat4(-0.018171439, -0.12269748, 0.09214298, 0.07735124, -0.38116398, 0.2625897, 0.045807257, 0.06052568, 0.15468815, -0.40968472, 0.37565818, 0.032876365, 0.058758568, 0.17787455, 0.11352259, 0.23624317) * go_0(-1.0, 0.0);
    result += mat4(-0.094512895, 0.15499377, -0.15345438, -0.18841587, -0.07849487, 0.037030153, -0.17632313, 0.10438565, -0.18453433, -0.079957336, 0.10274841, 0.07198532, -0.04770108, 0.16846456, 0.31273615, -0.13635644) * go_0(-1.0, 1.0);
    result += mat4(0.13088372, -0.008759914, 0.1716414, 0.082108594, -0.51469034, 0.18175006, -0.16164891, 0.1918173, 0.21287642, -0.094005, 0.20578988, 0.13113159, 0.07577773, 0.09737444, -0.08676422, -0.059179075) * go_0(0.0, -1.0);
    result += mat4(-0.28462783, 0.42669204, 0.3224737, -0.29510942, -0.12424295, -0.16050552, -0.12770653, 0.0930919, -0.22179118, 0.33128613, -0.42117682, -0.14691186, 0.41048542, -0.040950067, -0.13896315, -0.24155742) * go_0(0.0, 0.0);
    result += mat4(0.15060697, -0.088174045, 0.27417374, 0.0397946, 0.0078119785, 0.091031335, 0.008468849, -0.04850853, 0.03755719, -0.005380725, 0.13488528, -0.21345685, 0.12456556, 0.17801593, -0.21285392, -0.2111536) * go_0(0.0, 1.0);
    result += mat4(0.13265789, 0.0058933417, -0.35399312, -0.10547572, 0.014682838, 0.03247095, -0.046823166, -0.086899005, 0.022227641, -0.10579067, 0.13096501, -0.020894872, 0.08426519, 0.068370126, -0.051551163, -0.02995364) * go_0(1.0, -1.0);
    result += mat4(-0.19551872, 0.16199462, 0.31150326, 0.082667254, 0.20023693, -0.22914512, -0.29721177, -0.2741043, 0.08894789, -0.06843645, -0.019058365, -0.06370645, 0.11551113, 0.011740334, -0.17567629, -0.05505456) * go_0(1.0, 0.0);
    result += mat4(0.043439314, 0.19573408, -0.17608817, 0.043509595, 0.22829561, 0.059223037, 0.05529666, -0.16555707, 0.2754871, 0.042527672, 0.09646824, 0.07046857, 0.10173791, 0.04030276, -0.0544029, -0.26882443) * go_0(1.0, 1.0);
    result += mat4(0.022059897, -0.04408266, -0.18699357, -0.09142074, 0.044572234, -0.14162005, 0.108728774, -0.08984615, -0.14737117, 0.12838708, -0.0019777226, 0.21070306, -0.111902215, 0.23080471, 0.0134878885, 0.07111553) * go_1(-1.0, -1.0);
    result += mat4(0.12182694, 0.063630685, 0.110018775, -0.03879438, 0.333222, -0.45207745, 0.3209222, 0.123050354, -0.40609705, 0.48236838, 0.14323111, -0.12578699, 0.0015041681, -0.019454073, 0.07013497, 0.093687624) * go_1(-1.0, 0.0);
    result += mat4(0.07142873, -0.32094324, 0.3302099, -0.3693182, 0.15444939, -0.14791024, 0.07907135, -0.111387216, 0.045319714, -0.12518585, 0.13145387, 0.09406553, 0.038564056, -0.3085204, 0.39396307, 0.12083835) * go_1(-1.0, 1.0);
    result += mat4(0.16042647, -0.16409212, 0.105187505, 0.14153793, 0.269689, -0.14337258, 0.0915773, -0.26669213, -0.059172913, 0.1121628, -0.06627627, -0.29320538, -0.038348313, 0.060661227, -0.09798249, -0.027975965) * go_1(0.0, -1.0);
    result += mat4(-0.4110324, -0.06847458, -0.22187959, -0.17196147, -0.2673298, 0.15388274, -0.20157869, 0.45323396, 0.419686, -0.15836199, -0.08358049, 0.2121381, -0.33858112, 0.06060976, -0.0400928, 0.047277283) * go_1(0.0, 0.0);
    result += mat4(0.040201366, 0.12845124, 0.6901938, -0.009195482, 0.014911491, -0.06885409, -0.08029354, 0.1280681, 0.13877457, 0.0048243836, -0.13357066, 0.02874182, -0.07086705, -0.08369575, 0.070227675, 0.1674778) * go_1(0.0, 1.0);
    result += mat4(-0.009859274, -0.06701725, 0.25491804, -0.035013054, 0.15333284, -0.055876795, -0.22912641, -0.30044466, 0.05092424, 0.15086575, -0.062285095, 0.05064704, 0.02725196, 0.0008295126, -0.24010411, -0.0076930025) * go_1(1.0, -1.0);
    result += mat4(-0.033275966, -0.25090593, 0.2981365, 0.12117296, -0.04844607, 0.12529893, 0.041575357, -0.10317985, 0.048691675, 0.13610789, -0.15120777, -0.21308705, -0.019387634, 0.20519307, -0.09056782, -0.04757386) * go_1(1.0, 0.0);
    result += mat4(-0.010075166, -0.08621876, -0.19569752, 0.1553574, -0.115346536, -0.009765705, -0.37459797, -0.017294222, -0.18065308, 0.052127127, 0.045157496, 0.11466202, 0.036598917, 0.1750653, -0.18558112, 0.13441156) * go_1(1.0, 1.0);
    result += vec4(0.09810561, 0.044599928, -0.0019709724, 0.064204566);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_4_tf, ivec3(valid_xy, tile.inputLayer), result);
}