// Anime4K_Upscale_Denoise_CNN_x2_UL - Pass 2 of 25 - https://github.com/bloc97/Anime4K
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
//    glslc -fshader-stage=compute --target-env=vulkan1.2 \
//          <this_file> -o <output.spv>
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

layout(set = 0, binding = 3) uniform texture2DArray tex_MAIN;
layout(set = 0, binding = 4, rgba8) uniform image2DArray img_conv2d_tf1;
#define go_0(x_off, y_off) (texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer)))

vec4 hook() {
vec4 result = mat4(0.042849753, -0.11642484, 0.073895186, 0.15186316, -0.024499241, 0.056690346, 0.05013788, -0.10182528, -0.024302427, 0.06578479, -0.028199008, -0.070577, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.040659044, 0.22913207, -0.1847038, -0.11781796, 0.044752445, 0.009552658, -0.11374249, 0.12798874, 0.056919675, -0.20839268, 0.11021251, 0.044297826, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(-0.009999239, 0.1996945, -0.29797587, -0.4280957, -0.008521183, -0.10773894, 0.22186345, 0.254737, -0.003993275, -0.07186837, 0.16690473, 0.19043307, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(-0.16174923, 0.26882383, 0.50559163, 0.38955548, 0.14091976, -0.15637094, -0.11826545, -0.23424837, 0.01674066, -0.08578336, -0.16907434, -0.19845173, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(0.10735882, -0.016069679, 0.42237386, -0.19937111, 0.07271503, 0.07596921, -0.24035113, 0.12406044, 0.059160866, -0.051063746, -0.36897844, 0.061272774, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.015712388, -0.34878746, -0.66418105, -0.35441992, -0.12208571, 0.042238027, 0.30143425, 0.3610614, -0.09538538, 0.25334427, 0.24629802, 0.030739667, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(-0.0035519397, 0.07191882, -0.20775351, -0.15425798, 0.07919461, 0.07578178, 0.12668823, 0.0011835548, 0.03245292, -0.105801836, 0.24585879, 0.13730717, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(0.2415042, -0.16800308, 0.48690978, 0.75166744, 0.3876131, 0.038878918, -0.3293806, -0.47433355, 0.057803743, 0.09533431, -0.1342232, -0.2982094, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(-0.18697992, -0.60250723, -0.11149202, -0.015566043, -0.57483697, 0.07203411, 0.050863862, -0.078300595, -0.09433572, 0.27099958, -0.03195694, 0.10535165, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.043337345, 0.16099554, -0.030338328, 0.0074565704);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf1, ivec3(valid_xy, 0), result);
}