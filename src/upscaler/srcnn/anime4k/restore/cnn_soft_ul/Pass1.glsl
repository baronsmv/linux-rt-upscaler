// Anime4K_Restore_CNN_Soft_UL - Pass 1 of 25 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(set = 0, binding = 3) uniform texture2D tex_MAIN;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_tf;
#define go_0(x_off, y_off) (texture(sampler2D(tex_MAIN, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy)))

vec4 hook() {
vec4 result = mat4(-0.23234928, -0.070085905, 0.0040122913, 0.21575761, -0.25936925, -0.20185155, 0.022299573, 0.2812235, -0.11045535, -0.11106335, -0.12113332, -0.49919847, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.48585954, -0.058959674, 0.11114158, -0.1971666, -0.24872562, 0.2667282, -0.107163996, 0.12475151, -0.027792914, -0.06700173, -0.10966316, 0.09399147, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.16666615, -0.15644506, 0.048309084, 0.19122206, -0.1522582, 0.15417537, -0.23017146, 0.09460856, 0.074704535, 0.2168164, 0.2077189, -0.29264635, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.3167284, -0.20522436, -0.050071932, -0.036290437, 0.20206359, 0.012589764, -0.1251284, -0.2911492, -0.0006390347, -0.09853893, 0.14406726, 0.33612582, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(0.13786903, 0.51342535, -0.44004235, -0.23918492, 0.5614157, 0.011565876, 0.5419984, -0.15937872, -0.075360805, 0.018496322, 0.12582661, 0.40117717, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.19644158, 0.12697817, 0.15092115, 0.1963961, -0.03395398, -0.17465135, -0.04086773, 0.09187623, 0.18238129, -0.0063141263, -0.26402372, -0.28761682, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.010849395, 0.15082607, 0.095264904, -0.038952388, -0.1121466, 0.21590506, 0.029462064, -0.65400773, 0.18295552, 0.2425088, 0.121624336, 0.7189011, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.17197245, -0.04397748, 0.18232836, -0.04471754, 0.071163684, -0.20590816, 0.39706057, -0.5452873, -0.11754515, 0.006909551, 0.018450081, 0.5686299, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.077441245, -0.25645187, -0.19979256, -0.010363122, -0.04312338, -0.08810754, -0.059999906, 0.38630447, -0.11017497, -0.16309647, 0.026156282, -0.35432625, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.03509807, 0.029998481, -0.08691994, -0.017055636);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, gxy, result);
}