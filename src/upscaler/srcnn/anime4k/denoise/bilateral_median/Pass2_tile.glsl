// Anime4K_Denoise_Bilateral_Median - Pass 2 of 2 - https://github.com/bloc97/Anime4K
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

layout(set = 0, binding = 3) uniform texture2DArray tex_HOOKED;
layout(set = 0, binding = 4) uniform texture2DArray tex_LINELUMA;
layout(set = 0, binding = 5, rgba8) uniform image2D img_output;
#define INTENSITY_SIGMA 0.1 //Intensity window size, higher is stronger denoise, must be a positive real number
#define SPATIAL_SIGMA 1.0 //Spatial window size, higher is stronger denoise, must be a positive real number.
#define HISTOGRAM_REGULARIZATION 0.0 //Histogram regularization window size, higher values approximate a bilateral "closest-to-mean" filter.
#define INTENSITY_POWER_CURVE 1.0 //Intensity window power curve. Setting it to 0 will make the intensity window treat all intensities equally, while increasing it will make the window narrower in darker intensities and wider in brighter intensities.
#define KERNELSIZE int(max(int(SPATIAL_SIGMA), 1) * 2 + 1) //Kernel size, must be an positive odd integer.
#define KERNELHALFSIZE (int(KERNELSIZE/2)) //Half of the kernel size without remainder. Must be equal to trunc(KERNELSIZE/2).
#define KERNELLEN (KERNELSIZE * KERNELSIZE) //Total area of kernel. Must be equal to KERNELSIZE * KERNELSIZE.
#define GETOFFSET(i) vec2((i % KERNELSIZE) - KERNELHALFSIZE, (i / KERNELSIZE) - KERNELHALFSIZE)

float gaussian(float x, float s, float m) {
	float scaled = (x - m) / s;
	return exp(-0.5 * scaled * scaled);
}

vec4 getMedian(vec4 v[KERNELLEN], float w[KERNELLEN], float n) {
	
	for (int i=0; i<KERNELLEN; i++) {
		float w_above = 0.0;
		float w_below = 0.0;
		for (int j=0; j<KERNELLEN; j++) {
			if (v[j].x > v[i].x) {
				w_above += w[j];
			} else if (v[j].x < v[i].x) {
				w_below += w[j];
			}
		}
		
		if ((n - w_above) / n >= 0.5 && w_below / n <= 0.5) {
			return v[i];
		}
	}
}

vec4 hook() {
vec4 histogram_v[KERNELLEN];
	float histogram_l[KERNELLEN];
	float histogram_w[KERNELLEN];
	float n = 0.0;
	
	float vc = texture(sampler2DArray(tex_LINELUMA, pointSampler), vec3(pos, tile.inputLayer)).x;
	
	float is = pow(vc + 0.0001, INTENSITY_POWER_CURVE) * INTENSITY_SIGMA;
	float ss = SPATIAL_SIGMA;
	
	for (int i=0; i<KERNELLEN; i++) {
		vec2 ipos = GETOFFSET(i);
		histogram_v[i] = texture(sampler2DArray(tex_HOOKED, pointSampler), vec3(pos + (ipos) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer));
		histogram_l[i] = texture(sampler2DArray(tex_LINELUMA, pointSampler), vec3(pos + (ipos) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer)).x;
		histogram_w[i] = gaussian(histogram_l[i], is, vc) * gaussian(length(ipos), ss, 0.0);
		n += histogram_w[i];
	}
	
	if (HISTOGRAM_REGULARIZATION > 0.0) {
		float histogram_wn[KERNELLEN];
		n = 0.0;
		
		for (int i=0; i<KERNELLEN; i++) {
			histogram_wn[i] = 0.0;
		}
		
		for (int i=0; i<KERNELLEN; i++) {
			histogram_wn[i] += gaussian(0.0, HISTOGRAM_REGULARIZATION, 0.0) * histogram_w[i];
			for (int j=(i+1); j<KERNELLEN; j++) {
				float d = gaussian(histogram_l[j], HISTOGRAM_REGULARIZATION, histogram_l[i]);
				histogram_wn[j] += d * histogram_w[i];
				histogram_wn[i] += d * histogram_w[j];
			}
			n += histogram_wn[i];
		}
	
		return getMedian(histogram_v, histogram_wn, n);
	}
	
	return getMedian(histogram_v, histogram_w, n);
}

void main() {
    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);
    ivec2 valid_xy = interior_xy + ivec2(tile.margin);
    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);
    vec4 result = hook();
    imageStore(img_output, ivec2(valid_xy) + ivec2(tile.dstOffset), result);
}