// Anime4K_Restore_CNN_Soft_M - Pass 8 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2D tex_MAIN;
layout(set = 0, binding = 4) uniform texture2D tex_conv2d_tf;
layout(set = 0, binding = 5) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 6) uniform texture2D tex_conv2d_2_tf;
layout(set = 0, binding = 7) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 8) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 9) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 10) uniform texture2D tex_conv2d_6_tf;
layout(set = 0, binding = 11, rgba8) uniform image2D img_output;
#define g_0 (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_1 (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_2_tf, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_6_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.030150581, -0.002168429, 0.014918388, 0.0, 0.020940892, 0.04591048, 0.049137186, 0.0, 0.111167125, 0.05311203, 0.0625381, 0.0, 0.020043287, 0.04785493, 0.040921766, 0.0) * g_0;
    result += mat4(0.04158565, -0.008488135, 0.0020472286, 0.0, 0.049123142, -0.055042226, -0.06489915, 0.0, 0.09238876, 0.10387972, 0.09576964, 0.0, -0.054776173, -0.098954335, -0.09018853, 0.0) * g_1;
    result += mat4(0.2081418, 0.08273068, 0.040325668, 0.0, -0.09937802, -0.13162258, -0.13989717, 0.0, -0.13983749, 0.01309777, 0.0023888077, 0.0, -0.18937743, -0.07021057, -0.047152344, 0.0) * g_2;
    result += mat4(-0.09646629, 0.080605574, 0.10463501, 0.0, 0.22579835, 0.24077554, 0.22600271, 0.0, 0.049726978, 0.015292378, -0.0047161994, 0.0, 0.16281025, 0.048491795, 0.038338162, 0.0) * g_3;
    result += mat4(-0.09772107, -0.043998875, -0.054745924, 0.0, -0.1257736, -0.13175423, -0.10889618, 0.0, -0.015900036, 0.07074481, 0.08210496, 0.0, -0.11321135, -0.12526917, -0.105605066, 0.0) * g_4;
    result += mat4(0.14187162, 0.14032297, 0.13016908, 0.0, 0.018954534, 0.016011704, 0.010169183, 0.0, 0.04762765, -0.044460997, -0.06499567, 0.0, 0.11133751, 0.09464176, 0.08865274, 0.0) * g_5;
    result += mat4(-0.16567162, -0.1744712, -0.1637222, 0.0, -0.02412003, 0.0074480795, 0.007903436, 0.0, -0.06161098, -0.046788957, -0.03971239, 0.0, 0.030736001, 0.036460854, 0.03660504, 0.0) * g_6;
    result += mat4(0.084027, 0.10024112, 0.08152756, 0.0, 0.005087354, -0.026047802, -0.027264625, 0.0, 0.10519243, 0.08977278, 0.077558964, 0.0, -0.052826345, -0.06602686, -0.055083472, 0.0) * g_7;
    result += mat4(0.007862721, 0.009936555, 0.012004831, 0.0, -0.042322706, -0.061728776, -0.05359773, 0.0, 0.030532641, 0.045623366, 0.04214089, 0.0, 0.030569768, 0.011892851, 0.0074041556, 0.0) * g_8;
    result += mat4(0.03948997, 0.043119986, 0.039943404, 0.0, 0.0526772, 0.06820589, 0.058139592, 0.0, -0.062081397, -0.06755701, -0.054816127, 0.0, -0.004076369, 0.0061744447, 0.016273081, 0.0) * g_9;
    result += mat4(0.0071622543, 0.004829105, -0.002032197, 0.0, -0.048541367, -0.059043564, -0.05662218, 0.0, 0.0015553127, 0.009178359, 0.009577062, 0.0, 0.114169896, 0.1349016, 0.11432262, 0.0) * g_10;
    result += mat4(0.019324556, 0.028323999, 0.027396113, 0.0, 0.016746879, 0.01608199, 0.026891617, 0.0, 0.12068619, 0.13617857, 0.113496214, 0.0, -0.013930715, -0.014250072, -0.00824306, 0.0) * g_11;
    result += mat4(-0.0024534757, -0.0064973077, -0.007905654, 0.0, -0.019158727, -0.024820521, -0.020509848, 0.0, -0.09608131, -0.11177871, -0.10503465, 0.0, -0.011210447, -0.010875943, -0.015295865, 0.0) * g_12;
    result += mat4(0.09681486, 0.113604136, 0.10416855, 0.0, -0.08199983, -0.09013433, -0.08562243, 0.0, 0.041304465, 0.048315883, 0.042945288, 0.0, -0.09863276, -0.117853515, -0.09870226, 0.0) * g_13;
    result += vec4(-0.0039074384, -0.0085585555, -0.0132283475, 0.0);
    return result + texture(sampler2D(tex_MAIN, pointSampler), pos);
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_output, gxy, result);
}