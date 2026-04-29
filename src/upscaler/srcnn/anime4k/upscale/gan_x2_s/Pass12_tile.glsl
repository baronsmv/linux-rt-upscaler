// Anime4K_Upscale_GAN_x2_S - Pass 12 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_10_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.034931988, -0.10314893, 0.050731838, 0.008667428, 0.093605734, 0.18763398, 0.1329972, 0.32109565, 0.018679736, 0.16050446, -0.21393016, -0.5850818, -0.03595686, -0.06816087, 0.058053996, 0.14945738) * go_0(-1.0, -1.0);
    result += mat4(0.13086358, 0.1037956, 0.024482725, 0.28596595, 0.03427747, 0.03360277, -0.08412939, -0.09863662, -0.14649919, 0.049508557, -0.040583454, -0.3193693, 0.09898459, -0.055807225, -0.13826977, -0.24508655) * go_0(-1.0, 0.0);
    result += mat4(0.022690594, -0.049172435, -0.043048073, 0.28297383, -0.12327597, 0.12841734, 0.19118458, -0.14444864, 0.25481266, -0.1530131, -0.32560238, 0.28813502, 0.07987849, -0.081693284, 0.023993304, 0.051493756) * go_0(-1.0, 1.0);
    result += mat4(-0.21383128, 0.10948106, 0.29768178, 0.5630563, -0.097254336, 0.3000293, 0.27545682, -0.10354583, 0.064267136, -0.0722382, 0.16716443, -0.29272497, 0.124174535, -0.09405645, -0.07759505, -0.63239044) * go_0(0.0, -1.0);
    result += mat4(-0.049770556, -0.2611922, -0.11767422, -0.056895554, -0.10655438, 0.15822971, -0.15873717, -0.034663625, -0.22618848, -0.037567407, 0.8648974, 0.15630767, 0.24981938, 0.15488663, -0.01769864, -0.05102535) * go_0(0.0, 0.0);
    result += mat4(0.021745246, -0.019828277, -0.2533036, 0.08191131, 0.21484213, 0.07265768, 0.13022637, 0.12640825, 0.3097948, 0.1656624, 0.29834095, 0.26926345, 0.1445516, -0.096134044, 0.23720652, 0.104119554) * go_0(0.0, 1.0);
    result += mat4(-0.0026226363, -0.11969785, -0.07630252, 0.48163646, 0.020707106, 0.098053664, 0.15194124, -0.067455925, -0.0072260266, -0.063311785, -0.13165388, -0.2720021, 0.056918275, -0.46139827, 0.062053606, -0.2062505) * go_0(1.0, -1.0);
    result += mat4(0.18370466, -0.21412961, -0.08481129, 0.012198226, -0.08129054, 0.5550795, 0.047955874, 0.2502166, -0.07373375, 0.28914857, -0.0046189106, -0.014052611, -0.1366542, -0.4555943, -0.053266894, 0.4447608) * go_0(1.0, 0.0);
    result += mat4(-0.028673984, -0.05453405, -0.118545935, -0.069395766, 0.17180833, 0.17611517, 0.13780451, 0.28597325, -0.07254466, 0.05339366, 0.0095731495, 0.17107281, 0.08671597, -0.06200009, -0.06297748, 0.08674916) * go_0(1.0, 1.0);
    result += mat4(-0.040299665, 0.095958404, 0.052906267, -0.48397818, -0.1331588, -0.0012678325, -0.042020816, -0.33833674, -0.012395556, 0.07671447, -0.15005252, -0.083733305, 0.12279073, 0.13883469, -0.10359484, -0.31333458) * go_1(-1.0, -1.0);
    result += mat4(0.14495945, -0.12174993, -0.11281622, -0.018538697, -0.14329918, 0.12817283, -0.046540275, -0.1030246, -0.1832771, -0.30401602, -0.33390167, -0.052471336, 0.12632851, 0.23514742, 0.0011784412, -0.49560672) * go_1(-1.0, 0.0);
    result += mat4(0.08295849, 0.044828687, 0.27639604, 0.039427668, 0.02818349, -0.06210292, -0.27352595, 0.19817229, -0.18440844, -0.06898423, 0.0017214341, -0.18130824, -0.0071537187, 0.03517007, -0.2113949, 0.025240164) * go_1(-1.0, 1.0);
    result += mat4(-0.2006673, -0.041704424, 0.16268894, -0.25376207, 0.07905478, -0.17365594, 0.10044552, -0.20418073, 0.085226685, -0.16344517, -0.11064805, -0.2824042, 0.00095205643, 0.31177342, -0.3084233, -0.0908839) * go_1(0.0, -1.0);
    result += mat4(0.26129997, 0.3127755, 0.06982181, 0.23317924, -0.05344337, 0.008762884, 0.20765801, 0.13311344, -0.021598162, 0.0038430444, -0.40633947, 0.09444498, -0.097569115, 0.1161639, 0.051482536, -0.13007577) * go_1(0.0, 0.0);
    result += mat4(0.1168701, 0.10319956, -0.26231092, 0.13755418, -0.31545812, 0.21018027, -0.2570223, 0.11072984, 0.169098, -0.092338, 0.19418359, -0.24841106, 0.2179265, 0.26306525, -0.030364338, 0.011455713) * go_1(0.0, 1.0);
    result += mat4(0.013165953, -0.027480505, 0.019355817, -0.22797722, 0.10252238, -0.13104701, 0.043106645, -0.113860615, 0.077017605, 0.16079858, -0.13723075, 0.08403468, 0.07229952, -0.07288171, 0.153157, -0.30485252) * go_1(1.0, -1.0);
    result += mat4(-0.18590495, -0.02694476, 0.14553905, 0.135362, 0.033088487, -0.49798432, -0.11869643, 0.15896079, 0.09456545, -0.14991766, -0.15788183, -0.13954063, -0.1400199, 0.47176227, 0.1710854, 0.24664737) * go_1(1.0, 0.0);
    result += mat4(0.15082799, -0.1990422, -0.07347236, 0.106623515, -0.054368034, -0.10389193, -0.0711653, -0.022524087, -0.056636613, -0.07881972, 0.09727487, -0.16494693, 0.13156064, 0.176482, 0.11008391, 0.16038191) * go_1(1.0, 1.0);
    result += vec4(-0.0891901, 0.05071113, -0.026449949, -0.0051819966);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_10_tf, ivec3(valid_xy, tile.inputLayer), result);
}