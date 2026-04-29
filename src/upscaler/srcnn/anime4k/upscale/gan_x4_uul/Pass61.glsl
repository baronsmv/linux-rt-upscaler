// Anime4K_Upscale_GAN_x4_UUL - Pass 61 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_18_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_18_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_18_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_18_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_18_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_18_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_20_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_21_tf4;
#define g_0 (max((texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_18_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_18_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_18_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_18_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_18_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_18_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_25 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.1963867, 0.07699578, 0.14399086, -0.20231943, 0.1228945, 0.10025043, 0.21558635, -0.14002483, 0.18620099, 0.024811473, -0.006723965, -0.12215585, 0.19046861, -0.108267576, -0.12425069, -0.21237871) * g_0;
    result += mat4(0.246677, 0.0881537, 0.03614809, 0.24940786, -0.12583077, 0.3362467, -0.015060226, 0.09434887, -0.19725238, 0.37675261, -0.007914419, -0.09965565, 0.0195271, 0.09688557, 0.18034142, 0.25808018) * g_1;
    result += mat4(0.07988132, -0.15699178, -0.09968855, -0.05188315, 0.1189213, 0.2018036, 0.06732629, -0.049742103, -0.0012818838, 0.01787508, 0.17064866, 0.13609366, 0.045613803, -0.1356721, 0.0742584, 0.17483133) * g_2;
    result += mat4(-0.09535376, 0.062276363, 0.02677763, 0.18110538, -0.056094047, -0.06404993, -0.24868925, -0.005307554, 0.0036259799, 0.16573818, 0.07203683, 0.33113593, 0.17214227, -0.044549335, -0.013462563, -0.044395987) * g_3;
    result += mat4(-0.049357347, -0.20686656, -0.08514925, 0.13660856, -0.085490316, 0.1609961, 0.18058838, -0.043433487, 0.06679116, 0.020784464, 0.0350443, 0.11283589, 0.047845896, -0.15244545, -0.111651644, -0.13325566) * g_4;
    result += mat4(-0.2407646, -0.036201578, -0.056687888, -0.14974321, 0.039803684, -0.085988104, -0.036733832, -0.14233889, 0.010312457, -0.14597215, -0.1345812, -0.09528502, -0.069463976, -0.017104028, -0.21093526, 0.13846932) * g_5;
    result += mat4(-0.13820851, 0.02654045, -0.09661381, 0.17160213, 0.1978931, -0.12043106, -0.028641233, 0.08110245, -0.1875805, -0.06886384, 0.047143184, 0.33587673, -0.10415887, -0.18351205, 0.1407508, -0.1332706) * g_6;
    result += mat4(0.13994217, -0.013123574, -0.05953133, 0.10043616, -0.27695277, 0.051396918, -0.15545999, -0.12036323, -0.050617583, 0.056553494, -0.079539895, 0.14741984, -0.021349153, 0.07863958, -0.07300714, -0.16282727) * g_7;
    result += mat4(0.054927684, 0.16985811, 0.036917485, -0.0140152415, 0.08888437, -0.29275262, -0.03844096, -0.09088267, 0.1250863, -0.036014643, 0.054614082, -0.15399693, -0.110796444, 0.0925346, -0.22120771, 0.29702052) * g_8;
    result += mat4(0.06883671, 0.058238175, -0.26987633, 0.17383234, -0.100885935, 0.090576224, -0.16625507, 0.033924226, 0.3471819, -0.15876703, -0.003714482, -0.22869875, -0.51020795, 0.13920946, -0.060082283, -0.07045547) * g_9;
    result += mat4(0.02216123, 0.20307806, 0.1976366, 0.035313394, 0.21204922, 0.052470528, 0.03677106, -0.1063312, -0.019970786, 0.1678837, -0.13302676, 0.019388223, -0.10893328, -0.028289987, 0.042897556, -0.23842873) * g_10;
    result += mat4(0.036743134, 0.034039408, -0.010375282, 0.16331595, 0.01155292, -0.051256556, 0.063319005, 0.03891694, 0.028058654, 0.23070037, -0.004834602, 0.12538977, -0.16574672, 0.10670458, -0.054559533, -0.13865025) * g_11;
    result += mat4(0.34042284, -0.096626334, 0.1829246, 0.114188604, 0.088171884, 0.11710425, 0.14686471, 0.009725783, -0.12866455, 0.15149915, -0.13281596, 0.07473135, -0.11002946, -0.042536035, 0.35408425, 0.04991825) * g_12;
    result += mat4(-0.4470486, -0.04748823, -0.14250289, 0.017064111, -0.15611976, -0.052947167, -0.16508208, -0.11881081, 0.13243856, -0.08291998, -0.14834203, -0.4627348, 0.14895794, -0.054990955, -0.2850958, 0.032338817) * g_13;
    result += mat4(0.11025286, -0.047356833, -0.00029529104, 0.10499984, 0.115071274, -0.034509618, -0.17907608, -0.12972243, 0.14780535, -0.039031286, -0.23174866, 0.07155468, -0.2973685, -0.042398665, 0.011526313, 0.014337736) * g_14;
    result += mat4(-0.13286439, -0.15258804, -0.08101948, -0.03865954, -0.0005274504, 0.06358946, 0.20435862, -0.0018249828, 0.13777693, 0.091889404, 0.26195052, -0.10732939, 0.12700158, -0.0029639623, 0.08968977, 0.10790943) * g_15;
    result += mat4(-0.025876395, 0.04674395, 0.08705419, 0.11546646, 0.15677479, -0.09279832, 0.06123563, 0.027857538, -0.026071457, -0.07211418, 0.03904429, -0.07982592, -0.16422117, -0.022703126, -0.17293021, 0.14897922) * g_16;
    result += mat4(0.15511294, -0.2735757, -0.033055518, 0.010482124, 0.07846025, -0.28522226, -0.103355184, 0.0907831, -0.22074161, -0.25466454, 0.14828296, -0.085437566, 0.11504318, -0.16773705, 0.08680487, -0.012820092) * g_17;
    result += mat4(0.10127869, -0.18961814, 0.18196556, 0.08140379, -0.23042479, -0.11330197, 0.10758355, 0.027613612, -0.12754934, -0.030713173, 0.07453361, -0.1338413, -0.0014765146, 0.078984834, 0.019902518, 0.08373023) * g_18;
    result += mat4(0.016189277, 0.094952025, 0.037799377, 0.033959743, 0.11591709, 0.13379039, -0.07359717, 0.2147113, -0.067016184, 0.0006450209, 0.13055131, 0.06845076, -0.027489938, -0.19194192, -0.007896561, -0.08913592) * g_19;
    result += mat4(-0.04248823, -0.076337345, -0.10990166, -0.2680756, 0.08889121, -0.0177947, 0.21444084, 0.100478254, -0.016669227, 0.08470296, -0.069658354, -0.07584226, -0.05746039, 0.25226966, 0.009504905, 0.08502889) * g_20;
    result += mat4(0.031891428, -0.053127673, 0.033998042, -0.057896897, -0.07441638, -0.10886511, 0.079562426, 0.057446953, 0.1934566, -0.074068144, 0.00525264, 0.10135101, 0.13110499, -0.10722797, -0.0841621, -0.050043304) * g_21;
    result += mat4(0.066630974, 0.06632765, -0.18793635, -0.16781266, 0.13995983, 0.096131966, 0.123134784, -0.10111646, -0.12674555, -0.041563142, -0.0061982237, 0.023315776, 0.023906343, 0.019013697, -0.2010971, 0.04703861) * g_22;
    result += mat4(-0.15652168, -0.24982816, 0.17870888, 0.06907672, -0.057334036, -0.032808617, 0.11526983, 0.119979076, -0.1791687, 0.1222946, -0.11300223, -0.17275636, 0.021404041, -0.15254661, -0.04140363, -0.03240875) * g_23;
    result += mat4(0.027191963, -0.01434174, -0.14910434, -0.06411872, -0.061873678, 0.16904217, 0.047826875, 0.02332137, -0.14306058, 0.24481563, -0.033499192, -0.053609576, -0.056984827, -0.09177351, 0.10327636, -0.008282755) * g_24;
    result += mat4(-0.0013305998, -0.16498545, 0.13777103, -3.852495e-06, 0.09852269, 0.049945284, -0.15420936, 0.012355145, -0.0884347, -0.042019103, 0.07325865, 0.12033873, -0.17453258, 0.25127375, 0.003513564, 0.14359626) * g_25;
    result += mat4(0.088470936, -0.084289886, 0.12525322, -0.052040808, -0.02055114, 0.12212508, 0.0047877207, 0.0022971383, -0.16231592, -0.0012661765, -0.18805377, -0.01330223, -0.13868679, -0.07463934, 0.013851991, -0.39397895) * g_26;
    result += mat4(-0.29183444, 0.08526801, -0.009475625, 0.012616094, 0.106093206, -0.15813065, -0.023291823, 0.026072321, -0.09510553, 0.28779894, -0.03740373, -0.22849992, 0.14980063, -0.056065757, 0.1896184, 0.18598676) * g_27;
    result += vec4(-0.10836887, -0.05585613, 0.040955693, -0.094257936);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf4, gxy, result);
}