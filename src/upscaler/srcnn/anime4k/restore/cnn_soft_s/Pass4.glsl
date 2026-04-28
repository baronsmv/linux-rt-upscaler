// Anime4K_Restore_CNN_Soft_S - Pass 4 of 4 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 4) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 5, rgba8) uniform image2D img_output;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(0.08631539, 0.09499331, 0.065609254, 0.0, -0.023760278, -0.027293118, -0.022839671, 0.0, -0.012447854, -0.008565141, -0.012041815, 0.0, -0.033292875, -0.031266093, -0.02874347, 0.0) * go_0(-1.0, -1.0);
    result += mat4(0.08709062, 0.09760889, 0.08988583, 0.0, -0.09099671, -0.102120616, -0.098076016, 0.0, 0.057814583, 0.06999608, 0.05961344, 0.0, 0.12246188, 0.1319784, 0.12254915, 0.0) * go_0(-1.0, 0.0);
    result += mat4(0.07694916, 0.0822054, 0.07549296, 0.0, -0.046808865, -0.051509347, -0.035890795, 0.0, 0.01599848, 0.014677793, 0.0086143715, 0.0, 0.033142705, 0.0426565, 0.035911378, 0.0) * go_0(-1.0, 1.0);
    result += mat4(-0.0008269902, 0.0009082343, 0.014101725, 0.0, 0.0006387551, 0.005079344, -0.013034868, 0.0, 0.013909732, 0.011026747, 0.012485332, 0.0, 0.027028518, 0.022164145, 0.03183532, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.33575395, -0.36700967, -0.34140685, 0.0, 0.35850254, 0.37535715, 0.34613726, 0.0, -0.12680013, -0.1256115, -0.112494245, 0.0, -0.061541136, -0.059120018, -0.06552594, 0.0) * go_0(0.0, 0.0);
    result += mat4(-0.047570463, -0.050335366, -0.04665491, 0.0, -0.110970475, -0.12363716, -0.11072252, 0.0, 0.041563414, 0.059771337, 0.045290247, 0.0, -0.17999935, -0.19700716, -0.17459513, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.078488424, 0.07483357, 0.08347933, 0.0, -0.0063715233, 0.00035415235, -0.010886946, 0.0, 0.031237155, 0.02512343, 0.034399323, 0.0, -0.023146842, -0.026732154, -0.027644241, 0.0) * go_0(1.0, -1.0);
    result += mat4(-0.05906883, -0.06784104, -0.04506148, 0.0, -0.003939601, -0.0011749315, -0.006256036, 0.0, -0.1662408, -0.16871658, -0.16598499, 0.0, 0.051277652, 0.04837499, 0.05120855, 0.0) * go_0(1.0, 0.0);
    result += mat4(0.08158806, 0.08674548, 0.07437206, 0.0, -0.05765347, -0.06196418, -0.057311118, 0.0, 0.26747537, 0.2668808, 0.2389857, 0.0, -0.010376844, -0.01690028, -0.008414153, 0.0) * go_0(1.0, 1.0);
    result += mat4(0.030539425, 0.02415435, 0.039969034, 0.0, 0.006491679, 0.014436586, 0.005435709, 0.0, -0.0058292216, -0.013982021, -0.011243379, 0.0, 0.025942149, 0.015361476, 0.019134998, 0.0) * go_1(-1.0, -1.0);
    result += mat4(-0.06322247, -0.07146787, -0.06673042, 0.0, 0.028702464, 0.039047733, 0.039646607, 0.0, -0.072553575, -0.08046175, -0.07027197, 0.0, -0.1447189, -0.1539398, -0.1466465, 0.0) * go_1(-1.0, 0.0);
    result += mat4(-0.046430312, -0.054549117, -0.048076343, 0.0, 0.032971155, 0.02980819, 0.029172963, 0.0, -0.017612953, -0.015100736, -0.01202649, 0.0, -0.026717246, -0.028401854, -0.034548033, 0.0) * go_1(-1.0, 1.0);
    result += mat4(-0.0020459262, -0.0008748501, -0.012601956, 0.0, 0.0054226154, 0.008867029, 0.018921215, 0.0, -0.0021330053, -0.0036601655, -0.0022091097, 0.0, -0.08636891, -0.10203159, -0.09741449, 0.0) * go_1(0.0, -1.0);
    result += mat4(0.07306159, 0.08245483, 0.06548199, 0.0, -0.1933229, -0.20326294, -0.19189309, 0.0, 0.107496604, 0.11584994, 0.10907522, 0.0, 0.30877885, 0.31297725, 0.30890995, 0.0) * go_1(0.0, 0.0);
    result += mat4(0.03192904, 0.035112645, 0.033732817, 0.0, 0.074100636, 0.08349646, 0.06659352, 0.0, -0.1136165, -0.12470947, -0.11192198, 0.0, 0.14465587, 0.16328491, 0.13984151, 0.0) * go_1(0.0, 1.0);
    result += mat4(-0.05098033, -0.053096622, -0.05533725, 0.0, 0.0045651463, -0.007682458, 0.0026934785, 0.0, -0.021199327, -0.016210148, -0.030939564, 0.0, -0.031621892, -0.046702545, -0.02647333, 0.0) * go_1(1.0, -1.0);
    result += mat4(0.055801813, 0.06430485, 0.05052402, 0.0, 0.0241233, 0.013879883, 0.017344628, 0.0, 0.08707151, 0.10031039, 0.095042154, 0.0, -0.109053336, -0.11414017, -0.111838564, 0.0) * go_1(1.0, 0.0);
    result += mat4(0.030582374, 0.03604719, 0.040417343, 0.0, 0.038665913, 0.036998056, 0.030004544, 0.0, 0.09209076, 0.10010001, 0.08389406, 0.0, -0.014655714, -0.0074866647, -0.012227013, 0.0) * go_1(1.0, 1.0);
    result += vec4(-0.008303841, -0.008251826, -0.0069884053, 0.0);
    return result + texture(sampler2D(tex_MAIN, pointSampler), pos);
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_output, gxy, result);
}