// Anime4K_Restore_CNN_Soft_L - Pass 2 of 9 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_MAIN;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_tf1;
#define go_0(x_off, y_off) (texture(sampler2D(tex_MAIN, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy)))

vec4 hook() {
vec4 result = mat4(0.09844753, -0.19389127, 0.029695928, 0.3805915, 0.1353029, 0.027786473, 0.15621242, 0.09383762, -0.1097243, 0.021245124, -0.016402386, 0.09129394, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(0.3038283, 0.03778846, 0.1898852, 0.23949303, -0.34829387, 0.20485392, 0.60560244, 0.4089768, -0.260066, 0.42611003, 0.19227165, 0.03948586, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.033990905, 0.17583308, -0.2235879, 0.47376296, -0.1001787, 0.72851896, -0.056391567, -0.056544185, 0.0966166, -0.016663829, -0.15151545, -0.14227313, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(-0.16544957, 0.05889452, -0.3277256, -0.42792717, 0.32491356, -0.39113912, 0.16600312, -0.3097514, 0.27907088, -0.22553465, 0.048548058, -0.08310438, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(0.03992136, 0.17895368, 0.16562924, -0.536188, -0.25868654, -0.4869832, 0.2591772, -0.5191932, 0.020162001, -0.41568524, 0.4776641, 0.019298514, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.14911795, -0.5984171, -0.18241958, 0.5472136, -0.69194865, 0.033839397, 0.13408412, 0.09503547, -0.21318413, 0.53743845, 0.080091774, -0.1369053, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.038978565, 0.40742934, 0.20107205, -0.3550106, 0.227634, -0.16101603, -0.45037574, 0.23192371, 0.17923234, -0.13692904, 0.10395048, 0.3124129, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(-0.059144646, -0.22531863, -0.024704054, -0.20749553, 0.58086175, -0.32206532, -0.5130457, -0.14057957, 0.24317528, 0.088735096, -0.44098017, -0.16980846, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(-0.30321437, 0.17502202, 0.1910563, -0.10118702, 0.1465326, 0.3852395, -0.31210947, 0.18236226, -0.23306467, -0.28551704, -0.2982589, 0.072740674, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(0.029685514, 0.066621915, 0.03600017, -0.03497038);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf1, gxy, result);
}