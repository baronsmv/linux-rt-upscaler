// Anime4K_Restore_CNN_Soft_M - Pass 6 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_5_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(0.034357008, 0.00082413113, -0.13382089, -0.05066409, 0.26684088, -0.31363875, 0.073608615, 0.20824149, 0.21509308, -0.07118628, 0.11287014, -0.09817389, 0.16107765, 0.17146803, -0.13836654, -0.05962866) * go_0(-1.0, -1.0);
    result += mat4(0.029981667, 0.08738892, 0.17735903, 0.15817277, 0.041752994, -0.20031185, 0.064203605, 0.48786053, -0.0033609737, -0.42522693, 0.058846988, 0.22180536, 0.17181319, 0.13097888, -0.059532285, 0.062227458) * go_0(-1.0, 0.0);
    result += mat4(0.13188283, 0.07971828, 0.28278515, 0.038570832, -0.12815465, 0.29860008, -0.2785862, -0.07612298, -0.14369671, 0.12457525, 0.11982623, -0.018675303, 0.14936846, 0.1284789, -0.0042489986, 0.042810377) * go_0(-1.0, 1.0);
    result += mat4(0.2892425, -0.20834558, 0.07358541, -0.11190968, -0.16300741, 0.15674856, -0.04297203, -0.29218298, -0.036296643, -0.052267153, -0.22889943, -0.21203549, -0.03553075, -0.20343691, -0.07413655, -0.092966415) * go_0(0.0, -1.0);
    result += mat4(0.2484468, -0.23412868, -0.070199326, 0.2061922, 0.5047224, -0.48216155, -0.5792768, 0.610787, 0.023935676, -0.040435325, -0.1238493, -0.09576053, -0.26183444, 0.14510648, 0.5365255, 0.5499143) * go_0(0.0, 0.0);
    result += mat4(-0.058255754, 0.08133753, -0.18663554, 0.26190025, 0.26006857, -0.007619795, 0.14585225, 0.073580734, -0.0396066, 0.2821596, 0.31778112, -0.029853562, -0.19703479, 0.17809318, 0.21089044, -0.106730856) * go_0(0.0, 1.0);
    result += mat4(0.20549655, -0.05962688, 0.1432124, 0.013446325, -0.19064854, 0.061387196, 0.1792527, 0.0010619498, -0.1456842, 0.18950678, -0.13990986, -0.37644413, -0.083257, -0.2937246, 0.032096215, 0.14719158) * go_0(1.0, -1.0);
    result += mat4(-0.26601696, 0.4242341, -0.073702715, -0.3221337, 0.026037043, -0.0117916465, -0.024286825, 0.23183465, -0.030869482, -0.045915652, -0.040611852, 0.11372697, -0.25404635, 0.21859063, 0.13869432, 0.19651218) * go_0(1.0, 0.0);
    result += mat4(-0.028276298, -0.11217159, 0.27144867, -0.010531775, 0.11032058, -0.09957206, 0.12570262, 0.14724332, 0.08758557, -0.11042305, 0.025948172, -0.010910802, -0.029466914, -0.041135952, -0.017091949, 0.05501236) * go_0(1.0, 1.0);
    result += mat4(-0.12688768, -0.19051413, 0.052141912, -0.13618521, -0.16320245, -0.1601866, 0.16207355, -0.023218745, 0.2103894, -0.06212745, -0.07042835, 0.0996637, -0.1763831, 0.13890013, -0.12125462, -0.105104685) * go_1(-1.0, -1.0);
    result += mat4(0.10485512, -0.49283037, -0.504295, 0.009089699, -0.17389494, -0.12835866, 0.14188384, -0.22946316, 0.006298799, -0.0348454, -0.0852419, 0.17956656, -0.08088888, 0.35675287, 0.16014415, -0.055372503) * go_1(-1.0, 0.0);
    result += mat4(-0.17157564, 0.1557075, -0.17681694, 0.14834762, -0.13708206, 0.101721555, 0.17070566, -0.22522852, 0.08100986, -0.23204406, -0.38926315, -0.13165781, 0.1040296, -0.045591615, 0.15745829, -0.10410621) * go_1(-1.0, 1.0);
    result += mat4(-0.20517144, 0.35896194, -0.0010962893, -0.18043008, -0.016253468, 0.035292216, 0.06781499, 0.015984116, -0.20261237, -0.28905126, 0.007414641, 0.008870292, 0.52166605, -0.0996688, -0.23151648, 0.2811893) * go_1(0.0, -1.0);
    result += mat4(0.013482173, -0.04891998, -0.06094191, -0.14416319, -0.00087873987, 0.11979091, 0.06457245, -0.2305623, -0.1476981, 0.2634587, -0.058895197, -0.07394766, -0.27173743, 0.7530214, 0.037599873, 0.22086331) * go_1(0.0, 0.0);
    result += mat4(-0.10357755, 0.23899554, 0.034912035, -0.14336212, -0.019786308, -0.085470654, -0.03096524, 0.108783185, 0.28971127, 0.24527478, -0.19110362, -0.49510127, -0.15574701, 0.10968643, -0.13727877, 0.04502924) * go_1(0.0, 1.0);
    result += mat4(-0.10808282, -0.079148844, -0.3244773, -0.2210664, -0.0062175165, 0.1303082, 0.012592612, -0.38039228, 0.26899642, -0.16624425, -0.04438198, 0.42067865, -0.13381268, 0.03408099, -0.2999706, -0.3817641) * go_1(1.0, -1.0);
    result += mat4(0.030872926, -0.26852018, -0.14650428, 0.16869825, -0.19185568, -0.06341456, 0.12261606, -0.26597574, 0.44865233, 0.21416639, 0.40359476, 0.12814924, 0.2542566, -0.23348318, -0.43142912, -0.35113996) * go_1(1.0, 0.0);
    result += mat4(-0.03364283, 0.11002299, 0.3311268, -0.14580412, -0.10348537, 0.13331696, -0.0793144, -0.04116661, 0.040704627, -0.14875266, -0.09259674, -0.062087066, 0.063962296, 0.18420577, -0.085616685, -0.16555141) * go_1(1.0, 1.0);
    result += vec4(-0.037546165, -0.015675364, 0.13989694, 0.027605768);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_5_tf, gxy, result);
}