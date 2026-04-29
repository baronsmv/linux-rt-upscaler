// Anime4K_Upscale_GAN_x3_VL - Pass 6 of 47 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_3_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.09150374, 0.27307025, -0.29910362, -0.1348109, 0.22943531, -0.3949183, -0.5663888, 0.060001444, 0.10339246, -0.13657793, -0.07578187, 0.3050418, -0.06493081, 0.12776284, -0.38266462, 0.06579857) * g_0;
    result += mat4(-0.07931592, -0.067593426, 0.3326977, 0.08658692, -0.15738702, -0.24143377, -0.24007297, 0.3272038, -0.23275268, -0.07847532, 0.3563628, 0.32067114, -0.23376603, 0.0073057627, -0.26839128, 0.009836977) * g_1;
    result += mat4(-0.28198138, 0.32377273, 0.09081581, -0.086309046, -0.12054532, -0.462313, 0.0920237, 0.23586476, -0.021723233, 0.36585453, -0.00796165, -0.39974895, 0.29524347, -0.256584, -0.40205815, -0.19578406) * g_2;
    result += mat4(-0.28249493, -0.11078143, -0.1662569, 0.2984389, -0.0067178444, 0.34377992, 0.32329297, -0.23714112, -0.18873024, 0.24639177, -0.18014365, -0.214034, 0.4113513, -0.30601293, 0.09141208, 0.047741897) * g_3;
    result += mat4(-0.3642344, 0.4233032, -0.4503468, -0.11965398, -0.034085244, 0.18682572, 0.138233, -0.22629389, -0.08205921, 0.12951039, -0.07831761, 0.12225131, -0.08253673, -0.04149855, 0.1658926, -0.22672354) * g_4;
    result += mat4(-0.19474551, -0.098459534, -0.026704386, 0.12555447, -0.14878166, -0.13216433, 0.106912896, -0.116285235, -0.102333605, -0.084978595, -0.1978574, 0.26760474, -0.16923113, 0.1709896, 0.324137, -0.0039849947) * g_5;
    result += mat4(0.278326, -0.18800737, -0.4307119, 0.033457235, -0.36178744, -0.10627576, 0.108752854, -0.1976515, -0.03780597, -0.08123979, -0.12383117, 0.27845758, 0.17234688, 0.35611427, 0.20723963, -0.079292715) * g_6;
    result += mat4(-0.5295802, 0.08056841, 0.1919099, -0.067211255, 0.41047558, 0.14845635, 0.29295865, 0.36605957, 0.1662992, 0.26510397, 0.2262399, 0.105923004, -0.42799288, -0.020592844, -0.09260191, 0.041266896) * g_7;
    result += mat4(0.3346207, -0.1813917, 0.12152124, -0.10919295, 0.0510005, -0.03250092, 0.20248795, 0.05000007, 0.31189185, -0.5248881, 0.17411484, 0.50529236, -0.10991088, -0.055482015, 0.3692675, -0.08483728) * g_8;
    result += mat4(-0.209644, -0.294786, -0.23882675, 0.15662841, 0.15820913, 0.090583235, 0.09068973, -0.038006596, -0.16551273, 0.056037854, 0.108854815, -0.46387982, 0.092163965, 0.053796794, -0.24753033, -0.022790147) * g_9;
    result += vec4(-0.03865883, 0.02926021, -0.01725902, -0.013565478);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf, ivec3(valid_xy, tile.inputLayer), result);
}