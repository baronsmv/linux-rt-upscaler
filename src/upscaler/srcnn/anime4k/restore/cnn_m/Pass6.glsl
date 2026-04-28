// Anime4K_Restore_CNN_M - Pass 6 of 8 - https://github.com/bloc97/Anime4K
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
vec4 result = mat4(0.15332128, 0.027258258, 0.14900503, -0.15982795, 0.17021236, -0.51046044, -0.15287271, -0.058167327, 0.51826185, -0.34817994, 0.004513167, 0.05395769, 0.1990321, -0.049979225, 0.11391989, -0.16062729) * go_0(-1.0, -1.0);
    result += mat4(0.033682905, 0.019728886, 0.19931756, 0.17381927, 0.2585768, -0.2124572, -0.014632459, 0.39779893, -0.1146207, -0.2396625, 0.08960277, 0.38345298, 0.25497693, 0.11692859, -0.14207517, 0.12667973) * go_0(-1.0, 0.0);
    result += mat4(-0.14911255, 0.08910706, 0.16136818, 0.03914566, 0.24204038, -0.03607149, -0.4571109, 0.10802461, -0.0021356856, 0.00885878, 0.22297303, 0.2367231, 0.045177583, 0.11120606, -0.009971904, -0.059262395) * go_0(-1.0, 1.0);
    result += mat4(0.24565999, -0.2261384, 0.47373205, 0.024613412, -0.10923052, 0.039027315, -0.42707404, -0.3783373, 0.3544573, -0.5468578, -0.27599156, -0.09455918, 0.18760219, -0.19082001, 0.030565469, 0.20589156) * go_0(0.0, -1.0);
    result += mat4(0.1973198, -0.03433863, 0.059960485, 0.045642868, 0.1819595, -0.14460869, 0.1286175, 0.2067575, -0.042632047, -0.11842967, -0.11224446, -0.18764776, -0.19563004, 0.027425969, 0.24056377, 0.5949649) * go_0(0.0, 0.0);
    result += mat4(0.055027682, 0.16331595, -0.2608588, 0.12545955, 0.4588985, 0.03642909, 0.22187738, 0.45190734, -0.001210133, -0.057651415, -0.061199043, 0.11935476, -0.049561135, 0.27509886, 0.13778673, -0.124914035) * go_0(0.0, 1.0);
    result += mat4(-0.02257459, 0.27705106, 0.044165276, -0.26521233, 0.05982374, -0.2824302, 0.3171142, 0.08430561, -0.10155528, 0.16182268, -0.09183147, -0.19447176, 0.3295707, -0.50616395, -0.036964044, 0.23166709) * go_0(1.0, -1.0);
    result += mat4(-0.0232342, 0.07299799, -0.18038079, -0.13672702, -0.108305976, 0.15024792, -0.19531927, 0.0870979, -0.26488534, 0.19481428, 0.10737945, -0.14573483, -0.33094683, 0.24155116, -0.09850332, 0.2797003) * go_0(1.0, 0.0);
    result += mat4(-0.24089853, 0.19506595, 0.4799156, -0.058313113, 0.36212957, -0.44844806, 0.23864488, 0.15477742, -0.07795971, -0.0033861927, -0.11216164, 0.033454563, -0.25893036, 0.23793478, -0.15769425, -0.00033481256) * go_0(1.0, 1.0);
    result += mat4(0.05772507, -0.1640253, -0.13499664, -0.20460358, -0.024399966, 0.14966168, -0.090857334, -0.039677754, 0.00036956606, -0.24236615, -0.053542696, -0.0049544116, 0.026651502, 0.39019194, -0.2742246, -0.061242323) * go_1(-1.0, -1.0);
    result += mat4(-0.016323274, -0.036179908, 0.029965919, 0.11151491, -0.00016685206, -0.29573023, 0.17996423, -0.20145437, 0.1324275, -0.18442132, -0.24618152, 0.061780427, -0.02770517, 0.28452995, 0.39804098, -0.1174389) * go_1(-1.0, 0.0);
    result += mat4(-0.025068847, -0.053328387, -0.27053785, 0.26866457, -0.09866204, 0.057677213, 0.01850112, -0.18014707, -0.13319959, -0.14411181, -0.26355243, -0.022209354, -0.05062645, -0.036771543, 0.13294417, -0.18458557) * go_1(-1.0, 1.0);
    result += mat4(-0.046194963, 0.038230438, -0.08993043, -0.07236354, 0.11031123, -0.16504908, -0.09517036, -0.16459833, -0.5279925, 0.12686682, -0.05726125, 0.055361677, 0.31593755, 0.027328093, 0.001839602, 0.30581662) * go_1(0.0, -1.0);
    result += mat4(0.08608678, 0.03168437, 0.007713377, -0.26140293, -0.1268983, 0.13395861, -0.069848835, -0.24080403, 0.018839337, -0.049821075, -0.21461345, -0.14168301, -0.0872339, 0.47096667, 0.022512507, 0.14860632) * go_1(0.0, 0.0);
    result += mat4(0.06293673, 0.22462969, 0.045494985, 0.021673543, 0.18227446, -0.2956555, 0.08010543, -0.01919729, -0.012190269, 0.241983, -0.046537094, -0.40094566, -0.3853647, 0.1081711, -0.16926058, 0.16138376) * go_1(0.0, 1.0);
    result += mat4(-0.14854589, -0.17625804, -0.10849075, 0.221543, 0.099971965, 0.13901573, 0.29464146, 0.020068526, 0.054358527, -0.10351705, -0.0062914286, 0.24127026, -0.16914125, 0.12729423, -0.18377453, -0.6452375) * go_1(1.0, -1.0);
    result += mat4(0.12603393, -0.10986093, 0.2314103, 0.16915044, -0.13619255, -0.09349073, 0.20594226, -0.34507084, 0.19077192, 0.052500796, 0.07185645, 0.029082738, -0.015576321, 0.08254907, -0.5501743, -0.38495848) * go_1(1.0, 0.0);
    result += mat4(0.09300796, -0.079218306, 0.46825135, -0.08735625, 0.06321122, 0.16234867, 0.042932414, -0.013057422, 0.09697148, 0.23457524, 0.19417483, -0.16804664, 0.18379296, 0.17770062, -0.050235, -0.059676602) * go_1(1.0, 1.0);
    result += vec4(0.011169491, 0.032399546, 0.138099, 0.023857072);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_5_tf, gxy, result);
}