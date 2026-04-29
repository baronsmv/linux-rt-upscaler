// Anime4K_Upscale_GAN_x3_L - Pass 7 of 30 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_3_tf1;
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
vec4 result = mat4(0.029635962, 0.08045753, 0.03622311, 0.06677362, 0.14780864, -0.087087184, 0.22309896, -0.1772139, -0.08716722, 0.1075154, 0.044472143, 0.021324798, 0.10346262, -0.24718447, -0.2489118, 0.4517737) * g_0;
    result += mat4(0.20637918, -0.11695054, 0.27656725, 0.009858572, -0.62555677, 0.12796827, -0.057749186, -0.02636826, 0.11764726, -0.034879886, -0.062285252, -0.048256125, 0.37146622, -0.17392562, 0.24782267, 0.3184173) * g_1;
    result += mat4(0.2624149, 0.007052751, 0.1595428, 0.26269603, -0.33775207, -0.66331345, 0.18036188, -0.25012106, -0.15003558, 0.12337829, -0.3230818, 0.06187628, 0.096601635, 0.24300486, -0.13784438, 0.27110842) * g_2;
    result += mat4(-0.180413, 0.039972585, 0.48966697, -0.4130023, -0.03654654, -0.27514896, -0.025462124, 0.06652415, 0.28900522, 0.035381883, 0.20655172, 0.0073647103, -0.5028713, -0.0061578755, -0.09185675, -0.52771837) * g_3;
    result += mat4(-0.3205473, -0.23172325, -0.20749244, 0.058195353, 0.20280065, -0.106998004, 0.08968707, 0.10981961, -0.13291806, 0.0028465164, 0.11793527, 0.11942547, 0.100123264, -0.14852245, -0.032194547, -0.118260525) * g_4;
    result += mat4(0.004620961, -0.13271236, 0.110130526, -0.075169735, 0.35998157, -0.046072174, 0.02044828, -0.1019322, -0.038753018, -0.12328749, -0.28227237, 0.18373057, -0.23704045, 0.20384738, 0.097455874, -0.23102747) * g_5;
    result += mat4(0.30397, -0.007688397, -0.2519374, -0.14401323, -0.031671453, 0.10171321, -0.18295656, -0.029794114, 0.19171898, 0.23662621, 0.09319509, -0.3479054, 0.036986895, 0.13572362, 0.1142681, -0.17851138) * g_6;
    result += mat4(-0.19525734, 0.36855492, 0.05751295, -0.12524441, 0.06309533, 0.20228319, -0.07533531, 0.26733333, -0.21407285, -0.2900094, -0.28743416, 0.18039729, -0.27968687, -0.23786859, -0.21049118, -0.006130187) * g_7;
    result += mat4(0.34406897, -0.14967814, 0.56049985, -0.18166065, -0.061995413, 0.117799215, 0.3054206, 0.4034068, -0.2116504, -0.6017806, 0.004660423, 0.051566444, 0.4380975, -0.3172436, -0.09930328, -0.16182126) * g_8;
    result += mat4(-0.09316841, 0.036305115, -0.30209473, 0.098138526, -0.012532953, -0.050068337, -0.22571203, -0.30636647, -0.124337815, 0.07323685, -0.15504828, 0.19263308, -0.017216058, 0.34484297, -0.1460544, -0.24951003) * g_9;
    result += vec4(0.10388342, 0.00828351, 0.14884935, 0.034392886);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf1, ivec3(valid_xy, tile.inputLayer), result);
}