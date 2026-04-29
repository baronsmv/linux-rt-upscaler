// Anime4K_Upscale_GAN_x4_UUL - Pass 20 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_3_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_3_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_3_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_3_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_3_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_3_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_3_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_3_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_3_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_3_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.0947985, 0.2332559, -0.024840387, -0.12695168, -0.011602261, -0.14465079, 0.08024385, -0.22528623, 0.1340458, -0.07059673, -0.3695891, 0.12334664, 0.20933141, -0.09326808, -0.2975661, 0.061081678) * g_0;
    result += mat4(-0.11507307, 0.35812494, -0.17707227, -0.014434964, -0.15823618, 0.13134694, -0.18273474, -0.14312805, 0.12061932, 0.1496361, -0.03527865, 0.08025679, 0.21869129, 0.07058963, -0.16300866, 0.047147434) * g_1;
    result += mat4(-0.044750545, -0.009959345, -0.099832825, 0.05492685, -0.08516999, -0.05746863, -0.15037218, -0.12047596, 0.027117934, 0.08349217, -0.064510226, 0.19004482, 0.016504517, -0.19758373, -0.029387178, 0.024999566) * g_2;
    result += mat4(-0.19270788, -0.15476836, 0.24117126, -0.0379194, 0.3743418, -0.103265874, 0.13830991, -0.036348045, 0.0559878, -0.10660704, 0.13829483, -0.16407472, -0.11997183, 0.01790227, 0.14605843, -0.07279059) * g_3;
    result += mat4(0.28092733, -0.16125645, -0.2748912, 0.26881403, 0.059113085, -0.054873332, -0.021884039, 0.089765035, -0.1258933, -0.039875403, 0.08049244, 0.14648421, 0.15913528, 0.11868216, 0.26197466, 0.20166811) * g_4;
    result += mat4(0.15582782, 0.404659, 0.0015323871, 0.042285357, 0.03543343, 0.28058854, 0.09269268, -0.1961485, -0.050092928, 0.23627135, 0.18665306, -0.2269804, 0.019387577, -0.27056855, -0.032678973, -0.1313305) * g_5;
    result += mat4(0.041672353, -0.11869399, -0.10265229, -0.08001758, -0.083409294, 0.27257153, 0.029960267, 0.009504049, -0.25293326, -0.028966684, -0.26568112, 0.07192321, -0.45549354, 0.00988489, 0.2838676, -0.15658323) * g_6;
    result += mat4(-0.0969234, -0.44853622, 0.1312735, 0.36762837, 0.29700848, -0.055008043, -0.107015595, 0.26205721, -0.025227455, -0.26865402, 0.037786532, 0.14742893, -0.21797921, -0.09365055, 0.1648379, 0.11523759) * g_7;
    result += mat4(-0.08800255, -0.22999708, 0.15386356, -0.15094003, -0.1857585, 0.11688115, 0.23875357, 0.19499353, 0.0412525, -0.024864528, 0.22446378, -0.2659101, 0.08516812, 0.45923305, 0.10732433, -0.09354394) * g_8;
    result += mat4(0.20697595, -0.20005412, -0.035901353, -0.13551861, -0.025914649, -0.28284183, -0.11218443, -0.10993567, -0.07797817, 0.1730173, -0.09316322, 0.03815029, 0.10571366, -0.038362827, -0.1914281, -0.09927578) * g_9;
    result += mat4(-0.14568554, -0.11636077, 0.19675533, -0.041014023, -0.25883666, -0.12882718, 0.31183702, -0.0011882539, 0.14754722, 0.024993556, 0.0168953, 0.067850605, -0.19463025, 0.034864627, 0.041240662, -0.03222681) * g_10;
    result += mat4(-0.1426807, 0.15183157, 0.15200667, -0.14715526, -0.17436193, -0.2790302, 0.092628404, 0.17627066, 0.08689362, -0.12282142, -0.22965756, 0.0715357, -0.06378668, -0.038817883, 0.006680897, -0.16652597) * g_11;
    result += mat4(-0.112664886, 0.16732118, -0.082690485, -0.36430246, 0.1043046, -0.20746218, -0.26694834, 0.118057035, -0.005464113, 0.16917925, -0.007820917, 0.0140616475, -0.074033186, -0.21199086, 0.03959589, -0.024746282) * g_12;
    result += mat4(0.11506031, 0.23876894, -0.08834736, 0.21521813, -0.074349664, 0.13053001, -0.11863015, 0.0024896788, 0.031616643, -0.24681048, 0.1621546, 0.038487136, -0.001199782, 0.14914162, 0.013806334, 0.01951855) * g_13;
    result += mat4(-0.008453833, 0.26529935, -0.11500479, -0.44277295, 0.043010518, -0.15156142, -0.17212024, -0.13284442, 0.14113069, 0.076676466, -0.120249875, -0.10003942, 0.36022985, 0.35055906, -0.021890117, 0.13908324) * g_14;
    result += mat4(0.074958876, 0.18787664, 0.11494537, 0.3821255, 0.07704636, 0.175412, 0.024792312, 0.111158736, -0.060063202, -0.08937286, 0.21284722, 0.09321436, 0.050422233, -0.10608569, 0.13923599, 0.11934222) * g_15;
    result += mat4(-0.07895042, -0.019823313, -0.042007383, -0.044339843, 0.050560612, -0.13500823, -0.1591223, 0.2070823, 0.3217226, 0.0050152694, -0.08454321, 0.15309334, 0.1487958, 0.23113962, -0.037693724, -0.011872479) * g_16;
    result += mat4(-0.08302536, 0.12064725, 0.015102583, 0.019917564, -0.15781376, -0.03290087, -0.365194, -0.010774219, -0.15353476, 0.0021079888, 0.14096913, 0.015317738, -0.21820316, -0.18941125, -0.07205566, 0.16917731) * g_17;
    result += vec4(-0.05091759, 0.03221878, 0.05122183, -0.009628421);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf3, ivec3(valid_xy, tile.inputLayer), result);
}