// Anime4K_Upscale_Denoise_CNN_x2_S - Pass 3 of 5 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 4, rgba8) uniform image2DArray img_conv2d_2_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.0714004, -0.0545495, -0.050848898, 0.04724593, 0.2214181, 0.26353878, 0.07314053, -0.18771721, 0.06282607, -0.03720548, 0.020577375, -0.08951135, 0.40820515, 0.012179098, 0.52947706, -0.48448065) * go_0(-1.0, -1.0);
    result += mat4(0.10311368, -0.10970221, 0.07008208, -0.07143153, 0.073753305, 0.03786335, -0.4312538, -0.17680745, -0.15527713, -0.06711554, -0.21828765, 0.27252844, -0.0025433605, 0.31595528, -0.06065309, 0.059542265) * go_0(-1.0, 0.0);
    result += mat4(-0.036736265, 0.08704119, -0.06530063, 0.04546563, 0.010335546, -0.040761005, -0.021500558, 0.104531065, 0.094652064, -0.05088704, 0.14768088, -0.08585825, 0.057680476, 0.09885713, 0.18074304, -0.14277679) * go_0(-1.0, 1.0);
    result += mat4(-0.04810641, -0.01735864, -0.06405213, 0.04889552, -0.011552542, -0.04617259, 0.023976233, 0.27587202, -0.117965676, -0.07052052, -0.030583147, -0.036600694, -0.08542387, -0.053850796, 0.27242282, -0.73792183) * go_0(0.0, -1.0);
    result += mat4(-0.1340838, 0.1256252, -0.040528856, 0.13554344, -0.13733707, -0.14641404, 0.42666963, -0.4933124, -0.34908, 0.054332364, -0.2768947, 0.44689894, 0.42182985, -0.027279109, -0.17136064, -0.009496184) * go_0(0.0, 0.0);
    result += mat4(0.075086355, -0.025501372, 0.02172236, -0.052761186, -0.055753034, -0.028023237, -0.08829973, 0.14333946, 0.062496934, 0.034493748, 0.17640088, -0.084869936, 0.21283653, 0.1184779, 0.0016387368, -0.14988145) * go_0(0.0, 1.0);
    result += mat4(0.054841094, 0.040639404, -0.025044259, -0.071105786, -0.07473824, -0.04719771, 0.016553668, -0.10028357, 0.009365985, -0.0133521445, 0.022320358, -0.09318326, 0.17342545, 0.19281831, 0.16737404, -0.09583887) * go_0(1.0, -1.0);
    result += mat4(-0.03950585, 0.091417804, -0.021395942, 0.08735149, -0.029363452, -0.04763804, -0.1430701, 0.15344201, -0.006604305, 0.05897304, -0.13595524, 0.083323576, 0.008187976, 0.12946083, 0.14983748, -0.08178542) * go_0(1.0, 0.0);
    result += mat4(-0.00046765045, -0.07914878, 0.03529457, -0.007752294, -0.10084779, -0.1531338, -0.1408283, 0.20638838, 0.01466853, -0.059309185, -0.11161097, 0.08481583, 0.090416916, 0.081118226, 0.08677104, -0.20095336) * go_0(1.0, 1.0);
    result += mat4(0.3200496, -0.049090706, 0.11554867, -0.11949655, -0.18064958, 0.0012254696, -0.032284267, 0.00076361356, -0.13239916, -0.13838826, -0.20345089, 0.00692921, -0.2271236, -0.07132879, -0.097703665, 0.29881954) * go_1(-1.0, -1.0);
    result += mat4(0.4095371, 0.3008338, -0.43109173, -0.495734, 0.15016843, -0.3890023, 1.0669806, -0.20876339, -0.32241493, -0.10387533, -0.018227777, 0.1349976, -0.0019588785, -0.19263229, 0.38952798, 0.08135965) * go_1(-1.0, 0.0);
    result += mat4(0.01517036, -0.51562387, -0.13939962, -0.23287989, 0.09597558, 0.017624658, 0.16989397, -0.09395267, -0.29612765, 0.11843327, -0.07493133, 0.14523852, 0.040488124, 0.016568637, 0.10204776, -0.13137013) * go_1(-1.0, 1.0);
    result += mat4(-0.1512155, -0.12732185, 0.08002965, 0.024762904, 0.05106389, 0.011125884, -0.043196492, -0.17617282, 0.09791206, 0.120643355, 0.075500526, 0.10948051, 0.04969893, -0.20776172, -0.06905779, -0.20245977) * go_1(0.0, -1.0);
    result += mat4(-0.41836104, -0.82896453, -0.20962712, 0.7804863, 0.17322528, 0.53994787, -0.18730208, -0.021233026, 0.7417944, -0.4544313, 0.23165174, -0.63969344, 0.09383021, -0.046137553, -0.07796646, 0.11413524) * go_1(0.0, 0.0);
    result += mat4(-0.32532063, 0.09456587, 0.43708017, -0.40595353, 0.061229162, 0.006663704, -0.19821976, 0.07661682, -0.21427135, 0.17748164, -0.31958643, 0.3883502, 0.068938896, 0.022886515, 0.022923468, -0.04269318) * go_1(0.0, 1.0);
    result += mat4(0.23775512, 0.04026384, 0.12276414, -0.2545085, 0.0894177, 0.115443565, 0.029124375, 0.08887401, -0.0057824687, 0.017655179, -0.025270017, -0.06643964, 0.01316084, 0.024039604, 0.034566984, -0.12682836) * go_1(1.0, -1.0);
    result += mat4(0.036596492, 0.22772355, -0.05508538, -0.18005793, -0.06432669, -0.037058707, 0.2718052, -0.10313161, 0.016055575, 0.051271006, -0.038919963, -0.036601298, -0.019457681, 0.03805731, 0.03252896, -0.07179724) * go_1(1.0, 0.0);
    result += mat4(0.15046261, 0.13090402, -0.023847125, -0.039356075, 0.045424663, -0.20594294, 0.2154043, -0.18429665, -0.07969159, 0.08719893, -0.057626463, 0.08344988, -0.018651528, 0.047302175, 0.060727824, -0.035960387) * go_1(1.0, 1.0);
    result += vec4(0.04921464, -0.0011432811, 0.062071066, -0.06594219);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_2_tf, ivec3(valid_xy, 0), result);
}