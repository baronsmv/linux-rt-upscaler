// Anime4K_Upscale_GAN_x2_S - Pass 16 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups1;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.10813235, 0.05466766, -0.20426773, 0.03014769, -0.23742639, -0.18808678, -0.08507936, 0.11070251, -0.24421449, -0.047370236, -0.034263644, -0.36471045, 0.022079159, -0.13425855, -0.43840396, 0.14318791) * g_0;
    result += mat4(0.006743051, 0.07216438, 0.14125177, 0.06620228, 0.42031923, 0.2496421, -0.07731219, -0.013831615, 0.15525927, 0.090886295, 0.019504324, -0.048566148, -0.21346657, 0.022109412, 0.26717573, -0.11774596) * g_1;
    result += mat4(-0.28528357, -0.17186452, -0.20616518, 0.034786828, -0.10506841, -0.12335915, 0.07619831, -0.23998813, 0.19965814, 0.103892386, 0.04367025, -0.19183081, -0.16918147, -0.056264214, 0.20310691, 0.3341895) * g_2;
    result += mat4(0.20581162, 0.02040467, 0.35530564, -0.15494272, -0.010262163, 0.07301455, -0.074129246, 0.17339204, -0.00919498, -0.11473048, 0.042003002, -0.050515488, 0.24150477, 0.14734265, -0.102072336, -0.03404688) * g_3;
    result += mat4(-0.022791447, -0.005725081, 0.057149626, 0.013613261, 0.017012713, 0.0022030922, 0.06826359, -0.1473429, -0.055662345, 0.015804563, 0.07033723, 0.0380571, -0.030761583, -0.06867299, -0.0004780991, -0.10686876) * g_4;
    result += mat4(0.11448204, 0.08165584, 0.56496936, 0.2275344, 0.050801918, 0.115319155, 0.11518415, 0.05895198, 0.06831797, 0.08119943, 0.34825838, -0.048232127, 0.028284775, -0.03452888, 0.1979006, -0.041894354) * g_5;
    result += mat4(0.11946663, 0.03388757, -0.13882776, -0.14631757, -0.07182763, -0.08768853, 0.14146432, 0.10330784, -0.012143934, -0.022009725, -0.15579993, -0.050503176, -0.016312446, -0.054338187, -0.07755307, -0.07889432) * g_6;
    result += mat4(-0.02631465, 0.05617023, 0.13298586, 0.045326687, -0.11627329, -0.087329924, -0.05144727, -0.13488398, 0.06281482, 0.054220017, 0.25243595, 0.002556835, -0.03581036, 0.10341262, 0.10574532, 0.15461436) * g_7;
    result += mat4(0.07718563, 0.038919166, -0.06910819, -0.059710544, -0.09481636, -0.1109951, 0.5187051, 0.045543563, -0.048131686, 0.072409846, 0.4892963, -0.086976275, -0.07343929, -0.12501429, 0.26566443, 0.08579102) * g_8;
    result += mat4(0.005692247, 0.042074066, 0.13430944, 0.10093059, 0.023651319, 0.019474167, -0.13077211, -0.07782639, 0.072300054, 0.011820138, -0.1379879, -0.033925157, 0.012152839, 0.005247593, 0.15555158, -0.10433893) * g_9;
    result += mat4(-0.14903626, -0.0649052, 0.103872776, 0.18057188, 0.02891697, 0.13026263, 0.45847327, 0.09324349, -0.039312128, -0.05299939, 0.4332103, -0.25727344, 0.006733611, 0.05955007, 0.24531682, 0.053989712) * g_10;
    result += mat4(0.111072116, 0.11529407, -0.26600304, -0.032266896, 0.09633932, 0.0094333775, 0.060893714, -0.08118885, -0.03830528, 0.0037902966, -0.11128639, 0.13511918, 0.06553124, 0.054722965, 0.08178846, 0.06025588) * g_11;
    result += mat4(0.095904954, 0.0008960944, 0.35145932, 0.28108585, -0.011538731, -0.09239871, -0.21972048, -0.0820484, 0.112448506, -0.10381135, 0.09701949, 0.023723679, 0.04458077, 0.04700858, -0.056815177, 0.33785793) * g_12;
    result += mat4(0.08533725, 0.05978557, -0.40020186, -0.13684823, -0.0074113654, 0.1310689, 0.12906975, 0.11596462, 0.007170312, 0.13460107, 0.08450185, -0.019635776, 0.0966497, 0.021586724, -0.06784809, 0.12102399) * g_13;
    result += vec4(-0.032370187, 0.008661155, 0.020123083, 0.04574251);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups1, gxy, result);
}