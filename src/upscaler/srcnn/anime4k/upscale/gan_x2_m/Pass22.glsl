// Anime4K_Upscale_GAN_x2_M - Pass 22 of 23 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_12_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups2;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.22553514, -0.086349756, -0.07735866, 0.48776403, -0.33010843, 0.28214008, -0.2242988, -0.11439686, -0.14720698, 0.2391116, 0.017813087, 0.4352493, -0.16412133, -0.12791261, -0.019643517, 0.19420698) * g_0;
    result += mat4(-0.9178235, -0.6335296, 0.11146894, -0.0759723, -0.4519685, -0.3007054, 0.014501872, 0.49081457, 0.10673664, 0.035011876, 0.10259641, 0.106546804, 0.5186602, 0.44900152, 0.20597687, -0.39562696) * g_1;
    result += mat4(-0.11399027, -0.19542706, 0.087422565, -0.70140034, -0.41029623, -0.049330976, 0.19682989, 0.22516033, -0.22858454, -0.12200487, -0.14852463, -0.40852943, -0.035900578, 0.1886829, 0.019452838, -0.16703403) * g_2;
    result += mat4(0.077843145, 0.7323388, -0.022324003, 0.09445821, 0.026166735, -0.1790519, 0.086004496, -0.40011314, 0.01210975, -0.053515363, -0.2501869, 0.06671936, -0.71530163, -0.57196116, -0.38604704, 0.5024949) * g_3;
    result += mat4(0.30748057, 0.12223383, 0.059069566, 0.18568543, 0.008148904, 0.009438993, 0.053996127, -0.19665428, 0.38345802, 0.20945628, 0.01368962, -0.2834185, -0.15974379, -0.4628119, -0.18307796, 0.22361058) * g_4;
    result += mat4(0.00833237, -0.10446639, -0.028896136, -0.18917766, -0.24016596, -0.034934085, -0.013062447, 0.079293504, -0.16635038, -0.11056953, 0.2618598, 0.07227063, 0.057050053, 0.013885738, 0.09385356, -0.27068567) * g_5;
    result += mat4(-0.5675842, 0.13328329, -0.0252242, 0.34746942, 0.34712863, 0.13635597, 0.02356317, -0.1617803, -0.16861948, -0.018621348, 0.02680753, 0.30408886, -0.034069773, 0.08948961, -0.057724215, 0.111602895) * g_6;
    result += mat4(-0.03835732, -0.11742271, 0.025922403, 0.24378933, -0.36450952, -0.15091905, 0.1214089, 0.21004228, 0.28717628, 0.17053549, 0.10836553, -0.08449643, 0.17507422, -0.03195037, -0.03947606, 0.050725944) * g_7;
    result += mat4(-0.21257977, -0.0043600267, -0.12929972, -0.233982, -0.26728988, -0.21511734, 0.07835361, -0.24275993, -0.359975, -0.23956355, -0.07852281, 0.40282407, 0.17184453, 0.11672362, 0.0433819, -0.032416925) * g_8;
    result += mat4(0.20235331, 0.16114245, 0.015931258, -0.17612378, 0.2449233, 0.0031623375, -0.2784109, 0.3347522, 0.46005112, 0.20291579, 0.13030154, -0.23390344, -0.39526668, -0.09738018, 0.013237711, 0.15512206) * g_9;
    result += mat4(-0.1434995, -0.12447443, 0.095140964, -0.08841888, -0.05424789, -0.11747197, -0.097216785, 0.12958516, 0.34194428, 0.111434594, -0.02794559, -0.22843723, -0.043816507, -0.16116165, -0.29044297, 0.33768278) * g_10;
    result += mat4(0.39615574, 0.05410518, -0.07885892, -0.22024721, 0.011598219, 0.1446308, 0.11650995, -0.020602686, -0.51892537, 0.14221898, -0.01697185, 0.05188913, 0.07683384, 0.122416414, 0.02296055, 0.2932525) * g_11;
    result += mat4(-0.058334768, -0.12389275, -0.02024463, 0.46323973, 0.17553197, 0.35435143, 0.19796194, 0.06836581, 0.15947883, -0.056819815, -0.091066726, 0.22499265, -0.21629064, -0.22203816, 0.053594038, 0.09816408) * g_12;
    result += mat4(-0.016514458, -0.14323495, 0.017527288, -0.19750872, -0.47891942, -0.073656894, -0.086305656, 0.38173944, 0.1016976, 0.15224999, 0.048396923, -0.19529565, 0.13985658, 0.07292602, 0.06549534, 0.210662) * g_13;
    result += mat4(0.3459035, 0.0071707424, -0.019186711, 0.2527976, 0.29675815, 0.35949966, -0.06114439, -0.02610484, 0.5475115, -0.13828747, 0.019238133, 0.101953685, -0.52718824, 0.017254699, 0.08887026, -0.19507161) * g_14;
    result += mat4(-0.3064509, -0.031613164, 0.040971015, -0.24252266, -0.21725285, -0.35069898, 0.0951283, -0.065222666, -0.98867434, 0.08824426, 0.06094605, -0.21000125, -0.72066385, -0.34141323, 0.049487203, 0.0690126) * g_15;
    result += vec4(0.25545248, -0.112931795, -0.073284395, 0.29349956);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups2, gxy, result);
}