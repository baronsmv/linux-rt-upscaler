// Anime4K_Upscale_GAN_x4_UUL - Pass 17 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_3_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_3_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_3_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_3_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_5_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_6_tf;
#define g_0 (max((texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_3_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_3_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_3_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_3_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_3_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_3_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_3_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_3_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_3_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_5_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.2814602, 0.2277187, 0.29435065, 0.2408478, 0.105000384, -0.27356383, 0.036709026, -0.082270764, -0.051774833, -0.30756906, 0.22812237, -0.1716299, 0.066388845, 0.071013935, -0.17304003, 0.36941883) * g_0;
    result += mat4(0.010861255, 0.035956513, 0.15827346, -0.1573738, 0.28040013, -0.14285654, -0.1002935, -0.17466334, 0.23483588, -0.4468472, -0.083240435, -0.28713223, 0.20002778, -0.22584511, -0.017660992, 0.15582836) * g_1;
    result += mat4(-0.26468986, 0.0936422, -0.043597784, -0.18019813, 0.12215305, 0.30424714, 0.41272894, 0.2958579, -0.1279559, -0.1711416, -0.1494349, -0.15574773, -0.20571063, 0.33361194, 0.31610423, 0.07864312) * g_2;
    result += mat4(0.16455007, 0.23325196, -0.31887302, -0.02492541, -0.55856234, -0.0031886266, -0.11389042, -0.16259733, -0.25545537, 0.4201699, 0.13217591, 0.07380258, 0.030272568, 0.06883875, -0.16177692, 0.23754956) * g_3;
    result += mat4(-0.35823125, 0.26168248, 0.06723545, -0.25340518, -0.12674278, 0.16228193, -0.12574689, -0.018757205, 0.11605118, -0.2045155, 0.0029288447, -0.030387532, -0.25938132, -0.22786854, 0.19045345, -0.13012685) * g_4;
    result += mat4(-0.065970175, 0.0951907, 0.035318363, 0.13688375, 0.059882894, -0.11809705, -0.05243897, -0.352783, 0.39302433, 0.01651681, -0.25153002, 0.08879433, -0.20241016, 0.044586238, -0.41407117, 0.25752586) * g_5;
    result += mat4(-0.20024903, -0.029611953, -0.28356886, -0.025313022, 0.089501604, -0.033136155, -0.1373444, -0.044254545, 0.039401148, 0.18670277, -0.31939486, 0.21125056, 0.26854888, 0.02871854, 0.19365928, -0.18145144) * g_6;
    result += mat4(-0.14600311, -0.08483165, 0.018047078, 0.035864647, -0.20588812, 0.2844857, 0.14752424, 0.21875894, -0.30613014, 0.3414608, 0.30383223, 0.2768457, -0.0075907917, 0.40889844, 0.16538632, 0.32830665) * g_7;
    result += mat4(0.38021183, -0.12041459, 0.14818075, 0.19251712, -0.091613315, -0.27928743, -0.24842967, -0.23841564, -0.11372076, 0.09261184, 0.31207904, 0.16299677, 0.15786624, -0.03707239, -0.052265193, -0.21610543) * g_8;
    result += mat4(-0.043928284, -0.07245048, 0.17044666, 0.18489574, -0.02868591, 0.06388082, -0.21634308, 0.2171092, -0.25383195, -0.13655554, 0.050747488, 0.11323931, 0.14448066, 0.10746246, 0.021201093, -0.05081431) * g_9;
    result += mat4(0.010971268, -0.31695822, 0.06632742, 0.2854791, -0.056062803, -0.026609302, -0.011950665, -0.10058546, -0.18215255, 0.081689365, 0.19777119, 0.34793538, 0.30169576, 0.004764223, -0.076669544, 0.044626463) * g_10;
    result += mat4(0.18681169, 0.210494, 0.19781908, -0.08093209, -0.21912567, 0.11352498, 0.013049184, -0.21621475, 0.03843136, 0.26926485, 0.09463884, 0.23498456, 0.23216794, -0.13159363, 0.16778943, -0.025485182) * g_11;
    result += mat4(0.19025959, 0.58493006, 0.056999333, 0.05119183, 0.1487993, -0.38447016, -0.17310664, -0.39204964, -0.064214475, 0.08697591, 0.25842324, 0.04074829, 0.078874275, -0.24143232, -0.22189601, 0.024380466) * g_12;
    result += mat4(-0.10456438, -0.19316635, -0.092004195, -0.10626127, -0.18705751, 0.122325554, 0.07493597, 0.14279996, 0.31013626, 0.060707815, -0.14635678, -0.044795312, 0.006639313, 0.13290113, 0.3026528, -0.033154637) * g_13;
    result += mat4(0.16083871, 0.036329053, 0.12857045, -0.20901158, 0.071605735, 0.029462824, -0.022499103, -0.2286325, -0.53524, 0.04800241, 0.021400047, -0.39015284, -0.07230238, 0.18508849, -0.032816987, -0.21694009) * g_14;
    result += mat4(0.1175502, 0.2037501, -0.13257551, 0.101748504, 0.10230803, -0.12004787, -0.20809744, -0.17061722, -0.020457663, -0.3528951, 0.21511243, -0.07210097, 0.107290834, -0.30615744, 0.1965365, 0.18667313) * g_15;
    result += mat4(0.003279607, -0.13956092, 0.03445401, -0.0033504022, -0.095258705, -0.010740883, 0.014021217, 0.05173165, -0.053114057, -0.03752222, -0.05321192, 0.19231808, 0.11545275, -0.37370005, -0.2259635, 0.096631624) * g_16;
    result += mat4(0.11959142, 0.08352709, -0.059375286, -0.14197232, 0.04815708, 0.04520147, -0.112980366, 0.14088671, 0.01989498, -0.034033295, -0.08994673, -0.10527029, 0.17595868, -0.03632629, 0.28482202, 0.01762533) * g_17;
    result += vec4(0.066603035, 0.016885368, 0.04719387, 0.013140797);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, gxy, result);
}