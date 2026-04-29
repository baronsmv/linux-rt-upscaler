// Anime4K_Upscale_GAN_x3_VL - Pass 12 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf1;
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
vec4 result = mat4(-0.38945672, -0.15583369, 0.39306244, -0.13897201, 0.11470281, 0.0070681917, -0.033763073, 0.15643148, 0.22714609, 0.024933932, -0.15510249, -0.080083966, -0.0042226757, -0.06603862, 0.23811841, -0.32394788) * g_0;
    result += mat4(-0.06128401, 0.054259196, -0.08520396, -0.09865539, 0.34222758, 0.3883786, -0.30866903, -0.1013294, 0.1554453, -0.042319432, -0.088941224, 0.09722677, 0.13703698, 0.09614998, -0.085818544, 0.21931672) * g_1;
    result += mat4(0.21811181, -0.14642404, 0.15328391, 0.27492282, 0.017405918, -0.064721376, -0.17901668, 0.18575072, -0.22293139, 0.071663104, 0.086893745, 0.13848016, -0.043508906, 0.05155524, 0.01965522, -0.23922569) * g_2;
    result += mat4(0.20807248, -0.26891938, -0.15629172, -0.106703185, 0.38624528, 0.11624259, -0.01337477, -0.060828242, -0.40988693, -0.045406528, 0.24799256, -0.041767262, 0.0039274395, 0.10462824, 0.2424475, 0.329761) * g_3;
    result += mat4(-0.2549953, 0.02627463, 0.16588904, -0.16302574, -0.05798094, -0.102065355, 0.051757824, 0.20152503, -0.18023098, -0.43803477, -0.11134416, 0.22741254, -0.10234647, 0.17433725, -0.2685737, -0.18413258) * g_4;
    result += mat4(-0.27022618, 0.3230193, -0.30969992, -0.17705725, 0.13844849, 0.29754448, 0.10819534, -0.1418908, 0.10238312, 0.02931327, -0.2183156, -0.12163026, -0.13901141, -0.042728595, 0.04175075, -0.3803353) * g_5;
    result += mat4(-0.16304304, -0.091977976, -0.24040937, -0.21812437, -0.12155577, -0.16794856, 0.29842067, 0.17197362, 0.11366187, 0.22641197, -0.0904384, 0.22736219, -0.18613777, -0.24540202, -0.101548284, -0.2319356) * g_6;
    result += mat4(-0.06359172, 0.003388455, -0.06142785, -0.21898538, -0.13489254, 0.3798411, -0.11154017, -0.02557614, 0.38281298, -0.20294727, -0.09908404, 0.2206924, 0.18847103, -0.026022637, -0.021512525, 0.30209598) * g_7;
    result += mat4(-0.14910938, 0.08331422, -0.07876587, 0.33450446, 0.18822157, -0.28672597, -0.21216297, 0.09774327, -0.15903074, -0.11264206, 0.15068948, 0.24262539, -0.0555986, 0.040748212, 0.1432122, 0.021155685) * g_8;
    result += mat4(0.33370045, -0.21974795, -0.29980183, -0.13374488, 0.022646265, -0.13715576, 0.06832448, -0.02061188, 0.1425013, 0.027876817, 0.08250215, -0.064872354, -0.08560185, 0.2952806, 0.23416562, -0.03025477) * g_9;
    result += mat4(-0.09395241, 0.017307205, 0.12121946, 0.04245705, 0.064785376, -0.041980207, 0.25907257, 0.07365294, 0.176773, -0.07988214, -0.23026212, 0.10206242, -0.13956478, -0.05496991, -0.41516188, -0.120178975) * g_10;
    result += mat4(0.24655807, 0.28612685, -0.42955264, 0.047639456, -0.026326181, -0.051772635, 0.030225411, 0.0476083, -0.0844218, 0.27088377, 0.24819367, 0.023990134, -0.05364132, 0.01713283, -0.20104195, -0.030321445) * g_11;
    result += vec4(0.0063284356, -0.007114507, 0.014496636, -0.0048167584);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf1, ivec3(valid_xy, tile.inputLayer), result);
}