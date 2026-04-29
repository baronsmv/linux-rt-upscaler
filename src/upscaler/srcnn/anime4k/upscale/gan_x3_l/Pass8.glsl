// Anime4K_Upscale_GAN_x3_L - Pass 8 of 30 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_3_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.15275823, 0.31693572, 0.03429309, -0.06982273, 0.08535909, 0.019838037, -0.03189405, 0.3190016, 0.16633914, 0.48730284, -0.27923077, 0.31791112, 0.43154097, 0.005003616, -0.26277873, -0.009333685) * g_0;
    result += mat4(0.23504019, -0.12419379, 0.07217815, -0.090434305, -0.0380588, -0.14686479, -0.33812302, -0.20242776, -0.20776805, 0.24741934, -0.16489775, 0.07052134, -0.08030772, 0.23784883, -0.28709608, -0.17689173) * g_1;
    result += mat4(-0.05109775, -0.40860242, -0.003464472, -0.19893257, 0.23186824, -0.12760048, -0.22718583, 0.02299852, 0.27083093, 0.073904194, -0.056870755, -0.35324985, -0.023004858, -0.29591596, -0.020298446, -0.05753052) * g_2;
    result += mat4(0.0035456547, -0.37682405, 0.047876693, 0.1168026, 0.015805494, -0.04388269, 0.12970346, 0.2497829, -0.009891778, 0.116980106, 0.13058232, 0.22570355, 0.13866597, 0.036246244, 0.10916998, -0.040503114) * g_3;
    result += mat4(-0.25300103, -0.065156855, 0.063345924, 0.11406543, -0.1902478, 0.16440767, 0.043949526, 0.43318078, -0.03932035, -0.08510957, 0.19621156, -0.045045726, -0.08339006, -0.04335483, 0.37129655, -0.22328225) * g_4;
    result += mat4(0.16169593, 0.2758587, 0.38249364, 0.12606645, 0.4582731, 0.09374545, -0.10988087, -0.21678255, -0.004099455, -0.09436347, 0.33964127, 0.20880581, -0.06742301, -0.025149476, 0.12146305, 0.5012377) * g_5;
    result += mat4(0.11523535, 0.31662583, -0.0709322, -0.066175185, 0.08868106, -0.042457394, 0.32469732, -0.1987238, 0.41399983, 0.015568244, 0.14037918, 0.2879998, -0.32157704, 0.22491854, -0.07769691, 0.2052648) * g_6;
    result += mat4(-0.299831, -0.247278, -0.2011737, -0.3759366, -0.14935663, -0.095033385, 0.06259881, -0.23891686, -0.4340098, 0.07340212, -0.0012697511, -0.16527005, 0.0814454, -0.43962866, -0.3040046, 0.06242604) * g_7;
    result += mat4(0.11802704, 0.2323739, 0.13466287, -0.25053164, -0.08020803, 0.1628004, -0.030645542, -0.40872335, -0.24624921, 0.15931502, 0.40752286, -0.07906199, 0.4286516, -0.1651973, -0.07021073, 0.0867332) * g_8;
    result += mat4(-0.23617363, 0.053548977, -0.14130518, -0.37744048, -0.11805406, -0.13757266, -0.026939899, 0.028020354, 0.24626125, -0.06998214, -0.02793638, 0.10509643, 0.06577935, -0.17211749, -0.12747282, -0.16999653) * g_9;
    result += vec4(-0.022106458, -0.012578552, 0.016203664, 0.026009269);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf2, gxy, result);
}