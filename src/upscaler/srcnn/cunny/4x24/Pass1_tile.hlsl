// CuNNy-4x24-NVL - Pass 1 of 6 - https://github.com/funnyplanter/CuNNy
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
    // ---- Output location in the full upscaled frame ----
    uint2 dstOffset;               // top-left corner of this tile’s
                                   // output rectangle (in upscaled pixels)

    // ---- Dimensions of the tile’s output region ----
    uint2 tileOutExtent;           // width and height that this tile
                                   // actually writes to (may be smaller
                                   // at right/bottom edges)

    // ---- Size of the *full* output frame ----
    uint fullOutWidth;             // overall width  (upscaled pixels)
    uint fullOutHeight;            // overall height (upscaled pixels)

    // ---- Layer selection (only for array textures) ----
    uint inputLayer;               // which slice of the 2D array to read

    // ---- Context margin (pixels in the *current* feature-map space) ----
    uint margin;                   // for stage 1 = context_margin, for stage 2 = context_margin * 2

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
[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T4 : register(u4);
[[vk::image_format("rgba8")]] RWTexture2DArray<float4> T5 : register(u5);

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
    V4 r0 = 0.0, r1 = 0.0, r2 = 0.0, r3 = 0.0, r4 = 0.0, r5 = 0.0;

    s0_0_0 = L0(-1.0, -1.0); s0_0_1 = L0(0.0, -1.0); s0_0_2 = L0(1.0, -1.0);
    s0_1_0 = L0(-1.0, 0.0); s0_1_1 = L0(0.0, 0.0); s0_1_2 = L0(1.0, 0.0);
    s0_2_0 = L0(-1.0, 1.0); s0_2_1 = L0(0.0, 1.0); s0_2_2 = L0(1.0, 1.0);

    r0 += mul(s0_0_0, M3x4(-1.177e-02, -2.027e-02, -7.724e-04, 4.341e-03, 2.758e-02, 3.641e-02, 2.423e-02, 5.619e-03, -9.000e-03, -1.484e-02, 4.196e-03, -1.283e-03));
    r1 += mul(s0_0_0, M3x4(2.832e-04, 8.771e-03, 8.715e-03, -5.340e-03, 8.802e-03, 8.784e-03, 3.943e-02, 2.668e-03, 9.141e-03, 9.607e-03, 1.091e-02, -1.859e-03));
    r2 += mul(s0_0_0, M3x4(4.416e-02, 1.634e-03, 1.549e-02, -1.024e-01, 8.914e-02, 1.839e-03, -8.387e-02, -3.723e-02, -1.280e-01, -2.493e-03, 3.784e-03, 2.165e-01));
    r3 += mul(s0_0_0, M3x4(5.239e-03, -1.028e-01, 1.015e-02, 1.148e-01, -1.128e-02, -8.431e-02, -5.552e-03, -9.263e-02, 4.829e-03, 1.938e-01, 1.321e-02, -1.935e-02));
    r4 += mul(s0_0_0, M3x4(-2.217e-03, -1.229e-02, 1.847e-02, 1.491e-02, 9.509e-03, -1.073e-01, -1.593e-02, 6.071e-02, -7.069e-03, 1.236e-01, -2.817e-03, -3.018e-03));
    r5 += mul(s0_0_0, M3x4(-1.495e-02, -4.113e-01, -1.114e-02, 3.250e-02, 1.786e-02, 2.960e-01, -9.424e-03, -1.204e-02, 8.730e-03, 1.121e-01, -2.877e-03, -1.519e-02));

    r0 += mul(s0_0_1, M3x4(3.295e-01, 1.004e-01, -1.436e-02, 6.133e-02, 5.723e-01, 2.190e-01, -3.394e-02, -8.154e-02, 1.466e-01, -3.227e-01, -1.694e-02, 1.430e-02));
    r1 += mul(s0_0_1, M3x4(1.420e-02, -5.086e-03, -2.246e-02, 1.483e-02, 1.650e-02, -2.243e-02, -1.061e-02, -2.326e-02, -2.748e-02, -4.875e-03, 1.059e-02, 1.227e-02));
    r2 += mul(s0_0_1, M3x4(-2.630e-02, -2.718e-01, -1.333e-01, -1.329e-01, -6.482e-02, -6.270e-01, -1.254e-01, -1.934e-01, 8.711e-02, -9.990e-02, -5.920e-02, -8.588e-01));
    r3 += mul(s0_0_1, M3x4(-3.866e-03, -1.503e-01, -4.956e-03, -5.172e-01, -9.067e-03, 6.277e-02, -2.178e-02, 3.525e-01, 1.046e-03, 1.747e-01, -1.574e-02, 1.557e-01));
    r4 += mul(s0_0_1, M3x4(-1.650e-02, 2.626e-02, -6.623e-02, -3.181e-02, -2.635e-02, 3.613e-01, 8.333e-02, 1.934e-02, 1.262e-02, -3.889e-01, -1.274e-02, 2.628e-02));
    r5 += mul(s0_0_1, M3x4(6.305e-03, -1.255e-01, -2.622e-02, -3.542e-02, -1.680e-02, 9.984e-02, 2.105e-02, -9.452e-04, -9.734e-04, 3.107e-02, -1.564e-02, 3.137e-02));

    r0 += mul(s0_0_2, M3x4(-6.620e-03, 1.986e-01, -9.060e-04, 1.168e-02, 1.741e-02, 3.055e-01, -2.694e-04, -1.175e-02, -1.653e-03, -5.033e-01, 1.080e-02, 5.976e-03));
    r1 += mul(s0_0_2, M3x4(-1.788e-02, 6.218e-03, 1.456e-02, -9.505e-03, 5.741e-03, 1.849e-02, -5.043e-02, 1.557e-02, 7.161e-03, -2.038e-02, -1.012e-02, -4.639e-03));
    r2 += mul(s0_0_2, M3x4(6.994e-02, -8.778e-03, 7.138e-03, -2.621e-02, 5.404e-02, 1.286e-02, -4.434e-02, -4.194e-02, -1.189e-01, -7.077e-03, -8.910e-03, 1.469e-01));
    r3 += mul(s0_0_2, M3x4(7.636e-03, -1.255e-02, 8.219e-03, -2.502e-02, -2.747e-02, -9.468e-02, 6.159e-03, 7.438e-03, 9.301e-03, 9.128e-02, -4.840e-03, 2.408e-02));
    r4 += mul(s0_0_2, M3x4(1.233e-02, 6.620e-02, -9.021e-03, -1.042e-02, -1.540e-02, -4.381e-02, 9.692e-03, -6.786e-02, 3.922e-03, -2.904e-02, -3.444e-03, -1.846e-02));
    r5 += mul(s0_0_2, M3x4(1.780e-03, 6.299e-02, -8.119e-03, 2.395e-02, 2.260e-03, -2.838e-02, 1.914e-02, -1.978e-02, -5.345e-03, -3.610e-02, -1.487e-02, -4.498e-03));

    r0 += mul(s0_1_0, M3x4(1.242e-02, -2.684e-02, -2.113e-02, 5.212e-02, -4.072e-02, -8.399e-02, -3.313e-02, -6.720e-02, 9.130e-03, 1.070e-01, -4.958e-04, 1.127e-02));
    r1 += mul(s0_1_0, M3x4(-6.697e-03, -1.677e-02, 6.273e-03, 5.646e-03, -8.668e-03, -1.613e-02, -1.123e-02, -6.752e-03, 5.993e-03, -1.462e-02, -3.937e-03, 7.189e-04));
    r2 += mul(s0_1_0, M3x4(1.264e-01, 2.841e-03, -5.412e-02, 1.653e-01, -2.759e-02, -8.226e-03, -5.831e-02, 9.813e-02, -1.086e-01, 1.533e-03, -2.845e-02, -2.471e-02));
    r3 += mul(s0_1_0, M3x4(-1.250e-02, 1.270e-01, 2.481e-02, 4.558e-01, 1.680e-02, 1.382e-01, 7.105e-02, -3.089e-01, 1.319e-02, -3.010e-01, -1.968e-02, -1.479e-01));
    r4 += mul(s0_1_0, M3x4(-2.408e-02, 9.966e-03, -4.888e-02, -5.505e-02, -1.767e-02, 2.081e-01, 4.968e-02, -2.932e-02, 8.441e-03, -2.173e-01, -3.608e-03, -6.261e-04));
    r5 += mul(s0_1_0, M3x4(2.679e-01, -3.584e-01, -2.166e-02, -8.097e-02, 6.270e-01, 2.657e-01, 5.053e-02, 1.003e-01, 1.352e-01, 9.824e-02, 3.053e-03, -3.191e-02));

    r0 += mul(s0_1_1, M3x4(-3.350e-01, -3.740e-01, 3.071e-02, -9.043e-01, -5.596e-01, -5.887e-01, 5.684e-01, 9.499e-01, -1.309e-01, 9.707e-01, 1.016e-03, -5.593e-02));
    r1 += mul(s0_1_1, M3x4(-9.204e-02, -2.742e-01, -2.929e-01, -3.917e-01, -2.296e-01, -4.689e-01, -4.756e-01, -4.541e-01, -1.072e-01, -7.419e-02, -9.531e-02, -1.860e-01));
    r2 += mul(s0_1_1, M3x4(-7.984e-01, 2.730e-01, 2.583e-01, 4.873e-02, -2.906e-01, 6.396e-01, 3.526e-01, 7.115e-03, 1.082e+00, 9.706e-02, 8.927e-02, 1.794e-01));
    r3 += mul(s0_1_1, M3x4(-2.609e-01, 4.581e-01, -1.635e-01, 7.688e-02, -5.665e-01, 1.519e-01, -3.016e-01, -8.862e-02, -1.431e-01, -9.463e-01, -7.060e-02, 1.797e-02));
    r4 += mul(s0_1_1, M3x4(2.473e-01, 1.155e-01, 7.691e-01, 2.394e-01, 2.764e-01, 4.092e-01, -8.027e-01, 3.171e-01, 5.091e-02, -5.455e-01, 4.353e-02, 8.863e-02));
    r5 += mul(s0_1_1, M3x4(-2.549e-01, 7.561e-01, -1.891e-01, 5.371e-01, -6.251e-01, -5.723e-01, -1.724e-01, -5.735e-01, -1.257e-01, -1.870e-01, 6.467e-02, 6.172e-02));

    r0 += mul(s0_1_2, M3x4(1.667e-02, 1.431e-01, -3.221e-03, 7.749e-02, -2.463e-02, 1.744e-01, -6.372e-02, -8.819e-02, -7.462e-03, -3.203e-01, -9.681e-03, 3.184e-03));
    r1 += mul(s0_1_2, M3x4(2.026e-03, 7.198e-02, 1.328e-01, 3.888e-01, 3.098e-02, 1.100e-01, 2.360e-01, 4.615e-01, 1.709e-02, 4.834e-02, 3.986e-02, 1.836e-01));
    r2 += mul(s0_1_2, M3x4(7.190e-02, 1.314e-02, 2.495e-03, 3.483e-02, -5.103e-03, -1.723e-02, -3.615e-03, 8.386e-02, -6.164e-02, 8.268e-03, 7.329e-03, -2.552e-02));
    r3 += mul(s0_1_2, M3x4(-4.127e-03, -1.250e-01, -4.635e-03, -6.269e-01, -1.097e-03, 2.718e-02, 1.417e-02, 4.214e-01, -8.080e-03, 2.270e-01, -1.408e-02, 1.976e-01));
    r4 += mul(s0_1_2, M3x4(-7.007e-02, -1.112e-01, -8.220e-02, -1.450e-01, -1.102e-02, -4.413e-01, 8.548e-02, -1.339e-01, -3.443e-02, 5.762e-01, -1.352e-03, -8.961e-02));
    r5 += mul(s0_1_2, M3x4(1.490e-04, 4.291e-02, -7.273e-03, -6.840e-03, -3.433e-03, -3.627e-02, 4.597e-02, 3.729e-03, -9.389e-03, -9.533e-03, -1.480e-02, -1.400e-03));

    r0 += mul(s0_2_0, M3x4(-8.235e-03, 1.945e-02, 7.938e-03, 4.298e-02, 9.497e-03, 2.548e-02, 4.324e-03, -3.675e-02, -4.481e-03, -4.572e-02, 3.067e-03, -8.904e-03));
    r1 += mul(s0_2_0, M3x4(-1.554e-03, -1.357e-02, -3.245e-02, -1.069e-03, -2.171e-02, -7.033e-03, -3.354e-02, -1.320e-03, 1.416e-02, 8.193e-03, -3.218e-03, 3.822e-03));
    r2 += mul(s0_2_0, M3x4(1.250e-02, -5.030e-03, -2.006e-02, 2.725e-04, 3.296e-02, -6.669e-04, -3.703e-02, 2.748e-02, -3.503e-02, 9.027e-04, -2.540e-02, -7.489e-02));
    r3 += mul(s0_2_0, M3x4(2.589e-01, -8.786e-02, 1.346e-01, -1.691e-02, 5.957e-01, -1.708e-02, 2.940e-01, 1.944e-02, 1.315e-01, 9.491e-02, 6.791e-02, -4.254e-05));
    r4 += mul(s0_2_0, M3x4(1.469e-02, 6.812e-03, -3.528e-02, 5.807e-03, 7.904e-03, 2.902e-02, 3.427e-02, -4.575e-02, -2.779e-03, -4.076e-02, 3.621e-03, 1.498e-02));
    r5 += mul(s0_2_0, M3x4(9.936e-03, 1.104e-02, 1.396e-02, -2.594e-01, -2.081e-02, -1.215e-03, -3.582e-02, 3.254e-01, 3.259e-03, -8.764e-03, -6.937e-03, -6.613e-02));

    r0 += mul(s0_2_1, M3x4(1.461e-02, -4.951e-02, 1.235e-02, 8.366e-02, -1.048e-04, 8.710e-03, -7.593e-02, -9.932e-02, -3.959e-03, 3.821e-02, -1.257e-02, 1.849e-02));
    r1 += mul(s0_2_1, M3x4(-1.651e-02, 6.523e-02, 7.878e-02, 1.745e-04, 6.860e-02, 7.092e-02, 1.140e-01, -6.541e-03, 1.706e-02, 7.783e-03, 3.503e-02, -1.022e-03));
    r2 += mul(s0_2_1, M3x4(2.206e-01, -7.031e-04, -8.384e-03, -8.055e-02, -4.598e-02, -6.625e-04, 3.609e-05, -1.517e-02, -1.926e-01, 3.314e-03, 3.588e-02, 4.993e-02));
    r3 += mul(s0_2_1, M3x4(5.024e-03, 1.113e-01, -6.773e-03, 4.674e-01, 6.594e-03, 6.523e-03, -5.233e-03, -2.860e-01, -4.040e-03, -1.554e-01, 4.152e-02, -1.846e-01));
    r4 += mul(s0_2_1, M3x4(-1.018e-01, -7.894e-02, -8.081e-02, -1.425e-01, -6.243e-02, -3.233e-01, 9.485e-02, -3.662e-01, -1.474e-02, 4.261e-01, -1.486e-02, -1.469e-01));
    r5 += mul(s0_2_1, M3x4(-1.182e-02, 1.126e-01, 1.740e-02, -2.018e-01, 2.978e-02, -8.372e-02, 2.553e-02, 1.788e-01, -1.306e-02, -3.338e-02, 5.824e-03, 9.962e-03));

    r0 += mul(s0_2_2, M3x4(-1.023e-02, 1.709e-03, -1.148e-02, 8.545e-03, -9.436e-04, -1.005e-01, 2.045e-02, -1.188e-02, 2.601e-03, 1.018e-01, 1.548e-02, 6.398e-03));
    r1 += mul(s0_2_2, M3x4(4.131e-04, 1.567e-01, 8.772e-02, -4.603e-04, -2.784e-02, 3.080e-01, 1.666e-01, 1.247e-02, -9.368e-03, 4.113e-02, 1.053e-02, -6.552e-03));
    r2 += mul(s0_2_2, M3x4(9.972e-02, -3.257e-03, 4.352e-03, 1.871e-02, 9.180e-02, 4.687e-04, -7.627e-04, 4.785e-03, -1.848e-01, -2.062e-03, -7.350e-03, -4.168e-02));
    r3 += mul(s0_2_2, M3x4(6.599e-03, -9.527e-02, 2.067e-02, 5.786e-02, -6.712e-03, -3.371e-03, -3.337e-02, -1.854e-02, -5.940e-03, 1.115e-01, 5.519e-03, -3.865e-02));
    r4 += mul(s0_2_2, M3x4(-2.011e-02, -2.588e-02, -1.553e-02, 1.293e-01, -1.428e-01, -9.253e-02, 1.703e-02, 2.477e-01, -2.103e-02, 1.019e-01, -3.487e-03, 1.272e-01));
    r5 += mul(s0_2_2, M3x4(-8.335e-04, -8.765e-02, 3.406e-02, -9.178e-03, -9.444e-03, 6.080e-02, -3.284e-02, -1.818e-03, 1.007e-02, 2.961e-02, -1.296e-02, 1.727e-02));

    r0 += V4(4.601e-03, 1.374e-05, 2.911e-02, 5.045e-03);

    r0 = max(r0, 0.0);

    T0[uint3(gxy, tileParams.inputLayer)] = r0;

    r1 += V4(1.906e-01, 1.406e-02, -2.473e-02, -1.711e-04);

    r1 = max(r1, 0.0);

    T1[uint3(gxy, tileParams.inputLayer)] = r1;

    r2 += V4(3.670e-04, 1.667e-03, -1.476e-03, -2.538e-02);

    r2 = max(r2, 0.0);

    T2[uint3(gxy, tileParams.inputLayer)] = r2;

    r3 += V4(-9.699e-05, 1.416e-02, 1.732e-02, 4.374e-04);

    r3 = max(r3, 0.0);

    T3[uint3(gxy, tileParams.inputLayer)] = r3;

    r4 += V4(6.069e-03, -1.922e-04, -4.069e-03, 6.485e-03);

    r4 = max(r4, 0.0);

    T4[uint3(gxy, tileParams.inputLayer)] = r4;

    r5 += V4(7.883e-03, -2.966e-04, 2.954e-01, -2.987e-04);

    r5 = max(r5, 0.0);

    T5[uint3(gxy, tileParams.inputLayer)] = r5;
}