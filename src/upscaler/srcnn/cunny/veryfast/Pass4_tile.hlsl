// CuNNy-veryfast-NVL - Pass 4 of 4 - https://github.com/funnyplanter/CuNNy
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

Texture2D<float4> INPUT : register(t0);
Texture2DArray<float4> T0 : register(t1);

[[vk::image_format("rgba8")]] RWTexture2D<float4> OUTPUT : register(u0);

SamplerState SP : register(s0);
SamplerState SL : register(s1);

#define L0(x, y) V4(O(T0, x, y))

[numthreads(8,8,1)]
void main(uint3 id : SV_DispatchThreadID)
{
    // -----------------------------------------------------------------------------
    //  Coordinate mapping:
    //    The dispatch covers a *single* expanded tile. The workgroup's (x,y)
    //    position `id.xy` corresponds to the low-resolution feature-map pixel
    //    inside the expanded region.
    //
    //    All sizes are in the *current* feature-map space (e.g., 40x40 for an
    //    expanded 32x32 tile with margin 4).
    // -----------------------------------------------------------------------------

    // (1) texel size of the **feature map** (NOT the full output image)
    float2 pt = float2(1.0 / in_width, 1.0 / in_height);

    // (2) texel size of the **full output image** - used when sampling the
    //     residual (INPUT) texture.
    float2 full_opt = float2(1.0 / tileParams.fullOutWidth,
                              1.0 / tileParams.fullOutHeight);

    // (3) Sampling position inside the feature map.
    //     tileParams.margin is the context margin in feature-map pixels.
    //     We offset by (margin, margin) to skip the padded border and land on
    //     the start of the **valid interior** region. The +0.5 ensures we sample
    //     pixel centres.
    float2 pos = (float2(tileParams.margin, tileParams.margin)
                   + float2(id.xy) + 0.5) * pt;

    // (4) Each workgroup thread (id.xy) produces a 2x2 block of output pixels.
    //     `gxy` is the top-left pixel (in upscaled output coordinates) of this
    //     thread's 2x2 quad, **relative to the tile's output region**.
    int2 gxy = int2(id.xy) * 2;

    // (5) Convert to **global** output coordinates by adding the tile's offset
    //     within the full upscaled frame.
    int2 globalOutXY = gxy + int2(tileParams.dstOffset);

    // (6) The tile may be clipped at the right or bottom edge of the canvas.
    //     `maxOut` is the exclusive upper bound for valid writes.
    int2 maxOut = int2(tileParams.dstOffset) + int2(tileParams.tileOutExtent);

    V4 s0_0_0, s0_0_1, s0_0_2, s0_1_0, s0_1_1, s0_1_2, s0_2_0, s0_2_1, s0_2_2;
    V4 r0 = 0.0;

    s0_0_0 = L0(-1.0, -1.0); s0_0_1 = L0(0.0, -1.0); s0_0_2 = L0(1.0, -1.0);
    s0_1_0 = L0(-1.0, 0.0); s0_1_1 = L0(0.0, 0.0); s0_1_2 = L0(1.0, 0.0);
    s0_2_0 = L0(-1.0, 1.0); s0_2_1 = L0(0.0, 1.0); s0_2_2 = L0(1.0, 1.0);

    r0 += mul(s0_0_0, M4(-8.466e-03, 8.423e-03, -1.341e-02, 8.400e-03, 4.039e-02, 1.243e-02, 3.053e-03, 2.236e-02, -9.043e-02, -4.385e-02, 1.099e-02, -4.289e-03, 2.522e-02, -1.250e-02, 1.207e-02, -6.843e-04));

    r0 += mul(s0_0_1, M4(2.039e-02, 2.086e-02, 7.522e-03, -3.699e-02, 1.700e-01, 1.294e-01, -2.264e-02, 4.882e-03, -2.046e-02, -6.568e-02, -3.262e-03, 1.502e-02, 4.650e-02, 7.837e-02, -1.792e-03, 6.150e-03));

    r0 += mul(s0_0_2, M4(1.362e-03, -4.553e-03, -5.095e-03, -1.786e-02, 1.193e-02, 6.665e-02, 9.653e-03, -1.117e-02, -6.344e-03, -1.285e-03, 6.389e-04, -1.254e-04, -2.810e-02, -9.490e-03, 2.764e-03, 1.519e-02));

    r0 += mul(s0_1_0, M4(6.046e-02, -5.579e-02, 4.086e-02, -2.594e-02, -2.222e-01, 6.714e-02, 1.642e-01, 1.251e-02, 2.124e-01, 2.800e-02, -2.271e-01, -1.145e-01, 1.470e-01, 2.230e-03, -2.017e-01, 2.901e-02));

    r0 += mul(s0_1_1, M4(-6.934e-01, 6.074e-01, -3.916e-01, 3.975e-01, -1.182e-01, -1.321e+00, 5.566e-01, 3.135e-02, -1.213e-01, 1.228e-01, -2.879e-02, -1.585e-01, 3.785e-01, 3.936e-01, -3.096e-01, -5.809e-01));

    r0 += mul(s0_1_2, M4(5.465e-02, 1.837e-02, 6.128e-03, -2.014e-02, 2.840e-02, 1.509e-01, -1.450e-02, 1.985e-01, 8.899e-03, -6.614e-02, -1.062e-02, -8.987e-03, -3.886e-02, 5.009e-02, 1.448e-02, 3.161e-02));

    r0 += mul(s0_2_0, M4(-1.064e-02, 1.822e-02, 1.365e-03, -1.041e-02, -6.714e-02, -4.944e-02, -1.042e-01, -3.769e-02, 2.007e-01, 2.301e-02, 5.776e-01, 1.213e-01, 3.036e-03, 1.199e-02, 1.776e-02, 4.685e-03));

    r0 += mul(s0_2_1, M4(5.676e-02, 9.702e-03, -2.397e-01, 2.686e-01, 1.734e-02, 2.728e-02, 8.738e-02, -3.604e-01, -1.548e-01, 9.495e-02, -2.007e-01, 3.917e-01, -3.189e-02, -2.570e-02, 6.957e-02, 7.940e-02));

    r0 += mul(s0_2_2, M4(-1.035e-02, -2.055e-04, 3.797e-02, 3.525e-02, 2.739e-02, 1.148e-02, -1.547e-03, 3.837e-02, -5.462e-03, -7.788e-02, 4.641e-03, -1.392e-01, 8.643e-03, -7.950e-03, -8.491e-03, -1.800e-02));

    r0 += V4(-5.434e-06, 1.445e-05, -9.457e-05, -3.159e-05);

    static const float3x3 RY = {0.299, 0.587, 0.114, -0.169, -0.331, 0.5, 0.5, -0.419, -0.081}, YR = {1, -0.00093, 1.401687, 1, -0.3437, -0.71417, 1, 1.77216, 0.00099};

    float2 opt = float2(GetOutputPt());
    float2 fpos = (float2(globalOutXY) + 0.5) * full_opt;
    float3 yuv;

    yuv = mul(RY, INPUT.SampleLevel(SL, fpos + float2(0.0, 0.0) * opt, 0).rgb);
    if (globalOutXY.x < maxOut.x && globalOutXY.y < maxOut.y)
        OUTPUT[globalOutXY + int2(0, 0)] = float4(mul(YR, float3(saturate(yuv.r + r0.x), yuv.yz)), 1.0);
    yuv = mul(RY, INPUT.SampleLevel(SL, fpos + float2(1.0, 0.0) * opt, 0).rgb);
    if (globalOutXY.x + 1 < maxOut.x && globalOutXY.y < maxOut.y)
        OUTPUT[globalOutXY + int2(1, 0)] = float4(mul(YR, float3(saturate(yuv.r + r0.y), yuv.yz)), 1.0);
    yuv = mul(RY, INPUT.SampleLevel(SL, fpos + float2(0.0, 1.0) * opt, 0).rgb);
    if (globalOutXY.x < maxOut.x && globalOutXY.y + 1 < maxOut.y)
        OUTPUT[globalOutXY + int2(0, 1)] = float4(mul(YR, float3(saturate(yuv.r + r0.z), yuv.yz)), 1.0);
    yuv = mul(RY, INPUT.SampleLevel(SL, fpos + float2(1.0, 1.0) * opt, 0).rgb);
    if (globalOutXY.x + 1 < maxOut.x && globalOutXY.y + 1 < maxOut.y)
        OUTPUT[globalOutXY + int2(1, 1)] = float4(mul(YR, float3(saturate(yuv.r + r0.w), yuv.yz)), 1.0);
}