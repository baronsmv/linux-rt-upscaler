// Anime4K_Upscale_GAN_x4_UUL - Pass 18 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_3_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_3_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_3_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf1;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_3_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_3_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_3_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_3_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_3_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_3_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.028307766, 0.35418066, -0.08265425, 0.0524958, -0.052733433, -0.23152119, 0.060992382, 0.13296764, 0.20385887, 0.20722593, -0.18456522, -0.06654151, 0.073012725, 0.1738478, -0.081442595, -0.09303688) * g_0;
    result += mat4(-0.0879442, 0.117100604, -0.2022827, 0.2498845, -0.13747723, 0.012266356, 0.07140362, -0.17850813, -0.15422471, 0.06091594, -0.25272366, 0.06035512, -0.043132532, 0.14852233, -0.07621397, 0.15171692) * g_1;
    result += mat4(-0.020322306, -0.045558915, -0.04046774, 0.12558004, -0.36567464, -0.2146117, -0.014710619, 0.06968004, -0.18818662, -0.07847737, -0.03947554, -0.082270905, -0.1513966, -0.3303706, 0.15264171, -0.22679567) * g_2;
    result += mat4(-0.08894719, 0.12672763, 0.21034755, 0.07608016, 0.164807, 0.2194763, -0.0050431606, 0.2508391, 0.21810757, -0.12751459, 0.33856523, 0.119690664, 0.16341431, -0.11109964, -0.27633113, 0.017533202) * g_3;
    result += mat4(-0.06003009, -0.21883024, 0.1129707, 0.18688855, -0.25084695, -0.123959206, -0.044746067, 0.05043674, -0.20955594, -0.016574647, 0.2791325, 0.07776435, -0.23383816, -0.13642253, -0.1239683, -0.06908085) * g_4;
    result += mat4(0.065739244, 0.33356935, 0.046213064, -0.5236776, 0.13756007, 0.24683417, 0.20376736, 0.18232968, -0.044425983, 0.18467174, 0.33787662, 0.30031878, -0.07485783, 0.004371367, -0.06572547, -0.032950997) * g_5;
    result += mat4(0.29744133, -0.12391908, -0.22200936, -0.12863474, -0.121608935, -0.04758852, -0.12311768, -0.12681226, -0.2310094, -0.39655608, 0.19449705, 0.16235611, 0.21368645, -0.19411276, 0.124115534, 0.016622102) * g_6;
    result += mat4(0.11676303, 0.02057063, 0.25251, 0.009276932, 0.32482183, -0.040129874, -0.1519303, -0.10388706, -0.028108373, -0.102412194, 0.23188083, 0.18341891, 0.03013491, -0.048286173, 0.0058329282, -0.34457833) * g_7;
    result += mat4(-0.22898167, -0.117408544, -0.017038332, -0.15345758, 0.046906043, 0.19235781, 0.04426378, -0.19599624, -0.017836578, 0.15131067, 0.041776728, 0.14426501, 0.17741966, 0.22128138, -0.20428863, 0.20178981) * g_8;
    result += mat4(-0.004315044, -0.31666014, -0.29125935, -0.12128216, 0.050062098, -0.28783244, 0.20843488, 0.061466597, 0.0057525453, 0.20799558, -0.0835697, -0.004084688, -0.27317607, 0.04916592, -0.078759655, 0.19164392) * g_9;
    result += mat4(0.099757336, -0.11831386, -0.2699008, -0.30549145, 0.118077554, 0.25497273, 0.13997836, 0.075740926, 0.049060423, 0.06831763, -0.3817807, -0.006211132, -0.11377098, -0.09531877, 0.08467258, -0.14856833) * g_10;
    result += mat4(0.052639242, -0.18830816, -0.13748348, 0.28691578, 0.07127495, -0.5680293, 0.12841675, -0.39588076, -0.097284764, 0.36028334, -0.11519626, -0.2415703, 0.11885911, 0.046078153, 0.042018026, 0.03702952) * g_11;
    result += mat4(0.24275999, -0.22876017, 0.032914363, 0.1260231, 0.32194653, 0.0028965252, 0.17534332, 0.0040270244, 0.03671861, -0.2601385, -0.062798336, -0.13836406, -0.25233975, 0.09016869, 0.10884071, -0.1415055) * g_12;
    result += mat4(-0.101087205, -0.043435648, 0.08795096, -0.16750972, -0.30129662, -0.10044177, 0.03310268, 0.08606169, 0.03684131, 0.048794735, 0.08225686, 0.15893319, 0.28447697, -0.09976657, -0.1304865, 0.21622008) * g_13;
    result += mat4(0.0010363923, 0.25213385, 0.20465605, 0.22295177, 0.24521509, -0.2710824, -0.20280603, -0.12543409, -0.18289496, -0.06373974, -0.18411794, 0.061445527, -0.060365368, -0.08516493, 0.08249083, 0.07828689) * g_14;
    result += mat4(-0.060793873, -0.09924079, -0.09869246, -0.4285292, -0.37705702, 0.3411712, 0.22729903, 0.23361796, -0.2354948, 0.21899778, 0.059090182, -0.067654245, 0.16081595, -0.12565234, -0.19271798, -0.09305432) * g_15;
    result += mat4(0.12694947, 0.03796598, 0.032361817, 0.10044351, 0.04519685, -0.13140874, 0.024121989, 0.04257511, 0.07970886, 0.041310467, 0.022053141, -0.19843316, -0.08216455, -0.05973446, -0.12435201, -0.13035697) * g_16;
    result += mat4(-0.048266474, -0.12415696, 0.06391087, -0.15999964, 0.016235331, 0.09552785, 0.12677793, -0.14847611, -0.36091015, 0.027757538, -0.029300604, 0.09124694, 0.4466633, 0.0061744438, -0.055607114, -0.21320932) * g_17;
    result += vec4(-0.0014512301, -0.027619217, -0.016000178, 0.0588223);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf1, gxy, result);
}