// Anime4K_Upscale_GAN_x3_VL - Pass 11 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf;
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
vec4 result = mat4(0.26761916, -0.24422711, 0.21467628, -0.14429939, -0.16867152, 0.019657448, 0.13460818, -0.20023769, -0.11340837, 0.08858731, -0.13437305, -0.35356593, -0.166875, -0.3335764, -0.30487195, -0.18249014) * g_0;
    result += mat4(0.0103351595, 0.019523615, -0.085381895, 0.023507696, -0.06509177, -0.17890798, -0.106904104, 0.4792868, -0.16292045, 0.010498117, 0.119574495, -0.27299005, 0.03395923, 0.026821606, -0.41253936, -0.08301559) * g_1;
    result += mat4(0.26279557, -0.2541165, -0.18392049, -0.21962899, -0.14001782, -0.23177835, -0.022218328, -0.1427412, 0.091821305, 0.10855345, 0.44959477, 0.058340758, -0.24799977, 0.3565854, 0.013265246, 0.055574704) * g_2;
    result += mat4(-0.30022192, 0.09299804, -0.023125056, -0.123527065, 0.4004787, 0.08056971, -0.09605205, -0.121825874, 0.38889158, -0.1483759, 0.13983476, 0.29878005, -0.20108524, 0.1961977, -0.47242287, -0.06553211) * g_3;
    result += mat4(0.17079045, 0.08361359, 0.009484214, 0.1707653, -0.087261476, -0.087097056, -0.012763265, 0.29483643, -0.28490525, -0.3195555, -0.08523994, 0.12864676, 0.06112412, 0.06797802, 0.40068462, 0.11056894) * g_4;
    result += mat4(-0.13525724, 0.22686912, 0.28670293, 0.35410637, 0.25993523, -0.1638555, -0.17513171, 0.17038722, -0.044490904, 0.1274143, -0.025726566, -0.19816703, -0.29416955, -0.06961644, 0.030743139, 0.11367489) * g_5;
    result += mat4(0.18545562, -0.06487542, 0.33482194, -0.24661279, -0.32046458, 0.3974365, 0.23327115, -0.20816243, -0.121703945, -0.13698983, 0.037402794, -0.3681139, 0.2559689, 0.0068038814, 0.15202744, 0.28728062) * g_6;
    result += mat4(0.09979532, -0.014131657, -0.10398607, 0.2152131, -0.14150284, -0.05365564, -0.271173, -0.3405926, -0.11394731, -0.016010681, 0.25552076, 0.37970966, -0.2593704, 0.1591259, -0.25309658, -0.12218305) * g_7;
    result += mat4(0.1692998, 0.067247115, 0.12935598, -0.12525293, 0.32433978, -0.34517387, -0.069578916, -0.23326226, -0.064913265, 0.2855713, 0.20725873, -0.0967844, 0.083778754, 0.12616636, 0.018192552, 0.12799433) * g_8;
    result += mat4(-0.33400214, 0.22635528, -0.19802323, -0.047504075, 0.16644837, 0.04351617, 0.36790857, 0.08537014, -0.14359091, -0.1098514, 0.17290404, 0.15990348, -0.071987584, -0.05375565, 0.18347272, 0.08445061) * g_9;
    result += mat4(-0.0017842463, 0.11356512, -0.23591736, -0.25712514, -0.006414402, 0.4143378, 0.1908977, 0.52574486, -0.11780233, -0.16473259, 0.060708508, -0.054775394, -0.09365787, 0.2175931, 0.2067786, 0.34738192) * g_10;
    result += mat4(0.5713227, -0.43584484, 0.002311247, 0.35608718, -0.23530786, 0.031132858, 0.25841874, -0.1973695, -0.13229723, -0.1728666, 0.0757621, -0.29117447, -0.08741721, 0.13616516, -0.30073285, -0.18420693) * g_11;
    result += vec4(-0.021890169, -0.026031738, -0.06421138, -0.055722203);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, gxy, result);
}