// Anime4K_Upscale_GAN_x4_UUL - Pass 30 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_6_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_6_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_6_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_8_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_9_tf5;
#define g_0 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_6_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_6_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_6_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_6_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_6_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_6_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_6_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_6_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_8_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.1922669, 0.08802744, -0.028858658, 0.0018137145, 0.049583502, 0.054931905, 0.06461622, -0.1545738, -0.24787578, -0.3030694, -0.43755215, -0.08891142, -0.0072859223, 0.33978176, -0.08431318, -0.074049324) * g_0;
    result += mat4(0.12638506, -0.1162002, -0.13160661, -0.07876044, 0.0991572, 0.15431085, -0.014509431, -0.021629302, -0.03953747, -0.121313706, 0.11476493, -0.21827452, -0.055972893, -0.21574646, 0.013953077, 0.008131167) * g_1;
    result += mat4(0.22515556, -0.38520855, 0.08868661, 0.072899625, -0.0066298717, 0.17697194, 0.16426025, -0.047008827, 0.0667103, -0.20082757, -0.022680001, -0.13906951, -0.11068086, -0.18871038, -0.14856437, -0.22906394) * g_2;
    result += mat4(0.06496998, 0.33180842, 0.035600964, 0.008669803, -0.21089098, 0.024426313, 0.097489424, 0.19989817, 0.09799698, -0.19460952, 0.31317624, -0.054178897, 0.06745894, 0.24180534, -0.18725993, -0.09876676) * g_3;
    result += mat4(-0.14159264, -0.09821653, 0.111369886, -0.13888422, 0.19065087, -0.052074507, 0.25994346, -0.09896752, 0.009669414, 0.3327987, -0.03835561, 0.1502805, 0.06749692, -0.25075352, 0.1176795, 0.2861322) * g_4;
    result += mat4(0.08663468, -0.09579272, 0.15255743, 0.11586089, 0.096744135, -0.106523454, -0.23779331, -0.039372843, -0.044640735, -0.073639855, -0.09300802, -0.016469873, -0.017932354, -0.15118197, 0.07342249, 0.08470412) * g_5;
    result += mat4(-0.22996324, 0.2121147, -0.042765424, 0.29991713, -0.1105575, -0.22186373, -0.099884614, 0.28284577, 0.019985273, 0.18109971, 0.067379884, -0.05751364, -0.14203605, -0.1606955, -0.04072121, 0.14415282) * g_6;
    result += mat4(-0.010768784, 0.013500415, -0.05128568, -0.20169108, 0.21437442, -0.2470299, 0.0067167566, 0.3354006, 0.29098728, 0.3001768, 0.11471926, -0.34384128, 0.013220707, -0.21317835, -0.007173589, 0.056399934) * g_7;
    result += mat4(-0.25603592, 0.008419834, 0.035636842, -0.07926287, 0.05415962, -0.24778326, -0.24242976, 0.20616682, 0.13446097, -0.26829332, -0.043394912, -0.15304199, 0.26440972, -0.28728306, 0.0017775068, -0.031716976) * g_8;
    result += mat4(-0.2344917, -0.061300833, 0.40446028, 0.42343828, -0.2158991, 0.39550748, 0.13935845, -0.15041998, 0.13921916, 0.18082108, 0.04385846, 0.142258, -0.21331908, -0.26960972, 0.031336915, 0.23779747) * g_9;
    result += mat4(0.06346781, 0.07501524, -0.20003422, -0.115085386, -0.027196221, -0.027326047, 0.0592106, -0.23421998, -0.003150606, -0.31265986, 0.088709556, -0.10167917, -0.14837898, 0.37943587, 0.1447625, 0.080040015) * g_10;
    result += mat4(-0.15046267, 0.265076, -0.19776449, -0.20232256, 0.06413749, 0.26056677, 0.079985835, -0.23233825, -0.24333598, -0.18887608, -0.16819565, 0.047695916, 0.010287012, 0.3019047, 0.148884, -0.10863938) * g_11;
    result += mat4(-0.0018880082, -0.2375455, 0.41955757, 0.01565566, 0.0898848, 0.028822318, -0.1900471, 0.15390472, -0.07475509, 0.028788034, 0.14377898, -0.018586636, 0.15499766, -0.0181846, -0.1712958, 0.26694313) * g_12;
    result += mat4(-0.019247968, -0.22267476, -0.20527479, -0.05516891, -0.10443534, 0.0013541149, -0.35172266, 0.08538575, 0.033067722, -0.18152483, -0.23448412, -0.02623179, -0.13003229, 0.13998169, 0.0376709, -0.19369106) * g_13;
    result += mat4(0.3118797, 0.082491405, -0.34785077, -0.22611658, -0.07956514, 0.11574769, 0.16532372, -0.2226821, 0.06791281, -0.098187685, -0.08020048, 0.12613155, -0.2472526, -0.27066618, -0.139881, -0.18741405) * g_14;
    result += mat4(-0.12976451, 0.14284736, 0.19006614, 0.07724795, 0.062145814, -0.36040485, -0.25726667, -0.04952468, 0.02644045, 0.044718564, 0.27806777, -0.048151493, -0.06354555, -0.0005565615, 0.14224754, 0.17653286) * g_15;
    result += mat4(-0.17252563, 0.023060834, 0.02491499, 0.19027406, -0.212846, -0.01613939, -0.068693444, -0.14507875, -0.08602362, 0.02112319, 0.19688891, 0.28616062, 0.12502767, -0.16866814, 0.096094206, -0.087079056) * g_16;
    result += mat4(-0.0105957305, -0.00042306812, -0.073753655, 0.2258738, 0.015042403, 0.26525986, 0.09652541, 0.33078325, -0.054301977, -0.14386192, -0.09737477, -0.1822451, -0.07917178, 0.012320757, -0.1526825, -0.08518065) * g_17;
    result += mat4(-0.053449947, -0.26979092, 0.21039961, 0.0002728565, 0.1097202, -0.004250707, -0.038437147, 0.27996743, -0.046362147, -0.021696959, 0.077650055, -0.07844942, -0.10120125, 0.08145741, 0.10650856, 0.0026023765) * g_18;
    result += mat4(0.24465938, -0.095935315, -0.21770145, -0.24916768, 0.13544445, -0.013464758, 0.13948593, -0.123387456, 0.14965056, -0.027013663, 0.3156395, -0.06620409, 0.07764431, -0.14184502, -0.23861314, 0.11016456) * g_19;
    result += vec4(0.05315733, 0.009354445, 0.074799225, 0.048262358);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf5, gxy, result);
}