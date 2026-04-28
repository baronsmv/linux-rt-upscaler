// Anime4K_Upscale_Denoise_CNN_x2_VL - Pass 1 of 18 - https://github.com/bloc97/Anime4K
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
vec4 result = mat4(0.28296316, -0.020139743, 0.1038232, 0.09352482, -0.16964972, 0.07910997, -0.049914766, -0.10661066, -0.121037185, -0.029087039, -0.02511847, -0.078911744, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.3927183, 0.01805193, -0.031168332, -0.13300525, 0.20814548, 0.118818566, 0.1655351, 0.095023684, 0.17600809, -0.03928444, -0.014350658, 0.08458312, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(0.079089314, -0.0421829, 0.05452305, -0.22055493, 0.013279097, -0.12875281, 0.02452735, -0.101503745, -0.085946664, 0.05539176, 0.022408713, 0.14837204, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(-0.102643915, -0.011254746, 0.1478563, 0.1030208, 0.12396588, 0.0016621432, 0.2551224, -0.10399001, -0.01068436, 0.07155532, -0.104522154, 0.026937222, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.8789423, 0.35707328, -0.29964274, -0.064913996, 0.4962815, 0.26001287, -0.9511284, 0.49574667, 0.39539725, 0.16308042, 0.119878456, -0.30259115, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(-0.08852938, -0.32612664, -0.006712046, 0.28693515, 0.06320871, -0.3322611, 0.04651086, -0.11020996, 0.01821082, -0.22851005, -0.07803438, 0.021527015, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.12295851, -0.011285535, 0.015859747, 0.04005441, -0.018136669, 0.03171969, -0.0406123, -0.10731229, -0.12117574, 0.005033036, 0.047838476, 0.026843475, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.4655988, 0.05519082, 0.039515793, 0.28410903, -0.36144528, 0.13039446, 0.11338478, -0.2141387, -0.10026682, -0.07903024, -0.09410254, 0.043833878, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.110124744, -0.024725702, 0.028102143, -0.09493807, -0.06455328, -0.15164614, 0.04425987, 0.15483347, -0.045039337, 0.07210396, -0.005390788, -0.03832707, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(0.007907974, -0.035503313, 0.057224784, -0.19763541);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, gxy, result);
}