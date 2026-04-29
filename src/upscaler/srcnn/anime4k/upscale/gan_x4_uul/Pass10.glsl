// Anime4K_Upscale_GAN_x4_UUL - Pass 10 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.045708127, 0.042588994, 0.20735477, -0.051771507, 0.09030856, -0.018859424, 0.070019834, -0.12951517, -0.09864889, 0.0039071254, -0.2471996, -0.4045421, -0.13531524, 0.3199352, 0.18798132, -0.05220945) * g_0;
    result += mat4(-0.01900776, 0.14814821, -0.011676551, 0.05281246, -0.31253627, 0.07759687, 0.14841238, 0.15767692, 0.022344964, 0.03369595, 0.11200526, 0.24555564, 0.32339647, -0.08221667, 0.369651, 0.07480396) * g_1;
    result += mat4(0.15557157, -0.2438033, 0.2904723, 0.37869072, 0.031437404, -0.32791093, -0.30852196, 0.032672517, -0.29223853, 0.14301808, -0.13372968, -0.17571832, -0.24015012, -0.062435087, -0.5865883, 0.025141397) * g_2;
    result += mat4(0.018575411, -0.05546697, 0.0722868, -0.27057, -0.010986958, -0.1824116, 0.066343606, 0.1160373, 0.019109331, 0.1384729, -0.27752632, -0.09579411, 0.05585664, -0.16496943, -0.22690243, -0.035963364) * g_3;
    result += mat4(-0.24451451, 0.008807087, -0.050169405, -0.02992327, -0.029381998, 0.10529693, 0.3212115, 0.047833674, 0.19737382, -0.064389326, 0.07481576, 0.04658625, 0.16120902, 0.38747096, -0.017129492, 0.036965623) * g_4;
    result += mat4(0.024272425, 0.33644682, 0.57385606, 0.06969318, -0.18557239, 0.03263415, -0.098865986, -0.010410991, -0.27383336, 0.12643056, 0.13473713, -0.0072413897, 0.19951838, -0.26192865, -0.32222465, -0.03310627) * g_5;
    result += mat4(0.19670399, 0.21887897, -0.14813757, 0.13861343, -0.21291518, 0.11673954, -0.09706275, 0.1927499, 0.26426026, 0.15662387, -0.0998039, 0.20456441, 0.082849964, -0.3486019, 0.042286832, 0.111299105) * g_6;
    result += mat4(-0.17601213, 0.10744524, -0.13022378, -0.08145177, 0.17951357, -0.031804252, -0.11589841, -0.2375892, -0.17614031, -0.03204455, -0.3600058, -0.03791698, -0.18281102, -0.029681103, -0.5616249, -0.19369541) * g_7;
    result += mat4(-0.15129189, 0.062397495, -0.26206407, -0.35008666, 0.05224934, 0.32542625, 0.1367121, -0.06498142, 0.03794349, 0.10062078, 0.24966402, 0.16598183, 0.14065337, 0.021026433, 0.4124626, -0.04739923) * g_8;
    result += mat4(-0.42675805, -0.08062075, 0.24400486, 0.24982014, 0.013383713, -0.030127892, 0.21306989, -0.420491, 0.27569297, 0.1844745, 0.18380351, -0.007122975, 0.02176471, 0.11719434, 0.20086622, 0.09863608) * g_9;
    result += mat4(0.15059754, -0.060954567, -0.048324715, 0.06281138, -0.035452355, -0.105307326, -0.2821464, -0.17947711, -0.21891887, 0.31264433, 0.08331072, -0.23028368, -0.07125341, -0.25531566, -0.034880344, -0.10972097) * g_10;
    result += mat4(-0.26111153, -0.21509336, -0.40953597, -0.22704326, -0.06265872, -0.0076560513, 0.3454225, 0.036587927, -0.25836223, -0.017044103, -0.39408937, -0.04515616, -0.013889385, 0.21049121, -0.05811886, 0.11039355) * g_11;
    result += mat4(-0.5012236, -0.3288161, 0.76283616, -0.22785094, 0.15983264, 0.17595172, -0.19039781, -0.017620942, 0.088379174, -0.2810294, 0.14195396, -0.10567756, -0.26113996, -0.59151506, 0.064743236, 0.089407794) * g_12;
    result += mat4(0.09782677, 0.15405431, -0.38398, 0.025821349, -0.11564193, -0.2344232, 0.048547853, -0.0013135487, -0.021783575, -0.14494252, 0.10181801, 0.15313332, 0.22384043, 0.08691754, -0.18728645, 0.058859203) * g_13;
    result += mat4(0.30570078, 0.34977347, -0.2548985, 0.2440776, -0.12693292, 0.42302638, -0.2579403, -0.12731943, 0.02704416, -0.028827233, -0.103797026, 0.16991018, 0.18460067, -0.1430559, -0.40419313, -0.046166003) * g_14;
    result += mat4(-0.24799332, -0.4023106, 0.20775889, -0.1347491, 0.22718747, -0.5363376, -0.0045881635, -0.08498401, 0.12643133, -0.18700986, -0.031182116, 0.10537964, -0.12853408, 0.1540884, 0.14051637, 0.14159201) * g_15;
    result += vec4(-0.0549599, -0.005265513, 0.033013426, -0.018428912);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf1, gxy, result);
}