// Anime4K_Upscale_CNN_x2_VL - Pass 16 of 18 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 4) uniform texture2DArray tex_conv2d_tf1;
layout(set = 0, binding = 5) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 6) uniform texture2DArray tex_conv2d_1_tf1;
layout(set = 0, binding = 7) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 8) uniform texture2DArray tex_conv2d_2_tf1;
layout(set = 0, binding = 9) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 10) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 11) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 12) uniform texture2DArray tex_conv2d_4_tf1;
layout(set = 0, binding = 13) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 14) uniform texture2DArray tex_conv2d_5_tf1;
layout(set = 0, binding = 15) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 16) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 17, rgba8) uniform image2DArray img_conv2d_last_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max((texture(sampler2DArray(tex_conv2d_1_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_1_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max((texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max((texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max((texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_24 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_25 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_26 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.024905335, -0.0020974763, 0.02695263, 0.00016802056, -0.024053082, -0.02133723, -0.031614035, -0.031826317, 0.120421864, 0.10555479, 0.08609448, 0.116875134, 0.046175968, 0.04224941, 0.059216674, 0.035143953) * g_0;
    result += mat4(0.059397914, 0.016519934, 0.07189327, 0.047407165, 0.04808963, 0.02792908, 0.057017103, 0.034324065, 0.14228246, 0.11275426, 0.088058695, 0.059600517, 0.02063494, 0.052596953, 0.047207687, 0.08789091) * g_1;
    result += mat4(-0.013453174, 0.008474715, -0.017593835, 0.009218917, 0.070580654, 0.040542338, 0.08812338, 0.074653216, -0.016356857, 0.015809007, -0.008739107, 0.0097674895, -0.018381525, -0.007775341, -0.040571664, -0.011188163) * g_2;
    result += mat4(-0.026196122, -0.034825727, -0.042998232, -0.033436514, -0.01678153, -0.004592797, -0.010311677, 0.0008815291, -0.08899181, -0.10274026, -0.066960976, -0.082430154, -0.057137426, -0.07554528, -0.030993424, -0.050372377) * g_3;
    result += mat4(0.022921838, -0.010479244, -0.050794605, -0.073633075, -0.053708922, 0.009594084, -0.071259, -0.01054356, 0.005165821, -0.08024963, -0.049251772, -0.09581235, 0.17995799, 0.09743011, 0.13533138, 0.11643848) * g_4;
    result += mat4(0.09727046, 0.07292666, 0.06820908, 0.041535784, -0.0049705, 0.0048759184, -0.035702795, -0.015944308, -0.010730028, 0.018847652, 0.06466244, 0.086318985, -0.05661574, -0.040698618, 0.010839972, 0.0027009705) * g_5;
    result += mat4(-0.04628466, 0.010060396, 0.02609333, 0.08664702, 0.057045907, 0.033591177, 0.02186063, -0.024303377, 0.006569828, 0.08025825, 0.016128821, 0.10180713, -0.12228169, -0.112990454, -0.078443415, -0.09126021) * g_6;
    result += mat4(-0.12733299, -0.087755, -0.07374111, -0.044979006, -0.025347412, -0.004083168, 0.023782173, 0.02900392, -0.017815407, -0.041119996, -0.057978686, -0.13521095, 0.08364004, 0.06950181, 0.023554614, 0.008043734) * g_7;
    result += mat4(0.009062775, -0.003570175, -0.007378757, -0.0018487388, 0.01145638, 0.05217187, -0.008250244, 0.008433307, -0.056756936, -0.044681005, -0.08096105, -0.08033185, -0.023784965, -0.01859799, 0.013042476, 0.021188647) * g_8;
    result += mat4(-0.0071619656, -0.012498299, -0.05144986, -0.078112476, -0.034992415, -0.017038302, -0.04464615, -0.044504963, 0.024249, -0.004297534, 0.03674578, 0.03090718, 0.04698553, 0.008344952, 0.057619847, -0.0338724) * g_9;
    result += mat4(-0.011845145, -0.0045043705, -1.6646482e-06, -0.0038495932, -0.01992515, 0.004827126, 0.019493148, 0.00862289, 0.10151322, 0.0021909082, 0.09940764, 0.03728846, 0.027824005, 0.04358071, 0.014909185, 0.036326095) * g_10;
    result += mat4(0.022513246, 0.028257169, 0.0102195935, 0.03301329, 0.052253865, -0.0021944977, 0.08247392, 0.03256867, -0.040685873, -0.0052207555, -0.0451257, -0.054165114, 0.01647699, 0.0028809097, -0.015233776, -0.0008741886) * g_11;
    result += mat4(0.017371105, 0.01597189, -0.052552313, -0.008554715, -0.0023150423, 0.006076517, -0.012868931, 0.0039361073, -0.007524978, -0.004284313, -0.021520883, -0.010327569, 0.02543678, 0.008725823, -0.0073885336, 0.005528395) * g_12;
    result += mat4(0.019192757, 0.016561812, 0.0027538154, 0.0013078215, 0.007916496, -0.042525183, -0.013173432, -0.05265476, -0.062195376, -0.011255499, 0.020898128, 0.021532273, -0.001524097, 0.034835674, -0.004051403, -0.0292426) * g_13;
    result += mat4(-0.049191684, -9.43322e-06, -0.009106849, 0.012845289, -0.019482708, -0.011163468, 0.0034011535, -0.007062845, -0.006469714, 0.03177786, -0.033006195, -0.0006813464, -0.053963087, 0.00085209147, 0.02734121, 0.034086403) * g_14;
    result += mat4(-0.03232248, -0.004037002, -0.010319106, 0.030889064, 0.019604538, 0.0020888883, 0.010277864, 0.000661223, 0.057915937, 0.030683514, 0.00042533095, -0.013019287, -0.015896408, 0.0038484468, -0.0042103594, 0.02174542) * g_15;
    result += mat4(0.032975145, 0.0011456647, 0.04913679, -0.017063798, 0.0117176045, 0.007440557, 0.0020480808, 0.009415731, 0.027573857, 0.015140836, -0.01679426, -0.006124731, -0.03206279, -0.029842237, -0.010428016, -0.028513178) * g_16;
    result += mat4(-0.00506859, 0.055869613, 0.010164368, 0.027031485, 0.042289548, -0.0054258504, 0.032214936, -0.029970925, -0.0058315448, 0.022889478, 0.01681123, 0.02985076, -0.111186065, -0.02202099, 0.0030994313, -0.062343158) * g_17;
    result += mat4(-0.060951103, 0.06079555, -0.0396464, 0.070911355, -0.011480358, -0.06803282, 0.01637355, -0.043100975, -0.00423709, -0.028337711, 0.021635853, 0.0014857082, 0.030084312, 0.018155476, 0.043694943, 0.038795974) * g_18;
    result += mat4(-0.0060662925, 0.029721662, -0.008117774, 0.034551267, -0.024477571, 0.018841071, -0.027095588, 0.034495078, 0.082398005, 0.008998768, -0.016399248, -0.043801688, 0.05936684, 0.006066549, 0.045399766, 3.5319943e-05) * g_19;
    result += mat4(0.019259382, 0.02494012, 0.029301709, 0.028329274, 0.09122267, 0.06900443, 0.1412115, -0.043169618, -0.01627418, -0.004989528, -0.0042651827, -0.04556752, -0.023623291, 0.013007996, -0.04483056, -0.015727345) * g_20;
    result += mat4(0.016332543, 0.016384754, -0.030676385, 0.045312885, -0.0100853555, -0.032632045, 0.031514473, -0.0070776115, 0.13642761, 0.0023589598, 0.12214136, -0.062155515, 0.08240989, 0.08894205, 0.03325406, -0.016589595) * g_21;
    result += mat4(-0.06494277, -0.08158925, 0.030425413, 0.019835634, -0.012624623, 0.013942616, -0.030527417, -0.021668324, -0.09444672, -0.033064254, -0.044167448, 0.0011024752, 0.03210801, 0.12662941, -0.03912534, 0.1112649) * g_22;
    result += mat4(-0.04716062, -0.03751481, -0.031030515, -0.09067383, 0.0077815712, 0.02169541, -0.035285182, 0.02290573, -0.0704085, -0.03916127, -0.058103334, 0.004915147, -0.0333844, -0.011548617, -0.031151932, -0.00043817286) * g_23;
    result += mat4(0.05976319, -0.107285, -0.097245865, 0.17706421, -0.021453341, -0.0047738464, -0.017621001, 0.033400454, -0.07225561, -0.05599672, -0.027600193, 0.038664024, -0.03762786, -0.052429967, 0.0104017975, 0.007116869) * g_24;
    result += mat4(0.06014114, -0.029824806, 0.03209269, 0.04392036, 0.031300627, -0.16249833, 0.06878509, -0.12658615, -0.012383169, -0.025043553, -0.06527381, -0.08149099, -0.014006842, -0.018669648, 0.014510818, 0.042045828) * g_25;
    result += mat4(-0.023342922, 0.047104675, 0.029629575, -0.082307704, 0.04035797, -0.0013049254, 0.11085582, -0.11031226, 0.14778149, -0.016699014, -0.00634342, -0.055320874, 0.14306462, 0.15896587, -0.110229075, -0.1069649) * g_26;
    result += mat4(-0.17449625, 0.15787153, -0.06711028, -0.023110518, 0.06862914, 0.074063435, 0.042682912, 0.029800726, -0.08768606, -0.009814701, 0.14180017, 0.14780663, -0.05672417, -0.074305914, 0.07873489, 0.028458012) * g_27;
    result += vec4(0.06026231, 0.040204916, 0.037672628, 0.023496555);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_last_tf1, ivec3(valid_xy, 0), result);
}