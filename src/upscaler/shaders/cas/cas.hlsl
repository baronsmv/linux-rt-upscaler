// =============================================================================
//  Contrast Adaptive Sharpening (CAS) - Compute Shader
//  ----------------------------------------------------
//  Single-pass, full-screen sharpening for post-processing.
//
//  Features:
//    - Adaptive sharpening kernel - strength scales with local contrast.
//    - Clamped output - no over/undershoot beyond local min/max.
//    - Efficient 3x3 sampling using point loads (8 neighbours + centre).
//    - Configurable sharpening strength via constant buffer.
//    - Works on RGBA8 textures (input = output UAV).
//    - 16x16 thread groups for high occupancy.
//
//  Dispatch:
//    groupsX = ceil(dstWidth  / 16)
//    groupsY = ceil(dstHeight / 16)
//
//  Tuning:
//    - 0.0  = pass-through (no sharpening)
//    - 0.2  = subtle edge enhancement
//    - 0.4  = moderate (good for text / line art)
//    - 0.6+ = aggressive (risk of ringing)
//
//  Based on AMD FidelityFX CAS algorithm.
//  Optimised for linux-rt-upscaler pipeline.
// =============================================================================

Texture2D<float4> InputTex  : register(t0);          // screen texture (same as output)
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);        // UAV target (can be same as InputTex)

cbuffer Constants : register(b0)
{
    float sharpeningStrength;   // 0.0 - 1.0 (disable -> full)
    uint  dstWidth;             // output texture width
    uint  dstHeight;            // output texture height
    // pad to 16 bytes (Vulkan alignment)
    uint  _pad0;
};

// Helper to load a pixel with clamping to image borders.
float3 LoadPixel(int2 coord)
{
    // Clamp to valid range - prevents out-of-bounds sampling at edges.
    coord = clamp(coord, int2(0, 0), int2(dstWidth - 1, dstHeight - 1));
    return InputTex.Load(int3(coord, 0)).rgb;
}

// =============================================================================
//  CAS main kernel
// =============================================================================
[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 pos = dtid.xy;
    if (pos.x >= dstWidth || pos.y >= dstHeight)
        return;

    // Load the 3x3 neighbourhood.
    float3 c  = LoadPixel(int2(pos.x,   pos.y));         // centre
    float3 n  = LoadPixel(int2(pos.x,   pos.y - 1));     // north
    float3 s  = LoadPixel(int2(pos.x,   pos.y + 1));     // south
    float3 e  = LoadPixel(int2(pos.x + 1, pos.y));       // east
    float3 w  = LoadPixel(int2(pos.x - 1, pos.y));       // west
    float3 ne = LoadPixel(int2(pos.x + 1, pos.y - 1));   // north-east
    float3 nw = LoadPixel(int2(pos.x - 1, pos.y - 1));   // north-west
    float3 se = LoadPixel(int2(pos.x + 1, pos.y + 1));   // south-east
    float3 sw = LoadPixel(int2(pos.x - 1, pos.y + 1));   // south-west

    // Local min/max for clamping - preserves edges, avoids overshoot.
    float3 minRGB = min( c, min( min(min(n, s), min(e, w)),
                                 min(min(ne, nw), min(se, sw)) ) );
    float3 maxRGB = max( c, max( max(max(n, s), max(e, w)),
                                 max(max(ne, nw), max(se, sw)) ) );

    // Contrast as max difference between surrounding pixels.
    // This helps sharpening only in areas with real detail.
    float3 contrast = max( max(abs(n - s), abs(e - w)),
                           max(abs(ne - sw), abs(nw - se)) );

    // Compute the sharpened pixel using the AMD CAS formula:
    //   sharpen = c + strength * ((c*5) - (n+s+e+w))
    // The 5-tap Laplacian filter gives a high-boost sharpening effect.
    float3 sharpened = c + sharpeningStrength * (5.0 * c - (n + s + e + w));

    // Adapt strength locally based on contrast - reduces sharpening
    // in flat areas, preserving smooth gradients.
    // contrast * 2.0 maps high contrast to full strength.
    float3 localStrength = saturate(contrast * 2.0);
    sharpened = lerp(c, sharpened, localStrength);

    // Clamp to local min/max to prevent ringing / haloing.
    sharpened = clamp(sharpened, minRGB, maxRGB);

    OutputTex[pos] = float4(sharpened, 1.0);
}