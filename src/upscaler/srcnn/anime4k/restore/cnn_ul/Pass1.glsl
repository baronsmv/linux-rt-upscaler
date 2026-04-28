// Anime4K_Restore_CNN_UL - Pass 1 of 25 - https://github.com/bloc97/Anime4K
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
vec4 result = mat4(-0.28293434, -0.10095658, -0.013867814, 0.08509398, -0.31489053, -0.26828897, 0.01152665, 0.18905516, -0.23013242, -0.18878274, -0.17923735, -0.32707638, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.3519405, -0.12639853, 0.0981044, -0.23800656, -0.1666394, 0.2548722, -0.09458217, 0.17642984, -0.0016840132, -0.12355663, -0.13711694, 0.25234836, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.14581299, -0.060752276, 0.06813433, 0.32616982, -0.29410994, 0.28217724, -0.2221963, -0.051627193, 0.10754401, 0.31993762, 0.25542948, -0.4268778, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.2716687, -0.13160354, -0.056812827, -0.00881874, 0.3249303, 0.05037425, -0.117648534, -0.26370025, 0.032854702, -0.14214379, 0.10036965, 0.17808898, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(0.004323515, 0.37651265, -0.39865002, -0.18153298, 0.5224921, -0.11810103, 0.56151056, -0.063698344, -0.17272837, -0.053013492, 0.062254835, 0.28695017, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.2776938, 0.22578415, 0.110299006, 0.27424663, 0.012712999, -0.22353122, -0.0010140019, 0.08163494, 0.3611274, 0.014346184, -0.26426178, -0.26777005, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.09010997, 0.19958799, 0.22421049, 0.054506898, -0.11822318, 0.23656984, 0.11197124, -0.4646639, 0.17118955, 0.33748102, 0.20479581, 0.6810799, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.2121316, -0.08664465, 0.2507115, -0.223455, 0.22042283, -0.20352642, 0.42714027, -0.5048447, -0.10270271, 0.11400399, -0.019575266, 0.40490857, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.091496244, -0.24679382, -0.3801941, -0.08482344, -0.17183328, -0.09308921, -0.059639163, 0.3321586, -0.19797249, -0.17941834, 0.015049101, -0.13793056, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.02313247, 0.016216148, -0.053347506, -0.023317637);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, gxy, result);
}