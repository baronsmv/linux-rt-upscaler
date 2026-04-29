// Anime4K_Upscale_GAN_x2_S - Pass 5 of 17 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_5_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.014682038, -0.12901896, -0.16721351, -0.14512789, 0.1975804, 0.31713018, -0.13655594, -0.07817547, -0.1379136, 0.012892589, 0.23835693, 0.18214643, 0.15153849, -0.16835038, 0.2145134, -0.10536737) * go_0(-1.0, -1.0);
    result += mat4(0.020937767, 0.19783083, -0.54175997, 0.037820112, 0.2667656, 0.22040194, 0.37909588, 0.18100308, 0.020120522, -0.60052997, -0.043528315, -0.25213948, -0.15584327, 0.27506578, -0.092381746, 0.32063565) * go_0(-1.0, 0.0);
    result += mat4(0.122979, -0.16768639, -0.31459492, -0.0615338, 0.2467096, 0.39879864, 0.30217072, 0.05501944, -0.036550965, 0.30801496, -0.21168339, -0.13092734, -0.10309731, 0.02561574, -0.28071794, 0.111772805) * go_0(-1.0, 1.0);
    result += mat4(0.30419037, -0.27610013, -0.20951773, -0.4682423, 0.013910727, 0.45360255, 0.26947716, -0.28788614, -0.3465049, -0.027093071, 0.19358, -0.0759516, 0.05402844, 0.23829742, 0.14955573, 0.10131891) * go_0(0.0, -1.0);
    result += mat4(-0.18213613, 0.1460758, -0.13212326, -0.33431244, -0.038493834, -0.399577, 0.29018825, 0.046454914, 0.5486579, -0.37918556, -0.09230001, -0.06452045, -0.27307686, 0.16817085, -0.3927623, 0.4070809) * go_0(0.0, 0.0);
    result += mat4(0.3655112, 0.42978507, -0.20408633, -0.17724891, 0.018163562, 0.16742137, -0.20677765, -0.18758915, 0.08664044, 0.15635273, 0.04482592, -0.10135638, -0.042055663, 0.0120497495, -0.061840538, -0.23626032) * go_0(0.0, 1.0);
    result += mat4(0.29038852, -0.14159334, -0.07436412, -0.13352816, -0.3326411, 0.31299374, 0.2287002, 0.2508818, 0.26760912, -0.0037750339, 0.0058190194, -0.024687344, -0.1777058, -0.015039313, -0.07848877, -0.2052551) * go_0(1.0, -1.0);
    result += mat4(0.33255517, 0.45893422, 0.20505154, -0.11818784, -0.0353625, -0.2725971, 0.15468855, 0.14384854, -0.01441209, 0.12198328, -0.07893593, 0.0810518, 0.323934, -0.29967225, -0.24283892, -0.11573156) * go_0(1.0, 0.0);
    result += mat4(0.17880976, -0.20802346, 0.028815132, 0.22950941, 0.22764732, 0.32852155, -0.16896188, -0.22661959, 0.06486004, 0.00723564, -0.022966828, -0.05319699, 0.03109079, -0.00031444168, -0.16299056, -0.120937996) * go_0(1.0, 1.0);
    result += mat4(0.023376284, 0.029397544, -0.23599954, 0.15093243, -0.058068898, -0.022674788, 0.016787661, -0.100131355, -0.06670702, -0.0654595, 0.060609553, -0.24878198, 0.1184957, 0.12865701, -0.110585764, 0.027937055) * go_1(-1.0, -1.0);
    result += mat4(-0.21986784, -0.044010285, 0.07705757, -0.06578579, -0.34479773, -0.27297345, 0.07099886, 0.043877546, -0.3284597, 0.60647607, -0.13495111, 0.39562428, 0.12766926, -0.26691958, -0.13183068, 0.19720052) * go_1(-1.0, 0.0);
    result += mat4(-0.15688242, 0.02787055, 0.11245185, 0.010610981, 0.31926978, 0.6880586, -0.08503132, 0.2515481, -0.24620119, -0.3889153, 0.07599151, -0.04537119, -0.55283034, -0.170027, -0.14118128, -0.30742723) * go_1(-1.0, 1.0);
    result += mat4(0.037949517, 0.0026801233, 0.013419875, -0.07403992, -0.17499912, 0.012353954, 0.15956756, -0.14248073, -0.0017226954, 0.052071165, -0.19224213, 0.00033604537, -0.1924897, -0.21002872, -0.23516886, -0.09922695) * go_1(0.0, -1.0);
    result += mat4(-0.21850063, -0.22287996, -0.046637002, -0.28330007, -0.106190234, 0.027529838, 0.5553775, 0.3273539, 0.0110251075, 0.0067749587, 0.18001638, 0.18281236, 0.19831169, -0.03785556, 0.06003045, -0.12625378) * go_1(0.0, 0.0);
    result += mat4(-0.44703564, -0.2896555, 0.72527117, 0.29206118, -0.004199225, 0.46381885, 0.049183566, 0.14319502, -0.3226642, -0.39931563, 0.23164241, 0.10428929, -0.598285, -0.21007223, -0.36386037, 0.09704366) * go_1(0.0, 1.0);
    result += mat4(0.0462183, -0.063166276, 0.14364852, 0.212176, 0.17403619, -0.09878261, 0.0017970221, -0.31676117, -0.1104441, -0.073732674, -0.12653485, -0.20641124, 0.024175802, 0.005339486, -0.08178427, -0.2761102) * go_1(1.0, -1.0);
    result += mat4(-0.19256714, -0.246452, 0.3358081, -0.16956173, -0.2549593, 0.21122634, -0.06487135, -0.051329695, 0.110607915, -0.09860077, 0.1355533, -0.1489809, 0.023808947, 0.29945812, -0.056281622, 0.0020249223) * go_1(1.0, 0.0);
    result += mat4(-0.34458768, -0.074856885, -0.01856148, 0.06707525, -0.3314005, -0.16196185, 0.33313355, 0.20943385, -0.266928, -0.27552158, 0.018665945, 0.013205852, -0.33579, -0.16876023, -0.031895302, -0.13143763) * go_1(1.0, 1.0);
    result += vec4(-0.0375635, -0.08823075, 0.0025748173, 0.014370204);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_5_tf, ivec3(valid_xy, tile.inputLayer), result);
}