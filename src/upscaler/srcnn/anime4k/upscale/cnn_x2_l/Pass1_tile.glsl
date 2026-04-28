// Anime4K_Upscale_CNN_x2_L - Pass 1 of 10 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 4, rgba8) uniform image2DArray img_conv2d_tf;
#define go_0(x_off, y_off) (texture(sampler2DArray(tex_MAIN, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer)))

vec4 hook() {
vec4 result = mat4(-0.01802505, -0.06508559, 0.0017542128, -0.25521114, -0.024155967, 0.07601142, 0.07508073, -0.69212615, 0.06438325, 0.07916419, -0.07266247, -0.17089996, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, -1.0);
    result += mat4(-0.18881685, 0.063188724, 0.08637344, -0.20066689, -0.22774473, -0.10913083, -0.048009537, -0.27475306, -0.15950447, -0.027433012, 0.030303264, 0.018863251, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 0.0);
    result += mat4(0.19171959, 0.028070524, -0.09780952, 0.057611514, 0.26147488, 0.07180017, 0.09667393, 0.008605127, 0.011190245, 0.040944707, -0.025871381, -0.011468774, 0.0, 0.0, 0.0, 0.0) * go_0(-1.0, 1.0);
    result += mat4(-0.08601777, 0.2180965, -0.052060187, -0.08091977, 0.3995336, 0.21213862, 0.105202965, 0.010929526, -0.080743685, -0.040439352, -0.07998862, 0.08096829, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, -1.0);
    result += mat4(-0.08608087, -0.10902571, 0.5245411, 0.53331816, -0.5507893, 0.6141555, 0.9744618, 0.89056116, 0.081408836, 0.28096125, 0.13647869, 0.026274862, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 0.0);
    result += mat4(0.13985278, -0.29691598, -0.26792645, -0.042485088, 0.27941233, -0.65306807, -0.360506, 0.03810829, 0.09663724, -0.26655033, 0.04372338, 0.063264176, 0.0, 0.0, 0.0, 0.0) * go_0(0.0, 1.0);
    result += mat4(0.18246013, -0.070464276, 0.04686214, 0.059332885, 0.16861221, 0.022623831, -0.09161491, 0.07130491, 0.15691474, 0.095743366, 0.059467375, -0.009469478, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, -1.0);
    result += mat4(-0.07830576, 0.17082681, -0.013175545, -0.035535168, 0.1573564, -0.16532823, -0.49614525, -0.050994795, 0.027053844, -0.20359018, 0.08111269, 0.018715343, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 0.0);
    result += mat4(-0.060515754, 0.13169582, -0.15245132, -0.045724656, -0.50778043, -0.11690067, -0.08320143, 0.01093529, -0.1954136, 0.07388989, -0.1360143, -0.023233788, 0.0, 0.0, 0.0, 0.0) * go_0(1.0, 1.0);
    result += vec4(-0.0054077627, -0.15644358, 0.06612042, 0.014728144);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_tf, ivec3(valid_xy, 0), result);
}