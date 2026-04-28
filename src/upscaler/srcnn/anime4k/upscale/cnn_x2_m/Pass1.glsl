// Anime4K_Upscale_CNN_x2_M - Pass 1 of 9 - https://github.com/bloc97/Anime4K
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
vec4 result = mat4(-0.010995803, 0.077095956, -0.043992598, 0.06048717, 0.1164834, -0.11689607, 0.072985925, -0.078805886, 0.01182932, 0.054985743, -0.09018186, 0.044907484, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(0.1813623, -0.14752422, 0.025720436, -0.17639883, 0.15697388, 0.10445984, -0.1843076, 0.5264643, 0.047516696, -0.097305484, 0.09740847, -0.29619336, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.014534763, 0.09486465, 0.046173926, 0.039391946, 0.09609376, -0.060574662, 0.042200956, -0.3269777, 0.051006425, 0.059818447, 0.04366627, 0.17699827, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(0.04268535, -0.08152529, 0.10577459, -0.036936995, -0.051562306, 0.054872766, 0.09194519, 0.0025066638, -0.01073954, 0.00064474024, 0.10038221, 0.02131141, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.51751363, -0.40028602, 0.3469574, 0.5933738, -0.91357684, -0.67692596, 0.57815677, 0.39809322, -0.16341521, -0.27169713, 0.12232366, 0.4318641, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.12601124, -0.06263236, -0.45907676, -0.41514075, 0.3330334, -0.1929565, -0.6333532, -0.6552794, -0.045809917, 0.046351526, -0.26173338, -0.30252662, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.0030332592, 0.012103107, 0.010537323, -0.02038607, 0.095558085, 0.097704545, 0.083433494, 0.026790185, 0.01943357, -0.061712462, -0.00015703632, -0.032268334, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.016870102, 0.5215812, -0.11525501, 0.027527615, -0.09045733, 0.61310345, -0.1575268, 0.1905386, 0.020172214, 0.3503187, -0.08209157, -0.051328037, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.005494087, -0.010656317, 0.07682753, -0.08116042, -0.03934524, 0.16589017, 0.101483546, -0.066603065, 0.03494657, -0.07885597, 0.074227594, 0.0016264897, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(0.014463938, -0.0031906287, 0.007015422, -0.003888468);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, gxy, result);
}