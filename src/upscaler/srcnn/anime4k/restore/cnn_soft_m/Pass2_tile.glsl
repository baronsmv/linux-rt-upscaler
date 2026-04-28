// Anime4K_Restore_CNN_Soft_M - Pass 2 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2DArray tex_conv2d_tf;
layout(set = 0, binding = 4, rgba16f) uniform image2DArray img_conv2d_1_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.09419103, -0.1178418, 0.09523275, 0.24648252, 0.03595256, -0.05417468, -0.029167585, -0.012279932, 0.08852021, -0.12534834, 0.0604663, 0.050634373, -0.19536541, 0.21548285, 0.040379744, -0.28046605) * go_0(-1.0, -1.0);
    result += mat4(-0.13783203, 0.17191975, 0.06956328, 0.005270252, -0.029844455, -0.17657366, 0.03439078, 0.048861686, 0.12017991, -0.087307535, 0.11815637, 0.31309614, 0.08440897, 0.09969244, -0.06220224, 0.2633136) * go_0(-1.0, 0.0);
    result += mat4(0.098606475, -0.05856224, -0.01163882, -0.020945825, -0.08988821, 0.18520717, 0.011407763, 0.20973705, 0.21017794, 0.038311377, -0.018910313, 0.053878684, -0.08751144, -0.0081623215, 0.29060364, 0.14363094) * go_0(-1.0, 1.0);
    result += mat4(0.13354321, -0.38046083, 0.14157647, 0.10190452, -0.045502663, 0.0053245644, -0.10817685, -0.048371315, 0.16157807, 0.2086147, 0.07632662, 0.24636099, -0.0053555835, -0.19587666, -0.46687222, 0.002362032) * go_0(0.0, -1.0);
    result += mat4(0.28275147, -0.1468291, 0.24075283, -0.35119128, 0.18727398, 0.3833064, 0.08667899, 0.15021381, -0.092296466, -0.25686404, -0.116076745, 0.2231862, -0.27637103, 0.12317917, -0.0341737, -0.40077657) * go_0(0.0, 0.0);
    result += mat4(-0.007041629, 0.18089123, -0.21195571, -0.12346183, -0.06088577, -0.30784377, 0.0048495876, 0.06013008, 0.07200418, -0.0076884073, 0.02632822, -0.0011575016, 0.21025613, -0.2573419, -0.06994815, 0.32497165) * go_0(0.0, 1.0);
    result += mat4(0.0016823286, -0.014366541, -0.5049525, 0.048534572, -0.0057915323, -0.0030526456, -0.028976317, -0.16376147, -0.15560333, -0.053708192, -0.055678204, -0.13087665, 0.0048869387, 0.027514834, 0.017380254, -0.06743363) * go_0(1.0, -1.0);
    result += mat4(0.044514824, -0.1754644, -0.26664957, 0.1486667, 0.114894986, 0.061640915, -0.13305616, 0.06450565, 0.03552732, 0.2835473, 0.13800526, 0.005875215, 0.15751484, 0.41759813, -0.19406971, 0.071032055) * go_0(1.0, 0.0);
    result += mat4(-0.18419577, -0.05527526, 0.017057603, -0.1146602, 0.15775396, -0.01188916, 0.09368113, 0.05765405, 0.064170234, -0.017833546, 0.12100514, -0.06250493, 0.2421206, 0.15719843, 0.23718071, 0.023142194) * go_0(1.0, 1.0);
    result += mat4(0.079226464, 0.07877355, -0.022315226, -0.13507473, 0.14683898, 0.028739132, -0.24479519, -0.280197, -0.13223173, 0.21732429, -0.1546993, 0.045442928, 0.163642, -0.07062695, 0.03805918, 0.060860883) * go_1(-1.0, -1.0);
    result += mat4(0.095216066, -0.16650215, -0.34863555, -0.025274571, 0.3064775, -0.034196265, -0.25773287, 0.19570488, -0.005434017, 0.26308087, 0.009404902, -0.24736062, 0.05558232, -0.014217521, 0.03667355, -0.15134114) * go_1(-1.0, 0.0);
    result += mat4(-0.074846864, 0.010901994, 0.035149742, 0.12106729, -0.36042807, -0.011231913, 1.4317516, 0.6400351, 0.105860665, -0.11587906, -0.11065066, 0.19126756, 0.14132085, 0.021570992, -0.3618735, -0.081163004) * go_1(-1.0, 1.0);
    result += mat4(-0.06937371, 0.3815214, 0.026842717, -0.04051589, -0.09472515, -0.027198657, -0.16502109, 0.114273794, -0.15207845, -0.15054241, -0.25099036, -0.10871029, 0.14311226, 0.07640166, 0.47051275, 0.0447809) * go_1(0.0, -1.0);
    result += mat4(-0.25960425, 0.11150338, -0.042022616, -0.006633396, -0.29595324, -0.0149574205, 0.09806478, 0.03635802, 0.26789796, 0.41416678, 0.05145585, 0.61168057, 0.019582301, -0.118703716, 0.13974573, 0.04498941) * go_1(0.0, 0.0);
    result += mat4(-0.04119621, -0.15503803, 0.33170196, -0.1158483, -0.06258357, 0.2574262, -0.07890287, -0.6929032, 0.004379942, 0.097908296, 0.009286624, 0.27194506, -0.2476702, 0.13828708, 0.05071857, -0.43693772) * go_1(0.0, 1.0);
    result += mat4(-0.010842703, 0.13108006, 0.30126816, 0.20221521, 0.018797455, 0.0614624, 0.11102966, 0.019204421, 0.09975456, 0.04676902, -0.044540443, 0.118877, -0.04871634, -0.089208096, 0.027455999, 0.029557817) * go_1(1.0, -1.0);
    result += mat4(-0.10421777, 0.3135469, 0.14557797, 0.0497297, 0.0034963787, -0.20342828, 0.08332032, -0.09004643, 0.06574797, -0.14168271, -0.08754358, 0.30385306, -0.3374016, -0.4360316, 0.15854433, -0.24081887) * go_1(1.0, 0.0);
    result += mat4(0.1407836, 0.09678823, -0.02240152, -0.013985894, 0.012281648, -0.24124922, -0.46433777, -0.25915003, 0.042200714, -0.21701157, -0.016618999, 0.13135725, -0.34656256, -0.034729004, -0.29246503, -0.13514486) * go_1(1.0, 1.0);
    result += vec4(-0.08458621, -0.023144595, -0.057707336, -0.081382714);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_1_tf, ivec3(valid_xy, 0), result);
}