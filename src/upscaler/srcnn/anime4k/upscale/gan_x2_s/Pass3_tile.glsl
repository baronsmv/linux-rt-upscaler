// Anime4K_Upscale_GAN_x2_S - Pass 3 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_1_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.016554115, 0.41586095, -0.11134646, 0.041401796, -0.032285847, 0.07744446, 0.012422875, 0.08027069, -0.11944374, -0.4644861, -0.1625419, 0.09757052, 0.08459575, -0.32677624, -0.15526624, 0.13285875) * go_0(-1.0, -1.0);
    result += mat4(-0.05147117, -0.31841335, -0.07968151, -0.037866592, -0.1438723, 0.21164599, 0.042448167, 0.1660907, -0.03240849, 0.2866945, -0.123190455, -0.2005157, -0.100519955, -0.04109891, -0.14908177, -0.20055951) * go_0(-1.0, 0.0);
    result += mat4(-0.33594802, 0.17970876, -0.08458461, 0.22198248, 0.041744266, 0.053618595, -0.64927346, 0.43071616, -0.042823542, 0.36384553, 0.13817975, -0.23117469, -0.009722301, 0.043797005, -0.006320899, -0.056160737) * go_0(-1.0, 1.0);
    result += mat4(0.020939048, 0.15744017, -0.18557346, 0.2221421, 0.13683408, -0.17577636, -0.1028824, -0.05909411, -0.11116942, -0.23898265, 0.013275228, -0.10834194, -0.23541391, -0.045599524, 0.13663499, -0.061863456) * go_0(0.0, -1.0);
    result += mat4(-0.9347821, -1.0879762, 0.029261602, 0.0058627487, 0.37568024, 0.07800278, 0.22918043, -0.22581682, -0.24621771, 0.0565432, -0.01175261, 0.20289935, -0.18791674, -0.34127015, -0.20261073, 0.24382167) * go_0(0.0, 0.0);
    result += mat4(-0.42576772, -0.9465751, 0.36503372, 0.047452617, -0.03021601, 0.19896118, -0.9916106, 0.68441176, -0.097055614, -0.039465737, -0.3072724, 0.3834049, 0.044579748, 0.10185175, -0.07127564, 0.053964186) * go_0(0.0, 1.0);
    result += mat4(-0.12718496, -0.20010719, -0.13560185, -0.28841987, -0.18198563, 0.06924996, 0.15375975, 0.007953754, -0.03143177, 0.24778824, -0.41971257, -0.15984616, 0.06914517, -0.15320878, -0.058414314, -0.1829401) * go_0(1.0, -1.0);
    result += mat4(-0.05676951, -0.39852038, -0.0008664457, 0.073233515, -0.110736564, -0.12950265, -0.32641715, 0.05254214, -0.0013476483, 0.04590487, -0.6886247, -0.029103741, 0.13570555, -0.06356145, 0.26564398, 0.16304392) * go_0(1.0, 0.0);
    result += mat4(-0.14373688, 0.2627747, 0.19523594, -0.04094942, -0.027800431, 0.080428846, -0.21676755, 0.22764, -0.08686052, -0.14352795, 0.012905041, 0.12002593, 0.096998215, -0.0822731, 0.25796455, 0.3244333) * go_0(1.0, 1.0);
    result += mat4(0.13717347, -0.2534293, -0.08265135, 0.02238695, 0.061414074, -0.12315743, -0.105848454, -0.0324352, -0.019163579, 0.5106144, 0.111571215, -0.17051223, 0.14541212, 0.26512033, 0.17036803, -0.05180038) * go_1(-1.0, -1.0);
    result += mat4(0.10731618, -0.011980742, -0.06125307, -0.043496255, 0.06382452, -0.53873694, -0.21860467, 0.076045096, 0.014617647, -0.12188417, -0.23983037, 0.20181973, -0.03130421, -0.23090406, 0.07917799, 0.11006313) * go_1(-1.0, 0.0);
    result += mat4(-0.07749841, -0.17617406, -0.2105074, 0.20204528, 0.31133667, 0.045247886, 0.38000366, -0.23678038, 0.14622565, -0.077519946, 0.04709938, 0.28799757, -0.02295692, 0.021911716, 0.037108235, -0.050266817) * go_1(-1.0, 1.0);
    result += mat4(-0.04620016, -0.053893, 0.07671593, -0.08702991, -0.31122503, 0.08491399, 0.39734617, 0.10588835, 0.1706988, -0.0030106953, -0.23740743, 0.119870976, 0.04136371, -0.08475979, -0.26021543, -0.26772037) * go_1(0.0, -1.0);
    result += mat4(0.013240527, 0.27298495, 0.061895885, -0.1766251, -0.35479823, -0.5952594, -0.2486822, 0.40527418, 0.017724868, -0.64586586, -0.056991536, -0.22597985, 0.1953091, -0.09300436, 0.28394333, -0.17164071) * go_1(0.0, 0.0);
    result += mat4(-0.0437722, 0.20237646, 0.1734046, 0.12661959, 0.3563361, 0.20119205, 0.49104276, -0.62781703, 0.10580526, 0.09021795, 0.2986983, 0.05439145, -0.030656314, -0.06551242, 0.06034035, 0.24646781) * go_1(0.0, 1.0);
    result += mat4(0.07150872, 0.2634299, -0.15512806, 0.032365914, -0.04214553, -0.32488832, -0.029638838, -0.11298656, 0.016363487, -0.20394005, 0.13789146, -0.1160082, -0.29543686, 0.056006238, 0.022565948, -0.0209169) * go_1(1.0, -1.0);
    result += mat4(-0.08222271, 0.1397535, 0.18386504, -0.029725704, 0.19525485, -0.26657727, 0.3193575, 0.39357802, 0.13274485, 0.063030235, 0.5509124, 0.076320685, -0.24871972, -0.23029849, -0.29287627, 0.0009975942) * go_1(1.0, 0.0);
    result += mat4(-0.11978757, -0.115064315, -0.32878634, -0.091591395, 0.011527068, -0.07584138, 0.20703748, -0.16326526, -0.07295838, -0.088844456, 0.0057264403, 0.08162376, -0.17551814, 0.10645812, -0.1522622, -0.18409562) * go_1(1.0, 1.0);
    result += vec4(0.022193057, 0.0031918385, 0.04232464, -0.0056721596);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_1_tf, ivec3(valid_xy, tile.inputLayer), result);
}