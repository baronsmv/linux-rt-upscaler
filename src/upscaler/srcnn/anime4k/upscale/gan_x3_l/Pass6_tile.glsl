// Anime4K_Upscale_GAN_x3_L - Pass 6 of 30 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_3_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.02357968, 0.13800439, 0.054744735, -0.32328397, -0.2263118, -0.3222542, -0.15286992, -0.3053175, -0.20046607, 0.025345843, 0.032755207, 0.40165102, 0.03166696, 0.29110438, 0.28861988, 0.05585125) * g_0;
    result += mat4(0.11055126, -0.33034575, 0.039494887, -0.17843343, 0.35742196, 0.00032650787, 0.21049741, 0.18823248, -0.1741954, 0.27586365, -0.043366615, 0.02092058, -0.082515135, -0.15504313, 0.13261497, 0.14650741) * g_1;
    result += mat4(0.39276633, -0.031067554, -0.08830738, -0.23975314, -0.20294978, 0.030291535, 0.4623106, 0.06494191, 0.042467684, -0.28105733, -0.053258326, -0.17269841, 0.09479501, 0.11930515, 0.1258843, 0.11058792) * g_2;
    result += mat4(-0.18343425, -0.4381688, -0.08248827, -0.42846557, -0.08277779, 0.45192116, 0.21961756, 0.23076119, -0.2093829, -0.29050866, 0.26212537, -0.25469857, -0.4832557, -0.45126852, -0.35072148, -0.18368497) * g_3;
    result += mat4(0.10529696, 0.5964488, 0.13258573, -0.07494986, -0.3341919, 0.19418421, -0.18307082, 0.34982273, -0.0430461, 0.21097268, 0.03212202, -0.015623122, 0.43791813, 0.16207397, 0.123477034, -0.087993294) * g_4;
    result += mat4(-0.01878982, 0.007308694, 0.25769314, 0.18407181, 0.00095180905, -0.2600526, -0.31043288, -0.24622385, 0.07832029, 0.05502411, 0.37793204, -0.07329948, -0.28405467, -0.15038961, 0.19259417, 0.105486296) * g_5;
    result += mat4(0.047820415, 0.3303589, 0.035807017, -0.41168606, -0.2118325, -0.045765184, -0.15234827, 0.28021428, -0.2084036, -0.40200952, -0.3261011, -0.13480914, -0.06876906, -0.19167677, -0.20444186, -0.44851676) * g_6;
    result += mat4(-0.24726203, -0.0097923195, -0.23193192, 0.31947026, 0.4274281, -0.36929542, 0.10095328, -0.19663717, 0.3244895, 0.49458218, 0.24745567, 0.15722558, 0.43052208, 0.377559, 0.22543637, 0.13009055) * g_7;
    result += mat4(0.01817998, 0.111477636, -0.12727399, 0.27395004, 0.19770023, -0.1636959, 0.25407487, -0.24871433, -0.08552937, 0.3223687, 0.30668882, 0.40221208, -0.20192504, 0.14656074, 0.5100356, -0.0948956) * g_8;
    result += mat4(0.40383592, -0.043663148, 0.4813348, 0.10317451, -0.049076255, -0.022925228, 0.0872564, 0.21741754, 0.23656987, -0.22309794, -0.2260013, 0.20823886, -0.055542476, 0.016604664, -0.1964831, 0.11962174) * g_9;
    result += vec4(-0.049604952, -0.039514415, -0.06137416, -0.0015509313);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_3_tf, ivec3(valid_xy, tile.inputLayer), result);
}