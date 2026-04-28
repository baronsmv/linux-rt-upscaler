// Anime4K_Upscale_DTD_x2 - Pass 4 of 18 - https://github.com/bloc97/Anime4K
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
#define SIGMA 0.4

float gaussian(float x, float s, float m) {
	return (1.0 / (s * sqrt(2.0 * 3.14159))) * exp(-0.5 * pow(abs(x - m) / s, 2.0));
}

float lumGaussian(vec2 pos, vec2 d) {
	float s = SIGMA * vec2(ubo.in_width, ubo.in_height).y / 1080.0;
	float kernel_size = s * 2.0 + 1.0;
	
	float g = (texture(sampler2D(tex_MMKERNEL, pointSampler), pos).x) * gaussian(0.0, s, 0.0);
	float gn = gaussian(0.0, s, 0.0);
	
	g += (texture(sampler2D(tex_MMKERNEL, pointSampler), pos - d).x + texture(sampler2D(tex_MMKERNEL, pointSampler), pos + d).x) * gaussian(1.0, s, 0.0);
	gn += gaussian(1.0, s, 0.0) * 2.0;
	
	for (int i=2; float(i)<kernel_size; i++) {
		g += (texture(sampler2D(tex_MMKERNEL, pointSampler), pos - (d * float(i))).x + texture(sampler2D(tex_MMKERNEL, pointSampler), pos + (d * float(i))).x) * gaussian(float(i), s, 0.0);
		gn += gaussian(float(i), s, 0.0) * 2.0;
	}
	
	return g / gn;
}

vec4 hook() {
return vec4(lumGaussian(pos, vec2(vec2(ubo.in_dx, ubo.in_dy).x, 0)));
}

void main() {
    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);
    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_MMKERNEL, gxy, result);
}