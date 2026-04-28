// Anime4K_Upscale_Denoise_CNN_x2_M - Pass 4 of 9 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_3_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.13262276, 0.18682314, -0.1433667, -0.0061677806, -0.15057871, -0.15389217, 0.40721065, -0.082456455, 0.028175479, -0.06136406, 0.13517159, -0.0066659097, -0.03311807, -0.056219388, 0.066265404, -0.017012158) * go_0(-1.0, -1.0);
    result += mat4(0.0652481, -0.02717338, -0.17586891, -0.1458622, 0.37166637, -0.13651049, -0.095090784, 0.1450258, -0.08856753, -0.029000161, -0.11024598, 0.14231622, 0.027118085, 0.060637098, -0.028174674, 0.020973917) * go_0(-1.0, 0.0);
    result += mat4(0.17137158, 0.015818363, -0.1761587, -0.07798954, -0.22039492, -0.08250406, 0.15350278, 0.05466543, 0.07231244, 0.124937475, -0.14530692, -0.036220204, -0.20202135, 0.16154502, -0.1472417, 0.045183204) * go_0(-1.0, 1.0);
    result += mat4(-0.06751513, 0.3630837, -0.23374555, -0.17641832, 0.23866339, -0.12625019, 0.14955078, 0.3757683, 0.25546572, -0.0009440543, -0.029705383, 0.12500505, 0.039303612, 0.02745342, 0.06280759, -0.027673393) * go_0(0.0, -1.0);
    result += mat4(-0.40253955, 0.5532656, 0.15580782, 0.23305601, 0.04307387, -0.37548792, 0.021682428, -0.14554474, -0.44655007, 0.12335231, 0.22693188, -0.19185324, -0.39905196, -0.36661598, 0.34626722, 0.3220371) * go_0(0.0, 0.0);
    result += mat4(0.13051705, -0.051269528, 0.027860573, 0.12866034, 0.095374286, 0.0072371624, 0.06641015, -0.040609945, 0.14411138, 0.03813084, 0.024812538, -0.069997884, -0.2398024, 0.16384888, 0.004522481, -0.2734798) * go_0(0.0, 1.0);
    result += mat4(-0.048976544, 0.36923414, -0.23769425, -0.02964149, 0.13426293, -0.070416726, -0.036279447, 0.21007125, -0.0062456504, 0.12307804, -0.18920022, 0.016429992, 0.091225415, -0.00714184, -0.079064, 0.050525308) * go_0(1.0, -1.0);
    result += mat4(0.007005748, -0.1929285, -0.27960134, -0.014070343, -0.012031938, -0.21320626, 0.22591045, 0.06750757, 0.038049847, -0.08933499, 0.15640227, 0.36653376, 0.11274315, 0.0015512784, -0.14319079, -0.41117874) * go_0(1.0, 0.0);
    result += mat4(0.039254356, 0.04123307, -0.14476523, 0.19676228, -0.1746638, 0.068685316, 0.19318552, -0.007086376, -0.08810745, 0.041937724, 0.1393943, 0.27539206, -0.08331265, 0.043064818, -0.02783017, -0.13006629) * go_0(1.0, 1.0);
    result += mat4(0.18761271, -0.009960496, -0.18572417, 0.010640895, 0.10240658, 0.036137953, -0.109363064, 0.05820501, -0.04092678, 0.11809751, -0.11843415, 0.11893309, -0.06356792, 0.1509876, -0.12252014, -0.0070098704) * go_1(-1.0, -1.0);
    result += mat4(-0.0012312894, 0.038436964, -0.046054237, 0.04859312, -0.4190657, 0.2529927, 0.23133701, -0.00065297337, -0.039581586, 0.00905735, 0.16532114, -0.12568031, 0.17818217, -0.28053075, 0.38509414, -0.03763847) * go_1(-1.0, 0.0);
    result += mat4(-0.0897875, 0.063593514, 0.07660054, 0.12268424, 0.21554653, -0.1025501, 0.2557211, 0.04492533, 0.10992355, -0.035215836, -0.009733763, -0.02165148, 0.08618596, -0.19276536, 0.18174514, -0.18021213) * go_1(-1.0, 1.0);
    result += mat4(-0.002999377, -0.12630916, -0.030010369, -0.2676409, -0.20229307, 0.15253967, -0.12200155, -0.1552754, -0.16193017, 0.10819683, 0.10696224, -0.1920264, -0.29354608, -0.32021165, 0.08644405, -0.16153689) * go_1(0.0, -1.0);
    result += mat4(0.49931613, -0.3669461, -0.49107462, -0.3654748, 0.32047966, 0.03246311, -0.06424334, 0.009108802, 0.2367612, -0.46587244, 0.16957493, 0.3237888, 0.93676794, 0.01834384, -0.9349752, -0.04654371) * go_1(0.0, 0.0);
    result += mat4(-0.112562165, 0.006074484, -0.12288025, -0.08560263, 0.25336134, 0.025205871, 0.25063732, 0.12370882, -0.40429187, 0.12992847, -0.2816234, 0.08179623, 0.27197668, 0.066299304, -0.12988937, 0.16257611) * go_1(0.0, 1.0);
    result += mat4(0.047864527, -0.05821779, -0.06311128, -0.0065775234, -0.065763995, 0.014864688, 0.09148591, -0.25059348, 0.008846306, -0.22123712, 0.4062609, -0.100248575, -0.50293785, -0.13373566, 0.21480446, -0.0841981) * go_1(1.0, -1.0);
    result += mat4(0.19313097, -0.061253734, -0.1801314, -0.20178059, -0.039574936, 0.08167749, 0.010974997, 0.069656976, -0.13193963, 0.35555324, 0.62686867, -0.28656846, -0.27831817, -0.0040086447, 0.4031064, 0.47767937) * go_1(1.0, 0.0);
    result += mat4(0.15396428, 0.069321476, -0.15190981, -0.24133344, 0.106151104, -0.11271092, 0.06878746, 0.14279713, -0.02006402, -0.36284852, -0.00926688, -0.39887694, -0.20926239, -0.021860912, 0.07588468, 0.2620174) * go_1(1.0, 1.0);
    result += vec4(-0.0073282495, -0.040352557, -0.063710704, 0.07255652);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf, gxy, result);
}