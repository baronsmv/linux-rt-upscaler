// Anime4K_Upscale_GAN_x2_S - Pass 11 of 17 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_9_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_11_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.099030726, -0.06836123, 0.08793171, -0.08440806, 0.1367897, -0.18130925, -0.061028607, -0.0036578078, -0.2664728, 0.11683366, -0.106817886, 0.054352235, -0.037010342, -0.04099114, -0.024939198, 0.17543977) * go_0(-1.0, -1.0);
    result += mat4(-0.005120602, 0.033574037, 0.15293613, 0.14662915, 0.16131143, 0.14048538, -0.07979977, -0.09974233, 0.12065904, -0.027316207, 0.05308134, -0.39921048, -0.11916608, 0.05068417, -0.064156584, 0.0906338) * go_0(-1.0, 0.0);
    result += mat4(0.19719984, 0.031454016, 0.057130553, -0.08133089, -0.48387995, -0.20429122, -0.2968695, 0.17029694, 0.2686546, -0.32400158, 0.23564363, -0.12357238, -0.039444853, -0.25260264, -0.045210194, 0.009996893) * go_0(-1.0, 1.0);
    result += mat4(0.24888185, -0.16971394, 0.23991539, -0.20469886, -0.05449719, -0.22697294, -0.19475369, -0.14052935, 0.15595771, 0.09519395, -0.18674417, -0.19258659, -0.18656066, -0.07679601, 0.04305061, -0.052698307) * go_0(0.0, -1.0);
    result += mat4(0.26016366, 0.37886587, 0.29538265, 0.13591415, 0.08657945, 0.2248858, 0.13191143, -0.27878642, 0.38287383, -0.24528888, 0.16275367, -0.4445379, -0.15009366, 0.21030647, 0.04707718, -0.36865705) * go_0(0.0, 0.0);
    result += mat4(0.00060599507, -0.063061595, 0.09708327, 0.18096425, -0.18803552, -0.15204777, -0.21307996, 0.25915486, 0.180343, 0.15965502, 0.4193544, 0.11587751, -0.01724538, -0.0003311443, 0.118263096, 0.3388005) * go_0(0.0, 1.0);
    result += mat4(-0.11013732, -0.24454343, 0.11523979, 0.16267157, 0.037852544, -0.018723588, -0.044225607, 0.010824283, -0.09449054, -0.43009904, 0.17163227, 0.058022983, 0.3704038, -0.124312826, -0.04090871, -0.41738933) * go_0(1.0, -1.0);
    result += mat4(-0.08466185, -0.032986447, -0.12251885, -0.061746452, -0.28120902, -0.03351265, -0.07977477, 0.035497896, -0.40911916, -0.265343, 0.18400514, 0.18039864, 0.2885377, 0.17138512, -0.2672905, -0.17658347) * go_0(1.0, 0.0);
    result += mat4(0.14892288, 0.054083705, 0.074718416, 0.011234817, -0.1644216, 0.10958687, 0.016626561, 0.13260235, 0.15622494, 0.028492622, 0.16308293, 0.0817191, 0.004302441, -0.03425889, 0.019733155, 0.20729025) * go_0(1.0, 1.0);
    result += mat4(-0.10912273, 0.18627015, -0.12923245, -0.007432667, -0.15062776, 0.1132029, -0.039932206, -0.048926212, -0.19350322, -0.052288085, -0.062460408, 0.06341913, -0.22352171, 0.12735958, -0.030772611, 0.10314876) * go_1(-1.0, -1.0);
    result += mat4(0.055571638, -0.29345444, -0.05150461, 0.038981512, -0.20368473, -0.1620652, 0.2212063, 0.16812243, -0.25869122, -0.055914585, 0.1699279, 0.09515419, -0.051229157, 0.029384349, 0.2958992, 0.33411613) * go_1(-1.0, 0.0);
    result += mat4(-0.16893966, -0.11777383, -0.1890183, 0.3100362, 0.32964075, 0.1503138, 0.23687156, -0.1966872, -0.34989685, 0.018697567, -0.054476835, 0.2467992, 0.1404086, 0.042806204, 0.22713056, -0.07194008) * go_1(-1.0, 1.0);
    result += mat4(0.1294499, 0.08734431, -0.27748963, -0.30450672, 0.347131, 0.10832939, 0.094416045, -0.021583052, -0.03705905, 0.13216147, 0.060019907, 0.17617045, -0.31731188, 0.055844136, -0.32436728, 0.09127553) * go_1(0.0, -1.0);
    result += mat4(-0.37301856, -0.59706587, 0.14188358, -0.11759082, -0.123990245, 0.17104799, -0.22897844, 0.044174567, 0.08194783, 0.5041956, 0.080176726, 0.30695775, 0.14737315, 0.06887362, -0.14944588, 0.041438155) * go_1(0.0, 0.0);
    result += mat4(0.028311472, -0.12458831, 0.09180698, 0.21692544, 0.26750755, -0.095768556, 0.37605208, -0.09700436, -0.43799365, -0.2001086, -0.22588708, 0.21119161, 0.017415013, 0.15119827, -0.015756091, -0.097044095) * go_1(0.0, 1.0);
    result += mat4(0.07018085, 0.07628864, 0.03961951, 0.032012466, 0.09119677, -0.11489552, 0.086640276, -0.10799725, -0.09006475, 0.18994014, 0.015971951, 0.025477583, 0.034011904, -0.07448855, -0.090691224, -0.08970111) * go_1(1.0, -1.0);
    result += mat4(-0.036299143, 0.14122474, -0.1863209, 0.1802412, 0.25498003, 0.12084085, -0.15148233, -0.15718026, 0.00034174722, 0.13090368, -0.17938401, -0.064941354, -0.42650834, -0.24431564, 0.1735792, -0.08763975) * go_1(1.0, 0.0);
    result += mat4(-0.018800588, -0.09828807, 0.022626605, 0.19307971, 0.2295834, 0.021806285, 0.17869954, -0.089709155, 0.039047185, 0.1444108, -0.058205944, -0.0141449645, 0.10705844, 0.17592433, -0.017586943, 0.100735694) * go_1(1.0, 1.0);
    result += vec4(-0.10319947, 0.010868113, 0.0143356435, -0.007343647);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_11_tf, ivec3(valid_xy, tile.inputLayer), result);
}