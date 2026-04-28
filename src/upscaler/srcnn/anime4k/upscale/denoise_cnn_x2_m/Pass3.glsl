// Anime4K_Upscale_Denoise_CNN_x2_M - Pass 3 of 9 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(set = 0, binding = 3) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 4, rgba16f) uniform image2D img_conv2d_2_tf;
#define go_0(x_off, y_off) (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.088122115, -0.009916053, -0.124469265, -0.032139737, -0.13709281, 0.09177288, -0.06794775, -0.03962873, 0.17613642, -0.11064388, 0.2531882, -0.3817648, -0.1172188, -0.042132895, -0.098772734, -0.114560865) * go_0(-1.0, -1.0);
    result += mat4(0.18876404, -0.14613804, 0.23869626, 0.06580185, -0.13533239, 0.25754455, -0.29734856, 0.028218834, -0.39304733, -0.14716247, 0.19408274, -0.18518063, -0.31482637, -0.1508887, -0.3841371, 0.021975968) * go_0(-1.0, 0.0);
    result += mat4(-0.22316615, -0.0923483, 0.16932568, -0.13138154, 0.139829, 0.010975908, -0.0587337, -0.054484393, -0.13758336, -0.030077504, -0.050642505, -0.14933856, -0.040563874, -0.030220931, 0.2867556, 0.17022403) * go_0(-1.0, 1.0);
    result += mat4(0.12611523, -0.07087836, 0.08281469, 0.024588918, -0.023549056, -0.13102995, 0.17571726, 0.0740372, -0.3167631, 0.17491543, 0.4459055, -0.4687942, -0.19755729, 0.03723031, -0.06757113, 0.03502462) * go_0(0.0, -1.0);
    result += mat4(0.12098187, 0.12341856, -0.061940372, 0.7251308, 0.055730965, -0.5169302, 0.37959704, -0.08753306, -0.45700142, -0.4960699, 0.1690022, -0.40233734, 0.0262836, -0.13345262, 0.11002605, -0.16773209) * go_0(0.0, 0.0);
    result += mat4(-0.20428565, 0.117523015, -0.044863444, -0.1770644, 0.22925, 0.029694336, -0.23891294, 0.039587863, -0.11235541, -0.23890465, 0.037618574, -0.039127905, 0.14058869, 0.020599412, -0.074353516, 0.12343045) * go_0(0.0, 1.0);
    result += mat4(-0.04680316, -0.049870726, 0.06975308, -0.21486782, -0.08177838, 0.09760846, -0.031408366, 0.13881667, -0.14650045, 0.29182404, -0.080848776, -0.25525567, 0.018876432, -0.015662232, -0.016014043, -0.08435915) * go_0(1.0, -1.0);
    result += mat4(-0.100864016, -0.24647528, -0.007994345, 0.13047779, 0.14746517, 0.25517163, 0.054900885, -0.07251866, -0.29500577, -0.03758923, 0.05514366, -0.058372885, -0.03055354, -0.062586576, 0.017739896, 0.08644674) * go_0(1.0, 0.0);
    result += mat4(-0.029502464, -0.08905223, 0.0047584837, -0.09646073, 0.044714086, 0.15522493, -0.070930906, -0.026954453, 0.057949875, -0.017211404, -0.00566463, -0.0050975676, 0.0050182147, -0.010722001, 0.011812942, -0.04698445) * go_0(1.0, 1.0);
    result += mat4(0.18863353, -0.11575336, 0.26541254, -0.15280409, 0.14376, -0.05783716, 0.08554402, 0.27605456, 0.004611954, 0.074173525, -0.07963756, 0.082979314, 0.099553905, -0.06539344, 0.4330784, 0.07996894) * go_1(-1.0, -1.0);
    result += mat4(-0.31001288, 0.035875235, 0.049856357, -0.09614268, 0.23397788, -0.12425775, 0.45108303, 0.27973723, 0.0753222, 0.11388394, -0.043821793, -0.05610102, -0.06536777, 0.009822641, 0.7956708, -0.05798737) * go_1(-1.0, 0.0);
    result += mat4(0.19827974, 0.010130333, -0.13153136, 0.11593003, -0.15762039, -0.0040722084, 0.20404483, 0.28999883, 0.08152756, 0.07773477, 0.019730574, 0.0123460535, -0.034676805, -0.19133334, 0.01860159, -0.12945038) * go_1(-1.0, 1.0);
    result += mat4(-0.1861255, 0.039945368, 0.28345293, -0.17425321, 0.36748698, 0.03729066, -0.35957313, 0.11234573, -0.07122196, 0.012845119, -0.09049443, 0.10106711, 0.07425845, -0.14626606, 0.46169114, -0.2652126) * go_1(0.0, -1.0);
    result += mat4(-0.6222811, -0.08538015, 0.023319554, -0.7206892, -0.33495513, 0.2960924, -0.033479776, -0.29255456, 0.29802337, 0.47570458, 0.012769826, 0.19874385, -0.25652033, -0.4018595, 0.3055839, 0.1881051) * go_1(0.0, 0.0);
    result += mat4(0.32152474, 0.0024920676, -0.113435976, 0.14440896, -0.287736, 0.0251382, 0.28160754, 0.02769615, 0.067614004, 0.0832741, -0.095353454, -0.19792004, -0.40394694, -0.24224225, 0.3224996, 0.030300485) * go_1(0.0, 1.0);
    result += mat4(0.0045148246, -0.04621849, -0.026470715, 0.0588576, 0.14559188, 0.037437905, -0.13778603, 0.08173416, 0.033548757, -0.015654223, 0.15016593, 0.07761835, -0.016546778, 0.02640291, 0.112717085, 0.020371364) * go_1(1.0, -1.0);
    result += mat4(0.114227325, -0.0405595, -0.11662477, 0.014747093, 0.11170598, 0.58740836, -0.27560827, -0.1848705, -0.02491223, -0.15605451, 0.0028677192, -0.11290364, -0.12331832, -0.3191161, 0.3505101, 0.15236251) * go_1(1.0, 0.0);
    result += mat4(0.21131381, 0.13965495, -0.103683874, 0.26049778, -0.010777816, 0.015093082, 0.13207617, 0.14064828, -0.007847294, 0.025702007, -0.082993574, -0.04923462, -0.052900862, -0.006775377, 0.1432969, 0.09598549) * go_1(1.0, 1.0);
    result += vec4(0.08015534, 0.10264796, -0.031173404, 0.21282151);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_2_tf, gxy, result);
}