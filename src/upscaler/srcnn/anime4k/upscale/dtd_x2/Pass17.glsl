// Anime4K_Upscale_DTD_x2 - Pass 17 of 18 - https://github.com/bloc97/Anime4K
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
//    glslc -fshader-stage=compute --target-env=vulkan1.2 \
//          <this_file> -o <output.spv>
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

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;

layout(set = 0, binding = 3) uniform texture2D tex_HOOKED;
layout(set = 0, binding = 4) uniform texture2D tex_MMKERNEL;
layout(set = 0, binding = 5, rgba8) uniform image2D img_MMKERNEL;

float max3v(float a, float b, float c) {
	return max(max(a, b), c);
}
float min3v(float a, float b, float c) {
	return min(min(a, b), c);
}

vec2 minmax3(vec2 pos, vec2 d) {
	float a0 = texture(sampler2D(tex_MMKERNEL, pointSampler), pos - d).y;
	float b0 = texture(sampler2D(tex_MMKERNEL, pointSampler), pos).y;
	float c0 = texture(sampler2D(tex_MMKERNEL, pointSampler), pos + d).y;
	
	float a1 = texture(sampler2D(tex_MMKERNEL, pointSampler), pos - d).z;
	float b1 = texture(sampler2D(tex_MMKERNEL, pointSampler), pos).z;
	float c1 = texture(sampler2D(tex_MMKERNEL, pointSampler), pos + d).z;
	
	return vec2(min3v(a0, b0, c0), max3v(a1, b1, c1));
}

float lumGaussian7(vec2 pos, vec2 d) {
	float g = (texture(sampler2D(tex_MMKERNEL, pointSampler), pos - (d + d)).x + texture(sampler2D(tex_MMKERNEL, pointSampler), pos + (d + d)).x) * 0.06136;
	g = g + (texture(sampler2D(tex_MMKERNEL, pointSampler), pos - d).x + texture(sampler2D(tex_MMKERNEL, pointSampler), pos + d).x) * 0.24477;
	g = g + (texture(sampler2D(tex_MMKERNEL, pointSampler), pos).x) * 0.38774;
	
	return g;
}

vec4 hook() {
return vec4(lumGaussian7(pos, vec2(0, vec2(ubo.in_dx, ubo.in_dy).y)), minmax3(pos, vec2(0, vec2(ubo.in_dx, ubo.in_dy).y)), 0);
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_MMKERNEL, gxy, result);
}