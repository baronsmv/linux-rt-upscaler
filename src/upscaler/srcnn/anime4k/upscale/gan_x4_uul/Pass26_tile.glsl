// Anime4K_Upscale_GAN_x4_UUL - Pass 26 of 84 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_6_tf4;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_6_tf5;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_8_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_9_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_6_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_6_tf4, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_6_tf5, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_8_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.029247807, 0.43012354, -0.07769897, 0.15838203, -0.13324478, 0.017804278, 0.21924987, -0.024039736, -0.20728067, 0.044956654, 0.03079796, -0.23534241, -0.0500509, -0.18794334, 0.27260718, 0.24131943) * g_0;
    result += mat4(0.1303224, -0.32837823, -0.09135343, 0.05029881, 0.29270905, -0.042230245, 0.13552578, -0.022074893, -0.22813024, 0.16917036, -0.19837584, -0.025336651, -0.017484624, -0.07434934, -0.022696782, 0.14180793) * g_1;
    result += mat4(-0.17257185, 0.016180463, -0.16395493, -0.12969042, -0.17320508, -0.17256051, 0.124869406, -0.041106623, -0.29951182, -0.062248964, 0.14418627, 0.113648884, 0.19480251, -0.14825127, -0.30102882, 0.2543297) * g_2;
    result += mat4(-0.17920358, -0.056560468, -0.05815734, -0.094284005, 0.074466944, -0.1708937, 0.05045378, 0.22309071, 0.07125439, 0.1243207, 0.0996307, 0.11177492, -0.20849244, -0.016035903, 0.066763505, -0.03865284) * g_3;
    result += mat4(0.10919598, -0.05991637, 0.22679056, 0.07574283, 0.11607126, -0.12619832, -0.11305337, 0.09875149, -0.093926236, -0.31168574, 0.12892371, 0.03084246, -0.025373377, -0.18546598, -0.10146844, -0.06607364) * g_4;
    result += mat4(-0.0284226, -0.13437645, -0.01047342, -0.0643442, -0.112065926, 0.28130296, -0.028859612, 0.20614125, -0.104703404, -0.25221863, 0.06305746, 0.008987997, -0.06367191, -0.039423067, 0.55190355, 0.1131621) * g_5;
    result += mat4(0.017900897, 0.19151299, -0.012729769, -0.3720392, -0.043568056, 0.021792412, -0.14938483, -0.04563565, 0.13666408, 0.15488137, -0.058843106, 0.026964363, 0.2275412, -0.051935695, -0.3025488, 0.032634325) * g_6;
    result += mat4(0.080183186, 0.49439004, 0.09187155, 0.058713455, -0.14579555, -0.16108377, -0.074885435, 0.16271885, -0.02726071, 0.3746404, -0.07175874, 0.12927002, 0.048367534, 0.0068023684, -0.01004529, -0.10857275) * g_7;
    result += mat4(0.30240306, -0.05872737, 0.09092156, -0.044823427, 0.13460608, 0.27104214, -0.21677399, -0.078722954, 0.21395817, -0.27020204, 0.03407373, -0.27704158, -0.14948608, 0.045992948, 0.5086244, -0.14568712) * g_8;
    result += mat4(0.04736869, -0.012021483, -0.23633002, -0.09218725, 0.049316257, 0.031919852, 0.109669484, 0.028117038, -0.05681596, -0.19797502, 0.066302285, -0.16133904, -0.11359791, 0.047595903, -0.15282372, 0.14841823) * g_9;
    result += mat4(0.025813673, 0.18983132, -0.32590774, -0.017710522, 0.20602965, -0.06116333, 0.2023164, -0.38438424, 0.06915477, 0.077189915, 0.14604315, 0.21469697, 0.2905641, 0.099070854, -0.15827921, 0.09761589) * g_10;
    result += mat4(-0.045127008, 0.18940306, -0.08118834, 0.02602074, 0.0945136, -0.07572827, 0.058015335, -0.054117456, 0.13638207, -0.06921914, -0.018934516, -0.21474637, 0.072837576, 0.38855672, -0.2214727, -0.07032989) * g_11;
    result += mat4(-0.14499478, -0.103144266, -0.06795675, 0.097279154, -0.15780063, -0.00092860113, -0.06560443, 0.046918143, 0.116832, -0.041867204, -0.04294921, -0.16297981, 0.0017979478, -0.14739467, 0.06300005, -0.018958041) * g_12;
    result += mat4(-0.023155538, 0.013861143, 0.10273995, -0.23301847, -0.06355406, 0.23065268, 0.0100112315, 0.12967634, -0.015230428, 0.00040594305, 0.09417989, 0.24173634, 0.055267353, 0.0818368, -0.07358038, 0.11633795) * g_13;
    result += mat4(-0.033157397, -0.060810838, 6.0726292e-05, -0.07492996, -0.08209274, 0.036523078, 0.037038907, -0.0371525, 0.008616722, -0.25722533, 0.11118201, 0.00083808816, -0.16973083, -0.049985297, 0.016049283, 0.04555759) * g_14;
    result += mat4(-0.02391044, -0.12006143, -0.0040827403, -0.045583934, 0.005460344, 0.0015913033, -0.0840245, 0.06921067, 0.13523246, 0.25881252, 0.06931116, 0.12808272, -0.08047311, -0.0036380326, 0.029610094, -0.1336764) * g_15;
    result += mat4(0.07438417, 0.057508536, 0.34985167, 0.11944369, -0.21246617, -0.16596083, -0.31279483, -0.24151649, -0.090715386, -0.007790705, -0.10482516, 0.10915042, -0.08405226, 0.09904896, -0.08101267, -0.36275923) * g_16;
    result += mat4(0.032126356, 0.011326541, -0.2710429, -0.018045785, -0.024174925, 0.10995586, 0.32196537, -0.16372478, 0.005468728, -0.1943689, -0.111603215, -0.08804184, 0.039886538, 0.15763853, -0.011543824, -0.32507792) * g_17;
    result += mat4(0.02271385, 0.06408109, 0.02209524, 0.061272632, -0.12502407, -0.21633519, -0.34524658, 0.018734034, -0.2399288, 0.08478751, 0.1332156, -0.15286094, -0.10991463, -0.41120422, -0.3367541, -0.015484429) * g_18;
    result += mat4(0.109604605, -0.13112773, 0.034937084, -0.3441579, -0.22917384, 0.13396077, 0.13513319, 0.013879127, 0.09909886, -0.2781385, 0.10821879, 0.0012182732, 0.141571, -0.039386883, 0.2155932, -0.039853897) * g_19;
    result += vec4(0.011448396, 0.020379832, -0.0022957225, 0.013202214);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_9_tf1, ivec3(valid_xy, tile.inputLayer), result);
}