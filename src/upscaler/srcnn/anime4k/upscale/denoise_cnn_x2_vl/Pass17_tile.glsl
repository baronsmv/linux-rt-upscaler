// Anime4K_Upscale_Denoise_CNN_x2_VL - Pass 17 of 18 - https://github.com/bloc97/Anime4K
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
layout(set = 0, binding = 17, rgba16f) uniform image2DArray img_conv2d_last_tf2;
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
vec4 result = mat4(0.2006987, 0.17832398, 0.26342955, 0.23500517, -0.012297829, -0.009008417, -0.039950736, -0.039973143, 0.34800097, 0.32196492, 0.30505183, 0.29214156, -0.21410535, -0.21166423, -0.16437815, -0.19172792) * g_0;
    result += mat4(-0.008804151, -0.07085123, 0.013577994, -0.05192605, -0.08981402, -0.14702585, -0.09145975, -0.14835288, -0.15882517, -0.14785844, -0.2381482, -0.22867912, 0.010898514, 0.031957507, 0.040597558, 0.078252345) * g_1;
    result += mat4(-0.21658613, -0.1803885, -0.25954962, -0.20839214, -0.09597461, -0.09222647, -0.03909875, -0.03456191, -0.19723509, -0.16976605, -0.2041716, -0.1751425, 0.22901416, 0.24922715, 0.1800083, 0.23346905) * g_2;
    result += mat4(0.110020064, 0.103858806, 0.052446555, 0.061105963, 0.032901537, 0.07140097, 0.11518793, 0.13860466, 0.13930707, 0.12712196, 0.19071707, 0.18399614, -0.08036458, -0.07349171, 0.021504594, 0.0024937368) * g_3;
    result += mat4(0.059065036, 0.00698257, -0.099622436, -0.15676253, -0.10942482, -0.04869624, -0.13654554, -0.07341863, -0.014169851, -0.06390744, 0.016093008, -0.04540248, 0.29041344, 0.24451919, 0.26292154, 0.22136512) * g_4;
    result += mat4(0.107946776, 0.097849295, 0.10266876, 0.09360328, 0.08931344, 0.08896482, 0.046495322, 0.044040844, -0.020361643, -0.030911373, 0.026598722, 0.019815676, -0.072677925, -0.042410247, 0.14127749, 0.13434973) * g_5;
    result += mat4(-0.08809133, -0.03476601, 0.06420393, 0.14691353, 0.09296839, 0.06162562, 0.10992992, 0.0615685, 0.0168736, 0.06520281, 0.020010693, 0.046929173, -0.2219495, -0.21249783, -0.14622301, -0.14599061) * g_6;
    result += mat4(-0.13251069, -0.08977477, -0.08930347, -0.045490693, -0.10980218, -0.09510885, -0.07299872, -0.064053826, 0.011365247, 0.014091111, -0.054976214, -0.056936122, 0.10148144, 0.07451642, -0.08138598, -0.10161657) * g_7;
    result += mat4(-0.0075518745, -0.005738622, -0.007577811, -0.00032088626, 0.032614008, 0.04858922, 0.00054855715, 0.011565026, -0.022675224, -0.034442738, -0.03580643, -0.05069376, -0.0020376542, -0.01505518, 0.019388825, 0.03746554) * g_8;
    result += mat4(-0.011413172, -0.016877454, -0.048923567, -0.055012885, -0.007709447, -0.016109072, -0.047132388, -0.07146396, 0.002604099, 0.00014681708, 0.03429465, 0.043265607, 0.029014807, 0.03337814, 0.07582056, 0.041660666) * g_9;
    result += mat4(-0.020768544, -0.014378527, -0.01999972, -0.01385916, -0.012264676, -0.009959511, 0.0119015165, -0.016787319, 0.07266734, -0.0029914333, 0.08549183, 0.004367342, 0.008236065, 0.020370748, 0.0043428927, 0.007301017) * g_10;
    result += mat4(0.011654731, 0.025318999, -0.0029306612, 0.007426217, -0.00010868774, -0.020845588, 0.041991003, 0.024147986, -0.030741083, -0.012328637, -0.06617428, -0.06103115, 0.010491518, -0.013338451, -0.04666634, -0.046481613) * g_11;
    result += mat4(0.0268538, 0.043785956, -0.01799385, 0.008743307, -0.013197458, -0.015049436, -0.017189734, -0.0047999253, -0.00059730676, -0.0008936153, -0.016006093, -0.0073406673, 0.014875853, 0.011491735, 9.819833e-05, 0.0073417514) * g_12;
    result += mat4(0.019930955, 0.027112626, 0.01307941, 0.005268897, -0.060213763, -0.050415818, -0.069006495, -0.051405095, 0.0036414433, -0.008606397, 0.037427194, -0.0018103109, -0.037434716, 0.010187546, -0.026227329, -0.0033639795) * g_13;
    result += mat4(-0.03634798, 0.0007093891, -0.026819145, 0.009025687, -0.01750318, -0.020098133, -0.0063864207, -0.006606755, 0.0008565766, 0.028647956, -0.0024974607, 0.015250743, -0.048884176, -0.004310685, -0.0010757383, 0.00974984) * g_14;
    result += mat4(-0.031253602, -0.031743724, -0.009083253, 0.0145388115, 0.02048611, 0.0058071036, -0.0038228377, 0.00049654936, 0.0059105973, 0.03437731, -0.025785418, 0.004187733, 0.009980489, -4.08268e-05, 0.009384428, 0.0019492983) * g_15;
    result += mat4(0.012587245, -0.0032654977, 0.029739188, -0.009440694, -0.0018237908, -0.0080032, 0.010499013, 0.0012466761, 0.03461923, -0.0060207327, -0.008771263, -0.034545746, -0.015023473, -0.008901684, -0.011490296, -0.01976464) * g_16;
    result += mat4(-0.009444331, 0.020809013, 0.009985801, 0.020350901, 0.013234775, 0.004382635, -0.0007761826, -0.005247294, 0.034115106, 0.05190378, 0.039124765, 0.050993033, -0.0898732, -0.030428126, -0.044204578, -0.052484997) * g_17;
    result += mat4(-0.020434443, 0.053520404, 0.0007571144, 0.05895061, -0.018991265, -0.043982152, -0.004035192, -0.025452444, -0.012197152, -0.013770753, 0.0012919102, 0.003996682, 0.0056104586, 0.025686186, 0.05128293, 0.05105745) * g_18;
    result += mat4(0.030201769, 0.052521482, 0.029641917, 0.05559941, 0.0018870027, 0.020112835, -0.0043867202, 0.035877172, 0.02961142, 0.02163634, -0.027972858, -0.040669747, 0.03393723, 0.013455979, 0.03313782, 0.01968004) * g_19;
    result += mat4(0.034817442, 0.04045217, 0.054816365, 0.05092461, 0.06600807, 0.062576495, 0.09923777, 0.006663677, -0.039958935, -0.010009866, -0.041522443, -0.04959681, -0.020962957, 0.003845031, -0.04910384, -0.03233655) * g_20;
    result += mat4(0.015433112, 0.028965838, -0.0055138534, 0.042267464, -0.012690953, -0.009424165, 0.017896382, 0.01186686, 0.07231686, -0.038834292, 0.07033086, -0.052548733, 0.15721905, 0.09334892, 0.07676042, 0.06701375) * g_21;
    result += mat4(-0.09797534, -0.11201098, -0.0037222446, -0.008105951, -0.01152357, 0.012165641, -0.029051905, -0.021293389, -0.09600697, -0.028819272, -0.069084235, -0.035421908, 0.0054322914, 0.14168966, -0.0200274, 0.06505187) * g_22;
    result += mat4(-0.05034882, -0.06622497, -0.062471002, -0.100628324, 0.018115615, 0.019867867, -0.018836644, 0.007562053, -0.06317378, -0.034458403, -0.047243826, -0.009989589, -0.08270121, -0.018645251, -0.05160367, -0.023690399) * g_23;
    result += mat4(0.03897899, -0.10862529, -0.081805214, 0.1202324, -0.021866674, -0.00041882638, -0.018235246, 0.027227063, -0.0656312, -0.053432237, -0.0029235696, 0.03549672, -0.022848906, -0.057047505, 0.013400545, -0.0072439364) * g_24;
    result += mat4(0.06879516, -0.018637763, 0.058062725, 0.041045032, 0.011702424, -0.13693465, 0.05674195, -0.11679955, -0.022940686, -0.03856922, -0.07531371, -0.09692582, -0.019870926, -0.032572743, 0.026138868, 0.037639033) * g_25;
    result += mat4(-0.015270301, 0.06478719, 0.011016518, -0.04533957, 0.00688319, 0.024815995, 0.10159924, -0.08467507, 0.11939162, -0.01939453, -0.0058689644, -0.077881604, 0.118726775, 0.14489114, -0.10831982, -0.07972515) * g_26;
    result += mat4(-0.16734359, 0.10685446, -0.102714166, -0.010225307, 0.07306756, 0.07014447, 0.040464073, 0.04688462, -0.05489714, -0.01525318, 0.14690581, 0.17514132, -0.03250648, -0.03688211, 0.05047889, 0.03078089) * g_27;
    result += vec4(0.06614842, 0.045779686, 0.032838725, 0.017085627);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_last_tf2, ivec3(valid_xy, 0), result);
}