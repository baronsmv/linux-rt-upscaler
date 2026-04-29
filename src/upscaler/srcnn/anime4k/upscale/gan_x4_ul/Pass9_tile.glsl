// Anime4K_Upscale_GAN_x4_UL - Pass 9 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_3_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.2471731, -0.16232504, -0.30280364, 0.05774581, -0.33488455, -0.2850219, -0.14658487, 0.1705944, -0.24376623, -0.07736909, 0.13372669, 0.13659224, 0.15363434, 0.09130026, 0.118685074, -0.1887429) * g_0;
    result += mat4(-0.14029902, 0.04204984, 0.029388431, -0.16639939, 0.037349563, 0.090201415, 0.115845665, 0.094291255, -0.003028802, -0.1821114, -0.052043844, 0.18686622, -0.1255908, 0.1673359, 0.17418015, -0.24007064) * g_1;
    result += mat4(0.045778025, -0.038912218, 0.116795845, -0.118629694, -0.1916185, -0.21808104, 0.22124553, 0.12642126, -0.024481684, -0.32958513, -0.11877306, -0.13612218, 0.1202751, -0.17667405, 0.08483987, -0.07016802) * g_2;
    result += mat4(0.004220892, -0.060743902, -0.15420602, -0.32612783, 0.022069136, -0.11913074, 0.22228731, 0.43151212, -0.03867469, 0.29992265, -0.14474417, -0.1324549, -0.067330755, 0.07419592, -0.3801413, 0.25740635) * g_3;
    result += mat4(-0.43801382, 0.074864835, 0.22297561, -0.07522966, 0.089928746, -0.23775443, 0.12624952, 0.05267909, 0.11843678, 0.23380554, -0.16562468, 0.04727477, -0.07479534, -0.06559248, 0.41837972, 0.34442958) * g_4;
    result += mat4(0.3688564, 0.13552678, -0.12272029, -0.14460362, -0.052870844, -0.0072880904, -0.20343664, 0.051840555, -0.07027805, 0.025613135, 0.1342496, -0.15982226, 0.21681777, -0.22339828, 0.04231994, 0.11173033) * g_5;
    result += mat4(-0.014970335, -0.29749388, -0.17493735, 0.29414502, 0.040422376, 0.15367351, -0.16439381, -0.18030228, 0.11266584, 0.111256205, 0.14735286, 0.04284055, -0.15905188, 0.43124563, -0.32235175, -0.24786504) * g_6;
    result += mat4(-0.05143537, 0.11057835, 0.21779476, 0.23726006, -0.0005560291, 0.04139496, -0.16062462, -0.24794249, -0.1464781, 0.19482404, -0.312965, 0.06129383, -0.18794996, 0.16319337, 0.14189719, -0.30816367) * g_7;
    result += mat4(0.27121273, -0.004694028, -0.31637567, 0.032995105, -0.036668185, -0.11826119, 0.035944767, 0.21887423, -0.030638168, -0.3112658, 0.1413359, -0.05586408, 0.028680937, -0.109603494, -0.48359016, -0.085163146) * g_8;
    result += mat4(-0.15236667, -0.06385869, 0.31347254, 0.024068993, 0.2756432, -0.0046036905, 0.07813827, -0.19012104, 0.04450809, 0.00904128, -0.21091071, 0.10090084, -0.014248632, 0.1903685, 0.27477407, 0.06778423) * g_9;
    result += mat4(-0.13072848, 0.01106962, 0.09164927, 0.038539473, -0.27705765, 0.12634145, -0.32573533, 0.18789926, -0.089990735, -0.12661424, -0.19122249, 0.11970773, -0.15596688, -0.15337645, -0.39366686, 0.25173476) * g_10;
    result += mat4(0.133498, -0.1286767, 0.0066307387, 0.05333134, 0.32057172, 0.11854806, 0.23994155, 0.07014444, -0.0822214, 0.17359538, 0.011753332, -0.098263726, 0.09097752, 0.23439142, 0.24286969, 0.30044666) * g_11;
    result += vec4(-0.013156251, -0.073697254, 0.013861042, 0.029801248);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf2, ivec3(valid_xy, tile.inputLayer), result);
}