// Anime4K_Upscale_GAN_x4_UL - Pass 28 of 67 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_9_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_9_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_9_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_11_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_12_tf3;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_9_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_9_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_9_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_9_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_9_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_11_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.17770122, 0.29082096, 0.04282091, 0.02549757, -0.23898254, 0.0010372455, 0.12527937, -0.0698982, 0.2606404, -0.010801856, 0.32558066, -0.26030767, -0.04800019, -0.07218525, 0.14526579, -0.18770672) * g_0;
    result += mat4(0.15203147, -0.07794133, 0.007123589, 0.098241664, 0.09907035, -0.27661824, -0.086697206, -0.2342014, -0.31787968, 0.049847364, 0.06507202, 0.21814133, 0.32412624, -0.083394185, -0.09934146, 0.23159225) * g_1;
    result += mat4(-0.096130975, 0.08083216, 0.44819605, 0.03937152, -0.13312627, -0.18089001, -0.18645371, -0.010557667, -0.124474674, -0.10351831, -0.12635191, -0.05673057, 0.018399497, -0.24488576, 0.026230913, -0.15852088) * g_2;
    result += mat4(0.10968734, -0.035089277, -0.067034565, 0.066106535, -0.14149925, 0.1641957, -0.18244973, -0.22383699, -0.18098424, -0.151712, 0.260575, -0.00048691966, 0.27418098, 0.2131733, -0.12303702, -0.101710096) * g_3;
    result += mat4(-0.3226536, 0.01744138, -0.12473336, 0.05616008, -0.4558458, -0.33108178, 0.004296858, -0.25150925, 0.11538608, -0.08004571, 0.20220277, 0.1365363, 0.21196564, 0.07377505, -0.060209595, 0.039599787) * g_4;
    result += mat4(0.00477916, -0.114327356, 0.011587205, -0.2702971, 0.23033854, -0.27782437, 0.32360908, -0.44537735, -0.013454022, 0.056789074, 0.033459242, 0.12902088, -0.1313282, -0.004177221, 0.041425087, 0.250106) * g_5;
    result += mat4(-0.24296634, -0.2151481, -0.030868901, 0.25469768, -0.042654943, 0.15871386, -0.12589258, -0.016274497, -0.033228472, 0.17153168, 0.04850832, 0.3116558, 0.07950622, 0.16695933, -0.25321132, -0.32425934) * g_6;
    result += mat4(-0.17190868, -0.08966977, 0.0064142062, 0.2417195, -0.28092504, -0.06055805, 0.24716014, -0.020504756, -0.030874953, -0.048863903, -0.043293115, 0.02698432, 0.079950914, -0.055653498, 0.034776926, 0.064640135) * g_7;
    result += mat4(-0.13084945, 0.06205162, -0.13606736, 0.39602286, -0.0030491774, -0.02476442, 0.0069150706, -0.026167216, 0.032697376, -0.030357588, 0.25825238, -0.07841919, -0.17723657, -0.06571916, -0.079561666, -0.009374618) * g_8;
    result += mat4(-0.24869454, -0.20812686, 0.21540813, -0.06763655, 0.08248998, 0.09615888, 0.01718324, 0.21635905, 0.20144391, -0.07219777, 0.098456375, -0.3403119, 0.13258833, -0.13171546, 0.09525975, -0.048105728) * g_9;
    result += mat4(0.22724295, -0.08324391, 0.0316843, 0.0060743215, 0.010268236, -0.17710914, -0.26217553, 0.052261468, -0.0564278, 0.118447, -0.221497, -0.004723381, -0.082461685, -0.06658231, -0.05635201, -0.16272539) * g_10;
    result += mat4(-0.19052428, 0.087694265, 0.10222324, 0.11315066, 0.11910176, 0.11697917, 0.093398556, 0.28112432, 0.030032964, -0.0145031605, -0.30618244, 0.058343805, 0.29364142, 0.4507355, -0.012588871, -0.04779493) * g_11;
    result += mat4(-0.30753234, -0.16848947, -0.027776828, 0.04406865, 0.24091373, 0.30855393, -0.14061853, -0.1889476, -0.013829834, -0.265403, -0.27854362, 0.20213468, -0.012963777, -0.01078832, -0.07769813, -0.21151513) * g_12;
    result += mat4(0.26133433, 0.17727493, -0.109125234, 0.08433557, 0.072260365, 0.2561018, 0.090859175, -0.07598044, 0.1457562, -0.025295084, -0.021166144, 0.045864385, 0.039569605, 0.20864639, 0.02609065, 0.26301143) * g_13;
    result += mat4(-0.13943508, -0.13203211, 0.35905635, 0.27272087, 0.18303953, 0.012707511, 0.088180274, -0.14280272, -0.23073225, -0.13123025, -0.0930568, 0.074749425, 0.22671546, -0.22136143, -0.029851126, 0.12233923) * g_14;
    result += mat4(0.12482134, -0.10828533, -0.079140544, -0.2453333, -0.090807475, 0.0063584484, 0.1211467, 0.062918566, 0.14158563, 0.04865186, -0.047368318, 0.16969171, 0.05705982, -0.06532511, 0.039894924, -0.2492887) * g_15;
    result += mat4(0.045366418, -0.11773512, 0.3228948, 0.03694021, 0.08063588, 0.15884815, -0.20808393, -0.053136192, 0.12179582, -0.008855191, -0.09951698, 0.052134108, -0.23938279, -0.12222782, -0.12329915, -0.2170608) * g_16;
    result += mat4(-0.18194616, 0.10244923, 0.05732402, 0.10120477, 0.118554674, 0.006850547, -0.026597708, -0.19694051, -0.040258426, 0.3326919, 0.27358428, -0.22072372, -0.4095388, 0.15311103, 0.14642514, 0.4488546) * g_17;
    result += vec4(0.048863593, 0.012109077, -0.016607719, 0.037871145);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_12_tf3, ivec3(valid_xy, tile.inputLayer), result);
}