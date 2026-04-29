// Anime4K_Upscale_GAN_x4_UUL - Pass 28 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_6_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_6_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_6_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_8_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_9_tf3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.12601118, -0.021590643, 0.22313827, 0.12338326, -0.3594248, 0.08779226, -0.104447536, 0.0015953421, -0.041181516, -0.059177034, -0.03233909, 0.08123608, -0.06653031, 0.2396167, -0.04595078, -0.27699965) * g_0;
    result += mat4(0.21760523, -0.07761304, 0.10619168, 0.21848077, 0.043161202, -0.18573365, 0.18635494, 0.0596456, 0.00958352, 0.06870374, -0.22098882, -0.19535597, -0.01699866, -0.060843382, 0.020773342, -0.28626204) * g_1;
    result += mat4(-0.054788332, 0.43804136, -0.018370852, -0.11884852, -0.08396486, -0.02463395, -0.07859437, 0.04820491, 0.20736758, -0.05558528, 0.30823594, -0.11240249, 0.3560334, -0.16470565, -0.037384707, -0.26869738) * g_2;
    result += mat4(0.035860125, -0.19114108, -0.014263808, -0.2760586, -0.10599815, 0.24764514, -0.015626451, 0.06531905, 0.03168761, -0.06332368, -0.31058973, -0.04061597, -0.27505493, -0.1417053, -0.1537728, -0.0269434) * g_3;
    result += mat4(0.122250065, 0.014169642, 0.0028120647, 0.29171073, 0.03466068, -0.21740533, 0.017244201, 0.10237153, 0.2732552, 0.08788669, -0.18837062, -0.08003779, -0.16058928, 0.16513692, 0.3796974, 0.14405341) * g_4;
    result += mat4(0.07627521, 0.3994723, -0.2915726, -0.26149854, -0.17089921, 0.10311443, 0.118035555, 0.018972598, 0.060590137, 0.061291203, -0.08347645, 0.07799144, -0.2275661, -0.20265573, 0.008838914, -0.033791874) * g_5;
    result += mat4(-0.26082832, -0.20043238, -0.12740612, 0.022172654, -0.19137274, 0.16447131, -0.12194309, 0.11332352, 0.09688869, -0.11694857, -0.014670798, 0.029100897, 0.27688727, -0.095532894, -0.046852726, 0.15528652) * g_6;
    result += mat4(0.0843288, 0.2599002, 0.054038078, 0.030031947, -0.16868956, 0.47877824, -0.107127056, -0.19649811, 0.1452435, -0.061140474, -0.3746812, -0.1712981, 0.10090316, 0.003146686, 0.042054128, 0.2036839) * g_7;
    result += mat4(0.062476937, 0.109727405, 0.006085406, -0.09609198, 0.08157408, 0.26440763, -0.010807875, 0.4100666, -0.29008973, -0.29712662, 0.1449313, 0.2999071, -0.10133186, 0.14511426, 0.15570813, 0.1363124) * g_8;
    result += mat4(0.24777307, -0.018936818, -0.17767051, -0.2930885, -0.31651247, -0.21320899, 0.024395507, -0.14392355, -0.039903793, -0.028844833, 0.089801095, -0.16740274, 0.076601304, 0.12653774, -0.14753589, -0.076225005) * g_9;
    result += mat4(-0.18826364, 0.011248587, -0.021409662, -0.5352774, -0.08067719, -0.054373614, -0.16357093, 0.06124252, 0.033611584, 0.042493146, 0.05371003, 0.11711034, 0.11154937, -0.12328775, -0.06294046, 0.18647408) * g_10;
    result += mat4(0.0024605107, -0.056066483, 0.2467666, 0.11369053, 0.08489671, 0.0037346834, -0.013299427, 3.808174e-05, 0.11409715, 0.109892204, -0.06361007, -0.22800997, 0.18311475, 0.042961217, 0.06740135, -0.16150832) * g_11;
    result += mat4(-0.18291046, 0.026666109, -0.30111808, 0.17123716, 0.112474516, -0.26450562, -0.090437375, -0.14988331, -0.18449861, 0.007934273, -0.027180828, -0.43781853, 0.0977631, 0.27554545, -0.11660859, -0.23798843) * g_12;
    result += mat4(0.10251913, -0.18264107, -0.06369484, 0.05854778, -0.00926676, -0.29635468, -0.11716115, 0.011359037, 0.08007137, -0.049567226, 0.09789246, 0.36260337, -0.15627296, 0.22855914, 0.015385757, 0.083044454) * g_13;
    result += mat4(0.1003519, 0.024577776, -0.108722664, 0.011721353, -0.10047615, -0.17745872, 0.10435663, -0.08427653, 0.0010758807, 0.14079982, -0.3041788, 0.15151088, 0.008969225, 0.076604255, -0.06943796, 0.044038422) * g_14;
    result += mat4(0.05734037, 0.21680962, -0.11893755, -0.07738818, 0.13322085, -0.04214932, -0.3577641, 0.17797415, -0.07373375, 0.06449437, 0.065212585, 0.28000146, 0.13637395, 0.0667443, 0.040316172, -0.02156067) * g_15;
    result += mat4(0.20441194, 0.23352884, -0.0139005985, -0.16409983, -0.38869008, 0.061168108, 0.01810069, 0.2682549, -0.07966706, 0.08529747, -0.093861535, 0.06709627, -0.23922135, 0.25731438, 0.0763321, -0.1010017) * g_16;
    result += mat4(0.0023142244, -0.22895189, 0.07123541, -0.033806246, -0.49307954, 0.16494593, 0.011563014, 0.040604062, -0.18492593, -0.2750776, -0.13165577, 0.05981473, 0.03329094, -0.125094, -0.03672828, -0.019734263) * g_17;
    result += mat4(-0.049260493, 0.1662821, -0.18388951, 0.23048894, 0.2072809, 0.06807784, -0.29648736, -0.10056884, -0.03960093, 0.46342513, -0.057403132, -0.00022476891, -0.0005029868, 0.43624368, -0.19841333, -0.18943238) * g_18;
    result += mat4(-0.06875925, 0.19902602, 0.039521616, -0.025893142, 0.091499686, 0.020004159, 0.07892145, 0.12688632, 0.060283042, -0.11150475, 0.07054853, -0.1520924, -0.19681256, 0.07284978, 0.029370772, 0.22104816) * g_19;
    result += vec4(-0.0796562, -0.0549894, 0.3559776, 0.19150664);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf3, ivec3(valid_xy, tile.inputLayer), result);
}