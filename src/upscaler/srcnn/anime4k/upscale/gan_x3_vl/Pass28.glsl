// Anime4K_Upscale_GAN_x3_VL - Pass 28 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_14_tf;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_15_tf2;
#define g_0 (max((texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_3 (max(-(texture(sampler2D(tex_conv2d_12_tf, pointSampler), pos)), 0.0))
#define g_4 (max(-(texture(sampler2D(tex_conv2d_12_tf1, pointSampler), pos)), 0.0))
#define g_5 (max(-(texture(sampler2D(tex_conv2d_12_tf2, pointSampler), pos)), 0.0))
#define g_6 (max((texture(sampler2D(tex_conv2d_14_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_14_tf, pointSampler), pos)), 0.0))
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
vec4 result = mat4(-0.051234227, 0.12462721, -0.09787546, 0.25406766, 0.30560002, 0.17283113, -0.05798071, 0.2647435, 0.13788636, 0.08840858, -0.05289184, 0.25852382, -0.26674244, -0.07364587, 0.001191221, 0.22217625) * g_0;
    result += mat4(-0.26877132, -0.10157862, 0.092936665, -0.021073027, -0.16361141, 0.21253154, 0.22684343, -0.054344796, -0.05049234, 0.42118612, 0.29657525, 0.17409663, 0.15270026, 0.10825865, 0.22627294, 0.054406367) * g_1;
    result += mat4(0.2163665, 0.13454697, 0.033053502, -0.015820911, 0.17696854, 0.005023235, 0.15261635, -0.11690415, -0.15954569, 0.15751791, -0.082067445, 0.377173, 0.15451732, -0.21614599, -0.090183906, -0.22754942) * g_2;
    result += mat4(0.10186722, -0.3034483, -0.25445342, 0.09971074, -0.16596235, -0.051873583, 0.14013551, 0.3921163, -0.029541738, -0.21873768, 0.073057145, -0.18722391, 0.2500657, 0.036109924, 0.054032363, -0.5253905) * g_3;
    result += mat4(0.033514977, 0.13074529, -0.26700264, 0.14833573, -0.006180942, 0.12044789, -0.17576072, 0.023566427, 0.13765517, -0.047552105, -0.18236409, -0.2774939, 0.06162977, -0.055201646, -0.058275994, -0.12629794) * g_4;
    result += mat4(-0.1996918, 0.15683116, -0.3256319, 0.2057855, -0.0671691, 0.24640855, 0.22842555, 0.12610425, -0.090195596, 0.101964004, 0.22426924, -0.24429117, -0.26323536, 0.32974228, 0.08008744, 0.45575497) * g_5;
    result += mat4(-0.42316, -0.062756, 0.07857826, -0.14351259, -0.29394817, 0.5423037, 0.18915935, -0.17086914, 0.50753736, 0.0015875449, 0.29438123, -0.19376752, 0.09791069, -0.028306229, 0.05765373, -0.22298522) * g_6;
    result += mat4(0.03728915, 0.15399045, -0.04512004, -0.12652445, 0.28205284, -0.23605378, 0.17079072, -0.1082726, -0.15433414, -0.19789961, -0.28514484, 0.0077355634, -0.01829938, 0.34892595, -0.23294884, -0.22864898) * g_7;
    result += mat4(0.027223717, 0.12626694, 0.11476459, 0.1460455, 0.20033693, 0.026134387, -0.10378083, 0.02503927, 0.27902585, -0.0038183157, 0.115261704, 0.13458112, 0.31611767, -0.1142268, 0.0072508105, 0.0028353012) * g_8;
    result += mat4(0.021163143, 0.16883731, -0.058492687, -0.12585758, -0.061747592, -0.09557424, 0.121174686, 0.0743391, -0.08168162, -0.026392763, -0.00060598814, 0.12879269, -0.07671814, 0.065251, 0.1404438, -0.05534044) * g_9;
    result += mat4(0.14274202, -0.3996823, -0.324641, 0.005320553, 0.28041458, 0.10360115, -0.01966796, 0.12442266, 0.107218176, 0.004735665, -0.15030271, -0.23013945, -0.18984175, 0.078943305, 0.16392353, -0.07955006) * g_10;
    result += mat4(0.021630967, 0.29960495, -0.10998858, 0.06537184, 0.11009237, 0.028505472, 0.32113916, -0.15730233, 0.083316445, 0.112375356, -0.065724924, 0.0889756, -0.09385971, 0.089896984, 0.08292775, -0.2035827) * g_11;
    result += mat4(-0.13751891, -0.027330484, -0.13091096, 0.19190204, -0.09216561, -0.14242831, -0.10237887, 0.13343115, -0.14150177, 0.094059885, -0.10393571, -0.09336556, 0.20657797, 0.07327506, 0.13245964, -0.016539408) * g_12;
    result += mat4(-0.158201, -0.12623371, 0.09620584, -0.10184386, -0.057575878, 0.003921972, 0.021233508, 0.35487738, -0.11295889, -0.10775328, 0.039876595, 0.081189156, 0.106679484, 0.0747396, -0.028251883, 0.27306616) * g_13;
    result += mat4(-0.2361755, -0.13576986, 0.2919796, 0.09699708, 0.4581993, -0.1196168, -0.028562034, 0.00018960529, -0.11903206, 0.17371814, -0.07005846, 0.028902404, -0.09053355, -0.110385194, 0.25002465, 0.08581321) * g_14;
    result += mat4(0.06806976, 0.15122992, -0.33567524, 0.001315605, -0.11049211, 0.09723952, 0.29624012, -0.31183454, -0.1838605, -0.23770033, 0.2865799, -0.044371903, 0.05511511, 0.30258948, 0.28474173, -0.050289202) * g_15;
    result += mat4(-0.27601755, -0.06335842, -0.23002502, -0.31029934, 0.021644987, 0.24281926, 0.15377666, 0.22653481, 0.033689793, -0.010622847, 0.08636093, -0.16723068, 0.25021335, 0.3877554, -0.15065683, 0.01558507) * g_16;
    result += mat4(-0.08309524, 0.25966918, 0.17456721, 0.1898729, 0.248563, -0.23167695, 0.11267612, -0.048332583, -0.34379265, 0.042474393, -0.085350186, -0.05868464, -0.29812938, -0.054665178, -0.1093917, 0.22230257) * g_17;
    result += vec4(0.018145598, -0.032355547, -0.05915781, 0.02910991);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf2, gxy, result);
}