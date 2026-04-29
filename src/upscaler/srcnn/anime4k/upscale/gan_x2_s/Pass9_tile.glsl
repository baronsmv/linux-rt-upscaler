// Anime4K_Upscale_GAN_x2_S - Pass 9 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_7_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.43671334, -0.16534646, -0.13688485, -0.008512402, -0.10336664, -0.08822921, -0.116312236, -0.038849946, -0.035221335, 0.019403309, 0.060067646, -0.025432155, 0.090118125, -0.117073216, 0.16502255, 0.034231257) * go_0(-1.0, -1.0);
    result += mat4(0.17112842, -0.023511292, -0.2592198, -0.07303919, 0.048081987, -0.054403186, -0.060226068, -0.2663483, 0.16908844, -0.11529753, -0.036192283, 0.05631556, -0.12996213, 0.32429552, -0.17090482, 0.37093237) * go_0(-1.0, 0.0);
    result += mat4(-0.0398796, -0.21753207, -0.014232783, 0.04652695, 0.06361906, 0.11714849, -0.116917215, -0.0088206185, -0.15661797, 0.11036933, 0.043800946, 0.0088503305, 0.15252474, -0.21677117, -0.26665527, 0.11332868) * go_0(-1.0, 1.0);
    result += mat4(0.14935064, 0.03734691, 0.08192101, -0.28615516, 0.19225292, 0.09485945, -0.018961852, -0.04503368, -0.14962928, 0.14281853, 0.015293623, -0.0051231394, 0.31510183, 0.28869596, 0.1890055, -0.07833456) * go_0(0.0, -1.0);
    result += mat4(0.2734724, 0.37409434, -0.2611236, 0.06528365, -0.1886752, 0.045421556, 0.25771844, 0.14760634, -0.02859129, -0.071093805, -0.1635561, 0.06800318, 0.44370538, 0.43510497, 0.15145455, -0.029246451) * go_0(0.0, 0.0);
    result += mat4(0.17102292, 0.33519942, 0.2755555, -0.24724208, 0.042192735, -0.6907692, -0.10582406, 0.2008313, 0.04859614, -0.24115612, 0.015256011, -0.029317714, -0.057466604, -0.1004556, 0.24814546, -0.22135083) * go_0(0.0, 1.0);
    result += mat4(0.20959556, 0.113371, -0.021680012, -0.054057337, -0.017139604, -0.082443535, -0.03216185, 0.13644056, -0.105473205, -0.033690784, 0.030838218, 0.013347346, 0.49752173, -0.14028637, -0.23801191, 0.059374087) * go_0(1.0, -1.0);
    result += mat4(0.054281052, 0.04908332, 0.065993994, -0.09818599, 0.17124225, -0.22669722, -0.090717405, 0.20086871, 0.05861675, 0.09584638, 0.18013628, 0.026234226, 0.32684898, 0.28582916, -0.03517119, -0.21534745) * go_0(1.0, 0.0);
    result += mat4(0.2143339, -0.009243758, -0.043321237, -0.18695052, 0.0707111, -0.052678097, 0.04782485, 0.06970353, -0.029827276, 0.10827879, 0.049044352, -0.09452859, -0.08516196, 0.11786405, -0.18170272, -0.117841594) * go_0(1.0, 1.0);
    result += mat4(-0.23180094, 0.079831, -0.17606014, -0.06691572, 0.13079396, -0.054930445, 0.025274629, 0.059386294, 0.18818773, 0.071563244, -0.19136675, 0.031156426, 0.12569802, 0.057418842, -0.022066243, 0.09572557) * go_1(-1.0, -1.0);
    result += mat4(0.13405065, -0.038109858, 0.19447789, -0.121862344, -0.5014013, 0.030394621, -0.11468341, 0.24658446, -0.2861801, 0.11453208, 0.17080295, 0.32403797, 0.01776269, 0.21879151, -0.1487332, -0.13659461) * go_1(-1.0, 0.0);
    result += mat4(-0.16852567, 0.37488598, 0.103131816, 0.15805401, -0.5529941, -0.0106922565, 0.14309406, 0.018851891, 0.18253598, -0.18453355, -0.14344332, 0.14581451, 0.00017439971, -0.22823274, -0.02480218, -0.28830686) * go_1(-1.0, 1.0);
    result += mat4(-0.036933262, -0.105577976, 0.02778643, 0.21757011, -0.0051288083, 0.036500473, 0.12934865, -0.18750058, 0.05384686, -0.14823805, 0.12996665, -0.0717687, 0.15035072, 0.00028661545, -0.4272515, 0.102082215) * go_1(0.0, -1.0);
    result += mat4(0.3707243, -0.34236187, -0.037726954, 0.19196671, 0.101593964, 0.3211922, -0.30584693, -0.09473774, -0.012873282, -0.26314828, -0.3015266, -0.05155332, -0.23810461, -0.17289765, 0.16493215, 0.07951415) * go_1(0.0, 0.0);
    result += mat4(-0.054548983, 0.20742553, -0.17368966, -0.11417929, -0.14998713, 0.14250377, 0.08688373, -0.39742398, -0.29795423, 0.3917638, -0.24611169, -0.007993072, -0.052766692, -0.05993209, -0.017495412, 0.2881331) * go_1(0.0, 1.0);
    result += mat4(-0.05283335, 0.081839375, 0.013510656, -0.097930856, -0.09817993, -0.10169309, -0.024573473, -0.061191153, 0.14742163, 0.12549889, 0.21033141, -0.11116201, -0.046900082, 0.052657153, -0.10784069, 0.0005640972) * go_1(1.0, -1.0);
    result += mat4(0.036850937, -0.004740191, -0.105057694, 0.16894996, -0.39845806, -0.11454543, 0.044997875, 0.10780206, -0.15164936, -0.030377366, -0.015979659, -0.16242398, -0.045865484, 0.04037505, -0.03663904, 0.24529697) * go_1(1.0, 0.0);
    result += mat4(0.0041185757, 0.0843081, 0.07231875, 0.100667596, -0.31684703, -0.2574812, -0.03461963, 0.11267055, -0.22542828, -0.104221806, -0.095156625, -0.08219916, 0.18497708, -0.08431334, -0.074380755, 0.07518058) * go_1(1.0, 1.0);
    result += vec4(0.034884464, 0.055267137, 0.03452981, 0.012002485);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_7_tf, ivec3(valid_xy, tile.inputLayer), result);
}