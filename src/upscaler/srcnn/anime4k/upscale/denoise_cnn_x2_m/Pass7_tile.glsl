// Anime4K_Upscale_Denoise_CNN_x2_M - Pass 7 of 9 - https://github.com/bloc97/Anime4K
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
// -----------------------------------------------------------------------------
//  Push constants (only in tile-mode shaders)
//    layout(push_constant) uniform TileParams {
//        uint  inputLayer;      // array slice to read (0-based)
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  margin;          // context margin (pixels in feature-map space)
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
//    } tile;
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

layout(push_constant) uniform TileParams {
    uint inputLayer;
    uvec2 dstOffset;
    uint fullOutWidth;
    uint fullOutHeight;
    uint margin;
    uvec2 tileOutExtent;
} tile;

layout(set = 0, binding = 3) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 4, rgba16f) uniform image2DArray img_conv2d_6_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.008187961, -0.08433309, -0.17281345, 0.1306418, -0.2925821, 0.20668334, 0.14854355, -0.15960559, 0.08599311, -0.096088655, -0.10121403, 0.067429096, 0.049158614, 0.036637552, 0.22137405, -0.17016457) * go_0(-1.0, -1.0);
    result += mat4(0.024813082, 0.028489944, 0.06814137, -0.1245949, 0.54239255, 0.08648708, 0.28979865, 0.110916786, -0.1927179, -0.17756873, -0.1878214, 0.05795718, -0.080397904, 0.22125137, 0.1907366, -0.016493658) * go_0(-1.0, 0.0);
    result += mat4(0.027259264, 0.01494357, 0.04852894, 0.037580628, 0.031005561, 0.003570554, -0.072993, -0.053475574, 0.031119492, -0.14140029, -0.10386501, -0.015266508, 0.01153506, 0.16006693, 0.088294305, 0.04201491) * go_0(-1.0, 1.0);
    result += mat4(0.13026185, 0.097255, 0.49145448, -0.33619553, -0.21144676, 0.019042643, -0.27274492, 0.3033865, 0.14040698, -0.13656893, 0.28211337, -0.26930946, -0.1626638, 0.105105706, -0.50837296, 0.39536825) * go_0(0.0, -1.0);
    result += mat4(-0.42495522, 0.14972518, 0.0007564128, 0.37367433, 0.44553527, 0.3338494, -0.26058698, 0.087256804, -0.4324135, 0.20706014, 0.33552194, -0.13375738, -0.13469471, 0.22374928, -0.36969653, -0.34171587) * go_0(0.0, 0.0);
    result += mat4(0.26543954, -0.004381978, 0.10609993, -0.09718426, -0.15620759, -0.03287476, 0.093032375, 0.00028344034, -0.11699793, -0.016492033, 0.023340177, 0.0062737763, -0.14305823, -0.2721832, -0.160177, -0.06915171) * go_0(0.0, 1.0);
    result += mat4(0.03334679, 0.12436332, -0.13226178, 0.13868971, 0.017779246, -0.012697869, -0.11553709, 0.08638636, 0.0955215, -0.0309646, 0.040856246, -0.03978358, 0.023490254, -0.07178907, 0.23794931, -0.1714287) * go_0(1.0, -1.0);
    result += mat4(-0.11820261, 0.116130814, 0.58924234, -0.37785482, 0.016644944, -0.071019046, 0.0076222476, -0.024118654, -0.076183304, -0.14971451, 0.06356606, -0.07225465, -0.17400762, 0.030856986, 0.03957665, -0.0070553776) * go_0(1.0, 0.0);
    result += mat4(0.10954708, 0.063694, -0.058218896, 0.0010372304, 0.032423936, 0.006164447, -0.031383317, 0.012955956, -0.17115591, 0.16328962, 0.07279567, 0.06571465, 0.005532307, 0.13575353, 0.04082173, 0.041579492) * go_0(1.0, 1.0);
    result += mat4(0.03146011, -0.08227295, -0.03498218, 0.04772092, 0.12055223, -0.12383867, 0.05448358, -0.07948453, -0.019064998, -0.0964146, -0.024651276, 0.041473705, -0.06493721, -0.054806646, -0.21607941, 0.20078054) * go_1(-1.0, -1.0);
    result += mat4(-0.25740683, -0.33160943, -0.37422308, 0.12679969, -0.032204475, 0.41485202, 0.4538808, -0.082535125, 0.11784846, 0.10195789, 0.064491615, -0.10170162, -0.09500746, -0.15640756, -0.079364255, -0.12576963) * go_1(-1.0, 0.0);
    result += mat4(-0.02532797, -0.014487023, -0.09441118, -0.060885422, -0.41196415, -0.1359501, 0.07101173, -0.053279232, 0.010979353, 0.1914526, 0.054606825, 0.015926225, 0.10410896, 0.010272597, -0.048138764, -0.02698072) * go_1(-1.0, 1.0);
    result += mat4(-0.35856235, 0.099759184, -0.11972965, -0.03850837, -0.5143867, 0.3721666, -0.100802526, 0.21814734, -0.11864143, 0.15086797, 0.047075786, -0.14188164, 0.48882273, -0.12767795, 0.4937544, -0.41288656) * go_1(0.0, -1.0);
    result += mat4(0.21679138, 0.023770422, -0.5454043, 0.18567741, 0.15965948, -0.84900963, -0.4684333, -0.21884751, 0.5876668, -0.9346244, -0.30144307, 0.97177315, 0.24103107, 0.35953388, 0.2032729, 1.2934744) * go_1(0.0, 0.0);
    result += mat4(-0.5121466, -0.123357795, 0.1833694, 0.048652876, -0.20895603, 0.0619325, 0.064119816, 0.072841786, -0.21813762, -0.126957, -0.23441431, -0.009071302, -0.09766064, -0.12546945, 0.086008705, -0.0072638122) * go_1(0.0, 1.0);
    result += mat4(0.15312338, -0.051029235, 0.07638347, -0.14028431, 0.10694411, -0.14639509, 0.3193828, -0.22767228, -0.19987194, 0.18207504, -0.19648756, 0.24752761, -0.03402804, -0.04186147, -0.20177092, 0.09467012) * go_1(1.0, -1.0);
    result += mat4(-0.3587345, -0.20358992, -0.11016057, 0.21079709, -0.26201126, 0.040362626, 0.3186598, -0.059521858, 0.27564716, -0.041431133, 0.19315968, -0.30228892, 0.01191173, -0.10380854, 0.03030344, 0.026699625) * go_1(1.0, 0.0);
    result += mat4(0.13373446, -0.011457521, -0.24851708, 0.06563771, -0.051668253, 0.09096929, -0.013976447, 0.041433394, -0.046981215, -0.00015144625, 0.05696515, 0.024501698, 0.2714476, -0.017434085, 0.025333954, -0.054034695) * go_1(1.0, 1.0);
    result += vec4(0.06757453, -0.021112159, -0.015639946, 0.05520713);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, ivec3(valid_xy, 0), result);
}