// Anime4K_Upscale_GAN_x4_UUL - Pass 44 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_12_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_12_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_12_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_12_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_12_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_12_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_14_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_15_tf3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_12_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_12_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_12_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_12_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_12_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_12_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_12_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_12_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_14_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.1258338, 0.14226808, 0.240008, 0.20935175, -0.19359687, 0.10969335, -0.010278096, 0.05047169, -0.102325425, -0.14043438, -0.015837658, 0.057497922, -0.13778384, -0.13050987, 0.04406178, -0.39388844) * g_0;
    result += mat4(-0.06764633, -0.093226075, 0.19161254, 0.04461978, -0.0022064429, -0.0873564, 0.19151486, -0.19599946, -0.053517688, -0.17137547, -0.08812489, -0.15874967, -0.087588355, 0.10767261, -0.12681739, 0.043519877) * g_1;
    result += mat4(-0.056669228, 0.15541172, -0.22413507, -0.039581873, 0.117746115, -0.12828018, 0.2591866, 0.2189227, -0.020655332, -0.052517164, 0.14853618, 0.021707572, -0.1180331, -0.042699628, -0.059315376, 0.21756358) * g_2;
    result += mat4(0.030828092, 0.15607356, 0.28521895, -0.042055506, -0.11905841, -0.15199395, -0.07747248, 0.024884254, 0.26103246, -0.13039832, 0.29503205, -0.28014213, -0.030749863, 0.07596026, 0.06978804, 0.09495172) * g_3;
    result += mat4(-0.0061593466, -0.04792949, -0.04643929, 0.2671162, 0.10275537, 0.119533755, -0.03177247, 0.09164708, -0.06147422, -0.09079532, -0.17421386, 0.054402016, -0.19640115, 0.21798742, 0.08417971, -0.18372132) * g_4;
    result += mat4(-0.016552202, -0.14055125, -0.123929895, -0.03586157, 0.015958441, -0.024276946, -0.07081423, 0.075157166, 0.08328419, -0.3006715, -0.16210157, 0.048386306, 0.22541969, -0.09116436, -0.058013353, 0.046983466) * g_5;
    result += mat4(0.16410074, -0.24386454, 0.029308453, -0.22966138, 0.024182033, 0.0026562335, 0.10890961, -0.070607066, 0.009880331, 0.20278706, 0.06307576, -0.20934898, 0.054937962, 0.13425954, 0.008564824, -0.18836361) * g_6;
    result += mat4(-0.09830079, 0.03236859, 0.03107909, 0.22993204, -0.11275689, -0.387966, -0.028363353, 0.22778703, 0.21028486, 0.14199334, 0.12961474, 0.08735737, -0.09498103, -0.24960843, -0.097761855, 0.076679096) * g_7;
    result += mat4(-0.027410751, -0.050148983, -0.1589488, 0.123207964, 0.038601056, 0.026354158, -0.21397862, -0.08466078, 0.15880482, 0.055978496, 0.19484214, 0.11916298, 0.14721805, -0.23357584, 0.0078795785, -0.0996502) * g_8;
    result += mat4(-0.19617492, -0.21137202, 0.16017112, -0.15807675, -0.08558705, 0.15672047, -0.15000702, 0.11593056, -0.24458766, -0.3095287, 0.1798453, 0.25473964, 0.049579866, 0.05214217, -0.33104697, -0.20109792) * g_9;
    result += mat4(-0.16142516, -0.086649776, 0.12965636, -0.043352634, -0.22007716, -0.11945573, 0.17535049, -0.18496615, 0.09211835, -0.1083943, 0.02861594, 0.018325359, -0.008602158, -0.2642866, 0.23170324, -0.069464125) * g_10;
    result += mat4(-0.08273795, 0.44922677, -0.17449674, 0.036582816, -0.2044118, -0.0785363, -0.010560787, -0.020391712, -0.1472953, 0.06526804, 0.036532953, 0.041924234, 0.22576968, 0.030341445, 0.06348345, 0.1657037) * g_11;
    result += mat4(0.12300708, 0.10313409, -0.218913, 0.0925751, -0.04154223, 0.12221261, 0.17770545, -0.047017407, -0.11911827, 0.18008873, 0.07366393, -0.071406454, -0.1857546, -0.107086435, 0.13000482, 0.26223418) * g_12;
    result += mat4(0.27922675, -0.020313295, 0.124291986, -0.4803649, 0.0820355, 0.0075657824, -0.42316064, 0.13983229, 0.036435798, 0.086694, -0.022463394, -0.07225639, 0.15858616, 0.13137603, -0.3139255, -0.045889717) * g_13;
    result += mat4(0.009831248, -0.2589872, -0.27047434, 0.09680306, -0.25239283, -0.13848639, -0.06873848, 0.09892522, -0.111392066, -0.11744757, -0.0209528, 0.14345014, -0.17972618, -0.050757416, -0.11837715, 0.113276444) * g_14;
    result += mat4(-0.079554394, 0.03549963, 0.08195095, 0.10447346, 0.22000594, -0.07855921, 0.08771018, -0.074869476, -0.06463524, -0.029571146, 0.07834643, -0.054893587, -0.031394493, 0.11804174, 0.011439201, -0.012135598) * g_15;
    result += mat4(0.010138283, 0.123592444, 0.12088062, -0.072726145, -0.1476337, 0.05586365, -0.17523633, 0.1794935, -0.09707175, -0.0070755873, 0.015243624, 0.088103086, -0.09594741, 0.088290714, -0.25558707, -0.09352657) * g_16;
    result += mat4(-0.07432931, -0.23920125, 0.085965216, 0.005462481, -0.038702115, -0.06904665, -0.11373804, 0.0004949891, 0.15440702, -0.05119101, -0.15140614, -0.053231947, 0.0789753, -0.033853266, -0.042450577, 0.21443205) * g_17;
    result += mat4(0.20033926, 0.03339586, -0.038804412, 0.06836419, 0.042136673, 0.1732327, 0.1840776, 0.068900384, -0.014886417, 0.040377848, 0.14544998, -0.3117639, 0.062669605, -0.17392826, -0.10326911, 0.14575791) * g_18;
    result += mat4(-0.1810851, -0.14432015, -0.023838026, 0.20591272, -0.12021834, 0.12145132, 0.23006062, -0.22292806, 0.121778086, -0.010450825, 0.07063981, -0.12191605, -0.093348175, -0.23857832, 0.019086037, 0.037132252) * g_19;
    result += mat4(0.14685363, 0.11266721, -0.070741475, 0.12563772, -0.007161916, -0.06453287, 0.037466098, 0.048857793, -0.1628751, -0.22175354, 0.29700285, -0.11423984, 0.08846723, -0.23265848, 0.17491908, 0.080801815) * g_20;
    result += mat4(-0.1363871, 0.025643691, -0.16553839, -0.19008316, 0.11270188, 0.117668256, 0.5445655, 0.00021881262, -0.30459318, 0.42322806, -0.1023466, 0.078944914, -0.2456569, -0.049000096, -0.2082636, 0.08840609) * g_21;
    result += mat4(0.108215936, -0.12065532, 0.33155185, -0.08652035, 0.09861397, 0.266811, 0.22938332, -0.008803374, 0.2089193, -0.23314697, -0.12652464, -0.0832078, -0.11179262, -0.042625453, -0.33507705, 0.07660972) * g_22;
    result += mat4(-0.11835138, 0.0343298, 0.038553935, 0.10861632, 0.14620744, -0.1603159, -0.06951457, -0.0954962, 0.026970498, -0.0077033173, -0.029423261, -0.26626873, 0.028545115, 0.21267426, 0.51278436, 0.027819967) * g_23;
    result += vec4(-0.079484746, -0.06229742, -0.030395202, 0.033547744);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_15_tf3, ivec3(valid_xy, tile.inputLayer), result);
}