// Anime4K_Upscale_Denoise_CNN_x2_M - Pass 2 of 9 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(set = 0, binding = 3) uniform texture2D tex_conv2d_tf;
layout(set = 0, binding = 4, rgba8) uniform image2D img_conv2d_1_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.06215308, -0.054471835, 0.1285146, 0.037585296, -0.14467795, 0.0057610427, 0.006528968, 0.18607244, 0.03762581, -0.121003255, 0.0827445, 0.076479666, 0.07540097, 0.16371846, -0.18786757, -0.12048073) * go_0(-1.0, -1.0);
    result += mat4(-0.11520603, -0.22384967, 0.0970881, 0.045122143, -0.40358877, 0.12487416, -0.4489702, 0.04854906, -0.08240888, -0.0058777514, 0.19108902, 0.042189106, -0.07843178, 0.0012592699, -0.11303816, -0.1118517) * go_0(-1.0, 0.0);
    result += mat4(0.29387334, 0.08150406, -0.06009834, 0.07054583, -0.146034, 0.04053809, 0.23284695, -0.08233496, 0.0957811, 0.20221621, 0.13570721, -0.081069246, -0.031743366, -0.038912926, -0.059060514, 0.05190416) * go_0(-1.0, 1.0);
    result += mat4(0.18404631, -0.034244366, -0.13406059, 0.2242061, -0.23668705, -0.10359684, -0.09689738, -0.04932347, -0.0020525968, 0.15236467, -0.2634303, -0.029878438, 0.3283669, 0.09891668, -0.46656898, -0.03271751) * go_0(0.0, -1.0);
    result += mat4(-0.1824976, -1.0545974, 0.93027455, -0.13887188, 0.3128633, -0.2734884, -0.831517, -0.18065166, -0.2119423, 0.19241124, -0.13313763, -0.10523897, 0.2675327, -0.06853148, 0.007885104, 0.26000848) * go_0(0.0, 0.0);
    result += mat4(-0.18109167, -0.019768981, -0.14131357, -0.3181756, 0.22158594, 0.1431138, -0.12970252, -0.011459096, -0.03742945, 0.2316056, -0.054623842, -0.09360549, 0.10176328, -0.108150974, 0.122787155, 0.07614884) * go_0(0.0, 1.0);
    result += mat4(-0.02370754, -0.10264054, 0.030659392, 0.056694325, 0.034085, -0.0538203, 0.09111551, 0.0063995267, 0.0835243, -0.06623529, 0.20924146, 0.09457414, 0.27925664, 0.049511474, -0.22062886, 0.03312504) * go_0(1.0, -1.0);
    result += mat4(0.17009354, 0.34391564, -0.1680695, -0.051450633, -0.044037253, -0.1412577, 0.01097572, -0.049040757, 0.104024716, -0.34571946, 0.5213214, -0.17010914, -0.016452854, 0.3303069, -0.22249438, 0.23866816) * go_0(1.0, 0.0);
    result += mat4(0.20491506, 0.20098424, 0.015425732, -0.033999693, -0.0111842435, 0.09945295, -0.025766203, 0.17068656, 0.049262784, 0.0077788536, 0.068585835, 0.19229786, -0.013048818, 0.04877973, 0.024053875, -0.06846659) * go_0(1.0, 1.0);
    result += mat4(0.14208305, 0.09790381, -0.008420949, -0.016165754, 0.02445528, 0.08700781, 0.046639573, -0.22105917, -0.08529265, 0.06606378, 0.0947481, 0.08149193, -0.0959293, -0.037756894, -0.008136973, 0.046241503) * go_1(-1.0, -1.0);
    result += mat4(0.2577669, 0.13766493, 0.021107635, 0.018978242, 0.452542, 0.25566816, -0.68909633, 0.03804329, 0.06771752, 0.07894156, 0.22501312, -0.047511246, 0.00040517355, -0.0202232, -0.27541754, -0.040150844) * go_1(-1.0, 0.0);
    result += mat4(-0.30176973, -0.15739526, -0.038548045, -0.07003333, 0.32053417, 0.025467036, -0.044913124, 0.20454903, 0.12475206, -0.03966162, 0.07139637, 0.12101497, -0.10777517, -0.062379625, 0.06598757, -0.14795317) * go_1(-1.0, 1.0);
    result += mat4(0.12068516, 0.0026514034, -0.055378057, -0.0976728, 0.15887645, 0.15590422, 0.076294206, -0.15417404, -0.16548084, -0.18422292, -0.1670212, 0.041155312, -0.11765263, 0.16991171, -0.21535093, 0.01542368) * go_1(0.0, -1.0);
    result += mat4(-0.37845853, 0.5732961, 0.114283465, 0.14638355, -0.109194644, 0.087304994, -0.15938401, 0.58242995, -0.025850652, 0.02730721, -0.48582682, -0.2547883, 0.1899583, 0.24296008, -0.8162976, 0.018036429) * go_1(0.0, 0.0);
    result += mat4(0.1633212, -0.117295206, 0.021892091, 0.07762347, -0.09726402, -0.1364192, 0.10752197, 0.42020246, 0.06665656, -0.10822656, 0.1337331, 0.0552859, 0.04700212, 0.108017646, -0.2009353, -0.0435288) * go_1(0.0, 1.0);
    result += mat4(-0.045603696, 0.05774526, -0.0071174325, 0.24119262, -0.06899063, 0.016012343, 0.009982042, -0.19038968, -0.17796072, -0.12510185, 0.22739507, -0.1805478, -0.100294635, 0.017557602, 0.039842658, 0.13116726) * go_1(1.0, -1.0);
    result += mat4(0.0131523665, -0.20472725, 0.121814765, -0.17769355, 0.097669855, 0.09648846, -0.072887406, 0.22992326, -0.019087939, 0.35375193, -0.057155706, 0.17699116, 0.030690158, -0.423475, 0.03703492, -0.03429164) * go_1(1.0, 0.0);
    result += mat4(-0.12143413, -0.018402342, 0.04536776, -0.12743106, 0.03355068, -0.09694192, 0.09913357, -0.036602203, 0.11038047, 0.13236065, 0.12966877, -0.10163848, 0.0030612876, -0.116145626, 0.045318183, 0.11492169) * go_1(1.0, 1.0);
    result += vec4(0.05657016, -0.04848861, 0.10297782, -0.0076417355);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_1_tf, gxy, result);
}