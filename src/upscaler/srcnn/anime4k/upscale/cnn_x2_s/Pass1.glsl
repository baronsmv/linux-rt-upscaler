// Anime4K_Upscale_CNN_x2_S - Pass 1 of 5 - https://github.com/bloc97/Anime4K
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
//    glslc -fshader-stage=compute --target-env=vulkan1.2 \
//          <this_file> -o <output.spv>
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(set = 0, binding = 3) uniform texture2D tex_MAIN;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_tf;
#define go_0(x_off, y_off) (texture(sampler2D(tex_MAIN, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy)))

vec4 hook() {
vec4 result = mat4(-0.0057322932, 0.12928207, -0.056848746, 0.18680117, -0.0306273, 0.25602463, 0.053723164, 0.20419341, 0.0018709862, 0.022848232, -0.04105527, 0.10169034, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(0.009471417, -0.12957802, 0.096014425, 0.21836184, 0.00021601951, -0.22997683, 0.23666254, 0.41192335, 0.021762101, 0.0047863554, 0.008233427, 0.108514786, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.01156376, -0.18988979, 0.04614705, -0.044767227, 0.01050636, -0.26426336, 0.23741047, 0.0027636609, -0.027718676, -0.14202335, -0.016650287, -0.06637125, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.057809234, -0.11033858, 0.056533534, -0.06292466, 0.13880666, -0.18710336, 0.2441031, -0.25326246, 0.0032683122, -0.026437074, 0.0023248852, 7.640766e-05, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.49110603, 0.4429004, -0.44015464, -0.41174838, -0.87738293, 0.7808468, -1.0929365, -0.59699076, -0.18409836, 0.185138, -0.11773224, -0.17097276, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.10580959, -0.055947904, -0.03431237, -0.080236495, 0.14862584, -0.15393938, -0.18872876, -0.3170681, 0.03559387, -0.003990826, 0.021298569, 0.012844483, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.040715586, -0.25781113, 0.08896714, -0.1225879, -0.15790503, -0.54010904, 0.29588607, 0.10401059, 0.003413123, -0.108357325, 0.0112870345, -0.11888622, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.0049315444, 0.02376202, -0.08224771, 0.121118225, -0.041512914, -0.027994309, -0.585988, -0.069672115, -0.017247835, 0.0056576864, 0.04319012, 0.055003505, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.37521392, 0.15916082, 0.059708964, 0.19046007, 0.8120325, 0.38343868, 0.3436578, 0.5287958, 0.16570656, 0.06957687, 0.014022592, 0.074799836, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.01050964, -0.00939481, 0.17684458, 0.027366742);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, gxy, result);
}