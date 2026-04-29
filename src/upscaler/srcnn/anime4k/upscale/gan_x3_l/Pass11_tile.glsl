// Anime4K_Upscale_GAN_x3_L - Pass 11 of 30 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_3_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.15610647, -0.15150696, -0.076018915, 0.030773202, -0.13935511, 0.17644633, 0.028819937, 0.30125114, 0.38625193, 0.35517895, 0.0975343, 0.114022225, 0.25494647, -0.23291643, 0.29096943, 0.15063812) * g_0;
    result += mat4(-0.22949804, -0.1368772, -0.07729264, 0.08470473, -0.06426131, -0.0064847367, 0.08241476, -0.1476949, -0.13712044, -0.36110023, -0.081719294, 0.19409889, 0.05562042, 0.26609465, 0.020447321, 0.2567414) * g_1;
    result += mat4(0.03337578, 0.2905731, 0.21772428, -0.074480034, 0.071880735, 0.27764675, -0.17273173, -0.0037474795, -0.1842544, 0.21896398, -0.30134472, 0.1711769, 0.23913746, -0.0435854, -0.12745531, -0.050227556) * g_2;
    result += mat4(0.34923258, -0.5455803, -0.2904644, -0.5446842, -0.040965725, -0.055288248, -0.50672686, -0.10309429, 0.045286313, -0.04284262, -0.19785875, -0.16594213, -0.10000842, 0.47245356, -0.32767087, 0.32854807) * g_3;
    result += mat4(0.05952625, -0.062991776, 0.3438396, -0.08141334, -0.2488028, -0.04746144, 0.06563561, 0.45020792, -0.19996788, 0.015523991, -0.19214569, -0.24849077, -0.022107737, 0.28190804, 0.13384444, -0.12800638) * g_4;
    result += mat4(-0.37812218, 0.09970516, 0.015231938, 0.07226164, -0.33720142, -0.05899804, -0.0025790115, -0.17770731, 0.111127384, 0.008749534, -0.09077738, -0.060420215, -0.10196339, 0.09641038, 0.25222716, 0.12781976) * g_5;
    result += mat4(0.24168618, 0.18625724, -0.012904225, -0.011732107, 0.085045695, -0.4754185, 0.10896487, 0.09179793, -0.31662637, -0.117563, 0.5133052, -0.09457646, -0.15872721, -0.09779008, 0.56810176, 0.3339073) * g_6;
    result += mat4(-0.09105348, -0.17617023, -0.21897802, -0.14157395, 0.16165406, -0.46579927, 0.24905841, 0.11579037, 0.09073764, 0.36771873, -0.29340085, -0.04271419, -0.11684365, -0.17138094, 0.12188604, -0.14749436) * g_7;
    result += mat4(0.10943254, -0.17193961, -0.07027378, -0.26047203, 0.04288517, 0.21311204, 0.03997142, -0.17006959, 0.16181368, 0.28361118, 0.26655135, -0.097007245, -0.15998597, -0.09568138, -0.27558687, -0.11706871) * g_8;
    result += mat4(0.365517, 0.5422966, -0.0013869518, 0.3447622, -0.25885904, -0.098901175, -0.048043057, 0.15867509, -0.12303401, -0.15362008, 0.270228, -0.2756776, -0.44207478, -0.0419657, 0.09387863, -0.07240854) * g_9;
    result += mat4(0.15073416, -0.032387026, -0.039117433, -0.50999755, 0.073477276, -0.14495571, 0.15120687, -0.3443857, -0.29039595, -0.16189122, 0.14190345, -0.10934344, -0.21965231, -0.45768484, 0.11907852, 0.5091087) * g_10;
    result += mat4(0.23260471, 0.16441877, 0.16760987, 0.10740154, -0.21663232, -0.10124566, -0.20843595, 0.066555224, 0.24608357, 0.16345865, -0.11965141, 0.18451719, 0.41683537, -0.044497896, 0.39102596, -0.11944608) * g_11;
    result += vec4(-0.02423156, 0.015124756, -0.02608139, 0.030428935);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, ivec3(valid_xy, tile.inputLayer), result);
}