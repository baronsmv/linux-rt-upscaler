// Anime4K_Restore_CNN_Soft_S - Pass 1 of 4 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_tf;
#define go_0(x_off, y_off) (texture(sampler2D(tex_MAIN, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy)))

vec4 hook() {
vec4 result = mat4(0.10922428, -0.16249932, 0.15452726, -0.15669551, 0.053448875, -0.16528402, 0.01697721, -0.049275912, 0.20947173, -0.10576949, 0.19738325, -0.025417482, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.3285196, 0.15909512, -0.5273671, 0.23778777, -0.40508887, -0.0609677, -0.4188177, 0.11137456, -0.24131267, 0.10453423, -0.36216277, 0.053446792, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(0.23072472, -0.082083695, -0.0041477727, -0.09136237, 0.11958912, -0.312698, -0.15842685, -0.013882424, 0.10933724, 0.017880991, -0.022167003, 0.014662608, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(-0.2789985, 0.054727737, 0.22577816, -0.49625716, -0.48472273, -0.011525487, 0.5354349, -0.08814955, -0.27021924, -0.044563178, 0.008232271, -0.13480483, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.18203105, 0.09277001, 0.27071548, -0.17773713, -0.4335171, 1.2275106, -0.07663438, -0.29020032, 0.011992759, 0.060106967, 0.11002492, -0.046098012, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.08363418, 0.063420765, -0.10278259, 0.09357691, 0.38670546, 0.13577081, 0.048631024, -0.024960777, 0.0846784, -0.057097007, 0.06049236, 0.042082917, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.12315548, -0.056513585, -0.09826642, -0.17079762, 0.06479095, -0.36984903, -0.12512982, 0.042867575, 0.08360464, 0.12835538, -0.005067881, 0.02542005, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.18997705, 0.086363226, -0.0007131526, 0.19858918, 0.39745626, -0.0090341605, 0.27864447, 0.20052041, 0.010576528, -0.089242525, -0.025109483, -0.030768145, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.05427315, -0.060894873, 0.06548642, 0.095537595, 0.29116166, -0.16159569, -0.13293959, -0.112566955, 0.0059667625, 0.016041303, 0.03831561, 0.09869594, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(0.0113532655, -0.06449327, 0.035503868, 0.5683031);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, gxy, result);
}