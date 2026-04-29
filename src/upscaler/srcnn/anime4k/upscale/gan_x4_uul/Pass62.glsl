// Anime4K_Upscale_GAN_x4_UUL - Pass 62 of 84 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 1024) uniform texture2D tex_conv2d_18_tf;
layout(set = 0, binding = 1025) uniform texture2D tex_conv2d_18_tf1;
layout(set = 0, binding = 1026) uniform texture2D tex_conv2d_18_tf2;
layout(set = 0, binding = 1027) uniform texture2D tex_conv2d_18_tf3;
layout(set = 0, binding = 1028) uniform texture2D tex_conv2d_18_tf4;
layout(set = 0, binding = 1029) uniform texture2D tex_conv2d_18_tf5;
layout(set = 0, binding = 1030) uniform texture2D tex_conv2d_20_tf;
layout(set = 0, binding = 1031) uniform texture2D tex_conv2d_1_tf;
layout(set = 0, binding = 1032) uniform texture2D tex_conv2d_4_tf;
layout(set = 0, binding = 1033) uniform texture2D tex_conv2d_7_tf;
layout(set = 0, binding = 1034) uniform texture2D tex_conv2d_10_tf;
layout(set = 0, binding = 1035) uniform texture2D tex_conv2d_13_tf;
layout(set = 0, binding = 1036) uniform texture2D tex_conv2d_16_tf;
layout(set = 0, binding = 1037) uniform texture2D tex_conv2d_19_tf;
layout(set = 0, binding = 2048, rgba16f) uniform image2D img_conv2d_21_tf5;
#define g_0 (max((texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_1 (max((texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_2 (max((texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_3 (max((texture(sampler2D(tex_conv2d_18_tf3, pointSampler), pos)), 0.0))
#define g_4 (max((texture(sampler2D(tex_conv2d_18_tf4, pointSampler), pos)), 0.0))
#define g_5 (max((texture(sampler2D(tex_conv2d_18_tf5, pointSampler), pos)), 0.0))
#define g_6 (max(-(texture(sampler2D(tex_conv2d_18_tf, pointSampler), pos)), 0.0))
#define g_7 (max(-(texture(sampler2D(tex_conv2d_18_tf1, pointSampler), pos)), 0.0))
#define g_8 (max(-(texture(sampler2D(tex_conv2d_18_tf2, pointSampler), pos)), 0.0))
#define g_9 (max(-(texture(sampler2D(tex_conv2d_18_tf3, pointSampler), pos)), 0.0))
#define g_10 (max(-(texture(sampler2D(tex_conv2d_18_tf4, pointSampler), pos)), 0.0))
#define g_11 (max(-(texture(sampler2D(tex_conv2d_18_tf5, pointSampler), pos)), 0.0))
#define g_12 (max((texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_13 (max(-(texture(sampler2D(tex_conv2d_20_tf, pointSampler), pos)), 0.0))
#define g_14 (max((texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_15 (max(-(texture(sampler2D(tex_conv2d_1_tf, pointSampler), pos)), 0.0))
#define g_16 (max((texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_17 (max(-(texture(sampler2D(tex_conv2d_4_tf, pointSampler), pos)), 0.0))
#define g_18 (max((texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_19 (max(-(texture(sampler2D(tex_conv2d_7_tf, pointSampler), pos)), 0.0))
#define g_20 (max((texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_21 (max(-(texture(sampler2D(tex_conv2d_10_tf, pointSampler), pos)), 0.0))
#define g_22 (max((texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_23 (max(-(texture(sampler2D(tex_conv2d_13_tf, pointSampler), pos)), 0.0))
#define g_24 (max((texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_25 (max(-(texture(sampler2D(tex_conv2d_16_tf, pointSampler), pos)), 0.0))
#define g_26 (max((texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))
#define g_27 (max(-(texture(sampler2D(tex_conv2d_19_tf, pointSampler), pos)), 0.0))

vec4 hook() {
vec4 result = mat4(0.037292957, 0.111278884, 0.0040617813, -0.13005154, -0.14574225, -0.04561907, 0.08651799, 0.26120758, 0.08891994, -0.088803776, 0.042923294, 0.25807977, -0.018256422, -0.0701701, -0.005195042, -0.003834101) * g_0;
    result += mat4(0.02109605, -0.069872335, 0.019276647, 0.20458579, 0.19809006, 0.07492716, 0.08456779, 0.03991817, 0.17381856, -0.18353306, 0.033056915, 0.017351417, 0.27317572, 0.14745289, 0.112595454, 0.24492109) * g_1;
    result += mat4(-0.14570235, -0.17424104, -0.06727217, -0.3086037, 0.02525411, -0.044770114, 0.033749532, -0.11228765, -0.15769076, 0.00451067, -0.1788018, -0.30820736, 0.0041043786, -0.024795217, 0.15125588, 0.047423594) * g_2;
    result += mat4(-0.040195987, 0.044254698, 0.03855816, -0.20195895, 0.022790458, 0.096643284, -0.059985366, 0.08459743, 0.1324966, -0.040880192, -0.0043202005, 0.047319695, -0.032420613, 0.19165912, 0.00961678, 0.0183705) * g_3;
    result += mat4(0.16408893, 0.13368279, -0.0021361106, -0.18459465, -0.01461956, -0.025040925, 0.023046397, 0.18937416, -0.029725153, 0.024626948, -0.12168845, -0.17462288, -0.0018600278, -0.21533066, -0.031245705, 0.016543053) * g_4;
    result += mat4(-0.26195183, 0.01833496, -0.18704526, -0.021662816, 0.10616261, -0.043555334, 0.27241042, -0.14757007, -0.124572046, -0.02121388, 0.051727325, -0.0069818725, 0.043559317, -0.110680476, 0.04445242, 0.13625911) * g_5;
    result += mat4(-0.038022455, 0.03635892, -0.2756826, 0.08211933, -0.023213604, -0.08972885, 0.032142006, -0.09148028, -0.19298528, 0.1790908, -0.089981236, -0.17479765, -0.16850077, -0.1224998, 0.26742375, -0.05020889) * g_6;
    result += mat4(0.071032055, -0.00785422, 0.10790756, 0.0018305354, -0.027506126, -0.062212195, -0.23357867, 0.045895457, -0.1727715, 0.10876975, -0.230332, -0.17849782, -0.07430489, -0.18781832, -0.04600162, -0.11432774) * g_7;
    result += mat4(-0.092788436, -0.024297832, -0.014884651, 0.34521446, 0.19182527, -0.0007828303, 0.2955958, 0.14103474, -0.118902594, -0.21362142, 0.03223166, 0.11770545, 0.052067857, -0.09909963, -0.090388335, 0.042580575) * g_8;
    result += mat4(-0.1330214, 0.03868773, -0.11671803, 0.19015789, 0.10405984, -0.013677597, -0.045054883, 0.2648324, 0.091654226, 0.06342989, -0.18447904, -0.18814911, 0.08201126, -0.087983154, 0.19835882, 0.02320308) * g_9;
    result += mat4(-0.16742142, 0.04889244, -0.04224858, 0.09795042, 0.0742024, 0.08524124, 0.08547024, -0.08971748, -0.06742199, -0.01264819, 0.01967524, -0.085037805, -0.006368631, 0.087310255, 0.033242185, -0.109046064) * g_10;
    result += mat4(-0.036376826, -0.12445654, 0.2214164, 0.073704585, -0.057687093, 0.03161407, 0.030226182, 0.13798846, 0.004053758, -0.026847184, -0.18207215, 0.02327736, 0.15338598, 0.029355692, 0.15947832, 0.009741949) * g_11;
    result += mat4(-0.14350525, 0.44122484, -0.27216923, -0.32400486, -0.06935376, -0.07826008, 0.013052485, -0.15577343, -0.0602264, -0.1378567, -0.0988297, -0.0520038, 0.16281459, 0.21593477, 0.015656868, 0.021682512) * g_12;
    result += mat4(-0.110919766, -0.50870305, 0.13304098, 0.44846004, -0.11171717, 0.021876339, -0.1763441, 0.07960399, 0.19334543, 0.059901852, 0.35047033, 0.06759713, -0.1094105, -0.03440771, 0.12352318, -0.0851165) * g_13;
    result += mat4(-0.0568668, -0.025527416, 0.025759742, -0.12103697, 0.422481, -0.08913437, -0.055062406, 0.34310246, 0.21279198, -0.078316584, -0.013654249, -0.09046805, -0.07094275, 0.115192436, -0.065263025, 0.17215906) * g_14;
    result += mat4(0.07046529, -0.07284162, -0.11466734, -0.21302283, -0.03389403, 0.15734796, 0.1361196, 0.024044609, 0.029766176, 0.16577528, 0.024331262, 0.060340524, 0.44355944, 0.0003581332, 0.3078238, 0.2574837) * g_15;
    result += mat4(0.00071162626, 0.07135437, 0.07894501, -0.0018909698, 0.056075454, 0.2710218, 0.05085683, -0.09762287, 0.3231151, -0.19741713, 0.17338343, 0.0155739505, -0.041763403, -0.1287588, -0.12640484, -0.23130493) * g_16;
    result += mat4(0.07035256, -0.11294888, -0.14101484, -0.15230694, -0.10483314, -0.0016073174, 0.057297777, -0.09009508, -0.12830521, 0.03709873, -0.06290859, -0.08136984, 0.113198824, -0.1655927, -0.13494876, 0.24072471) * g_17;
    result += mat4(-0.032724876, -0.09534773, -0.26204878, -0.3292954, -0.061760694, -0.0520527, 0.114927344, -0.19985563, -0.14206612, 0.29207164, -0.18231356, -0.023020215, -0.08598638, 0.14821911, 0.03660733, -0.19112201) * g_18;
    result += mat4(0.037955362, 0.010134931, 0.36916158, -0.17044878, 0.21356396, -0.1560363, 0.26455376, 0.20915791, -0.1306162, -0.2429591, 0.1719089, 0.18352278, 0.0679352, -0.065386556, -0.022702005, -0.066387825) * g_19;
    result += mat4(0.19960098, -0.14576043, -0.10151787, 0.09198339, 0.1231411, 0.087754674, 0.11652834, 0.013271647, 0.036118887, 0.15265918, 0.013385129, 0.14981005, -0.21563594, -0.08766662, -0.0654284, 0.12685579) * g_20;
    result += mat4(-0.094955795, 0.24225567, 0.048474804, -0.07734907, 0.01806047, 0.14843795, 0.06016524, 0.35317475, -0.11599948, -0.07693678, 0.18482585, -0.019892018, 0.114919215, 0.1710398, -0.048565853, 0.13335803) * g_21;
    result += mat4(-0.09855322, -0.025525704, -0.06842548, 0.1469744, -0.018368883, 0.15323098, 0.20133962, 0.12638539, -0.045463845, -0.08798743, 0.11472818, -0.033174478, 0.012110788, -0.06817629, -0.011605086, -0.16827421) * g_22;
    result += mat4(-0.045262296, 0.13600074, 0.1300623, -0.034807224, -0.34226584, 0.017031498, -0.039954994, -0.08290169, 0.10082742, 0.021582376, -0.09534511, 0.20549543, -0.051487718, -0.1630972, 0.33449423, -0.048398267) * g_23;
    result += mat4(0.029700171, 0.007352428, 0.18526569, 0.073091626, 0.11026601, 0.122599594, -0.11891045, 0.01342231, 0.15690641, 0.04361259, 0.2773186, 0.09948339, 0.19514516, -0.26567987, 0.27316755, -0.004506885) * g_24;
    result += mat4(0.015102482, 0.5311715, -0.04495627, -0.29039982, 0.043197848, -0.045482073, -0.015217863, 0.12423151, 0.06713047, -0.28593946, -0.26324463, -0.10622171, 0.08733315, 0.26325643, -0.109262615, 0.032678623) * g_25;
    result += mat4(0.20356876, 0.13201593, 0.54593295, -0.009429143, -0.047878712, 0.112797454, 0.10636369, -0.031002715, 0.04968258, -0.01192892, -0.08390279, 0.2962574, -0.037763555, 0.23986666, 0.2914927, -0.19597684) * g_26;
    result += mat4(-0.17221802, -0.3117124, -0.30086198, -0.09605459, 0.06022855, 0.0932599, 0.21669184, 0.025771603, 0.10568125, 0.09046417, 0.23842993, 0.15542446, 0.085549235, -0.39743817, -0.35149595, -0.10991869) * g_27;
    result += vec4(0.041429322, -0.04519541, -0.021303019, 0.03556548);
    return result;
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_conv2d_21_tf5, gxy, result);
}