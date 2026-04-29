// Anime4K_Upscale_GAN_x3_VL - Pass 31 of 47 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_17_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_7_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_10_tf;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_13_tf;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_16_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_18_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_15_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_15_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_15_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_17_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
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

vec4 hook() {
vec4 result = mat4(-0.015411904, -0.3481058, -0.14065851, 0.25672877, 0.11077625, 0.14430125, 0.075987406, 0.13401817, -0.028904252, 0.010471815, -0.13755904, -0.043050054, -0.23878446, 0.032667324, 0.0065731215, -0.24957936) * g_0;
    result += mat4(-0.11764895, -0.045424536, -0.039502602, 0.12982897, 0.229541, -0.18251237, 0.07418932, -0.019108484, 0.07372666, 0.032683663, 0.2243215, 0.30212626, 0.12498196, 0.24965945, 0.04350288, 0.3903582) * g_1;
    result += mat4(0.20100635, 0.15522125, 0.18275909, -0.0052163424, -0.08758867, -0.22356448, 0.22349271, 0.22447799, 0.07740293, -0.3192609, -0.06672845, -0.0633777, 0.056181088, -0.21348128, -0.13974325, -0.036865283) * g_2;
    result += mat4(0.18827224, -0.13507625, -0.08306733, 0.049136307, -0.095121965, 0.16284102, 0.05845094, 0.11416881, 0.062486872, 0.1405637, 0.1685204, 0.13717267, -0.07496871, 0.25640628, 0.11199113, -0.01789177) * g_3;
    result += mat4(0.27167314, 0.035950907, 0.032459494, -0.11790055, 0.12248767, 0.06978094, 0.3084216, 0.08794611, 0.07387762, 0.053205058, 0.099851795, -0.10258492, -0.14328477, 0.13806304, 0.026629662, -0.28694016) * g_4;
    result += mat4(-0.06586842, -0.06801413, -0.14677979, -0.0768508, 0.26984748, 0.11354619, 0.116293885, 0.014563355, -0.21626909, 0.19715959, -0.10084105, -0.20142159, 0.03564203, -0.102611236, -0.050990574, -0.09135196) * g_5;
    result += mat4(0.35307628, -0.14951418, -0.35223207, 0.030067248, 0.12195168, 0.28564107, -0.02129123, 0.13029817, 0.11705502, 0.020162629, 0.06902506, -0.3966005, -0.4818593, -0.33073005, 0.072956145, -0.12939528) * g_6;
    result += mat4(0.00530956, -0.12135435, 0.070373125, -0.16821058, -0.008556209, -0.17572887, 0.14526288, -0.16719544, 0.038015194, 0.21531321, -0.0031482165, 0.43273294, -0.28057137, 0.20323606, 0.06625515, 0.21552464) * g_7;
    result += mat4(-0.063178524, 0.24973153, 0.013720456, 0.056591444, 0.019021465, -0.26067972, -0.10853732, 0.030659003, -0.0700846, 0.033658378, -0.14822826, 0.004289035, -0.043764096, 0.20344602, -0.09091495, 0.071616665) * g_8;
    result += mat4(0.12145554, -0.0624854, 0.19910428, -0.22141473, -0.06820842, 0.14774227, 0.23123792, -0.20847356, -0.0788949, -0.02772492, 0.161529, -0.056242056, -0.09748238, 0.17754894, -0.10482487, 0.004179268) * g_9;
    result += mat4(0.33851695, 0.24063228, 0.061941892, -0.17925197, 0.009762858, -0.110571444, 0.17266293, 0.018386278, -0.13628517, 0.012900279, -0.20001967, 0.07412768, 0.092519194, 0.025905496, 0.013374791, -0.18080667) * g_10;
    result += mat4(-0.35484606, -0.24163297, -0.20655888, 0.25741658, -0.054093473, 0.24703228, -0.13321623, 0.06730745, 0.1915146, -0.12488617, -0.039931353, -0.16139272, -0.17825414, 0.005273623, -0.06986308, -0.20182024) * g_11;
    result += mat4(0.10539724, -0.14134564, -0.09422101, 0.07420711, 0.124219745, -0.050976872, -0.0036057911, -0.18727909, 0.024319967, 0.29918167, 0.07634522, 0.19821624, 0.32139403, 0.23670414, -0.32440105, -0.038693212) * g_12;
    result += mat4(-0.18223715, 0.18983413, 0.48830718, 0.024916872, -0.3343574, -0.12711638, 0.11339659, 0.122138545, -0.105839044, -0.14808372, -0.18010806, -0.15808982, -0.26355624, 0.12354337, -0.11911975, -0.10833433) * g_13;
    result += mat4(0.38319695, 0.05502718, 0.011898256, 0.042783014, 0.21362592, 0.042454682, 0.19834186, -0.073223054, 0.057000954, -0.056501992, 0.06412959, 0.036385205, 0.1374011, -0.062440563, 0.17463037, 0.047360953) * g_14;
    result += mat4(0.08570211, -0.06420987, 0.061411254, -0.15230267, -0.12127754, 0.06184008, -0.17644596, 0.022357073, 0.08968545, 0.10179604, -0.14161776, -0.10706859, 0.014307138, -0.120175295, -0.1018418, 0.04443384) * g_15;
    result += mat4(-0.07310467, -0.09482765, 0.11474074, -0.21321261, -0.036888484, -0.036406234, -0.14175038, -0.18403974, 0.073185734, -0.11334264, -0.04354356, -0.1334644, -0.28488088, 0.155462, 0.13175695, -0.045593392) * g_16;
    result += mat4(-0.0013599097, -0.094864406, -0.2907292, 0.1529276, -0.019177636, -0.04425709, -0.11138836, 0.13960573, 0.28229222, 0.032372613, -0.12031677, -0.037267342, 0.19885163, -0.07453253, -0.008422101, -0.18792655) * g_17;
    result += mat4(0.2524008, -0.056883294, 0.2737073, 0.25479946, -0.105945334, 0.18521947, 0.09495465, -0.16628663, 0.10909617, -0.34263077, 0.13374376, 0.034627344, -0.15817793, -0.014514654, -0.089533, -0.007011694) * g_18;
    result += mat4(-0.26738396, 0.22419624, -0.06836402, 0.032150477, 0.13000076, -0.08652478, -0.0856218, -0.07700419, 0.10129944, 0.0689117, 0.027205365, -0.07991292, 0.23872668, -0.081905946, 0.028084237, -0.09570726) * g_19;
    result += vec4(-0.030411588, -0.03504694, 0.0062963464, -0.0060779224);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_18_tf, ivec3(valid_xy, tile.inputLayer), result);
}