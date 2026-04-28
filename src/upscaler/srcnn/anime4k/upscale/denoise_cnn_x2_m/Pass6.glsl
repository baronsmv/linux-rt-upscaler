// Anime4K_Upscale_Denoise_CNN_x2_M - Pass 6 of 9 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_5_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(0.11029161, 0.027180295, -0.115622066, 0.16493714, 0.29633296, -0.11739625, -0.36390316, 0.15221693, -0.009233659, -0.062213745, -0.07184558, 0.07418268, -0.05182182, 0.0066014086, -0.006811494, -0.010030367) * go_0(-1.0, -1.0);
    result += mat4(-0.18361749, 0.08565693, 0.24127418, -0.20478591, 0.6198113, -0.17994536, -0.011840256, 0.120292775, 0.2873902, -0.019704796, -0.062267166, 0.0104749305, -0.048370067, -0.028105626, 0.11494511, -0.15941763) * go_0(-1.0, 0.0);
    result += mat4(-0.08084502, 0.10195475, -0.03200553, 0.032734055, 0.030348243, -0.028927604, 0.045914374, 0.029237835, 0.07756032, -0.06346545, -0.290196, 0.057043966, 0.13982558, -0.12195619, -0.15895663, -0.10097537) * go_0(-1.0, 1.0);
    result += mat4(-0.12018707, -0.320156, -0.4089669, 0.26015735, 0.59622765, -0.05654362, 0.28581724, 0.32069868, -0.0013007161, -0.060870633, -0.2732852, 0.2357145, 0.2137239, 0.0110256495, -0.069258444, 0.113870576) * go_0(0.0, -1.0);
    result += mat4(0.54700065, -0.072552234, 0.27267826, -0.26660076, 0.7043544, 0.18192886, 0.80024594, 0.2447395, -0.3289639, -0.2681839, 0.063631415, -1.0118654, 0.45691678, 0.42904988, -0.2301862, -0.6652257) * go_0(0.0, 0.0);
    result += mat4(0.19215634, 0.030154131, 0.07679603, 0.50318545, 0.056434657, 0.028623195, -0.14471184, -0.13905096, -0.03254216, -0.1191584, -0.18907212, 0.49208716, 0.5069476, -0.1490824, -0.104480386, -0.06595394) * go_0(0.0, 1.0);
    result += mat4(-0.08893682, 0.13113782, 0.023672188, 0.013086517, -0.25986442, 0.038162243, -0.10951209, -0.2027832, -0.013547809, -0.029482972, -0.17670235, 0.13529542, -0.0621569, -0.0979757, -0.10714689, -0.08474307) * go_0(1.0, -1.0);
    result += mat4(-0.032828752, 0.00037559783, 0.023968933, -0.047482926, -0.20302027, 0.08830911, -0.20885307, -0.11137413, 0.16585048, -0.076796696, -0.030462325, -0.2020944, 0.048723634, -0.45607433, -0.29950324, -0.5867916) * go_0(1.0, 0.0);
    result += mat4(0.008863689, 0.061761267, -0.039097138, 0.24465923, -0.05917457, -0.21383028, -0.085846715, -0.14150433, 0.0988731, -0.0160538, -0.045119412, 0.095252946, -0.057551738, 0.21348421, -0.03480491, -0.26071647) * go_0(1.0, 1.0);
    result += mat4(-0.21351442, 0.10038809, 0.34001955, -0.100911774, 0.0208522, -0.028755441, 0.025793588, 0.013080005, 0.03849989, 0.13662058, 0.04311886, 0.17398632, -0.01397261, -0.016415505, -0.0070752064, 0.007656161) * go_1(-1.0, -1.0);
    result += mat4(-0.280189, 0.09252764, -0.077729605, 0.12662902, -0.10433321, 0.03644144, -0.06625324, 0.05696802, 0.15468478, 0.08328583, 0.069849946, 0.061947342, -0.05560477, -0.0074776993, -0.15365681, -0.03526299) * go_1(-1.0, 0.0);
    result += mat4(0.05886785, 0.15303846, 0.0066637015, -0.19983207, -0.07803175, -0.10772685, -0.12690999, -0.08275092, 0.033436153, 0.08424011, 0.17092863, 0.0043526487, 0.014620474, 0.044702258, 0.1686881, -0.016890949) * go_1(-1.0, 1.0);
    result += mat4(0.1833738, 0.14381635, -0.025888365, -0.14182197, -0.25804865, 0.07216123, 0.025790794, 0.14096753, 0.023591481, 0.15610993, 0.026975863, 0.008755717, -0.13039349, -0.063048325, -0.121329494, -0.12331732) * go_1(0.0, -1.0);
    result += mat4(0.0005065098, 0.44017914, 0.18493074, 0.13099027, -0.36087477, -0.37567857, -0.48981526, 0.5590752, -0.23918836, 0.19170256, 0.16816153, -0.29986876, -0.44738817, 0.018545123, 0.66217834, 0.31810755) * go_1(0.0, 0.0);
    result += mat4(-0.16725904, 0.05753713, 0.058880586, -0.336765, 0.013667228, 0.056172702, 0.13465533, -0.07573556, -0.06313958, 0.06746643, 0.18878669, 0.09404202, -0.21780397, 0.12862128, -0.09476746, -0.34096682) * go_1(0.0, 1.0);
    result += mat4(-0.07169524, 0.072302215, 0.052789338, -0.14035568, 0.078670934, -0.22246763, -0.0098074945, 0.024950746, 0.10949147, 0.06182366, 0.021721192, 0.12129548, 0.094007075, 0.06076156, 0.016474832, 0.08092115) * go_1(1.0, -1.0);
    result += mat4(-0.10960447, 0.1878152, -0.029822018, 0.10598909, 0.1582181, 0.086522795, 0.093725055, 0.12908185, 0.23202112, -0.28859115, 0.26614165, 0.124523655, 0.19427507, 0.059677128, 0.003624697, 0.44220912) * go_1(1.0, 0.0);
    result += mat4(-0.03620583, -0.102766834, 0.025527107, -0.11316131, -0.1507822, 0.0543862, -0.08225627, -0.06438472, 0.04580623, 0.6329729, 0.23854075, 0.35752076, 0.04363613, -0.12580468, -0.0006126687, -0.04995386) * go_1(1.0, 1.0);
    result += vec4(0.060475674, -0.042036578, 0.06406282, 0.05569301);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_5_tf, gxy, result);
}