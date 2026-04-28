// Anime4K_Restore_CNN_Soft_M - Pass 4 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 4, rgba8) uniform image2DArray img_conv2d_3_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.07447851, -0.07888509, -0.28236163, 0.2479792, -0.065199964, 0.24733023, 0.099619575, -0.26430824, -0.03523585, -0.03547245, -0.10619345, -0.25326422, -0.116270036, -0.065133184, -0.30401528, 0.01563764) * go_0(-1.0, -1.0);
    result += mat4(-0.19106275, -0.26104823, -0.14457102, -0.17298317, 0.24148639, -0.10950928, 0.062851585, 0.042540826, 0.13287601, 0.06975747, 0.15848075, -0.3854902, -0.13132331, -0.16468687, -0.029844414, 0.27754608) * go_0(-1.0, 0.0);
    result += mat4(0.015378025, -0.14203559, 0.08058816, 0.32896644, -0.074871175, -0.26611313, -0.18830848, 0.091641426, -0.16522385, -0.23424402, -0.12279703, -0.13343342, -0.2509982, -0.0554576, 0.07286022, -0.028823337) * go_0(-1.0, 1.0);
    result += mat4(-0.13543738, 0.049395677, -0.015148539, 0.13301241, -0.12827122, -0.012590744, 0.012936948, 0.008271658, 0.12442749, 0.3497426, -0.16126058, -0.2670464, -0.010479037, 0.07037434, -0.15527055, 0.13205245) * go_0(0.0, -1.0);
    result += mat4(-0.09535385, -0.3931354, 0.24716614, -0.21284536, 0.14652656, 0.38149378, -0.09607391, 0.06350967, 0.48615915, 0.32634613, 0.146291, 0.2566475, -0.40927815, -0.05268087, -0.04110691, -0.0068722935) * go_0(0.0, 0.0);
    result += mat4(0.089152284, -0.01860622, 0.016856732, 0.31244752, 0.022529159, -0.0071319416, -0.09786801, -0.13005258, 0.1524636, 0.21627748, -0.07395979, -0.087633945, -0.38435504, -0.08842507, -0.0058702417, -0.32936293) * go_0(0.0, 1.0);
    result += mat4(0.0816838, 0.0012210817, 0.28217188, 0.36141106, 0.0014665248, -0.0636269, 0.042035818, -0.056671552, -0.032501306, -0.22908778, -0.2067977, -0.004497514, -0.23052917, 0.26728114, 0.15353456, -0.17732324) * go_0(1.0, -1.0);
    result += mat4(-0.17229734, 0.0818218, -0.10076918, 0.030027041, -0.14819005, -0.085340135, 0.050100215, 0.05683199, -0.12653661, -0.036583595, -0.32319903, -0.15273796, -0.15346588, 0.20005536, 0.23097478, -0.19834782) * go_0(1.0, 0.0);
    result += mat4(0.055430107, -0.2886931, 0.361814, 0.33160287, -0.084407054, 0.06254009, -0.02332793, -0.018134018, -0.014879812, 0.112346604, -0.20686437, -0.23408228, -0.01091196, -0.062669374, 0.085567676, 0.23738655) * go_0(1.0, 1.0);
    result += mat4(0.080383554, -0.1172084, 0.19703126, 0.27777427, -0.07559937, -0.25445858, 0.3450109, -0.071967736, 0.2034805, 0.33716002, 0.15314537, -0.22953224, 0.113631405, -0.0058444734, 0.2890972, 0.06557255) * go_1(-1.0, -1.0);
    result += mat4(-0.17646056, -0.025448758, -0.14952567, 0.017148364, -0.15238142, 0.1435677, 0.20273875, 0.22255951, -0.011660059, -0.003515217, -0.17305166, -0.13478355, -0.06558679, -0.032662887, -0.20914736, -0.5397283) * go_1(-1.0, 0.0);
    result += mat4(0.1679393, -0.109410115, -0.117427185, 0.14982319, -0.06457877, -0.06607065, 0.0018200208, -0.0118605625, 0.046539318, -0.020642165, -0.14413542, -0.09530688, 0.22196163, -0.2187166, -0.10759705, 0.013234591) * go_1(-1.0, 1.0);
    result += mat4(-0.13220267, -0.12540027, 0.26163217, 0.12791659, 0.16204996, -0.4023048, -0.13485721, -0.10187536, 0.059764992, 0.048170995, -0.25281772, 0.2090587, -0.06542371, -0.10791867, -0.21286209, -0.309109) * go_1(0.0, -1.0);
    result += mat4(0.16233061, 0.120428756, -0.11460241, 0.24531102, -0.2670459, -0.24195078, -0.20964348, -0.12930301, -0.2343609, -0.22543164, -0.28909695, -0.33560297, 0.6009884, 0.39171818, -0.1276308, -0.020736236) * go_1(0.0, 0.0);
    result += mat4(0.40162864, 0.045881115, 0.032667033, 0.31454235, -0.17351128, -0.009387306, 0.17341217, 0.30810982, -0.025815086, -0.10390133, 0.012544771, 0.036918722, 0.34386298, 0.23177734, -0.046727546, 0.20098232) * go_1(0.0, 1.0);
    result += mat4(0.11541034, -0.11647824, -0.12874861, 0.004921287, -0.13921295, -0.25733355, -0.1112383, -0.033295818, 0.0035326157, 0.3782048, 0.055785846, -0.1547331, 0.17358719, -0.2789715, -0.13400431, 0.1583795) * go_1(1.0, -1.0);
    result += mat4(0.4130191, -0.33944547, -0.064674884, 0.39617148, -0.11483455, -0.022601767, 0.1129301, -0.09713594, 0.14681247, 0.34442267, 0.08721343, -0.08309499, 0.088704996, -0.20943391, -0.2891408, 0.1709401) * go_1(1.0, 0.0);
    result += mat4(0.19503653, 0.17490312, -0.23491044, -0.028934423, 0.04479765, -0.0334551, 0.0602648, 0.0019939998, 0.23314747, 0.21557438, 0.07273092, 0.15467109, -0.11194509, 0.0736583, -0.17628083, -0.3851578) * go_1(1.0, 1.0);
    result += vec4(0.022887055, 0.01521631, 0.17967467, -0.0131908795);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf, ivec3(valid_xy, 0), result);
}