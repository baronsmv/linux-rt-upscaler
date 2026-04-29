// Anime4K_Upscale_GAN_x4_UL - Pass 19 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_6_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_6_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_8_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_9_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.09864263, 0.16643536, -0.10098628, -0.27088618, 0.2439447, -0.15055421, -0.16554014, 0.15346923, 0.22877191, 0.36627764, 0.0009881472, -0.29182792, -0.1399589, 0.20674823, -0.1336018, -0.23139776) * g_0;
    result += mat4(0.30116054, -0.14907749, -0.057519797, -0.115984246, -0.010677967, 0.24336332, 0.18829945, -0.009448468, -0.20248725, 0.1898866, 0.10740923, 0.070664346, 0.19182079, 0.19262572, -0.10405306, -0.14409591) * g_1;
    result += mat4(0.02424672, 0.18151794, -0.3288155, 0.09967775, 0.08982069, -0.33101448, -0.13098675, 0.001805271, 0.093248144, 0.0062144175, -0.27785897, 0.15994431, 0.07629904, 0.11391333, -0.09452774, 0.028830891) * g_2;
    result += mat4(-0.12576537, 0.124780804, -0.005383383, 0.010800503, 0.074371964, -0.15757772, -0.012425731, 0.26471737, -0.12934509, 0.18494883, -0.019696942, 0.39016318, 0.108690634, -0.12907083, 0.23849326, 0.2127003) * g_3;
    result += mat4(0.06064956, 0.13181925, -0.06518252, 0.09022306, 0.10722941, -0.029313153, 0.05462699, -0.12941502, -0.32090643, -0.2399227, -0.0010322831, 0.2706631, -0.018146884, -0.25801313, 0.2318069, 0.114894636) * g_4;
    result += mat4(-0.12751573, -0.13918388, 0.20377824, -0.033067297, -0.0028459544, -0.17263114, 0.07472814, -0.08497229, -0.19693358, -0.23583023, -0.23746331, -0.1620524, 0.12260008, 0.20666504, 0.018275812, 0.05227883) * g_5;
    result += mat4(0.017006887, -0.079197586, -0.1751486, -0.24029018, 0.17393425, 0.19827369, 0.14355439, 0.07403027, 0.26099652, 0.34026688, -0.07905064, 0.1136539, -0.033830065, 0.0038907684, -0.25529358, -0.3126053) * g_6;
    result += mat4(-0.18364787, 0.06289015, 0.30731493, 0.2604622, 0.14766745, -0.19659941, -0.24400567, -0.13139778, -0.20132752, -0.31973583, -0.04709369, 0.2157305, -0.05968398, 0.41553238, -0.26575878, 0.12818466) * g_7;
    result += mat4(0.1777632, 0.30519867, 0.04919452, -0.050079886, -0.09780533, 0.071669996, -0.30823946, -0.05612444, 0.13824712, -0.17230682, 0.1516716, -0.42944372, 0.26453936, -0.3669238, -0.2791366, -0.158038) * g_8;
    result += mat4(-0.16834885, -0.36678392, -0.116782546, -0.12371954, 0.030408079, 0.030037245, -0.118157424, 0.21994841, -0.06582355, 0.35889858, -0.08357428, 0.33521906, 0.0730811, 0.12300713, 0.08012372, 0.13627763) * g_9;
    result += mat4(0.3792248, 0.2113681, -0.057442214, 0.056784596, -0.07914339, 0.2952479, 0.0039747343, -0.010485219, -0.21411481, -0.26210615, 0.14048009, -0.09856881, 0.17023402, -0.059730083, 0.019566841, -0.016332023) * g_10;
    result += mat4(-0.61801714, -0.31580862, 0.024079382, -0.26253095, 0.15262255, -0.05209289, -0.058584727, -0.17753975, 0.09153676, 0.018372437, -0.08778411, 0.15213694, 0.23527849, 0.0651243, 0.082912475, -0.12144174) * g_11;
    result += mat4(-0.10203859, -0.2157538, 0.09766386, 0.255458, 0.14621232, 0.15972705, 0.037336424, 0.29910806, -0.23335846, -0.27241442, 0.056837723, -0.15916888, 0.14921062, 0.018489221, 0.29236946, -0.21704453) * g_12;
    result += mat4(-0.20196709, 0.03039717, -0.016681867, 0.09106574, 0.016594073, -0.11138761, -0.39326677, -0.12731183, 0.017273927, 0.20023176, 0.40969402, -0.09844807, -0.21699667, -0.08527532, 0.03868599, 0.08391285) * g_13;
    result += mat4(0.04918593, -0.28722, 0.13262631, 0.19763342, 0.07408771, 0.20518765, -0.08351114, 0.023192497, 0.08808452, -0.024055472, 0.2863115, 0.028993187, 0.18309475, 0.14929788, 0.41230813, -0.14815095) * g_14;
    result += mat4(-0.068900704, -0.085048415, -0.3247905, -0.04743062, -0.09697462, 0.015716264, 0.016111441, -0.020915799, 0.0722674, 0.23050514, -0.038081765, 0.23436533, 0.0045003896, -0.25709474, -0.11242606, -0.2509955) * g_15;
    result += vec4(0.016932571, 0.01285098, 0.065885656, -0.045639206);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf, ivec3(valid_xy, tile.inputLayer), result);
}