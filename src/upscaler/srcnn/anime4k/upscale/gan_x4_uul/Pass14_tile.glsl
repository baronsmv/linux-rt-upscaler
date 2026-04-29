// Anime4K_Upscale_GAN_x4_UUL - Pass 14 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_3_tf5;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.056609534, -0.072912574, -0.08224053, -0.27446464, 0.06299807, 0.17494963, 0.02013175, -0.3135523, -0.20414291, -0.002206245, -0.19089301, -0.035810925, -0.15909109, 0.23343667, 0.043236874, -0.05090461) * g_0;
    result += mat4(0.071143255, 0.2344495, -0.08178796, 0.19529581, -0.15652603, -0.08692345, 0.15054622, -0.24628481, 0.13293579, 0.099183284, -0.14319651, -0.21706218, 0.18046993, -0.046167973, -0.2622163, 0.14739317) * g_1;
    result += mat4(0.028098702, 0.16937847, -0.31955224, -0.13086726, 0.035734467, -0.12136727, -0.05286461, 0.13372248, -0.012013819, -0.013996318, 0.09585827, -0.0980455, -0.18155457, 0.058416523, 0.05363468, 0.2844176) * g_2;
    result += mat4(-0.040509474, -0.040644035, -0.14309056, 0.109604076, -0.089917555, -0.05080418, -0.06218365, 0.08950535, -0.13581185, 0.30530998, 0.35584477, 0.25160718, 0.11817752, -0.15588048, -0.18560979, -0.021720303) * g_3;
    result += mat4(0.19979374, -0.24442586, 0.06666042, -0.12413865, 0.0723267, -0.08070183, -0.050162878, 0.053533528, -0.23414859, 0.14660425, 0.0535612, 0.1824936, -0.06853291, 0.028537972, 0.08894496, -0.3005856) * g_4;
    result += mat4(0.053230897, -0.14692295, -0.010351058, -0.03423785, -0.34997204, 0.17045908, -0.20471387, -0.05596227, 0.37312284, -0.166506, 0.027370568, -0.19885068, 0.22860329, -0.34381005, 0.13689034, 0.100899346) * g_5;
    result += mat4(0.100836754, 0.172524, 0.14670734, 0.19648418, -0.22542813, -0.14784352, 0.16542062, 0.31592578, 0.09034929, 0.029557507, 0.016295122, 0.06270892, 0.119690046, -0.039440215, 0.1076754, 0.055114914) * g_6;
    result += mat4(0.22560626, -0.19063824, 0.2289656, -0.12238879, 0.062091034, -0.17536564, -0.1097042, 0.18370546, 0.054991204, -0.16073585, 0.24551688, 0.29919684, -0.33145493, 0.06585065, 0.15001276, -0.12141834) * g_7;
    result += mat4(0.0072760796, -0.33641306, 0.27806035, -0.0012592864, -0.031354345, 0.14530547, 0.026439384, -0.08998722, 0.16388611, 0.008192195, -0.031645425, 0.23180926, -0.106261194, -0.21588798, -0.01746241, -0.35864678) * g_8;
    result += mat4(0.11795532, 0.24395278, 0.06954797, 0.05902286, 0.002836295, 0.13273323, 0.17765377, -0.09331522, 0.13427891, -0.12334423, -0.2206351, -0.11630769, -0.19114569, 0.1635797, 0.17295037, 0.012300116) * g_9;
    result += mat4(-0.16389936, 0.104410745, -0.046638153, -0.08462526, -0.05850656, 0.07821304, 0.12509613, -0.08973294, 0.2538881, 0.013903494, -0.18470205, 0.01099874, -0.10122345, -0.2053046, -0.15341048, 0.19987997) * g_10;
    result += mat4(-0.10358656, 0.29928508, 0.07767035, -0.065468244, 0.33847088, -0.010010049, -0.18632844, -0.022442589, -0.20640668, 0.12077326, 0.17598887, -0.036393534, 0.057061106, 0.32527304, -0.17863084, -0.08244848) * g_11;
    result += mat4(-0.019896565, 0.18471427, -0.23525807, -0.090934336, -0.22715406, 0.025219338, 0.08826347, -0.11013379, 0.053721644, 0.020721693, -0.14894027, 0.017000167, -0.077067815, 0.005117918, -0.60429895, -0.46772584) * g_12;
    result += mat4(0.27064618, 0.124304846, 0.17178236, 0.0067777717, 0.20274666, -0.0066843866, -0.10537028, 0.07832309, -0.100172564, -0.084412105, -0.029130317, 0.04364024, 0.08182053, -0.100823514, -0.0935743, -0.029079227) * g_13;
    result += mat4(-0.26241225, -0.05721237, 0.101424344, -0.34958288, 0.31858712, -0.076861545, -0.46517807, 0.30126542, 0.086722255, -0.13480917, 0.11960615, 0.4943688, -0.32738853, -0.19455571, 0.026463214, 0.07926301) * g_14;
    result += mat4(0.16170315, 0.13929573, 0.059762456, 0.23802169, -0.3277194, 0.24683446, 0.112627044, -0.1602516, 0.08662639, 0.1476813, 0.1104441, -0.3317887, 0.16108729, 0.11565731, -0.18657148, 0.01665966) * g_15;
    result += vec4(-0.11646883, -0.009549349, 0.02843715, 0.004513963);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf5, ivec3(valid_xy, tile.inputLayer), result);
}