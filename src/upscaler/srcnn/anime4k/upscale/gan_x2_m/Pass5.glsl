// Anime4K_Upscale_GAN_x2_M - Pass 5 of 23 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.26519376, -0.45442572, -0.24128473, 0.56122154, 0.45048368, 0.32492852, -0.14123245, -0.027976234, -0.11764467, -0.47563952, -0.09401533, 0.024141679, -0.19278349, -0.5169275, -0.26203018, 0.04326379) * g_0;
    result += mat4(-0.14198317, 0.18704857, -0.20165806, 0.3868074, 0.26532957, 0.13556235, -0.5872983, 0.13357028, 0.48151335, -0.3750496, 0.020972235, -0.32213062, -0.46967435, 0.10506199, 0.24039303, -0.3906582) * g_1;
    result += mat4(0.10981934, -0.0040414287, -0.0025180888, -0.23061854, -0.6781062, -0.27331296, -0.1538456, 0.31020573, -0.05341261, 0.45214307, 0.23456645, 0.3261386, -0.020520406, 0.46579385, 0.57791334, 0.441774) * g_2;
    result += mat4(0.11475315, 0.18062253, 0.21255025, -0.1963313, -0.22190428, -0.19369084, 0.5878038, -0.051808596, -0.39728877, -0.044071846, 0.0066692936, -0.0066007506, 0.03501876, 0.27602142, 0.11396466, 0.81461775) * g_3;
    result += mat4(-0.44411597, -0.11377309, 0.16160126, 0.47119814, 0.22932883, -0.43011594, 0.01986201, 0.01446102, -0.2783236, -0.07647468, -0.5016725, 0.4227215, 0.31808656, 0.23829709, -0.12855907, -0.15950239) * g_4;
    result += mat4(-0.4784548, -0.042179376, -0.4882858, -0.046462137, -0.21421364, -0.35029694, -0.15496174, 0.11386904, 0.22592051, 0.1590684, 0.49690887, -0.37077406, -0.48519966, -0.14407466, 0.24836525, 0.38462397) * g_5;
    result += mat4(-0.043213595, -0.004892144, 0.29046863, 0.57064444, 0.37136674, -0.5603234, -0.30733815, 0.26740906, 0.016959883, -0.26567596, 0.101653986, 0.34387913, -0.13222592, -0.34239995, 0.32046688, 0.023962379) * g_6;
    result += mat4(-0.2955613, 0.44671535, 0.056253802, -0.6011664, -0.30715483, 0.16890973, 0.041257784, -0.1544008, 0.4653661, -0.22183, -0.23155628, -0.063779, 0.10350268, 0.02045104, -0.22509801, 0.14633855) * g_7;
    result += vec4(-0.00089101185, -0.038285345, 0.023986168, -0.122330956);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf, gxy, result);
}