// Anime4K_Upscale_GAN_x2_S - Pass 2 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_2_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.02899383, 0.12331602, 0.1755303, 0.14228395, -0.23719487, 0.28783783, -0.15755224, 0.16501419, 0.09971766, -0.112085044, 0.15989542, 0.013457646, -0.21386063, -0.10184436, 0.2920392, 0.11544854) * go_0(-1.0, -1.0);
    result += mat4(-0.09577094, 0.052495796, 0.5072853, -0.16720837, -0.030821526, -0.13200149, 0.061197, 0.09785798, 0.097248554, -0.056709435, -0.12684566, 0.25153175, 0.12550084, 0.5723225, -0.061046973, 0.2737185) * go_0(-1.0, 0.0);
    result += mat4(0.14275773, 0.3116807, 0.020866666, -0.029567914, 0.054051064, -0.018836629, 0.16237853, 0.23302408, 0.23014219, -0.20245266, -0.040263597, 0.10550008, -0.1419676, -0.07544839, -0.04724355, 0.06713984) * go_0(-1.0, 1.0);
    result += mat4(-0.36056906, 0.21647012, -0.21559654, -0.1321654, 0.26311335, -0.35098836, 0.08977303, -0.2912846, -0.03221502, -0.33539286, 0.55078757, 0.14826211, 0.12334663, 0.031169238, 0.0626983, 0.13543329) * go_0(0.0, -1.0);
    result += mat4(0.032711882, 0.53162986, 0.1736962, 0.22126123, 0.13229683, 0.12998195, -0.08843839, 0.3830243, -0.29015037, -0.13158421, 0.2987182, 0.0039998284, -0.4924434, -0.34931743, 0.3501415, -0.015819922) * go_0(0.0, 0.0);
    result += mat4(0.039777573, -0.039639533, -0.27015024, -0.33144557, -0.11338446, -0.19242573, 0.48813564, -0.24602202, 0.120988116, -0.12362437, 0.23984735, -0.33717445, 0.14359151, -0.09583342, -0.015998919, -0.19725454) * go_0(0.0, 1.0);
    result += mat4(0.17751572, -0.14914338, -0.24518701, 0.22713365, 0.10613938, 0.12027283, 0.1582502, 0.011725502, -0.02418084, 0.106176965, 0.10111444, 0.07009088, 0.017611375, 0.369643, -0.21788761, -0.15093188) * go_0(1.0, -1.0);
    result += mat4(0.0863035, -0.43148708, 0.0994751, 0.17801163, -0.42566994, -0.2744198, -0.028655952, -0.2481176, -0.26144302, -0.26753834, 0.11043684, -0.48341632, 0.41320416, 0.25118062, -0.31461874, 0.36563694) * go_0(1.0, 0.0);
    result += mat4(-0.04845539, -0.2790916, -0.1626853, 0.18036526, 0.2368911, -0.5688802, 0.05240968, -0.034105603, -0.14011742, -0.37861058, -0.096871816, -0.27824572, 0.41195226, 0.23514003, 0.12282304, 0.28447765) * go_0(1.0, 1.0);
    result += mat4(-0.13261828, -0.13148594, 0.05470859, -0.114724025, 0.17642413, -0.05585294, 0.44086194, -0.10915775, -0.23456413, -0.18385538, -0.4193869, 0.2708079, 0.03720121, 0.15744475, 0.092449814, -0.0922205) * go_1(-1.0, -1.0);
    result += mat4(-0.14146912, 0.386554, -0.15197717, 0.1682067, -0.33229175, 0.18661757, 0.142476, -0.05811066, -0.12433686, 0.20817612, 0.17710523, 0.24227881, -0.3699883, -0.14644128, -0.066485085, -0.010829679) * go_1(-1.0, 0.0);
    result += mat4(0.02267665, -0.21349631, 0.05916224, 0.07111888, -0.3317847, -0.044436328, -0.08067249, -0.13602455, -0.2652356, -0.13666181, 0.022768881, -0.21616152, 0.10042784, 0.13159652, -0.062913835, -0.12882891) * go_1(-1.0, 1.0);
    result += mat4(-0.21270499, 0.14776433, 0.26771793, 0.41242316, -0.22445452, 0.3885536, -0.36809587, 0.09838256, 0.030300573, -0.016225152, -0.41985163, -0.32797396, 0.3021247, -0.2566993, 0.24282119, 0.071926266) * go_1(0.0, -1.0);
    result += mat4(-0.14173156, 0.10360139, 0.03603846, 0.23004, -0.37078354, -0.7556456, 0.43359467, -0.42839774, -0.08143208, -0.061868757, -0.017048405, -0.1806454, 0.07700074, -0.028751602, -0.49057922, -0.07150736) * go_1(0.0, 0.0);
    result += mat4(-0.21411006, -0.039522924, -0.11006789, 0.30172586, -0.019509817, 0.34646508, 0.03348711, 0.3949624, 0.09367525, 0.11841692, 0.064099714, 0.30587056, 0.00071666663, 0.09569139, 0.07905173, -0.043038815) * go_1(0.0, 1.0);
    result += mat4(-0.1082019, -0.081530154, 0.1997084, 0.0064345463, -0.002075576, 0.0122295255, -0.21594198, -0.20039533, 0.023058774, 0.061136324, -0.043233447, 0.018114857, -0.12538326, -0.008044748, 0.08879177, 0.29855737) * go_1(1.0, -1.0);
    result += mat4(0.06425974, -0.162355, -0.07716668, -0.1783711, 0.08560717, 0.42500424, 0.15796345, 0.25115898, 0.39673963, 0.24484198, -0.16364126, 0.45589596, -0.54474986, -0.41130677, 0.15731613, -0.13945425) * go_1(1.0, 0.0);
    result += mat4(-0.4015527, -0.22220162, 0.088239804, -0.16343592, -0.05973259, -0.053600565, -0.11719207, 0.340347, 0.07810557, 0.06943392, 0.07088433, 0.36863637, -0.16925047, -0.09059371, -0.086145744, -0.26417965) * go_1(1.0, 1.0);
    result += vec4(-0.041068032, 0.02181786, -0.02366552, 0.07215206);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_2_tf, ivec3(valid_xy, tile.inputLayer), result);
}