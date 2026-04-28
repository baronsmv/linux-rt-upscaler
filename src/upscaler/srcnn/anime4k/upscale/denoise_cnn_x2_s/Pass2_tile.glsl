// Anime4K_Upscale_Denoise_CNN_x2_S - Pass 2 of 5 - https://github.com/bloc97/Anime4K
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
//    glslc -fshader-stage=compute --target-env=vulkan1.2 \
//          <this_file> -o <output.spv>
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
//        uint  inputLayer;      // array slice to read (0-based)
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  margin;          // context margin (pixels in feature-map space)
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(push_constant) uniform TileParams {
    uint inputLayer;
    uvec2 dstOffset;
    uint fullOutWidth;
    uint fullOutHeight;
    uint margin;
    uvec2 tileOutExtent;
} tile;

layout(set = 0, binding = 3) uniform texture2DArray tex_conv2d_tf;
layout(set = 0, binding = 4, rgba8) uniform image2DArray img_conv2d_1_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.103708945, -0.050891697, -0.2067834, -0.033582103, -0.08676132, 0.15528207, -0.10070597, -0.13641205, 0.030959459, 0.12798834, -0.058627255, -0.008511715, 0.023304658, -0.027084433, 0.120355256, -0.023104342) * go_0(-1.0, -1.0);
    result += mat4(0.0550643, -0.26851672, 0.11073926, 0.21989855, 0.012853378, 0.028077757, 0.073306665, -0.04551125, 0.16005373, -0.018154016, -0.12347146, -0.07590073, -0.10193998, 0.084696375, 0.04041413, -0.030883553) * go_0(-1.0, 0.0);
    result += mat4(-0.04816972, 0.0804637, 0.0071406, -0.08482986, 0.11176785, 0.060121994, -0.047804814, -0.036170192, 0.01989302, -0.12537469, -0.16283676, 0.19132937, -0.052577138, -0.005143432, 0.045614418, 0.04198543) * go_0(-1.0, 1.0);
    result += mat4(-0.33660156, 0.036350835, -0.4623589, -0.04140598, 0.2436438, -0.044735093, 0.20876355, -0.004252532, 0.81046224, -0.18550895, 0.32743093, 0.109012894, -0.34675312, -0.03464997, -0.09489919, -0.07961427) * go_0(0.0, -1.0);
    result += mat4(-0.08862038, -0.8168393, 0.03584266, 0.32159033, 0.06634099, 0.2985745, -0.18204363, -0.016070427, 0.35503992, 1.1388919, 0.16171643, -0.63834023, -0.0037699202, -0.27919513, -0.20949292, 0.03270466) * go_0(0.0, 0.0);
    result += mat4(0.021701936, -0.04537874, -0.05514495, 0.23225744, 0.024968185, 0.1816845, 0.03485249, -0.28249854, -0.37759346, -0.3225813, 0.021595621, 0.17104608, -0.0044055753, 0.01621266, -0.015169225, 0.08956203) * go_0(0.0, 1.0);
    result += mat4(-0.033255238, -0.110517226, 0.10664505, 0.019566126, -0.0695305, 0.059743922, -0.19161415, -0.024217626, -0.08578889, -0.16358584, -0.23050265, -0.004697784, -0.060790297, 0.1174991, 0.08205285, -0.011846926) * go_0(1.0, -1.0);
    result += mat4(0.6119327, 0.0791928, -0.118774265, 0.42233524, -0.16248553, -0.017692063, 0.13530938, -0.3207985, -0.147722, -0.24525681, 0.05243329, -0.38583818, 0.5147888, -0.072632834, -0.6014986, 0.26713687) * go_0(1.0, 0.0);
    result += mat4(0.23735437, -0.032110002, 0.17445332, -0.3272264, 0.020623574, 0.26734766, -0.16806662, 0.0796467, -0.34921628, 0.016648084, -0.14200358, 0.59190625, 0.13177821, 0.11139572, -0.14972521, -0.16784541) * go_0(1.0, 1.0);
    result += mat4(-0.047283772, -0.003196778, 0.44890094, 0.14619343, -0.17113213, -0.068454474, 0.07681565, -0.04306807, -0.0022641511, -0.20954822, 0.0344229, 0.014815744, -0.010632933, 0.13355999, -0.0860752, -0.069001146) * go_1(-1.0, -1.0);
    result += mat4(0.11664345, 0.099102855, 0.1642523, 0.047408774, 0.038490184, 0.16064398, -0.08694127, -0.2149453, -0.1413128, -0.06531084, -0.10105762, 0.19743964, 0.10458527, -0.04133969, 0.1425028, -0.013283083) * go_1(-1.0, 0.0);
    result += mat4(0.0138432095, -0.20053013, 0.079355195, 0.273772, 0.05484276, 0.13891658, 0.16240036, -0.25245088, 0.011192391, 0.104164094, 0.08112111, -0.250435, -0.0559613, -0.031029798, -0.015725998, 0.09240792) * go_1(-1.0, 1.0);
    result += mat4(0.18754779, -0.33171803, 0.34917468, 0.29074225, -0.37954012, 0.20898043, -0.24973525, -0.13707505, -0.31585664, 0.13607393, -0.29118514, 0.015055187, 0.18549949, -0.06351915, 0.2823401, -0.00019733967) * go_1(0.0, -1.0);
    result += mat4(0.10060476, 0.2883022, -0.15810104, -0.041112892, 0.31050095, 0.18517002, 0.020033397, -0.35919502, -0.17903808, -0.43506318, -0.14783014, 0.20092726, -0.002020754, 0.13320895, 0.040995706, 0.052643474) * go_1(0.0, 0.0);
    result += mat4(-0.014892139, 0.005828587, 0.044784732, -0.27272886, 0.21069369, 0.044396695, -0.03411123, 0.031441864, 0.17224072, 0.1708587, -0.00729118, -0.13070418, -0.19128975, -0.09342688, -0.051133234, -0.089075714) * go_1(0.0, 1.0);
    result += mat4(0.08799108, 0.04157696, -0.15010124, 0.26832178, -0.0040120087, 0.040308744, 0.17632529, -0.09464763, 0.07786305, 0.038288828, 0.40799135, 0.037377868, -0.049877923, -0.25080636, 0.00068664295, 0.0013101585) * go_1(1.0, -1.0);
    result += mat4(0.0353459, -0.21445732, 0.112647906, -0.3513759, 0.16887255, 0.3224789, -0.17073384, 0.10875396, 0.18919177, 0.14288992, 0.07364533, 0.20205943, -0.34363645, -0.3520186, 0.6763608, -0.19051236) * go_1(1.0, 0.0);
    result += mat4(-0.032245517, 0.039594565, -0.11825768, 0.16509856, 0.11749939, -0.005166539, 0.10740687, -0.3794017, 0.12722437, 0.14066173, 0.08025407, -0.34773758, -0.027300838, -0.08963159, 0.29774833, 0.053532287) * go_1(1.0, 1.0);
    result += vec4(0.022899346, 0.033619333, 0.030674957, -0.017047008);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_1_tf, ivec3(valid_xy, 0), result);
}