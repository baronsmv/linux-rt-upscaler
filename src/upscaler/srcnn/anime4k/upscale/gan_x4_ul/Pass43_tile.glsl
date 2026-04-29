// Anime4K_Upscale_GAN_x4_UL - Pass 43 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_18_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_18_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_18_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_18_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_20_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_21_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_18_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_18_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_18_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_18_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_18_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_18_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_18_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_18_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max((texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.08710418, 0.07755426, -0.19372784, -0.12006015, -0.08683475, -0.051511686, -0.113844275, -0.01831389, 0.13441756, -0.18682177, -0.11446414, -0.053224254, 0.066490404, 0.15588047, 0.075582, -0.033167917) * g_0;
    result += mat4(-0.20958789, 0.15148236, -0.04583152, 0.12812352, -0.00044433025, -0.13340057, -0.09522131, -0.25912568, -0.005632191, 0.2783046, 0.13194086, -0.13088284, 0.2362872, 0.0900396, 0.28009146, 0.004059817) * g_1;
    result += mat4(0.10685089, -0.034242, 0.13198791, -0.1327393, 0.17671722, -0.21151659, -0.14577065, -0.20913975, 0.085521296, 0.035992414, 0.017195407, -0.10016802, 0.12933257, 0.046163887, -0.011927488, -0.23875898) * g_2;
    result += mat4(-0.08416457, 0.17505676, 0.24870509, 0.06930309, -0.191712, -0.0808669, -0.015740015, 0.0652813, -0.059006322, -0.018401904, -0.036595564, -0.1605108, 0.12305627, 0.060691502, 0.1619963, 0.08043304) * g_3;
    result += mat4(-0.1162042, 0.07235142, 0.074100144, 0.0062329075, 0.15629326, -0.004988086, -0.12807561, 0.2089372, -0.11417878, -0.0070988503, -0.08123769, 0.15964252, 0.1242517, 0.15018217, -0.16828871, -0.10980319) * g_4;
    result += mat4(0.097435325, -0.10224905, 0.061068628, 0.22532623, -0.046067998, 0.19951521, -0.11546273, 0.10270359, 0.027507411, -0.1484107, -0.0939577, 0.08855171, -0.25780675, -0.20141928, -0.051490895, 0.06990546) * g_5;
    result += mat4(-0.0502339, -0.0052296333, -0.07589294, -0.105127886, 0.006349035, 0.34075886, 0.050190937, -0.094317205, 0.097337745, -0.07065814, -0.16456902, 0.21397485, 0.022255344, -0.14672112, -0.19206822, 0.1821241) * g_6;
    result += mat4(0.07189387, 0.15896799, -0.055312637, -0.012296496, 0.18629979, 0.21605793, 0.3112103, -0.053981252, 0.164744, -0.13682634, 0.28319356, 0.0054148296, 0.12050483, 0.021165732, -0.090522125, 0.019760927) * g_7;
    result += mat4(-0.017540403, 0.0062772045, 0.18213348, -0.06998202, 0.042053856, -0.12266181, -0.03696476, 0.1198641, -0.4831862, -0.08289988, -0.09672259, 0.11441492, -0.19695596, -0.20243177, 0.120301224, -0.03885659) * g_8;
    result += mat4(-0.012043374, -0.12636301, 0.07465572, -0.026296021, 0.21566753, 0.18964884, -0.21407917, 0.06082264, 0.16858701, 0.22547795, 0.060304616, 0.21083428, 0.2195806, 0.06386552, -0.13011286, 0.07762842) * g_9;
    result += mat4(-0.048389256, 0.043716315, 0.07394857, 0.23185648, -0.22878529, 0.1262599, 0.04561782, -0.21576522, -0.11676992, 0.25556034, 0.08847371, 0.08644613, 0.026928827, 0.20417346, 0.058586314, 0.0476593) * g_10;
    result += mat4(-0.001416993, -0.26372138, -0.17127669, -0.21048187, 0.14255156, -0.22319807, -0.08061204, 0.03961634, 0.023157349, 0.05760616, -0.27544355, -0.1383328, 0.15652739, 0.011641045, 0.03508059, 0.23525323) * g_11;
    result += mat4(-0.23829429, 0.14674664, 0.08100075, 0.2795668, 0.18427856, 0.05980292, -0.24882336, -0.036076378, 0.08043839, -0.18109713, 0.10270382, -0.16545536, 0.086006865, 0.07463311, -0.2029149, 0.010671285) * g_12;
    result += mat4(0.14745244, -0.09021049, 0.03856137, -0.24550879, 0.31875673, 0.19743665, -0.18928793, -0.022744423, 0.09933925, 0.06840095, 0.07151117, 0.16670194, -0.17345333, -0.17679518, 0.0803156, 0.1323218) * g_13;
    result += mat4(-0.22606997, 0.23559661, -0.1356115, -0.16298714, -0.08236835, -0.11082772, -0.17032886, -0.36395928, 0.0076418323, 0.09497255, -0.009910129, -0.06704425, 0.118186295, -0.07905629, 0.16229996, 0.13862097) * g_14;
    result += mat4(-0.05605825, 0.03226995, -0.09783728, 0.1276114, -0.03132329, 0.17624037, 0.1554618, 0.13293655, -0.14832236, 0.0038608431, -0.1074844, 0.15878479, -0.2007515, -0.15159251, -0.08711506, 0.0011561218) * g_15;
    result += mat4(0.17221819, -0.13795783, 0.004547347, 0.07184666, 0.013688652, -0.05573553, -0.039471798, 0.23344308, 0.097293355, -0.042974688, 0.12051542, 0.015702134, 0.17581677, -0.052126184, -0.09377827, -0.072589) * g_16;
    result += mat4(0.1141422, -0.13473512, 0.1427384, -0.0516325, -0.25478005, -0.20733416, -0.065446824, 0.017821401, -0.06606627, 0.09842118, 0.10977934, -0.08284073, -0.23268555, 0.17497909, 0.15409274, 0.1766027) * g_17;
    result += mat4(0.16349804, -0.031991642, -0.03544694, 0.19030678, -0.10905752, -0.21243256, -0.1682402, -0.20092581, 0.049650017, -0.10322993, -0.056542892, -0.055122282, -0.04017231, -0.05765047, -0.11291076, -0.1375772) * g_18;
    result += mat4(-0.12520963, 0.03948451, -0.1080389, -0.2411598, -0.2384441, 0.04583776, 0.05708465, -0.13598098, -0.0027632138, 0.059042323, 0.1888617, 0.049241446, 0.20129628, 0.08619466, 0.19998649, 0.3488563) * g_19;
    result += mat4(0.04955111, 0.082809135, 0.0030273702, 0.027085733, -0.24155019, 0.18543921, -0.14815515, -0.07323729, -0.083096445, -0.018511815, -0.24441625, -0.042126883, 0.16707252, 0.15324517, -0.22174944, 0.20144019) * g_20;
    result += mat4(-0.06967862, -0.13329996, -0.17944409, 0.01734243, 0.075320974, -0.22839668, 0.24706283, -0.08456183, 0.101465605, 0.011808895, 0.014018943, -0.020431247, 0.08659333, -0.08047589, 0.015925674, 0.00016753716) * g_21;
    result += mat4(0.3392523, 0.10867626, 0.13746454, -0.035315026, 0.25138593, -0.21969056, 0.0074967514, -0.076253906, 0.040552594, -0.05231798, 0.05877078, -0.028507937, -0.31218964, 0.10618994, -0.35251832, 0.33440894) * g_22;
    result += mat4(-0.18962376, 0.01081502, -0.079535306, -0.47144732, 0.277589, -0.081428155, -0.4717694, 0.02221676, -0.058384646, -0.45954156, 0.031163838, -0.16281652, 0.20378628, 0.22339214, 0.06407888, -0.03579875) * g_23;
    result += vec4(-0.009340076, 0.0065150703, 0.010082239, 0.012676137);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf, ivec3(valid_xy, tile.inputLayer), result);
}