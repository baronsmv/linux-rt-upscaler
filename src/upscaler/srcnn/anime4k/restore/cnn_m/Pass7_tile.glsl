// Anime4K_Restore_CNN_M - Pass 7 of 8 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 4, rgba8) uniform image2DArray img_conv2d_6_tf;
#define go_0(x_off, y_off) (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))
#define go_1(x_off, y_off) (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos + (vec2(x_off, y_off)) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.22753362, -0.08612073, 0.33140692, 0.08699529, -0.18788953, -0.056579117, -0.12905197, -0.06694621, 0.054559365, 0.15031597, -0.13430363, 0.021646025, 0.14884405, -0.0694291, 0.26149413, 0.11270503) * go_0(-1.0, -1.0);
    result += mat4(0.17876762, -0.09637848, 0.11285323, 0.2004893, 0.1317187, -0.036162686, 0.17958368, -0.069625, 0.28760737, -0.12505141, 0.12760694, 0.047717955, -0.16811855, -0.16340709, 0.13278298, -0.08403954) * go_0(-1.0, 0.0);
    result += mat4(-0.21917523, 0.079711854, -0.28642535, 0.2822416, 0.03001489, -0.014772918, -0.3487396, 0.10597145, -0.013841082, 0.17034237, 0.10810282, -0.08089695, -0.22184245, -0.59067357, 0.44113398, 0.13045649) * go_0(-1.0, 1.0);
    result += mat4(-0.29906932, 0.013923749, 0.2031124, -0.11846688, -0.13953634, 0.08003455, -0.10164494, -0.21218559, 0.10563715, 0.31033117, -0.075903505, 0.047310907, -0.37824214, -0.14506383, 0.11866701, -0.21384487) * go_0(0.0, -1.0);
    result += mat4(-0.1353849, 0.19258606, 0.063908584, -0.2043788, 0.27244982, 0.1665306, -0.29357895, -0.22441709, 0.18514316, -0.17840464, 0.20986097, 0.14351055, -0.057732623, 0.42166704, -0.23182064, -0.4957248) * go_0(0.0, 0.0);
    result += mat4(-0.34830126, 0.109066755, -0.28285867, -0.048280068, -0.12290918, 0.04291651, -0.047484186, -0.03702595, 0.23047262, 0.09398974, 0.022467108, 0.08271034, 0.3066665, -0.54077, 0.057771873, 0.23194093) * go_0(0.0, 1.0);
    result += mat4(-0.17731948, -0.3175927, 0.1452728, 0.09396786, -0.16433562, -0.01833653, -0.22345604, -0.04161193, -0.14827462, 0.18544114, -0.15544125, -0.06179007, 0.16989979, -0.20985202, 0.16391534, -0.09447268) * go_0(1.0, -1.0);
    result += mat4(-0.053878862, -0.21034616, 0.023831524, 0.19772215, 0.31647214, 0.0126534775, -0.19130844, -0.049282108, -0.21446131, 0.067189045, 0.09117449, -0.25548774, 0.12109098, 0.22009392, -0.3924665, -0.13340388) * go_0(1.0, 0.0);
    result += mat4(-0.16096684, -0.18495405, 0.10410178, 0.0015673033, -0.00183498, -0.044303037, -0.062745355, -0.090802394, 0.043269135, 0.06924481, -0.21367405, -0.14619029, 0.11555763, -0.20292862, 0.5799557, 0.14739846) * go_0(1.0, 1.0);
    result += mat4(-0.21030277, -0.09578802, 0.013482288, -0.21484336, 0.12995781, 0.40431052, -0.3347856, -0.18183486, 0.15550353, -0.04402301, 0.4603779, 0.14874357, -0.07694621, -0.053523075, -0.19607326, -0.10850742) * go_1(-1.0, -1.0);
    result += mat4(-0.2347211, 0.2697403, -0.0634794, -0.17925987, 0.17231455, 0.24999185, -0.5208536, -0.10491828, -0.233575, 0.52950364, 0.0038063182, -0.1380038, 0.022935199, 0.19369157, 0.14586553, 0.1938704) * go_1(-1.0, 0.0);
    result += mat4(-0.10245223, 0.34150192, 0.25862157, -0.20165509, 0.5597771, 0.114510864, -0.122526556, -0.04010975, 0.1704679, -0.23335956, -0.16771887, -0.03783455, -0.056995615, 0.24153493, -0.08082429, -0.24210933) * go_1(-1.0, 1.0);
    result += mat4(-0.103466526, 0.15278348, -0.30526164, -0.080755696, 0.103505425, 0.15862796, 0.14696524, -0.008358076, -0.09180311, -0.12505089, 0.28052542, -0.13551563, 0.07528779, -0.09636086, -0.10369617, 0.23656134) * go_1(0.0, -1.0);
    result += mat4(-0.25752836, 0.099439755, -0.30716348, 0.035077725, 0.023509016, 0.23106368, 0.05277125, 0.34910464, 0.088015385, 0.26995596, 0.1390645, -0.40671825, 0.18096298, -0.100688554, 0.5492049, 0.2482101) * go_1(0.0, 0.0);
    result += mat4(0.41411775, -0.107200556, -0.13813478, 0.13768874, 0.27137747, 0.06313619, -0.08522967, 0.03218302, -0.03166121, -0.3415683, -0.52242, -0.1741813, -0.36956537, 0.179129, -0.09742935, -0.11696616) * go_1(0.0, 1.0);
    result += mat4(-0.07975504, 0.17964838, 0.37122533, 0.16064765, 0.14309953, 0.29473078, 0.0926391, -0.22333665, 0.34612748, -0.3387473, 0.0077308523, -0.07239449, 0.18522519, -0.21297298, 0.11493978, 0.16117814) * go_1(1.0, -1.0);
    result += mat4(-0.17402779, 0.10023144, 0.11712206, 0.031971734, 0.18713303, 0.08736295, 0.013007052, -0.06943139, -0.20102951, -0.010721135, -0.2562522, 0.34877458, -0.13732676, -0.40258047, 0.25824392, 0.15720639) * go_1(1.0, 0.0);
    result += mat4(0.044494305, 0.3296108, 0.0017603852, 0.09362289, 0.38839245, 0.40015858, -0.13395199, -0.044521853, -0.56266373, 0.251378, 0.5005789, -0.13106057, -0.18491416, -0.046887, 0.067797676, -0.14694957) * go_1(1.0, 1.0);
    result += vec4(0.013687534, -0.08185164, -0.04755438, 0.290178);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, ivec3(valid_xy, 0), result);
}