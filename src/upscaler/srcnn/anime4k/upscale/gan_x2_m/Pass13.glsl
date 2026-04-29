// Anime4K_Upscale_GAN_x2_M - Pass 13 of 23 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_2 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.13591515, 0.21395922, 0.040862843, 0.3054825, -0.088837944, -0.6928339, -0.15643471, 0.13081591, 0.07604966, 0.37446347, -0.34723157, -0.17870799, -0.2037286, -0.106576756, 0.25523958, -0.13762575) * g_0;
    result += mat4(0.21503459, 0.0373132, -0.008046219, -0.18440363, -0.09729587, 0.043958187, 0.23459528, -0.044009138, 0.1686642, -0.1615934, -0.13173419, -0.079085656, -0.07647595, -0.37286422, -0.06148421, 0.015342882) * g_1;
    result += mat4(-0.14785692, -0.2707874, -0.017647093, -0.2908642, 0.5612585, 0.4271698, -0.48191005, 0.11905855, -0.21741737, -0.2821245, 0.29278705, -0.20538986, 0.03150152, 0.03138199, 0.10423793, -0.045527548) * g_2;
    result += mat4(0.31277063, 0.07915742, -0.34087706, 0.39680582, -0.022496004, -0.33672526, -0.111507386, 0.025953399, -0.15757395, 0.11465282, 0.28329894, 0.12420795, -0.36261007, 0.46334505, 0.30303243, -0.03249052) * g_3;
    result += mat4(0.57927984, 0.06878386, -0.24236098, 0.31338137, 0.10464923, -0.07153124, 0.13588428, -0.02373762, -0.19124955, -0.1138502, 0.17388438, 0.01707623, -0.24228282, 0.04736911, 0.6398566, -0.32334659) * g_4;
    result += mat4(-0.54402775, -0.24674532, 0.11212342, -0.09593871, -0.17339998, 0.1323692, -0.1680261, 0.025882099, -0.19121705, 0.1832492, -0.08548955, -0.14068407, 0.13255714, 0.10409962, -0.01394588, 0.22216345) * g_5;
    result += mat4(0.2702694, -0.56255573, -0.5357781, 0.05541389, 0.070275396, -0.08012564, -0.13473864, -0.113696516, 0.06642909, 0.23810093, 0.0728827, -0.17656006, 0.48172018, -0.25749484, -0.1752313, 0.33768335) * g_6;
    result += mat4(0.46950498, 0.059317388, -0.09860531, -0.006304164, -0.4128484, -0.049649406, 0.2954393, -0.190237, -0.20938443, 0.034176145, 0.063109055, 0.07802573, -0.20652357, -0.23180202, -0.11936575, 0.2589604) * g_7;
    result += mat4(0.3843954, -0.08686217, 0.18839231, 0.01876761, -0.03335079, -0.12043262, -0.42323095, -0.02321388, -0.22252762, -0.049455926, 0.2268798, 0.082169, 0.2473631, 0.23347862, 0.002254042, 0.2757807) * g_8;
    result += mat4(0.1020188, -0.037612554, -0.33062017, 0.1570476, 0.19851524, 0.35976177, -0.016449552, 0.22057539, 0.20401593, 0.07004227, -0.062413715, -0.10547836, 0.14671406, -0.3905135, -0.038352408, -0.28926837) * g_9;
    result += mat4(0.4110517, 0.06280497, 0.16709873, -0.49500167, -0.10045096, -0.2238529, 0.012172345, 0.19666891, -0.16135901, 0.017100533, 0.35809904, 0.35188627, 0.20347194, -0.14602524, 0.71737736, 0.14195462) * g_10;
    result += mat4(-0.5236819, 0.4352016, -0.4066126, -0.04252335, 0.1086945, 0.145471, 0.21984594, -0.24670586, -0.07109616, -0.2711473, -0.89353126, -0.3953869, 0.17096898, 0.12978637, -0.42527854, -0.019720567) * g_11;
    result += vec4(-0.027689768, -0.16386859, -0.009289161, 0.09287236);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf, gxy, result);
}