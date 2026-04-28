// Anime4K_Restore_CNN_Soft_M - Pass 7 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3072) uniform sampler pointSampler;

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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.35835463, 0.038305778, -0.10198824, -0.021951782, 0.02142098, -0.072417736, -0.2577152, 0.054713376, 0.075116105, -0.21191697, -0.1213158, -0.105036296, 0.12030758, -0.17591658, 0.1726511, 0.17754573) * go_0(-1.0, -1.0);
    result += mat4(0.32325825, 0.19869742, 0.333873, 0.39670366, 0.20716824, 0.09557955, 0.120742686, -0.2271023, 0.37509173, -0.031341635, 0.10247365, 0.031520665, -0.092765376, -0.13535516, 0.8333728, 0.05886494) * go_0(-1.0, 0.0);
    result += mat4(-0.17573749, 0.16768494, 0.021141645, 0.19668253, 0.21080776, 0.31503728, -0.26834, 0.19103156, 0.21946241, 0.14559007, -0.09761235, -0.23565038, -0.49393657, -0.5332298, 0.09806347, 0.054431103) * go_0(-1.0, 1.0);
    result += mat4(-0.042109374, -0.05564321, 0.27586877, 0.010382545, 0.007322007, 0.13193823, -0.18262729, 0.06399193, 0.14174329, 0.3898842, -0.10398105, 0.01846146, -0.24542394, -0.13020967, -0.16491668, -0.03544872) * go_0(0.0, -1.0);
    result += mat4(-0.15291597, 0.1566557, 0.14745249, -0.23258151, 0.17843612, 0.15885495, -0.691466, -0.41177312, 0.40330106, -0.07991953, 0.2832403, 0.10656986, -0.19571523, 0.3670614, -0.62296015, -0.5666968) * go_0(0.0, 0.0);
    result += mat4(-0.17513512, 0.011393021, -0.44352317, -0.059153114, -0.2227142, -0.033094753, 0.09624524, 0.051315393, 0.2632246, 0.09945105, 0.042561427, -0.1234722, 0.23755905, -0.506999, 0.114180565, 0.27887583) * go_0(0.0, 1.0);
    result += mat4(-0.459564, -0.120326266, 0.17507194, 0.06701153, -0.14124362, -0.36653697, -0.2856802, -0.22955593, -0.08515889, 0.18788262, 0.23427077, 0.021544341, 0.31996533, -0.2668834, 0.08469808, -0.01347926) * go_0(1.0, -1.0);
    result += mat4(-0.14092083, -0.31244513, -0.044023518, 0.013948701, 0.33119613, -0.011959397, -0.1494438, -0.111066826, -0.11994278, 0.116068155, -0.13032633, -0.037004936, 0.13851176, -0.006655432, -0.39841232, -0.079951204) * go_0(1.0, 0.0);
    result += mat4(-0.08959123, 0.18297827, -0.0763483, 0.11364159, -0.04361797, -0.029816678, -0.19314721, -0.03484794, 0.044681285, 0.04669291, -0.30017474, -0.07453036, 0.090825416, -0.27414632, 0.36355078, 0.15742934) * go_0(1.0, 1.0);
    result += mat4(0.18470702, 0.113800436, -0.18546791, 0.044184085, 0.12490399, 0.1826781, -0.01313173, -0.19048993, -0.026458051, -0.1693334, 0.21958382, 0.030458853, -0.059242606, 0.039351143, -0.061676584, -0.06904634) * go_1(-1.0, -1.0);
    result += mat4(-0.114877924, -0.03781683, -0.19207929, 0.007679428, 0.2409049, 0.2965285, -0.38395065, 0.11604976, -0.22588749, 0.48505852, 0.09866521, -0.2585994, -0.011380872, -0.018334057, -0.047188547, 0.3038583) * go_1(-1.0, 0.0);
    result += mat4(-0.2783936, -0.17609318, 0.4904369, -0.31848624, 0.39725313, 0.082951784, -0.15595853, -0.007526218, 0.2355193, -0.30003366, -0.27686292, 0.120900005, -0.1223885, 0.40760317, 0.0013726618, -0.24877374) * go_1(-1.0, 1.0);
    result += mat4(0.1580051, -0.044973504, 0.00053594523, -0.057797022, 0.18895927, 0.23527777, -0.18095906, -0.076961614, 0.2544444, -0.05932328, 0.13717431, -0.024487074, 0.33157274, -0.09072586, -0.004386734, -0.05180953) * go_1(0.0, -1.0);
    result += mat4(-0.21685815, 0.061656334, -0.066127226, 0.24831405, 0.26001146, 0.046466008, -0.047196623, 0.13538954, -0.06449239, 0.45951647, -0.13132116, -0.7079741, -0.06683439, -0.47628635, 0.42461708, 0.6475073) * go_1(0.0, 0.0);
    result += mat4(0.2590011, -0.26020283, 0.0005333198, 0.01555692, 0.37920526, 0.29205114, -0.20281325, -0.1455974, 0.056119893, 0.022032745, -0.30095813, 0.48154855, -0.35761952, 0.07582935, 0.12462687, 0.068093665) * go_1(0.0, 1.0);
    result += mat4(0.20434918, 0.26690874, 0.028224666, 0.042565826, 0.037406113, 0.5059272, -0.0047208676, 0.0019095197, 0.16626422, -0.23407575, -0.072687164, 0.00063299487, -0.10172441, -0.11645544, 0.008715937, -0.012423992) * go_1(1.0, -1.0);
    result += mat4(0.08269191, 0.116322584, -0.08155921, -0.04790326, 0.09546776, 0.3632936, -0.08139031, -0.10399187, 0.06618616, -0.26862565, 0.25058737, 0.0410593, -0.07191658, -0.20559746, 0.21857823, 0.12776822) * go_1(1.0, 0.0);
    result += mat4(0.54989135, 0.38051483, 0.015739547, -0.0068143173, 0.26107135, 0.2585036, -0.12345306, -0.13934542, -0.19018838, 0.2730626, 0.42644337, 0.16693048, -0.15189888, 0.023638237, 0.11272267, 0.039560657) * go_1(1.0, 1.0);
    result += vec4(-0.20554838, -0.10647836, -0.02824578, 0.08658529);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, ivec3(valid_xy, 0), result);
}