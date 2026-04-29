// Anime4K_Upscale_GAN_x2_M - Pass 9 of 23 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_1_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_6_tf;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max(-(texture(sampler2DArray(tex_conv2d_1_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(-0.4756803, -0.16041027, 0.30747655, 0.27719444, 0.33626345, -0.093426555, -0.08751585, -0.025898175, 0.12469858, 0.162526, 0.071950376, 0.36727026, -0.26165214, 0.17652564, -0.081568465, 0.17669047) * g_0;
    result += mat4(0.10045615, -0.47277164, 0.13970673, -0.036603283, 0.10723418, -0.0733819, 0.07046736, 0.04479655, -0.5100679, 0.4051206, -0.3043826, 0.07709692, 0.25090587, -0.5827475, 0.27195984, 0.42297873) * g_1;
    result += mat4(-0.34415862, -0.056642354, -0.32332316, 0.049897127, 0.08399151, 0.683046, -0.16349371, -0.4878456, -0.097749546, 0.7214421, -0.2821467, -0.16691755, 0.3712332, -0.71557045, 0.40365914, 0.37325174) * g_2;
    result += mat4(-0.333854, 0.11971563, -0.26533902, -0.033346854, 0.09896302, -0.19311592, -0.006087015, -0.104003794, 0.05347405, -0.16057043, 0.15876219, 0.1538847, -0.07954591, 0.24062383, -0.025401022, -0.33599105) * g_3;
    result += mat4(0.11794056, -0.0031797416, 0.08360105, 0.12222232, -0.16638078, 0.26014742, -0.047267277, -0.27900735, 0.17616066, -0.12788172, 0.22856903, -0.39034957, -0.36313176, 0.12272574, 0.2235959, -0.31102005) * g_4;
    result += mat4(0.03297161, 0.19597028, -0.068131894, -0.059938233, 0.18935929, -0.12004069, 0.08705267, 0.26411813, -0.021374375, 0.24630849, -0.08980925, 0.15982057, 0.3533297, -0.15414584, -0.19008748, 0.11310849) * g_5;
    result += mat4(-0.4622819, 0.31923467, -0.38989246, 0.5539857, -0.035433546, -0.12729715, -0.0669769, -0.048216928, -0.32078394, 0.26958883, 0.08897814, -0.31043166, 0.26743132, 0.38835636, -0.30535862, -0.22241123) * g_6;
    result += mat4(0.47431698, -0.755935, -0.075302646, 0.27771655, 0.052087527, -0.17221431, 0.0008429987, 0.15527548, -0.04587466, -0.11802989, 0.39905685, -0.07758683, -0.11415051, 0.004637339, -0.19803126, 0.19956517) * g_7;
    result += mat4(0.36277947, -0.13364364, 0.18459712, -0.1705512, -0.46083033, 0.43629453, 0.112646095, -0.18511245, 0.037818372, 0.1220617, -0.22268273, -0.11983507, -0.5432721, -0.2102279, -0.014456884, 0.16428374) * g_8;
    result += mat4(0.22811654, 0.16262956, 0.18411161, 0.49102694, -0.15078211, -0.6144134, -0.11632199, 0.2740543, -0.11322067, -0.16751853, 0.18453367, 0.14305107, 0.36418238, -0.34248996, -0.055178564, 0.37168074) * g_9;
    result += vec4(0.07878663, -0.045328207, -0.07142425, -0.006036755);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_6_tf, ivec3(valid_xy, tile.inputLayer), result);
}