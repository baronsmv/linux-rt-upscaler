// Anime4K_Upscale_GAN_x2_S - Pass 14 of 17 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_12_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_13_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(0.122954965, 0.18889557, -0.050585095, -0.09285047, 0.041825704, -0.10147826, -0.0524878, 0.042394586, 0.26654795, -0.052367304, 0.32582784, 0.23248254, -0.18429202, -0.036516707, 0.034441825, 0.13747402) * go_0(-1.0, -1.0);
    result += mat4(0.39325443, 0.12691088, -0.14018032, 0.2601387, -0.0128762275, 0.09533191, -0.15545139, -0.064879976, 0.4752176, -0.46358192, -0.048625924, 0.07356933, -0.030162415, -0.09837143, -0.34081137, 0.09620003) * go_0(-1.0, 0.0);
    result += mat4(0.11647179, 0.020975508, -0.06064534, -0.1789612, 0.057696175, 0.11116113, -0.015037568, -0.024370348, -0.03656938, -0.2899815, -0.10285936, 0.055147626, 0.19246738, 0.30268162, -0.4149779, -0.0402745) * go_0(-1.0, 1.0);
    result += mat4(-0.009147066, -0.17453548, 0.23320405, -0.009745345, 0.080975994, 0.07396582, -0.13413322, 0.17224005, -0.19477916, 0.16737588, 0.5310824, -0.48741058, 0.3713329, -0.061815146, -0.19980642, 0.25318542) * go_0(0.0, -1.0);
    result += mat4(0.34857947, 0.09298978, 0.20253287, 1.0750674, 0.074417695, 0.15859176, 0.17113946, 0.3587233, -0.3720992, 0.5499863, -0.3334931, -0.7303378, 0.28977355, -0.40827954, -0.15625797, 0.44504634) * go_0(0.0, 0.0);
    result += mat4(0.00963027, -0.103650935, -0.15111534, -0.054710496, 0.068436116, -0.04733752, -0.014022155, -0.06435892, 0.46522453, 0.06746723, -0.13256127, -0.354952, 0.036626723, -0.2881872, -0.20110025, 0.18387023) * go_0(0.0, 1.0);
    result += mat4(-0.042692482, -0.08184722, 0.29142103, 0.10918554, 0.022569105, -0.03967552, -0.029662814, 0.16549924, -0.06727612, 0.49291298, 0.12881728, -0.02918886, -0.01579875, -0.12708642, -0.21163678, -0.24313599) * go_0(1.0, -1.0);
    result += mat4(-0.044082023, -0.047357306, -0.044077095, 0.20591871, -0.015887344, 0.05115381, -0.19811073, -0.035676513, 0.019275555, 0.4578326, 0.5141636, 0.0702626, 0.13119744, -0.17745942, -0.1892288, -0.062224492) * go_0(1.0, 0.0);
    result += mat4(0.06651709, -0.016656881, -0.0052546742, 0.014599082, -0.032204926, 0.09341175, -0.010483702, -0.04786155, 0.23358113, 0.13316281, 0.21748747, 0.04741849, -0.11040673, 0.06230487, 0.16795471, -0.104242735) * go_0(1.0, 1.0);
    result += mat4(-0.06844235, -0.01974277, 0.03758873, 0.0437811, -0.057502225, -0.076013766, 0.05226354, 0.16626364, -0.15094693, -0.06513261, -0.07178063, -0.25390542, -0.046331745, 0.048600584, -0.09498597, -0.029823082) * go_1(-1.0, -1.0);
    result += mat4(0.055906143, -0.09671702, -0.022703249, -0.074096285, -0.18490121, -0.14549334, 0.42093202, 0.087242134, -0.29526195, 0.31182536, 0.044069793, -0.17393354, -0.17096926, -0.15162584, 0.25237793, 0.047123164) * go_1(-1.0, 0.0);
    result += mat4(-0.0007076463, 0.0037513115, -0.044519257, 0.05986656, -0.12090617, 0.17659539, -0.07153321, 0.043799683, -0.050228495, -0.04225425, 0.24785443, 0.19911547, -0.05966556, -0.19790268, 0.20703633, 0.0048266468) * go_1(-1.0, 1.0);
    result += mat4(0.21739465, -0.046017647, -0.17681813, 0.21452186, 0.230653, -0.47062522, -0.23921433, 0.39329913, -0.036690675, 0.3303968, -0.47879925, -0.16289225, -0.1494594, 0.27207994, 0.1856394, -0.47609702) * go_1(0.0, -1.0);
    result += mat4(0.3214577, -0.023753606, 0.21297608, -0.7130707, 0.050221473, 0.9629573, 0.5004743, 0.10413513, 0.10723351, -0.07022509, 0.23218232, -0.5185978, -0.6921137, 0.0619471, 0.16877905, -0.60311705) * go_1(0.0, 0.0);
    result += mat4(0.0079998905, -0.066334635, 0.24110058, 0.06277327, -0.099571265, 0.28088686, 0.089555554, 0.049777288, -0.12143259, 0.19382764, 0.028673613, 0.14329565, -0.10053404, -0.07129261, -0.06196109, -0.54130787) * go_1(0.0, 1.0);
    result += mat4(0.0602462, -0.21520244, -0.17295553, 0.01296868, 0.09711833, 0.051904213, -0.20535164, -0.17658444, 0.27075645, 0.0784139, 0.13146368, -1.7129825e-05, -0.06117924, 0.24631894, -0.01026257, 0.0030612787) * go_1(1.0, -1.0);
    result += mat4(0.19062799, 0.122910775, 0.09640838, 0.06539721, 0.057701044, -0.20118104, -0.06261069, 0.107874714, 0.0973878, -0.20830666, -0.108459, -0.10059624, -0.08533175, -0.025608283, -0.07584223, -0.26741856) * go_1(1.0, 0.0);
    result += mat4(-0.1459836, -0.092159286, 0.05037609, 0.07709965, -0.18563168, -0.017586546, -0.16244653, -0.017426869, -0.20880185, -0.26068223, 0.037480514, 0.056800563, 0.14884543, 0.13592677, -0.1492276, 0.023280073) * go_1(1.0, 1.0);
    result += vec4(-0.03207076, 0.045260444, 0.040100798, -0.014172305);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_13_tf, gxy, result);
}