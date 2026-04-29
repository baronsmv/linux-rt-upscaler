// Anime4K_Upscale_GAN_x3_L - Pass 26 of 30 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_12_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_11_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv0ups1;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_11_tf, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.0029025443, 0.021165721, 0.0070854356, 0.065646365, 0.024636142, 0.20825955, -0.0917655, -0.1706138, -0.1827491, 0.13347003, 0.12910214, 0.06828513, -0.026193604, -0.11451178, 0.0356333, -0.08071165) * g_0;
    result += mat4(-0.027241195, 0.032633994, -0.17490302, -0.5352789, -0.15734912, 0.24714436, 0.029301014, 0.212763, -0.051665317, -0.06783505, -0.040298667, 0.041179724, 0.49683514, -0.35600296, -0.2518442, -0.22965558) * g_1;
    result += mat4(-0.061614696, -0.10463926, 0.1594845, 0.036565617, 0.09095015, -0.15100475, -0.09242749, 0.08335822, -0.027257469, 0.4156707, 0.03322028, 0.19685929, 0.07034635, 0.10204465, 0.03657313, 0.30920812) * g_2;
    result += mat4(-0.20980133, -0.054115582, 0.031674277, -0.040077273, -0.21693806, 0.016596884, -0.029177245, -0.16924128, 0.121823296, -0.0004884774, 0.10644538, 0.068388954, 0.16517027, -0.12152921, -0.18299894, -0.17595083) * g_3;
    result += mat4(-0.0006413291, -0.09444853, 0.15260176, 0.23014128, 0.09366626, 0.06947763, 0.04956597, -0.07001088, -0.075523324, 0.16111156, -0.11700089, 0.14528704, -0.096407495, 0.027310526, -0.03946532, 0.15302157) * g_4;
    result += mat4(0.086061105, -0.0070365844, -0.25230658, 0.18741103, -0.36380208, -0.058444727, 0.25284684, -0.26617825, -0.08817363, -0.12209333, 0.011920746, -0.031505488, -0.21880315, 0.16762236, 0.14518112, 0.13803998) * g_5;
    result += mat4(-0.17088315, -0.06812898, -0.085912764, 0.25550255, -0.26439053, 0.23305506, 0.18186118, -0.06186191, 0.0075220955, 0.10316868, 0.04271979, -0.008083033, -0.19474187, -0.06700431, 0.15485007, -0.11886802) * g_6;
    result += mat4(0.06597312, -0.31435877, -0.08179224, -0.2568261, 0.29904976, 0.21664406, -0.15343861, -0.11589945, 0.12654455, -0.042093027, -0.17231914, -0.26832506, -0.12008876, 0.11483079, 0.10222754, 0.12562539) * g_7;
    result += mat4(-0.09949413, 0.01479024, -0.16933955, 0.025359191, -0.2210058, -0.19663176, 0.19453603, -0.111461386, -0.12529027, 0.14243664, 0.122677036, -0.101476125, 0.011010597, -0.014422488, -0.048979994, 0.03657997) * g_8;
    result += mat4(-0.06923051, -0.1223873, 0.021781938, 0.1323696, -0.11582021, -0.018292433, 0.07495496, 0.043008957, 0.0070410958, -0.14431225, -0.06380941, -0.17411429, 0.052226365, 0.021460915, 0.097367965, 0.37138346) * g_9;
    result += mat4(0.16420697, 0.008790036, 0.17185563, -0.025144322, -0.108827055, -0.13030754, -0.14254087, 0.05208047, 0.03751449, 0.06774824, -0.07746288, 0.2250457, 0.039049506, 0.101244815, -0.18138403, -0.12212992) * g_10;
    result += mat4(-0.05138809, 0.19150224, 0.05698308, 0.015970863, 0.23931703, -0.085039265, -0.18294281, 0.03647365, -0.041568805, -0.2920049, 0.013272974, -0.41181135, -0.08101046, 0.028989056, 0.2952233, 0.16312017) * g_11;
    result += mat4(0.093839854, -0.038790308, -0.086285874, -0.17890124, -0.2598202, 0.069419555, -0.0065180454, 0.01453452, -0.090191156, 0.012278203, -0.13148692, -0.025104592, 0.09296121, -0.1833281, 0.074660525, -0.031280298) * g_12;
    result += mat4(-0.05336347, 0.08608969, -0.074649446, 0.014608438, 0.22511393, 0.18610351, -0.0029040743, 0.096127085, -0.20254624, 0.14036441, -0.005226189, 0.055212848, 0.20482111, 0.06645607, -0.12018032, 0.062814355) * g_13;
    result += mat4(0.13722958, -0.077169575, 0.07269382, 0.20902501, -0.103985704, -0.21184038, -0.12424109, -0.3059887, -0.185413, -0.1964241, -0.14370187, 0.07646031, -0.057924826, 0.28884047, -0.06701312, -0.14548934) * g_14;
    result += mat4(0.14129579, 0.12990993, -0.08791828, 0.07986884, -0.006362554, 0.005971629, 0.016816271, 0.075642705, -0.060138028, 0.13658188, 0.0020529197, -0.38745758, -0.16191563, 0.20532359, 0.34441018, 0.0071060034) * g_15;
    result += mat4(-0.03236983, -0.08242242, 0.065607354, -0.072457135, 0.024461512, 0.15522943, 0.120296456, 0.052112654, 0.21442589, 0.19565494, 0.06760742, 0.37604833, 0.097620994, -0.002347599, 0.09269131, -0.34238556) * g_16;
    result += mat4(0.3276042, -0.17974046, -0.095954694, -0.123248585, 0.08306674, -0.3486506, -0.4620704, -0.40518835, -0.17438394, 0.24350463, 0.05616052, -0.14715664, 0.2078043, -0.007834002, -0.21199054, 0.026597755) * g_17;
    result += vec4(-0.015380624, 0.018387195, 0.052286647, 0.055403516);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups1, gxy, result);
}