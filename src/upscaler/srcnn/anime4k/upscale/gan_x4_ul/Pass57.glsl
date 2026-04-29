// Anime4K_Upscale_GAN_x4_UL - Pass 57 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_24_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_24_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_24_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_24_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_26_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_22_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_25_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_27_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_24_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_24_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_24_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_24_tf3, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_24_tf, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_24_tf1, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_24_tf2, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_24_tf3, pointSampler), pos)), 0.0))
#define g_8 (max((texture(sampler2D(tex_conv2d_26_tf, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_26_tf, pointSampler), pos)), 0.0))
#define g_10 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_25 (max(-(texture(sampler2D(tex_conv2d_22_tf, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_25_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(-0.019710967, 0.08727079, 0.13289316, 0.03551607, 0.0777452, -0.112196796, -0.16325843, 0.1558316, -0.022001125, -0.2075691, 0.11862199, 0.02857829, 0.020248298, -0.0094446875, -0.07760552, -0.117990285) * g_0;
    result += mat4(-0.29817292, 0.10518408, 0.21746357, 0.05733823, 0.03669798, -0.08149275, -0.10093382, 0.008025974, 0.041065153, 0.13907155, 0.03632113, -0.13297954, 0.060014922, 0.17260654, -0.19085334, -0.08275422) * g_1;
    result += mat4(0.12151083, -0.14669828, -0.1620568, -0.16574967, 0.074872755, 0.19607818, -0.3769676, -0.058607124, 0.033677254, -0.056256827, -0.16380833, 0.20182659, 0.04105756, -0.014290442, -0.113356315, 0.09061605) * g_2;
    result += mat4(-0.24904074, 0.01590407, -0.003319224, 0.022379734, -0.06170071, -0.10397567, 0.15287766, 0.088777915, 0.020472175, -0.06658154, -0.11527278, 0.018785367, 0.1344412, 0.17483887, 0.09392446, 0.14208129) * g_3;
    result += mat4(-0.12065394, -0.07425183, 0.19492783, -0.0121520795, -0.21886127, -0.22013198, 0.21618968, 0.1857871, 0.012718742, 0.27063718, 0.2922766, 0.14129776, 0.15681101, -0.11397562, 0.2161061, 0.28459883) * g_4;
    result += mat4(0.18279836, 0.059465416, -0.2686552, 0.08636607, -0.2511355, 0.105158694, 0.16153961, 0.0084084505, -0.2347149, -0.24694109, -0.06095133, -0.13584507, 0.1535036, -0.070038, 0.14755426, 0.15813471) * g_5;
    result += mat4(0.05638502, 0.12059284, 0.119747244, -0.025995718, 0.018165832, -0.16386032, -0.0039485083, -0.12419894, -0.18031433, 0.0659284, -0.048997298, 0.05746441, 0.0037581213, 0.0475356, 0.026042571, 0.0461644) * g_6;
    result += mat4(0.29047623, -0.03317755, 0.012561449, 0.0762115, -0.22357285, 0.09418904, -0.1308704, 0.03420321, 0.3186606, -0.08401149, -0.06973756, -0.1454678, 0.1048745, 0.12291292, -0.014862143, -0.1947549) * g_7;
    result += mat4(0.24438359, -0.33590525, 0.08984905, 0.3105651, -0.116628, -0.25711998, 0.114802435, -0.062869534, 0.26591647, 0.016051942, 0.14616686, -0.012595678, 0.31504416, -0.2826693, 0.25454178, 0.13212447) * g_8;
    result += mat4(-0.012505105, 0.25267395, -0.34087932, -0.11540549, 0.23704751, 0.20673543, -0.15236458, 0.08962316, 0.19622429, 0.12039237, -0.1578033, -0.0637722, -0.21207733, -0.03394972, 0.22895417, 0.15027094) * g_9;
    result += mat4(-0.14031585, -0.035249453, 0.079809986, -0.16434458, 0.10221193, 0.035313964, 0.018961012, -0.16648005, 0.30393958, -0.1710883, -0.19866116, 0.44803715, 0.0661874, 0.08189988, 0.08553425, 0.28069958) * g_10;
    result += mat4(-0.19560876, 0.13451014, 0.13100468, 0.35829562, -0.15475325, 0.02990502, -0.0061779036, -0.22534068, -0.33936733, 0.27095476, 0.14239429, -0.5767695, 0.087701306, -0.1332555, 0.05407353, -0.21649647) * g_11;
    result += mat4(0.08749871, -0.2221962, 0.14391874, -0.073948324, -0.025453761, 0.12343736, 0.17743391, -0.07681618, -0.40484402, 0.19426289, -0.09875697, 0.01706343, 0.03982282, -0.17358004, 0.26000148, -0.115895495) * g_12;
    result += mat4(-0.13025936, 0.2896371, 0.05801185, 0.08293986, -0.0893019, 0.039711192, -0.16405399, 0.12870799, 0.003430463, 0.09525632, -0.16785814, -0.11364755, -0.18278702, -0.016319456, -0.047153126, -0.020832052) * g_13;
    result += mat4(0.082251646, 0.029341506, 0.17133091, -0.18122095, 0.14725228, 0.11916899, -0.28950807, 0.03370702, 0.0347592, 0.032789018, -0.045912996, -0.19743393, -0.19047977, -0.00169078, 0.10430928, 0.09070872) * g_14;
    result += mat4(-0.092634596, -0.010618818, -0.03247302, 0.036561195, 0.11044694, 0.12613513, -0.028009905, -0.29851934, 0.087764055, 0.03672974, -0.018752236, 0.13566239, 0.12001229, 0.11018802, -0.11403856, 0.12471705) * g_15;
    result += mat4(-0.0038836685, -0.2424455, -0.15008962, 0.082429685, -0.027996138, -0.03844133, -0.15668187, -0.04586779, -0.0009184358, -0.04966999, -0.143867, -0.11818294, 0.014227782, 0.17745559, 0.1543326, 0.12324403) * g_16;
    result += mat4(-0.19125207, -0.072080135, 0.22001915, -0.15000911, 0.006092946, 0.0276868, 0.049183417, -0.023606265, -0.055075668, 0.0023213453, -0.006831625, 0.054617073, 0.028141601, -0.28144443, -0.15619376, 0.012505551) * g_17;
    result += mat4(-0.002071177, -0.25345835, 0.28130552, 0.02935035, 0.021427564, 0.076878846, 0.10711918, 0.17818032, -0.16705897, 0.0842015, 0.025515607, -0.04167417, -0.06023519, 0.03835697, 0.02799301, -0.15039864) * g_18;
    result += mat4(0.065405816, 0.13527295, 0.0067324284, -0.12423678, 0.021669216, -0.082277656, 0.14112775, -0.18604228, 0.13923156, -0.09100899, 0.048483785, 0.022520756, 0.14296904, -0.109883346, 0.006980882, -0.07817121) * g_19;
    result += mat4(-0.037226293, -0.110121734, 0.07505908, 0.11474654, 0.209037, -0.026594287, -0.04906321, 0.25379568, 0.18203714, -0.0306505, -0.30535626, -0.015043494, -0.12235582, 0.25040084, -0.6705801, 0.1575759) * g_20;
    result += mat4(0.18554471, 0.22335277, 0.22220112, 0.16374512, -0.14779869, -0.013078052, 0.14746222, -0.06868247, -0.17210856, 0.13750106, 0.13263366, 0.056304373, -0.20586984, 0.009876655, 0.23746644, -0.11166203) * g_21;
    result += mat4(-0.26620933, -0.0082564615, -0.078228526, 0.2707986, -0.20045628, -0.08139448, 0.0045745936, 0.09325633, -0.05672884, -0.0876488, 0.074889794, 0.13535088, 0.009728256, -0.009059547, -0.20067231, -0.17888282) * g_22;
    result += mat4(0.18152374, 0.012155946, -0.17208481, 0.017410867, -0.13088197, 0.008807619, 0.075113654, 0.101879686, -0.071657784, 0.19019592, 0.15560628, -0.07696461, -0.14242226, -0.12567873, 0.048841417, 0.09410027) * g_23;
    result += mat4(0.097054265, 0.17632675, 0.070473716, 0.007048641, -0.042248275, -0.15942219, -0.20265426, -0.11571704, 0.06452315, -0.07014653, 0.15223622, -0.046541333, -0.024594152, 0.19610131, -0.020526761, -0.11271823) * g_24;
    result += mat4(-0.033343684, 0.08648372, 0.10469339, 0.015983986, -0.0068075475, 0.11311371, 0.179533, -0.11297559, 0.33167574, 0.086799785, 0.042009678, -0.27057844, 0.077861145, 0.09749471, 0.06263665, 0.09029921) * g_25;
    result += mat4(-0.17208366, 0.1823461, 0.05647835, 0.10694644, -0.3164003, -0.0020529446, -0.01364865, -0.03349827, 0.12650657, -0.13572167, -0.07308267, -0.06336381, -0.05660443, -0.043583434, -0.28769398, -0.27051786) * g_26;
    result += mat4(-0.03592598, -0.4689105, 0.24144898, -0.030977558, 0.002880143, -0.3730606, 0.14906044, -0.07306277, 0.021631535, 0.29016364, -0.10610739, -0.04341038, 0.08593863, 0.07535527, 0.137121, 0.040470026) * g_27;
    result += vec4(-0.0023638057, -0.06318492, 0.031060705, 0.012420308);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_27_tf2, gxy, result);
}