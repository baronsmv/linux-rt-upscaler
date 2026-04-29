// Anime4K_Upscale_Denoise_CNN_x2_UL - Pass 24 of 25 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2DArray tex_conv2d_2_tf;
layout(set = 0, binding = 1025) uniform texture2DArray tex_conv2d_2_tf1;
layout(set = 0, binding = 1026) uniform texture2DArray tex_conv2d_2_tf2;
layout(set = 0, binding = 1027) uniform texture2DArray tex_conv2d_3_tf;
layout(set = 0, binding = 1028) uniform texture2DArray tex_conv2d_3_tf1;
layout(set = 0, binding = 1029) uniform texture2DArray tex_conv2d_3_tf2;
layout(set = 0, binding = 1030) uniform texture2DArray tex_conv2d_4_tf;
layout(set = 0, binding = 1031) uniform texture2DArray tex_conv2d_4_tf1;
layout(set = 0, binding = 1032) uniform texture2DArray tex_conv2d_4_tf2;
layout(set = 0, binding = 1033) uniform texture2DArray tex_conv2d_5_tf;
layout(set = 0, binding = 1034) uniform texture2DArray tex_conv2d_5_tf1;
layout(set = 0, binding = 1035) uniform texture2DArray tex_conv2d_5_tf2;
layout(set = 0, binding = 1036) uniform texture2DArray tex_conv2d_6_tf;
layout(set = 0, binding = 1037) uniform texture2DArray tex_conv2d_6_tf1;
layout(set = 0, binding = 1038) uniform texture2DArray tex_conv2d_6_tf2;
layout(set = 0, binding = 2048, rgba16f) uniform image2DArray img_conv2d_last_tf2;
#define g_0 (max((texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_1 (max((texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_2 (max((texture(sampler2DArray(tex_conv2d_2_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_3 (max(-(texture(sampler2DArray(tex_conv2d_2_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_4 (max(-(texture(sampler2DArray(tex_conv2d_2_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_5 (max(-(texture(sampler2DArray(tex_conv2d_2_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_6 (max((texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_7 (max((texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_8 (max((texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_9 (max(-(texture(sampler2DArray(tex_conv2d_3_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_10 (max(-(texture(sampler2DArray(tex_conv2d_3_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_11 (max(-(texture(sampler2DArray(tex_conv2d_3_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_12 (max((texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_13 (max((texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_14 (max((texture(sampler2DArray(tex_conv2d_4_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_15 (max(-(texture(sampler2DArray(tex_conv2d_4_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_16 (max(-(texture(sampler2DArray(tex_conv2d_4_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_17 (max(-(texture(sampler2DArray(tex_conv2d_4_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_18 (max((texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_19 (max((texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_20 (max((texture(sampler2DArray(tex_conv2d_5_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_21 (max(-(texture(sampler2DArray(tex_conv2d_5_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_22 (max(-(texture(sampler2DArray(tex_conv2d_5_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_23 (max(-(texture(sampler2DArray(tex_conv2d_5_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_24 (max((texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_25 (max((texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_26 (max((texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_27 (max(-(texture(sampler2DArray(tex_conv2d_6_tf, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_28 (max(-(texture(sampler2DArray(tex_conv2d_6_tf1, pointSampler), vec3(pos, tile.inputLayer))), 0.0))
#define g_29 (max(-(texture(sampler2DArray(tex_conv2d_6_tf2, pointSampler), vec3(pos, tile.inputLayer))), 0.0))

vec4 hook() {
vec4 result = mat4(0.17312507, 0.18378204, 0.07926516, 0.1067288, 0.21052518, 0.13378853, 0.19536258, 0.14002354, 0.11711924, 0.08335183, 0.056983225, 0.028226014, 0.03449669, 0.044664416, 0.06761993, 0.044069722) * g_0;
    result += mat4(0.049151406, 0.027747469, 0.013829845, 0.010793505, 0.16125697, 0.10510845, 0.13865222, 0.08505211, -0.20990449, -0.19430009, -0.15810025, -0.15454805, -0.035844944, -0.11059333, -0.018675208, -0.09188628) * g_1;
    result += mat4(0.006685408, 0.11628241, 0.039672334, 0.1436817, 0.015559294, 0.009202889, 0.004621052, -0.006609141, 0.007991005, 0.08041883, -0.014427849, 0.057766948, -0.067192554, -0.10489045, -0.058118373, -0.10879217) * g_2;
    result += mat4(-0.13102308, -0.16938946, -0.049558997, -0.08738032, -0.15949999, -0.098247744, -0.21387893, -0.16764748, -0.036459852, -0.08977845, -0.063770026, -0.085683785, -0.04874994, -0.050357077, -0.040709995, -0.12104794) * g_3;
    result += mat4(-0.0016424131, -0.04231474, -0.008843509, -0.026220948, -0.13888876, -0.10844901, -0.10787409, -0.067019746, 0.1705322, 0.16687205, 0.16005264, 0.15010779, 0.084698394, 0.092028156, 0.07699169, 0.079460666) * g_4;
    result += mat4(0.0075197075, -0.020141402, -0.1006905, -0.11359611, -0.0085215755, -0.005612361, -0.0018493677, 0.007426326, -0.06751104, -0.08159549, 0.0120629985, -0.012342098, 0.03995728, 0.036384724, 0.09553051, 0.09851564) * g_5;
    result += mat4(-0.029465627, -0.054333087, 0.02729686, -0.0045043076, -0.13339953, -0.032064863, 0.0070489575, 0.1158326, -0.0006455828, -0.05559491, 0.016300855, -0.016093824, 0.0035336027, 0.025718046, -0.002194457, 0.009156581) * g_6;
    result += mat4(-0.03060067, -0.088183194, 0.08511207, 0.023555957, 0.030279126, 0.037585177, 0.016086163, 0.017970216, -0.05365472, 0.008709411, -0.022766082, 0.026308894, -0.026761275, -0.012835554, 0.02677239, 0.06120358) * g_7;
    result += mat4(-0.030154163, 0.016827311, -0.0070917453, 0.049568735, -0.06463202, -0.095433265, 0.059520688, 0.039794426, -0.11667492, -0.040507805, -0.05257038, 0.025766404, -0.04885214, 0.042495333, -0.022887079, 0.08385772) * g_8;
    result += mat4(0.024346549, 0.054313555, -0.005122175, 0.019812366, 0.13365328, 0.014708698, -0.010476813, -0.1185288, 0.0023148789, 0.052297566, -0.03189476, 0.005272433, -0.03835005, -0.026765257, -0.0094220815, 0.0047409064) * g_9;
    result += mat4(-0.007440264, 0.12066173, -0.12320844, 0.0016777752, -0.011408617, -0.029569637, 0.008827655, -0.007016294, 0.06650651, -0.031428255, 0.034667335, -0.023670185, 0.007218744, -0.004491109, -0.035605032, -0.07145819) * g_10;
    result += mat4(0.049787126, -0.0017957676, -0.006283968, -0.058967303, 0.05774073, 0.09960317, -0.059987612, -0.036502153, 0.07282059, 0.005348924, 0.013446346, -0.04757274, 0.045422055, -0.0634229, 0.024715338, -0.08555914) * g_11;
    result += mat4(-0.005835691, 0.016965812, -0.028456861, -0.0033920892, 0.009836867, 0.0006767609, 0.01886044, 0.012588657, -0.00884555, -0.0037418597, -0.009430517, -0.019091168, -0.002798804, 0.0039561144, 0.017126411, 0.004825749) * g_12;
    result += mat4(0.028191822, 0.029202491, 0.032901034, 0.011502915, -0.010819439, -0.0069572316, 0.006472295, 0.0053685335, 0.00079939753, 0.0037769184, 0.011775226, 0.01399779, 0.0033956952, 0.0052899374, -0.010259701, 0.0077763535) * g_13;
    result += mat4(0.008361512, -0.0117131, -0.0049652294, -0.01998969, 0.022627737, -0.008692346, 0.0019018264, -0.023467707, -0.008756792, -0.017017934, -0.031440705, -0.008512948, 0.0054877545, -0.00070786494, 0.019616788, 0.00793716) * g_14;
    result += mat4(-0.013002159, -0.03813209, 0.026482832, -0.00023578315, -0.004977621, 0.0014138863, -0.0057627726, -0.0042974507, -0.007416917, -0.008726386, -0.011688116, 0.010687058, -0.011166254, -0.020983206, 0.0066195372, 0.003834876) * g_15;
    result += mat4(0.0048169903, 0.0076203775, -0.015507004, -0.023508213, -0.052957263, -0.0069484734, -0.0011737008, 0.03410549, 0.0030833874, 0.012800496, -0.019242208, -0.005873537, -0.005420416, -0.009030759, -0.01785444, -0.01966881) * g_16;
    result += mat4(-0.012387838, -0.014545728, 0.035943765, 0.024116462, 0.0008325086, 0.017050253, 0.0024911535, 0.019210132, 0.02221826, 0.020303903, 0.004521489, -0.009177796, -0.07020659, -0.040271588, 0.013064882, 0.028324096) * g_17;
    result += mat4(-0.0069806273, 0.09828906, -0.049242873, 0.014799003, -0.008970328, 0.003844374, 0.0010211956, 0.008877965, 0.039977968, -0.17025097, 0.14956547, -0.02214056, -0.00973778, -0.018551195, 0.034893923, 0.027594449) * g_18;
    result += mat4(0.011814281, -0.015895301, 0.04550156, 0.04049697, 0.0076704635, -0.018837227, 0.005477875, -0.04887477, 0.05526271, 0.11000575, -0.03529281, -0.023258513, -0.0022530397, -0.026560089, -0.0021712275, 0.0056000547) * g_19;
    result += mat4(0.013357528, 0.014710138, 0.043349367, 0.053752452, -0.010020186, -0.0048438436, -0.023880936, -0.011357083, 0.033450976, 0.022771686, 0.0326334, 0.0068722614, -0.0512848, 0.026570365, -0.07270785, -0.006190101) * g_20;
    result += mat4(-0.025186045, -0.01740991, 0.003838567, 0.027091907, -0.0071685803, -0.00027341367, -0.02992052, -0.008542527, -0.013445479, -0.015780428, -0.042524435, -0.00881602, -0.011120149, 0.009015556, -0.013422532, -0.032560103) * g_21;
    result += mat4(-0.09606898, 0.025490688, -0.008527585, -0.075416856, -0.0028138838, -0.035580438, -0.006531162, 0.023687562, 0.0055310167, -0.010112962, 0.014539237, 0.01172912, 0.09965159, 0.075306684, 0.11886721, 0.095253) * g_22;
    result += mat4(0.011965668, -0.072057776, 0.024608271, -0.054251578, 0.012394993, 0.114785306, -0.0419942, -0.011279603, -0.021266261, -0.0042840955, -0.015289745, -0.029362924, 0.0103631085, -0.06942332, 0.042722963, -0.021691492) * g_23;
    result += mat4(0.033176757, 0.04084371, 0.015103838, -0.057419725, 0.037109293, -0.016537853, -0.059167393, 0.08598897, 0.015969522, -0.010902342, 0.03118472, 0.008363948, -0.041729625, 0.057053857, -0.08161458, 0.052837733) * g_24;
    result += mat4(-0.092430755, 0.07110693, -0.034382034, 0.062702626, 0.014907711, 0.07141848, -0.0019698131, -0.054372307, 0.0128283445, 0.013943152, -0.0034115645, -0.030608373, -0.005405216, 0.03866557, -0.034109335, -0.0013265307) * g_25;
    result += mat4(0.06594738, 0.029660825, -0.037681, -0.07724883, 0.03563272, 0.041913237, 0.0042468007, 0.0069140824, 0.039035708, -0.09520566, -0.04894546, -0.0034723799, -0.06357319, -0.052821137, 0.022598358, 0.041650392) * g_26;
    result += mat4(0.004992455, -0.06508938, 0.030750059, 0.022826253, 0.002092941, 0.0037119875, 0.030300831, -0.0454966, -0.05877186, -0.024108075, -0.07177208, -0.047089674, -0.014241358, -0.015470063, 0.029174741, -0.0012050892) * g_27;
    result += mat4(0.033182934, -0.0073093693, -0.017909355, -0.018535342, -0.0415075, -0.010425076, -0.0039859596, 0.015540642, 0.05229552, -0.08504954, 0.06377993, -0.035305116, -0.06266023, -0.102613874, 0.10803333, 0.06006112) * g_28;
    result += mat4(-0.0026692066, 0.020269373, -0.018895708, 0.010902005, -0.084507205, -0.018323625, 0.03897616, 0.008709061, -0.005905961, 0.05540135, 0.0050392286, 0.019433267, -0.0011370446, -0.02185742, 0.004525434, 0.010520601) * g_29;
    result += vec4(0.00428531, -0.011541925, 0.00898425, -0.01374321);
    return result;
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_last_tf2, ivec3(valid_xy, tile.inputLayer), result);
}