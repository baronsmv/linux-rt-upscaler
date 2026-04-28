// Anime4K_Restore_CNN_Soft_M - Pass 5 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3072) uniform sampler pointSampler;

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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_4_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.10233342, -0.30233157, 0.24238978, -0.007108631, 0.14248851, 0.08486557, 0.0028373515, 0.122387215, 0.10996857, -0.17286511, 0.19819227, 0.07023527, 0.07579955, -0.16861476, -0.210025, 0.12760942) * go_0(-1.0, -1.0);
    result += mat4(0.091181986, -0.41497424, -0.27567792, -0.09938067, -0.12210428, 0.20617811, -0.017644284, -0.22552875, 0.049019493, -0.18990634, 0.11057753, -0.043193225, -0.15278774, -0.18331046, -0.1837594, 0.029758787) * go_0(-1.0, 0.0);
    result += mat4(-0.1757096, -0.199691, -0.034743477, -0.15369363, -0.1701244, -0.0459655, 0.10508695, -0.09795581, 0.13464944, 0.37202564, 0.14706515, 0.23416734, 0.08302458, 0.20696343, -0.13935481, 0.03092827) * go_0(-1.0, 1.0);
    result += mat4(-0.49887478, 0.24046332, -0.029459715, 0.17374687, -0.15019977, 0.31086043, -0.28297687, -0.22239804, 0.12314376, 0.11594825, 0.17682782, 0.09753434, -0.26263535, -0.12739435, -0.57744014, 0.087381124) * go_0(0.0, -1.0);
    result += mat4(0.08101439, -0.16185337, 0.112901986, 0.24439482, -0.44051018, -0.70680356, -0.23015513, 0.63106006, -0.08817581, -0.057614524, 0.15352182, -0.049620207, 0.17742544, -0.49583626, -0.3844133, 0.18385352) * go_0(0.0, 0.0);
    result += mat4(0.17149475, 0.31255633, 0.19286609, 0.21052869, -0.11856372, -0.032373343, 0.06503625, -0.31664965, 0.040755365, -0.027614031, -0.33330554, 0.40148625, 0.056921627, -0.27068445, 0.047014963, 0.103712596) * go_0(0.0, 1.0);
    result += mat4(-0.09326643, 0.13677256, 0.06390537, 0.08080093, -0.10685094, 0.124757454, 0.14696303, 0.10871933, -0.10971212, 0.01655797, -0.11052674, -0.17361104, 0.015513338, -0.1917502, -0.26384255, -0.022672707) * go_0(1.0, -1.0);
    result += mat4(0.032367155, -0.087523445, -0.06951093, -0.08128242, 0.2627859, 0.14933161, 0.3114999, -0.007791172, -0.4146471, -0.2530298, -0.43175155, -0.06878434, 0.5724947, 0.25498095, 0.4838959, 0.15076154) * go_0(1.0, 0.0);
    result += mat4(-0.13427481, -0.10134261, 0.087439895, 0.015921364, 0.15421022, 0.20205952, 0.22928835, -0.07339068, -0.33318612, -0.17467582, -0.04758165, 0.11858059, 0.17408857, -0.099393494, -0.06389948, -0.06494366) * go_0(1.0, 1.0);
    result += mat4(0.15349221, 0.08508258, -0.09294437, -0.03204993, -0.22561033, -0.15088828, -0.020105945, 0.10041996, -0.024723593, 0.06610271, -0.24423431, -0.050512858, -0.100530736, 0.16394953, 0.16365045, -0.012055956) * go_1(-1.0, -1.0);
    result += mat4(0.16342951, 0.23113559, 0.21289586, 0.28391558, 0.052211206, -0.17983536, -0.008415342, 0.08977486, -0.054481823, 0.17506577, -0.14162593, -0.070448756, 0.093877845, 0.05161232, -0.25006327, 0.007014646) * go_1(-1.0, 0.0);
    result += mat4(0.104965575, 0.20048036, 0.024134496, 0.5442797, 0.19958296, -0.05165447, 0.076928124, 0.030868227, -0.0563495, -0.19757621, 0.10801544, -0.24202053, 0.0067657093, -0.17784451, -0.03134409, -0.06741009) * go_1(-1.0, 1.0);
    result += mat4(0.33347723, -0.12338564, 0.23495969, -0.23091966, 0.059872203, 0.028045453, -0.06781438, 0.111325614, -0.21861015, -0.030451605, -0.04267672, -0.0039260075, 0.0911101, 0.054191053, -0.08498816, 0.04810343) * go_1(0.0, -1.0);
    result += mat4(-0.05028896, 0.21515386, 0.16005337, -0.32279232, 0.19178568, 0.779363, -0.12682606, -0.4378189, 0.37980273, 0.063021325, 0.19370794, -0.05618088, -0.00088428083, 0.29736623, 0.24649377, -0.0021625878) * go_1(0.0, 0.0);
    result += mat4(-0.45007992, -0.16040307, -0.1714593, -0.16251564, 0.070867635, 0.21317895, -0.070962, 0.17147541, -0.27786884, -0.33259448, -0.022767346, -0.17967366, 0.21208113, 0.19740848, 0.16877973, 0.09630738) * go_1(0.0, 1.0);
    result += mat4(0.09235827, -0.35231477, -0.093315996, -0.035850406, -0.08311695, 0.054329164, 0.17788444, -0.020736141, -0.03739786, -0.1678283, 0.12676615, 0.17182353, 0.17408027, 0.07699043, 0.095501214, 0.0069830767) * go_1(1.0, -1.0);
    result += mat4(-0.16631392, -0.16925642, -0.17081848, 0.017719474, -0.20530944, 0.19215193, -0.039511178, -0.08296625, 0.2240653, 0.100644305, 0.2901835, 0.32166973, -0.10026419, -0.14864013, -0.19926691, -0.11607018) * go_1(1.0, 0.0);
    result += mat4(-0.13750182, 0.07445518, -0.033964884, -0.085812084, -0.03903257, -0.054933593, 0.06765632, 0.064338475, 0.27182797, 0.07721309, -0.0334218, -0.19344835, -0.14405386, 0.046106674, 0.16596143, 0.0879945) * go_1(1.0, 1.0);
    result += vec4(0.049844168, 0.02670437, 0.050967637, -0.10779561);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_4_tf, ivec3(valid_xy, tile.inputLayer), result);
}