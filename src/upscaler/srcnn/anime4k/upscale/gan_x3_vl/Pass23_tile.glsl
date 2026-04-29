// Anime4K_Upscale_GAN_x3_VL - Pass 23 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.022616543, -0.07495665, 0.20578638, -0.24614015, 0.20188546, 0.07821132, -0.55689156, 0.078048594, 0.16035397, -0.18943994, -0.109294415, 0.11644118, -0.25667566, -0.17004293, -0.34455723, -0.08808675) * g_0;
    result += mat4(0.28649247, 0.056165792, -0.49363118, -0.1529661, 0.07703691, 0.07966694, 0.58834124, 0.20894507, 0.46345595, 0.19134133, 0.12830314, -0.06366993, 0.1250579, 0.18356793, -0.1408607, -0.16252096) * g_1;
    result += mat4(-0.059020188, -0.21338785, 0.017160866, -0.06280688, -0.12539028, 0.032399278, 0.046102162, -0.012033963, 0.19066435, -0.21461637, 0.07392558, 0.022834225, 0.18924391, -0.027622582, -0.24777018, -0.090185896) * g_2;
    result += mat4(-0.32912537, -0.12669958, 0.092723176, 0.09256268, 0.013792983, -0.13308536, 0.16042812, -0.2033247, -0.06560468, -0.019620765, 0.08362642, 0.055273537, 0.12208806, -0.20194231, 0.084021725, 0.38380083) * g_3;
    result += mat4(-0.1571086, 0.03144169, -0.2251698, -0.06480453, 0.001744102, 0.0010039994, -0.027967803, -0.11266107, -0.40678036, -0.07481646, -0.24311328, 0.042732738, 0.018475516, -0.113912515, 0.03153217, -0.034913916) * g_4;
    result += mat4(0.014403644, -0.020557571, 0.38122526, 0.03807282, 0.28673846, 0.13712813, -0.042157043, -0.12968376, 0.12554988, -0.14628744, -0.00392324, 0.014086664, 0.079255715, 0.09928858, -0.11087327, 0.0699405) * g_5;
    result += mat4(-0.35458207, 0.029392743, -0.31504998, 0.13302153, 0.17734766, -0.10416982, -0.0036142413, -0.12197593, -0.17005852, 0.1727392, 0.11929178, 0.16293883, -0.25592133, 0.08175675, 0.2355234, 0.022874065) * g_6;
    result += mat4(0.21167323, -0.26767167, 0.08588045, 0.058573887, -0.01292999, 0.22167805, 0.11722694, 0.5700164, 0.044330835, -0.29406846, -0.11540253, -0.21386458, -0.08779367, -0.12368158, 0.0667155, 0.32094228) * g_7;
    result += mat4(-0.08529116, 0.09712954, 0.09333625, 0.06606905, -0.1782532, 0.051486395, -0.10986318, -0.20011626, -0.023568239, 0.20281026, 0.03716514, 0.1831125, 0.22586478, -0.058135565, 0.0030777368, 0.0015794474) * g_8;
    result += mat4(-0.007098127, -0.11688584, 0.0133981705, 0.17757058, 0.02897332, -0.18530834, -0.0032577885, -0.08089542, -0.0020816326, -0.3233896, -0.13044983, -0.04108618, 0.0110450545, -0.01834794, -0.17684971, -0.06611739) * g_9;
    result += mat4(0.2604118, 0.3291361, 0.07571542, 0.32165763, -0.06534106, -0.10623649, 0.18254459, 0.063651256, -0.021245563, 0.06759048, -0.39714596, -0.12235311, -0.059783626, 0.10078259, 0.26484212, -0.13679399) * g_10;
    result += mat4(0.13124742, 0.11206922, -0.0684187, -0.20119804, -0.09549651, 0.0703663, -0.19196616, -0.14344019, 0.029426184, -0.057151172, 0.19186652, 0.24676153, 0.35762733, 0.10300911, 0.08581454, -0.015290781) * g_11;
    result += mat4(0.06758918, 0.37075385, -0.2334613, 0.25336525, -0.026440224, 0.024827614, 0.07352414, -0.1794877, -0.018798998, 0.10824414, 0.01850616, 0.03725088, -0.079103224, -0.056518886, -0.01137129, -0.00012351258) * g_12;
    result += mat4(0.09624113, -0.18910943, 0.30205646, 0.43680936, 0.21888132, -0.22264229, -0.15398757, 0.29324576, 0.006859953, -0.077507176, -0.090208314, -0.20981432, -0.21420066, 0.06341929, -0.07640488, -0.031766582) * g_13;
    result += mat4(-0.025704857, 0.09863719, 0.04335183, -0.06731708, 0.019300275, -0.39722142, -0.13667129, 0.15554759, -0.3567945, -0.008414992, -0.05418159, -0.2149799, -0.17905809, 0.0051317243, 0.037312187, -0.05859764) * g_14;
    result += mat4(0.25617346, 0.009854824, -0.019909287, 0.06340188, -0.10071771, 0.10874236, 0.38549116, 0.098355606, 0.2930539, 0.11536922, -0.14541107, 0.035229255, -0.3127395, 0.27851996, -0.0048802355, 0.02862268) * g_15;
    result += vec4(-0.0006504641, -0.014806257, -0.015985647, 0.021676043);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf2, ivec3(valid_xy, tile.inputLayer), result);
}