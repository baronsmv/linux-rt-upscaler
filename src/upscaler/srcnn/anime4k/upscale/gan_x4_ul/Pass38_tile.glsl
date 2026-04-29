// Anime4K_Upscale_GAN_x4_UL - Pass 38 of 67 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_15_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_15_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_15_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_15_tf3;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_17_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_18_tf1;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max((texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max(-(texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_15_tf3, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.19856872, 0.11904717, -0.064469926, -0.060562156, 0.088999204, 0.34987435, 0.19510469, 0.31565446, -0.22311617, 0.05800273, -0.070240505, 0.07316653, -0.104855716, 0.06083218, -0.19869952, 0.16014937) * g_0;
    result += mat4(0.25990537, -0.0699571, -0.20297414, -0.14829135, 0.12648308, -0.10045799, 0.16074577, 0.018881219, -0.13109452, -0.07432639, -0.07032176, -0.016821157, -0.27503675, 0.019903673, -0.14726853, -0.031217257) * g_1;
    result += mat4(-0.06882065, -0.00869124, -0.08228761, -0.09555077, 0.10960049, 0.1492122, -0.030764349, -0.013157832, -0.0692061, 0.045005288, 0.22895455, 0.031483006, -0.012937336, 0.23743461, -0.03126466, -0.035970267) * g_2;
    result += mat4(0.22776505, -0.15405187, -0.27868515, 0.06471627, 0.31427258, 0.1402745, 0.06863169, -0.051754337, 0.10026417, -0.2574256, -0.08802628, 0.068399504, 0.071888685, 0.022936821, -0.12540928, -0.015080033) * g_3;
    result += mat4(-0.039721105, -0.14838658, 0.24391836, -0.069194034, -0.16316739, 0.13536945, -0.13266453, -0.004489543, 0.18704645, -0.04657965, 0.025766708, -0.1476673, 0.27578717, -0.009918311, -0.27262732, 0.16296776) * g_4;
    result += mat4(-0.05249631, -0.2803283, 0.13727781, -0.09695497, -0.24535981, 0.10808846, 0.0022599236, 0.12974386, -0.07886284, 0.015886888, 0.037709296, -0.034715742, 0.048587516, -0.026816653, -0.04620663, 0.009604917) * g_5;
    result += mat4(0.20355739, 0.26263452, -0.016582636, -0.088004105, 0.0283301, -0.1646068, -0.14768231, 0.06584749, 0.09362991, 0.073038615, 0.03585095, 0.14700644, 0.30650404, 0.115159705, 0.094853185, 0.1412418) * g_6;
    result += mat4(0.19348627, 0.02455195, 0.04202425, -0.10602589, -0.087195724, 0.16053778, -0.15648113, -0.21084791, 0.119239464, 0.29533407, -0.23261383, -0.27815127, -0.030562209, -0.016111122, 0.029648153, 0.15206608) * g_7;
    result += mat4(0.03864564, -0.013641563, 0.008269305, 0.08444338, -0.37716612, -0.119036004, -0.37552136, 0.22999282, -0.03647035, 0.11136046, -0.11673442, -0.22254193, -0.31966165, 0.30993468, 0.26735285, -0.11855201) * g_8;
    result += mat4(-0.14826044, 0.08726846, -0.02775652, 0.095674574, 0.0414766, -0.11637243, 0.22545882, 0.024133151, -0.22550999, 0.17247951, 0.008702564, 0.015936209, 0.08907862, -0.1164228, -0.18179186, -0.088854164) * g_9;
    result += mat4(0.043506436, -0.22450508, 0.3010276, 0.109547526, 0.18712491, 0.086767204, -0.058926016, -0.0066756974, -0.035483465, 0.00068262784, 0.053788308, 0.11970851, -0.02235205, -0.254944, -0.12766762, -0.03977307) * g_10;
    result += mat4(0.18281984, 0.05554126, -0.009539485, 0.043676183, -0.007973203, -0.033897012, -0.10886124, -0.045664012, 0.18444513, 0.10041875, -0.13144056, -0.30685145, -0.23832887, 0.15063612, 0.03259291, 0.13059925) * g_11;
    result += mat4(-0.18238647, -0.24912533, 0.0064255036, 0.20445079, 0.071332455, -0.24193963, 0.058854166, 0.15322176, 0.08335828, 0.08328783, -0.120153025, -0.05942993, -0.10702824, 0.17542586, 0.27479908, 0.2176634) * g_12;
    result += mat4(0.08722579, 0.22445773, -0.22038916, -0.1705768, -0.33885807, 0.2610493, -0.14401726, 0.036701087, 0.05118682, 0.016674992, 0.017907443, 0.33134872, 0.24759968, -0.2189978, 0.17513935, -0.31552628) * g_13;
    result += mat4(0.09722241, 0.09016698, 0.0020826897, 0.014243476, -0.09178259, 0.26038414, -0.119483896, 0.06568409, 0.112089686, -0.1854509, -0.0032295822, 0.082286656, -0.20125629, 0.36961597, -0.15095985, 0.090025686) * g_14;
    result += mat4(-0.03207223, -0.016992198, -0.019505465, -0.3158222, -0.15192394, 0.18241268, -0.3502777, 0.05187207, 0.16714574, -0.067549706, -0.08512221, 0.03171733, -0.21070172, -0.14597628, 0.16120993, -0.002882248) * g_15;
    result += mat4(0.06358728, 0.06935574, -0.065100305, 0.02331908, 0.20260555, 0.14417367, 0.11311691, 0.041373946, -0.17366521, -0.24190584, 0.14318806, -0.12791471, -0.005797247, -0.01352598, 0.09355765, 0.08071775) * g_16;
    result += mat4(-0.21877107, -0.06376343, 0.015047983, -0.05071754, 0.24015504, -0.096376784, -0.050906435, -0.108564705, 0.0022815794, 0.10404753, -0.017777193, -0.18843737, 0.33381376, -0.009765667, 0.10630329, 0.04319869) * g_17;
    result += mat4(0.03913534, -0.18320137, -0.1895394, -0.35816035, 0.06605666, 0.14718485, 0.0705968, 0.03142451, -0.018191794, -0.03973546, 0.09669648, -0.06763489, 0.077504024, 0.22267477, -0.3280302, 0.051078096) * g_18;
    result += mat4(0.17017639, 0.048948385, 0.17666607, 0.28847146, -0.27951127, -0.2408892, -0.3000307, 0.1043314, 0.0788232, -0.13186172, -0.20950924, -0.11522397, -0.24694261, 0.1315647, -0.11994133, 0.09964028) * g_19;
    result += mat4(-0.03482202, -0.21670073, -0.24369243, 0.048367083, -0.3383805, -0.28556088, -0.05187166, -0.04785393, -0.056278072, -0.0046066013, -0.10573621, -0.12896368, 0.02629063, -0.07221729, 0.349292, -0.06192709) * g_20;
    result += mat4(-0.14670531, 0.02437431, 0.18400094, -0.18659692, 0.2216187, 0.034236856, -0.12323594, 0.1603975, 0.22086559, -0.0026523015, -0.13258888, 0.12981693, -0.033014633, 0.105112545, 0.03881624, -0.08425293) * g_21;
    result += vec4(0.0119343875, -0.042267065, 0.010792121, 0.007296717);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf1, ivec3(valid_xy, tile.inputLayer), result);
}