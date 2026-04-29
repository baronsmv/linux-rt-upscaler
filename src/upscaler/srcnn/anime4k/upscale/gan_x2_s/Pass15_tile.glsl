// Anime4K_Upscale_GAN_x2_S - Pass 15 of 17 - https://github.com/bloc97/Anime4K
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
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  inputLayer;      // array slice to read (0-based)
//        uint  margin;          // context margin (pixels in feature-map space)
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

layout(set = 0, binding = 3072) uniform sampler pointSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(push_constant) uniform TileParams {
    uvec2 dstOffset;
    uvec2 tileOutExtent;
    uvec2 fullOut;
    uint inputLayer;
    uint margin;
} tile;

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_12_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv0ups;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max(-(texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.06499131, -0.18188648, -0.3129073, 0.46508536, 0.12730247, -0.0048228996, -0.29037076, -0.040671512, -0.37960687, -0.014975028, 0.051478356, -0.17510629, 0.24467152, -0.3726265, -0.05205153, 0.29063764) * g_0;
    result += mat4(-0.036466975, -0.021365412, 0.19166216, 0.2391551, 0.38419026, 0.16602032, 0.06468244, 0.7733659, 0.004007756, 0.03079535, -0.0030497843, -0.2033753, -0.3095698, 0.40909737, 0.067926906, -0.16948561) * g_1;
    result += mat4(-0.07662823, 0.021806711, 0.05107831, 0.09089961, -0.051882017, -0.00308805, -0.08946813, -0.085923605, 0.13135786, -0.040860962, -0.12652986, -0.17011258, -0.23838595, 0.16027555, -0.27720237, 0.3512776) * g_2;
    result += mat4(0.054664467, -0.012412156, -0.11934643, -0.20614244, 0.005247195, -0.07548066, 0.1898925, -0.08086777, -0.27888495, 0.08055913, 0.2733805, 0.05444851, 0.22015096, -0.15712278, 0.070828624, -0.12955543) * g_3;
    result += mat4(-0.19064794, 0.10234088, -0.07635815, 0.15928909, 0.25309163, -0.0055202493, -0.04807871, 0.1251584, -0.19122045, 0.050241888, 0.020203145, 0.12914757, 0.20982412, -0.042472344, 0.12709813, -0.10014193) * g_4;
    result += mat4(-0.025030518, -0.077239156, 0.12003885, -0.07962912, -0.17808792, -0.027223784, 0.13286914, -0.026946044, 0.044607714, -0.045288526, 0.12821364, -0.19116278, 0.053770527, -0.05832497, -0.14832996, -0.08657012) * g_5;
    result += mat4(0.17286317, -0.029046731, -0.06853154, -0.080361344, -0.14082976, -0.076902896, 0.08296736, -0.17621617, 0.10048785, -0.01766402, -0.06414528, -0.012933831, 0.13066664, -0.05233094, 0.09176876, 0.0053013414) * g_6;
    result += mat4(0.09860572, 0.0578288, 0.05035504, 0.017596964, 0.055266783, -0.084020205, 0.1214565, -0.04180339, -0.16650584, 0.02645373, 0.08516016, 0.123672284, -0.11207144, 0.03805417, 0.017909998, 0.08631275) * g_7;
    result += mat4(0.08567236, 0.11860556, -0.2603184, 0.04399533, -0.13169551, -0.14144541, 0.11864987, -0.19813964, -0.14435594, 0.0943669, 0.318387, -0.039731313, -0.05394642, 0.018096905, 0.11445131, -0.07224858) * g_8;
    result += mat4(-0.066673055, -0.0079072425, 0.15320915, 0.1241549, -0.03786454, 0.02686796, 0.062339537, 0.0921351, 0.24909046, -0.13677734, -0.08606315, -0.1311618, -0.11268947, 0.017006561, -0.010060483, -0.016905207) * g_9;
    result += mat4(0.11682704, -0.06385352, 0.048959445, 0.2103904, -0.24271931, -0.114691064, 0.106675364, -0.16527846, 0.20034032, -0.19069487, 0.13964948, -0.2999216, -0.05324707, 0.03835898, 0.002079623, -0.042824514) * g_10;
    result += mat4(0.021089941, 0.058709584, -0.026687654, 0.061108842, 0.13278545, 0.0154480925, -0.1858288, 0.07775379, -0.013820952, 0.04138522, 0.040989578, 0.19044249, -0.05938495, 0.049729984, 0.022488212, 0.13883443) * g_11;
    result += mat4(-0.12241166, 0.24528268, -0.5302565, 0.045535725, -0.054705787, -0.038350295, -0.0833044, 0.18413262, -0.16520579, 0.087780885, -0.42400438, 0.30506396, -0.05254002, 0.0068022306, -0.6969388, 1.901328) * g_12;
    result += mat4(-0.12879479, -0.13513997, -0.068150125, 0.34132335, 0.08568371, 0.086309135, -0.10726202, 0.053040955, -0.007894386, 0.0694188, 0.13861355, -0.06504751, 0.1669743, -0.06529014, -0.048758753, -0.10337064) * g_13;
    result += vec4(-0.022439916, 0.020257013, 0.041364692, 0.0141367195);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv0ups, ivec3(valid_xy, tile.inputLayer), result);
}