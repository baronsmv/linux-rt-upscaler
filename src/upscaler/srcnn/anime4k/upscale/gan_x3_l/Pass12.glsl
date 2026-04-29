// Anime4K_Upscale_GAN_x3_L - Pass 12 of 30 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_3_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.12407633, -0.027812717, 0.23094666, 0.060302667, -0.16624144, -0.0007371851, -0.28186718, 0.22369424, 0.022404855, 0.09096415, 0.0017822908, 0.336001, -0.09130467, 0.034111694, 0.19113103, -0.14513424) * g_0;
    result += mat4(-0.014768806, -0.31290373, 0.015769936, -0.13507901, -0.010203078, 0.4945444, -0.01088852, -0.1582938, -0.14903755, -0.1840089, -0.009966903, -0.19425109, -0.21303283, 0.26285252, -0.046254523, -0.15465552) * g_1;
    result += mat4(0.07533467, 0.26080438, 0.024856985, 0.34277654, -0.3129344, 0.30575162, 0.06931557, -0.044698272, 0.18042412, 0.45999247, -0.5192437, 0.022618707, -0.020097036, -0.27706465, -0.0050434433, -0.12770803) * g_2;
    result += mat4(0.098648146, -0.21701503, 0.10266521, -0.085537605, 0.02402345, -0.28643832, 0.19378376, -0.12658586, 0.115897186, 0.01580828, 0.11827048, 0.29019687, -0.19341177, 0.09564265, 0.03476779, 0.11699004) * g_3;
    result += mat4(0.058346223, 0.25530934, -0.026972264, 0.3190419, 0.12263199, 0.124316074, 0.04734691, 0.011293402, -0.17419139, -0.15893947, 0.093723476, 0.23282392, 0.19400646, -0.0533148, 0.026266033, 0.19663234) * g_4;
    result += mat4(-0.06663804, 0.20435949, 0.044924624, -0.24982749, 0.20327586, 0.12442739, -0.3155765, -0.18541007, 0.18991531, -0.19276267, 0.21697456, 0.03178544, -0.3381796, -0.15325621, -0.25820518, -0.07297032) * g_5;
    result += mat4(0.098007046, -0.17018083, 0.3390076, -0.2280134, 0.12989196, -0.044336785, -0.10702673, -0.37464848, 0.028437488, 0.24224928, -0.107826136, 0.0031239046, -0.34256136, -0.17936559, 0.091159485, -0.054418396) * g_6;
    result += mat4(0.053965975, -0.17428857, -0.43524495, -0.15119378, -0.25487635, 0.16371927, 0.1467712, -0.08216164, -0.5624722, -0.11886804, -0.058240388, 0.17669299, -0.15173754, 0.13094892, 0.39045286, -0.017048221) * g_7;
    result += mat4(-0.15798661, -0.36355045, 0.1957264, -0.05392931, 0.098283805, 0.14677107, 0.16887192, -0.11125151, -0.113571666, 0.15960959, -0.09331763, -0.032195523, 0.17286941, 0.33965907, 0.09051416, -0.25542957) * g_8;
    result += mat4(0.16866244, 0.05636189, -0.100324616, 0.20495924, -0.102705345, -0.08387417, -0.09328024, 0.21541446, 0.1430065, 0.0308464, -0.0793588, -0.029477509, -0.28854427, -0.29555637, 0.33754608, -0.18144317) * g_9;
    result += mat4(-0.11338383, 0.019528843, -0.24414338, -0.36290777, 0.54908705, -0.083018646, 0.007534378, -0.1406417, 0.37853354, 0.09911941, -0.047861155, -0.3186758, 0.2125856, -0.114667036, -0.07411896, 0.050717812) * g_10;
    result += mat4(0.2961511, 0.28937215, -0.36593223, -0.16141813, -0.087650776, -0.47516292, 0.0052091824, 0.033959586, -0.06072628, -0.0012637508, -0.037578013, -0.35235298, 0.11726439, 0.6064031, 0.34058803, 0.45300734) * g_11;
    result += vec4(-0.0038817346, -0.052502215, 0.008882693, -0.017785465);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf1, gxy, result);
}