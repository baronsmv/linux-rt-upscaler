// Anime4K_Upscale_GAN_x2_S - Pass 8 of 17 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_8_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.43036512, 0.052133385, 0.1917228, -0.0080327755, -0.13650647, 0.23129214, -0.03926996, -0.07268268, -0.039649602, -0.04959827, 0.04222682, 0.00578327, -0.6177682, -0.5984116, -0.055091057, -0.41249448) * go_0(-1.0, -1.0);
    result += mat4(-0.41248822, 0.42497736, 0.3476831, 0.11943562, 0.071097784, 0.1390214, 0.05519766, -0.13476476, -0.36376685, 0.058813993, -0.05142066, 0.059006505, -0.17129485, 0.18402734, 0.412061, -0.38983205) * go_0(-1.0, 0.0);
    result += mat4(-0.19183454, -0.11911039, 0.20892574, 0.1218832, -0.23423564, 0.10342528, 0.09782025, 0.027760351, -0.08676245, 0.07389133, 0.009934853, 0.015378812, 0.28361297, -0.23730409, -0.10037592, -0.24095006) * go_0(-1.0, 1.0);
    result += mat4(0.035607535, -0.3156877, -0.013944192, 0.22095163, 0.20762561, -0.26094976, 0.049627785, -0.20424393, 0.07220507, 0.14855692, -0.04763761, 0.09102831, -0.6707187, 0.044909656, 0.73606086, 0.3112647) * go_0(0.0, -1.0);
    result += mat4(0.28717026, -0.027964758, 0.19860156, -0.18898363, -0.10064204, 0.05297523, 0.014720102, -0.10856063, -0.517343, -0.17088185, 0.21192405, 0.040609106, 0.07515164, -0.22581428, 0.54721195, 0.40544033) * go_0(0.0, 0.0);
    result += mat4(-0.021332845, -0.28534392, -0.053418603, -0.5890941, 0.3246433, 0.255651, 0.07088422, -0.10737213, -0.116894506, 0.13120323, 0.09616092, -0.0067616547, 0.085571416, 0.14623387, -0.26895332, -0.12028506) * go_0(0.0, 1.0);
    result += mat4(-0.052351072, -0.73936135, -0.07819111, -0.35983723, 0.13252614, -0.3479261, -0.07381629, 0.008948218, 0.0053645126, -0.039163757, -0.061387096, 0.0041966103, -0.22976315, -0.10269704, 0.5676015, -0.2502383) * go_0(1.0, -1.0);
    result += mat4(0.09443165, 0.13924311, 0.15899155, -0.029454758, 0.002642519, 0.4178081, -0.19227526, 0.25177202, -0.26731998, -0.14999937, -0.15141752, -0.16183105, -0.4617529, -0.43337283, 0.2787283, -0.72364557) * go_0(1.0, 0.0);
    result += mat4(0.18768649, -0.33622888, 0.10795176, -0.3965141, -0.1887279, 0.2281405, -0.45963305, -0.16073631, -0.015594818, 0.07035953, -0.16940016, -0.28909472, -0.017725285, -0.35240498, 0.30173686, 0.20117418) * go_0(1.0, 1.0);
    result += mat4(0.03129677, -0.04133618, -0.011259672, 0.03561297, 0.0852418, 0.04584553, 0.19103919, 0.09809102, -0.14594959, -0.4438363, 0.16297287, -0.20317835, 0.115456745, -0.06761671, 0.15409957, 0.04450018) * go_1(-1.0, -1.0);
    result += mat4(0.039826628, -0.45614466, 0.0642495, 0.05919764, -0.44811794, 0.30939403, -0.09915154, 0.1356114, 0.24242148, -0.5744648, 0.051002555, 0.2401494, -0.24656531, -0.025525048, 0.0022000005, 0.16019441) * go_1(-1.0, 0.0);
    result += mat4(-0.30609047, -0.44622147, -0.1323853, 0.27586594, 0.28131932, -0.1788347, -0.13601942, -0.056978267, 0.1390773, 0.023616405, 0.23695482, 0.014369665, 0.1065836, 0.2862605, 0.12936947, -0.08392774) * go_1(-1.0, 1.0);
    result += mat4(-0.21285766, -0.19791842, -0.08064578, -0.15698087, -0.6196114, -0.30824217, -0.048959345, 0.30395007, -0.41899, -0.3358852, -0.097170554, 0.28982377, 0.087944746, 0.15887393, 0.12179637, -0.33221152) * go_1(0.0, -1.0);
    result += mat4(-0.13241346, 0.035703655, -0.4474765, 0.110112734, -0.27055773, 0.41301596, -0.6500781, -0.15217184, -0.2048386, 0.011350564, -0.45242086, 0.4019483, -0.13381444, -0.34816414, -0.5594909, 0.06767518) * go_1(0.0, 0.0);
    result += mat4(-0.16038893, 0.035530727, -0.029575568, 0.4231352, 0.024787677, 0.63239074, -0.039876997, -0.025136393, -0.51243687, 0.05607693, -0.26631242, 0.089419514, -0.051774174, 0.08727033, -0.055868924, -0.0934304) * go_1(0.0, 1.0);
    result += mat4(0.08607903, 0.10347359, -0.08568057, -0.04361689, -0.09244961, 0.032459106, 0.07126668, 0.40926656, -0.17473985, -0.2854381, -0.07475363, -0.16183083, 0.22286943, 0.068349905, -0.07890174, -0.18732166) * go_1(1.0, -1.0);
    result += mat4(0.17825048, -0.31030193, -0.21215369, 0.015413245, -0.0980228, -0.3963089, -0.09465454, -0.39197174, 0.22134416, -0.10105557, 0.3249675, -0.027290137, -0.10875647, -0.2393993, -0.015305307, 0.21288091) * go_1(1.0, 0.0);
    result += mat4(0.26367134, -0.11709682, 0.10634492, -0.13768406, 0.5535611, 0.6967819, -0.31092402, -0.5262172, 0.14721805, -0.05149995, 0.22435789, -0.21493623, 0.27388602, -0.14029293, -0.1060113, 0.083680965) * go_1(1.0, 1.0);
    result += vec4(0.017177593, -0.03303642, 0.018293152, -0.0153594585);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_8_tf, gxy, result);
}