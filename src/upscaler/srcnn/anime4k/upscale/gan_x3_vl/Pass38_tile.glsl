// Anime4K_Upscale_GAN_x3_VL - Pass 38 of 47 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_18_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_18_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_18_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_20_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_21_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_18_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_18_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_18_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_18_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_18_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_18_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_20_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max(-(texture(sampler2DArray(tex_conv2d_7_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_10_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max((texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_13_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max(-(texture(sampler2DArray(tex_conv2d_16_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_19_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.27361542, -0.082130425, 0.20547335, 0.16596498, -0.14146517, 0.18249078, 0.011518224, 0.11089219, -0.07630722, -0.054221917, -0.08349243, -0.028766789, -0.1906754, -0.108578265, 0.16413508, 0.13962057) * g_0;
    result += mat4(-0.02704147, -0.05976295, -0.12531951, 0.28034255, -0.17998871, 0.21086335, -0.04899309, -0.06144566, 0.06704049, -0.20967261, -0.03849724, -0.1063394, -0.040219773, -0.278173, 0.17341371, -0.011255667) * g_1;
    result += mat4(0.11230826, 0.022198819, -0.07899587, -0.0996965, -0.17873608, 0.13698925, -0.07870312, 0.1263333, 0.06711576, 0.07580918, 0.09481, 0.0825171, 0.11062839, -0.074613, 0.14020012, 0.2198393) * g_2;
    result += mat4(0.0028868434, -0.14465499, 0.18715319, 0.04548598, -0.0548704, 0.026883353, 0.08329182, -0.013520626, 0.08103766, 0.15715094, 0.13981456, -0.045514885, 0.112214044, -0.086184554, 0.014993669, 0.025903665) * g_3;
    result += mat4(0.12547491, -0.059728432, 0.17963155, -0.10817097, -0.100438006, -0.20602228, -0.15391783, 0.18270193, 0.08778924, -0.01655036, -0.18359496, -0.08576666, 0.109551124, 0.052976392, -0.16009195, 0.16581026) * g_4;
    result += mat4(-0.14505734, -0.0042488463, 0.17690867, -0.065921634, 0.23016429, 0.025626905, 0.11722592, -0.23542455, 0.12642547, 0.2802526, -0.09389537, -0.15698028, -0.1603324, -0.06829095, 0.10116497, -0.13783391) * g_5;
    result += mat4(0.15477929, -0.30527925, 0.15042041, 0.20866217, 0.13238567, -0.112839095, 0.15069273, -0.03174599, 0.24253696, 0.55339885, 0.033312403, -0.0016563814, 0.10960435, -0.0046957172, -0.24474236, -0.39900017) * g_6;
    result += mat4(-0.13976818, 0.15527318, -0.27346796, -0.15548058, 0.06493512, 0.08048214, -0.136374, -0.08525939, 0.27204737, -0.1013713, 0.1346666, 0.045041572, -0.12573871, -0.02424908, -0.14287473, 0.01571419) * g_7;
    result += mat4(-0.06758758, -0.20439683, -0.18058217, 0.0014974873, 0.04916309, 0.062314447, -0.2727905, 0.026782978, -0.005523231, 0.27266318, -0.16010733, -0.108470164, -0.15430328, -0.19484589, -0.3256893, -0.076337814) * g_8;
    result += mat4(-0.046945795, 0.0489837, -0.37631997, -0.206914, -0.031842437, 0.03959601, 0.054311134, -0.27745926, -0.2616194, 0.015333021, 0.1562857, -0.09994365, 0.1625487, -0.22026569, -0.01425276, 0.11845421) * g_9;
    result += mat4(-0.07944464, 0.038867, -0.29721326, -0.08270903, 0.03819214, -0.22673243, -0.019076617, -0.082782984, 0.15610558, 0.15448374, 0.08024717, -0.026800446, -0.2867148, 0.11126167, 0.21778513, 0.0803098) * g_10;
    result += mat4(-0.16599156, 0.029314978, 0.06395618, 0.06147069, 0.3273304, -0.15791246, -0.18337882, 0.22403763, 0.0038289267, -0.11374167, 0.019104691, -0.03859104, 0.06862462, 0.08082749, -0.11613864, 0.03697278) * g_11;
    result += mat4(0.007748403, 0.08750577, 0.07155799, -0.045760393, 0.055088032, 0.040909674, -0.21044537, -0.006774753, 0.041435767, -0.21444651, 0.11146028, -0.015305192, 0.1736952, 0.08569524, -0.11013171, 0.20451164) * g_12;
    result += mat4(0.060957868, -0.030028345, -0.032370888, 0.009256305, 0.085932784, 0.07008612, -0.12535034, 0.02922682, 0.068161115, 0.10938504, 0.14336275, -0.15049717, -0.105244614, -0.06773861, 0.16236088, -0.10205375) * g_13;
    result += mat4(0.22060202, 0.12885413, -0.06610741, -0.054895487, 0.27707383, -0.17114922, -0.17298199, -0.14735572, 0.121042944, 0.17805979, 0.24409181, -0.1536033, -0.2114284, 0.18976912, 0.19461404, -0.15320121) * g_14;
    result += mat4(0.04362077, 0.067338824, 0.13164803, 0.088066556, -0.055310402, 0.006420305, -0.019129515, 0.104561836, -0.0177281, -0.05549579, -0.05083655, 0.118114345, -0.0325892, 0.14835551, 0.09986534, -0.1493018) * g_15;
    result += mat4(0.13353525, -0.018843373, -0.38207877, -0.056904096, 0.0043200236, 0.33000615, -0.08322631, 0.16492364, -0.022802876, 0.011855873, -0.02483137, -0.0648857, 0.02270555, 0.009097881, -0.010122987, 0.12883057) * g_16;
    result += mat4(0.12964436, -0.0793745, -0.1326546, -0.06956091, -0.21922931, 0.05091461, -0.27575865, 0.09199549, 0.09375192, 0.047268208, 0.05267489, 0.30156332, 0.14469145, -0.06455131, 0.087691374, 0.046157785) * g_17;
    result += mat4(-0.21176293, -0.08989047, 0.03180079, 0.06659217, -0.1453242, 0.06772006, 0.017562179, -0.11958127, -0.034170456, 0.21188316, 0.117544524, 0.007319009, -0.09175878, 0.042179152, -0.15155235, 0.0072725313) * g_18;
    result += mat4(0.27448505, 0.219317, -0.027090587, -0.110271394, 0.15367448, -0.22380124, -0.18359132, -0.07701026, 0.0387728, -0.20798631, -0.15410027, -0.13094926, 0.11535367, 0.16782966, 0.26729038, 0.06455724) * g_19;
    result += mat4(-0.46956277, -0.2555739, -0.06807893, 0.15456976, -0.16843104, -0.18085335, -0.17501417, 0.3328664, 0.13444093, 0.20759131, -0.44945636, -0.28116164, -0.04072912, -0.097071156, 0.24616174, 0.192637) * g_20;
    result += mat4(0.055160224, -0.09051332, -0.23766883, -0.029569078, -0.008335112, 0.14387378, 0.25602153, 0.039339148, 0.006418962, -0.1502487, 0.1705312, -0.020727253, 0.087699726, -0.058968496, 0.35786387, -0.30345708) * g_21;
    result += vec4(0.01591211, -0.027196284, -0.033567958, 6.241704e-05);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf2, ivec3(valid_xy, tile.inputLayer), result);
}