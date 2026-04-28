// CuNNy-4x16-NVL - Pass 1 of 6 - https://github.com/funnyplanter/CuNNy
// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler
//
// Compile with:
// dxc -T cs_6_0 -E main -spirv <this_file> \
//     -fvk-auto-shift-bindings \
//     -fvk-t-shift 1024 0 \
//     -fvk-u-shift 2048 0 \
//     -fvk-s-shift 3072 0 \
//     -fvk-use-dx-layout \
//     -fvk-use-scalar-layout \
//     -Fo <output.spv>
//
// =============================================================================
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// 
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
// =============================================================================

// -----------------------------------------------------------------------------
//  Constant buffer - set once per stage, shared by all tiles.
// -----------------------------------------------------------------------------
cbuffer Constants : register(b0) {
    // --- Feature-map dimensions for the *current* stage ---
    uint in_width;                 // width  of the texture(s) we sample this pass
    uint in_height;                // height of the texture(s) we sample this pass
    //   For intermediate passes:
    //     = expanded_tile_size (tile_size + 2 * margin).
    //   For final pass:
    //     = expanded_tile_size * scale (e.g., 2x or 4x tile)
    //
    // --- Dimensions of the full upscaled output frame ---
    uint out_width;                // only used in final pass: = full_out_w
    uint out_height;               // only used in final pass: = full_out_h
    //   Intermediate passes don't read these fields; they exist for layout compatibility.

    // --- Precomputed reciprocals (1.0 / dimension) ---
    //     Avoids division in the hot loop; every thread uses the same values.
    float in_dx;                   // = 1.0 / in_width
    float in_dy;                   // = 1.0 / in_height
    float out_dx;                  // = 1.0 / out_width   (final pass only)
    float out_dy;                  // = 1.0 / out_height  (final pass only)
};

// -----------------------------------------------------------------------------
// Push-constant block: passed from Python, contains per-tile metadata.
// Layout must match the struct.pack("I"*8, ...) in TileProcessor.
// -----------------------------------------------------------------------------
struct TileParams {
    // ---- Layer selection (only for array textures) ----
    uint inputLayer;               // which slice of the 2D array to read

    // ---- Output location in the full upscaled frame ----
    uint2 dstOffset;               // top-left corner of this tile’s
                                   // output rectangle (in upscaled pixels)

    // ---- Size of the *full* output frame ----
    uint fullOutWidth;             // overall width  (upscaled pixels)
    uint fullOutHeight;            // overall height (upscaled pixels)

    // ---- Context margin (pixels in the *current* feature-map space) ----
    uint margin;                   // for stage 1 = context_margin, for stage 2 = context_margin * 2

    // ---- Dimensions of the tile’s output region ----
    uint2 tileOutExtent;           // width and height that this tile
                                   // actually writes to (may be smaller
                                   // at right/bottom edges)
};
[[vk::push_constant]] TileParams tileParams;

float2 GetInputPt() { return float2(in_dx, in_dy); }
float2 GetOutputPt() { return float2(out_dx, out_dy); }
uint2 GetInputSize() { return uint2(in_width, in_height); }
uint2 GetOutputSize() { return uint2(out_width, out_height); }

#define O(t, x, y) t.SampleLevel(SP, float3(pos + float2(x, y) * pt, tileParams.inputLayer), 0)
#define V4 min16float4
#define M4 min16float4x4
#define V3 min16float3
#define M3x4 min16float3x4

Texture2DArray<float4> INPUT : register(t0);

[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T0 : register(u0);
[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T1 : register(u1);
[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T2 : register(u2);
[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T3 : register(u3);

SamplerState SP : register(s0);
SamplerState SL : register(s1);

#define L0(x, y) V3(O(INPUT, x, y).rgb)

[numthreads(8,8,1)]
void main(uint3 id : SV_DispatchThreadID)
{
    // -----------------------------------------------------------------------------
    //  Coordinate mapping for intermediate passes
    //
    //    Each thread processes exactly one output pixel.
    //    The dispatch grid covers the entire input texture (1:1 mapping).
    // -----------------------------------------------------------------------------
    
    // (1) texel size of the **input** texture(s) for this pass.
    //     In tile mode this is the expanded tile size (e.g., 40x40),
    //     in full-frame mode it is the crop width/height.
    float2 pt = float2(GetInputPt());
    
    // (2) position of this thread’s output pixel within the input grid.
    //     gxy is the pixel coordinate (x, y), directly from the dispatch ID.
    uint2 gxy = id.xy;
    
    // (3) normalized sampling position (0-1) - pixel *centre*.
    //     pt converts pixel coordinates to UV space; +0.5 aligns to pixel centres.
    float2 pos = (gxy + 0.5) * pt;
    
    //   In subsequent macro O(t, x, y) we sample at (pos + float2(x,y)*pt),
    //   which yields the centre of neighbouring pixels (x,y offsets in pixels).

    V3 s0_0_0, s0_0_1, s0_0_2, s0_1_0, s0_1_1, s0_1_2, s0_2_0, s0_2_1, s0_2_2;
    V4 r0 = 0.0, r1 = 0.0, r2 = 0.0, r3 = 0.0;

    s0_0_0 = L0(-1.0, -1.0); s0_0_1 = L0(0.0, -1.0); s0_0_2 = L0(1.0, -1.0);
    s0_1_0 = L0(-1.0, 0.0); s0_1_1 = L0(0.0, 0.0); s0_1_2 = L0(1.0, 0.0);
    s0_2_0 = L0(-1.0, 1.0); s0_2_1 = L0(0.0, 1.0); s0_2_2 = L0(1.0, 1.0);

    r0 += mul(s0_0_0, M3x4(7.157e-03, 1.490e-02, 8.311e-03, -1.157e-03, 6.252e-02, -8.575e-03, 4.185e-02, 1.996e-02, -3.998e-03, -4.913e-03, -2.806e-02, -9.369e-03));
    r1 += mul(s0_0_0, M3x4(-9.445e-05, 5.493e-03, 3.455e-02, -1.350e-02, -4.914e-02, 1.802e-02, -7.098e-02, -2.797e-02, 6.551e-04, -1.144e-02, -7.462e-04, 5.474e-03));
    r2 += mul(s0_0_0, M3x4(1.800e-02, 3.464e-02, -1.416e-02, -8.819e-02, -3.611e-02, 3.967e-02, 5.867e-03, 9.414e-02, -4.628e-02, -1.848e-02, 3.075e-04, -1.116e-02));
    r3 += mul(s0_0_0, M3x4(-7.233e-03, -2.764e-02, -2.142e-02, 2.087e-02, 1.905e-02, -5.868e-02, -4.900e-02, 3.184e-02, 1.831e-03, 4.915e-03, 2.649e-02, -1.217e-02));

    r0 += mul(s0_0_1, M3x4(5.857e-03, 9.514e-03, 1.102e-02, -1.616e-03, -7.543e-02, -1.011e-02, -1.817e-02, -1.148e-02, 1.734e-03, 1.404e-03, -3.328e-03, 9.912e-03));
    r1 += mul(s0_0_1, M3x4(-1.850e-02, 2.933e-01, -6.853e-02, 2.949e-02, -3.841e-02, 6.708e-01, 5.893e-02, 3.614e-01, 9.383e-03, 1.069e-01, 3.493e-03, 1.655e-03));
    r2 += mul(s0_0_1, M3x4(9.473e-02, 4.626e-03, 1.054e-02, -1.005e-01, 2.881e-01, 8.076e-03, 2.435e-02, 1.111e-01, -6.196e-02, -7.233e-03, 7.476e-03, -6.289e-03));
    r3 += mul(s0_0_1, M3x4(6.262e-03, 3.516e-03, 2.109e-02, 8.779e-03, -2.143e-02, 4.856e-02, -4.855e-02, -4.048e-02, 2.852e-03, -1.029e-02, -4.945e-02, -1.199e-02));

    r0 += mul(s0_0_2, M3x4(-1.176e-03, -2.588e-03, -3.174e-02, -6.474e-03, -4.673e-03, -2.921e-05, -2.364e-02, 2.064e-03, 3.611e-03, 3.187e-03, 9.060e-02, 6.318e-04));
    r1 += mul(s0_0_2, M3x4(1.771e-02, 5.698e-03, 1.709e-02, -3.503e-02, 5.520e-03, 3.892e-02, -1.585e-02, -9.999e-03, -7.066e-03, -1.358e-02, -6.007e-04, 2.835e-03));
    r2 += mul(s0_0_2, M3x4(1.550e-02, 3.339e-02, -1.560e-03, -1.513e-02, 7.854e-02, 2.149e-02, -2.321e-03, 7.129e-03, -1.244e-02, 6.597e-04, -5.545e-03, 5.801e-03));
    r3 += mul(s0_0_2, M3x4(-5.756e-03, -9.332e-04, 7.462e-03, -2.783e-02, 1.247e-04, 1.930e-02, -5.367e-02, 6.196e-03, -2.841e-03, -2.488e-03, 3.808e-02, -6.416e-04));

    r0 += mul(s0_1_0, M3x4(3.175e-01, -3.259e-02, 5.764e-03, 3.572e-01, 6.230e-01, 3.457e-02, -2.519e-02, 6.973e-01, 1.037e-01, -2.233e-03, 2.533e-02, 1.058e-01));
    r1 += mul(s0_1_0, M3x4(5.013e-02, 2.124e-03, -3.317e-02, 1.362e-02, 8.784e-02, -3.546e-02, 1.501e-01, -3.481e-02, 1.142e-02, 1.639e-02, 1.085e-02, -5.622e-03));
    r2 += mul(s0_1_0, M3x4(1.018e-01, 1.750e-02, 9.937e-02, 9.039e-01, 1.865e-01, 2.924e-02, -1.143e-02, -8.926e-01, -5.468e-02, -3.759e-02, -1.213e-02, 2.427e-02));
    r3 += mul(s0_1_0, M3x4(-1.728e-02, -2.822e-01, -7.844e-02, -5.404e-02, -5.536e-02, -5.129e-01, 1.272e-02, -4.425e-02, -5.391e-03, -6.419e-02, -2.723e-02, 1.895e-02));

    r0 += mul(s0_1_1, M3x4(-3.135e-01, 1.039e-01, -2.092e-02, -3.584e-01, -6.341e-01, -8.082e-02, -2.023e-02, -6.899e-01, -9.937e-02, -1.752e-02, 1.861e-02, -1.137e-01));
    r1 += mul(s0_1_1, M3x4(-1.899e-01, -2.959e-01, 4.434e-01, 4.040e-02, 4.209e-01, -6.660e-01, -3.923e-01, -1.362e-01, -1.875e-02, -9.937e-02, 7.274e-03, -1.664e-02));
    r2 += mul(s0_1_1, M3x4(-1.285e-02, -3.076e-01, -2.356e-02, 1.420e-02, -1.861e-01, -2.874e-01, -9.692e-02, 7.617e-03, 1.460e-01, 1.130e-01, -1.789e-02, -3.112e-02));
    r3 += mul(s0_1_1, M3x4(-3.037e-01, 2.982e-01, 4.015e-01, -2.343e-01, -5.697e-01, 5.332e-01, 9.464e-01, -5.139e-01, -7.152e-02, 7.354e-02, 4.921e-02, -3.209e-02));

    r0 += mul(s0_1_2, M3x4(2.575e-02, 4.951e-01, 7.005e-02, 7.335e-03, -2.310e-02, -4.872e-01, 2.339e-01, -9.570e-03, 1.262e-03, -1.385e-02, 1.686e-01, 5.026e-03));
    r1 += mul(s0_1_2, M3x4(7.112e-02, -1.259e-02, -4.966e-02, -3.044e-02, -6.528e-02, -3.708e-02, 2.255e-01, 1.337e-02, 1.147e-02, 1.541e-02, 2.419e-04, -5.793e-04));
    r2 += mul(s0_1_2, M3x4(-1.679e-01, 4.385e-02, 4.834e-02, -3.524e-02, -2.842e-01, -1.049e-02, 1.458e-03, 3.501e-02, 4.593e-02, -1.034e-02, 9.453e-03, -2.663e-03));
    r3 += mul(s0_1_2, M3x4(7.414e-03, -8.961e-03, -9.222e-03, -1.505e-03, 7.776e-03, 3.633e-03, -1.130e-01, -3.001e-02, 1.463e-02, -7.014e-03, -6.145e-02, -1.919e-02));

    r0 += mul(s0_2_0, M3x4(5.313e-03, -9.997e-03, -3.144e-02, 1.395e-02, 1.068e-01, 3.945e-05, -4.951e-02, 1.874e-03, -6.101e-03, 1.351e-02, 1.806e-02, -9.222e-03));
    r1 += mul(s0_2_0, M3x4(-2.050e-02, -1.242e-02, 5.457e-03, 1.360e-02, -2.155e-02, 5.849e-03, -4.120e-02, -2.882e-03, -5.776e-03, -5.614e-03, -4.758e-03, 2.753e-03));
    r2 += mul(s0_2_0, M3x4(2.717e-02, 2.725e-02, -9.739e-02, -8.745e-02, 3.573e-02, 2.733e-02, 2.979e-02, 1.004e-01, 9.685e-03, 4.758e-03, -1.871e-03, -1.864e-02));
    r3 += mul(s0_2_0, M3x4(2.245e-02, -1.159e-02, 4.099e-02, -2.380e-02, 2.692e-02, -1.038e-01, -2.480e-02, -3.101e-03, -4.996e-03, 2.104e-03, 1.954e-02, -3.133e-02));

    r0 += mul(s0_2_1, M3x4(-3.370e-02, -7.489e-01, 9.913e-03, -3.727e-03, -2.200e-02, 7.189e-01, 8.426e-02, -1.251e-02, 3.844e-03, 7.860e-03, 1.343e-01, 1.060e-02));
    r1 += mul(s0_2_1, M3x4(2.718e-02, 1.739e-02, -1.048e-01, -6.029e-03, 5.644e-03, 5.693e-03, 1.256e-01, 4.214e-02, 3.031e-03, -6.308e-03, -1.031e-02, 7.556e-03));
    r2 += mul(s0_2_1, M3x4(-8.227e-02, -2.763e-02, 2.261e-01, -7.162e-02, 1.635e-03, 4.283e-02, 9.947e-02, 7.666e-02, 2.887e-02, 7.367e-03, 1.854e-02, -4.228e-03));
    r3 += mul(s0_2_1, M3x4(3.075e-01, 2.363e-02, -6.788e-02, 2.479e-01, 5.996e-01, 4.575e-02, -4.749e-02, 4.628e-01, 6.661e-02, -5.581e-03, -3.518e-02, 6.356e-02));

    r0 += mul(s0_2_2, M3x4(4.938e-03, 1.720e-01, -1.095e-04, -6.701e-03, -1.233e-02, -1.695e-01, -1.677e-01, 3.480e-03, 1.336e-03, 1.412e-02, -7.429e-01, 3.504e-04));
    r1 += mul(s0_2_2, M3x4(3.460e-02, 2.450e-03, -8.434e-02, -1.975e-02, 2.967e-03, -1.477e-04, 9.797e-02, 1.727e-02, 7.965e-03, -1.813e-03, 1.288e-03, -6.565e-04));
    r2 += mul(s0_2_2, M3x4(-1.458e-02, 3.034e-02, 4.005e-03, -4.391e-02, -8.667e-02, 3.182e-04, -7.493e-02, 2.559e-02, -4.620e-02, -4.471e-03, 7.274e-03, 1.621e-02));
    r3 += mul(s0_2_2, M3x4(-6.385e-03, -1.216e-02, 7.528e-03, 1.992e-02, -1.993e-03, 6.777e-03, -2.777e-02, 9.337e-02, -2.772e-03, 1.418e-03, 2.503e-02, 7.394e-03));

    r0 += V4(1.406e-02, -1.134e-03, -1.611e-02, -2.320e-04);

    r0 = max(r0, 0.0);

    T0[uint3(gxy, tileParams.inputLayer)] = r0;

    r1 += V4(3.087e-02, 1.628e-03, 3.260e-02, 5.064e-03);

    r1 = max(r1, 0.0);

    T1[uint3(gxy, tileParams.inputLayer)] = r1;

    r2 += V4(8.945e-03, 1.333e-01, 1.492e-02, -4.488e-03);

    r2 = max(r2, 0.0);

    T2[uint3(gxy, tileParams.inputLayer)] = r2;

    r3 += V4(2.635e-03, -9.137e-03, -8.033e-01, -1.303e-02);

    r3 = max(r3, 0.0);

    T3[uint3(gxy, tileParams.inputLayer)] = r3;
}