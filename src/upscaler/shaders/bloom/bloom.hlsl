// =============================================================================
//  Subtle VN Bloom - Compute Shader
//  --------------------------------
//  Aesthetic glow for visual-novel backgrounds. Adds a soft, dreamy halo
//  around bright areas without blurring line art or text.
//
//  Features:
//    - Wide 4-tap blur at configurable radius (default 4 pixels).
//    - Brightness threshold - only pixels above the threshold contribute.
//    - Linear-light processing - consistent luminance blending.
//    - Screen blend - prevents oversaturation, preserves contrast.
//    - Clamped output - no overshoot beyond local min/max.
//
//  Workgroup size  16x16 threads.
//  Dispatch: same as other full-screen passes.
//
//  Tuning:
//      bloomStrength   = 0.0 (off)  -  0.15 (strong)
//      bloomThreshold  = 0.7 (wide glow)  -  0.95 (only pure white)
//      radius          = integer, 2 - 8  (blur extent)
//
//  Integration:
//    - Use a separate intermediate texture (in-place may hazard).
//    - Place after CAS sharpening, before film grain.
//
//  Adapted from Karis Average / Unreal Engine 4 Bloom for linux-rt-upscaler.
// =============================================================================

Texture2D<float4> InputTex  : register(t0);
[[vk::image_format("rgba8")]]
RWTexture2D<float4> OutputTex : register(u0);

cbuffer Constants : register(b0)
{
    float bloomStrength;        // 0.0 - 0.15 (for VN)
    uint  dstWidth;
    uint  dstHeight;
    float bloomThreshold;       // 0.8 recommended
    uint  radius;               // default 4
};

// -----------------------------------------------------------------------------
//  Load a pixel, convert to approximate linear light
// -----------------------------------------------------------------------------
float3 LoadLinear(int2 coord)
{
    coord = clamp(coord, int2(0, 0), int2(dstWidth - 1, dstHeight - 1));
    float3 c = InputTex.Load(int3(coord, 0)).rgb;
    return c * c;
}

[numthreads(16, 16, 1)]
void main(uint3 dtid : SV_DispatchThreadID)
{
    uint2 pos = dtid.xy;
    if (pos.x >= dstWidth || pos.y >= dstHeight)
        return;

    float3 center = LoadLinear(pos);

    // ---- 1. Compute blurred glow (4 taps at `radius` distance) --------------
    int r = int(radius);
    float3 s1 = LoadLinear(pos + int2(-r, -r));
    float3 s2 = LoadLinear(pos + int2( r, -r));
    float3 s3 = LoadLinear(pos + int2(-r,  r));
    float3 s4 = LoadLinear(pos + int2( r,  r));
    float3 blurred = (s1 + s2 + s3 + s4) * 0.25;

    // ---- 2. Threshold softness ----------------------------------------------
    //  Pixels brighter than `bloomThreshold` contribute fully;
    //  below threshold they fade out gradually.
    float  brightness  = max(blurred.r, max(blurred.g, blurred.b));
    float  softFactor  = saturate((brightness - bloomThreshold) / (1.0 - bloomThreshold + 1e-5));

    float3 glow = blurred * softFactor * bloomStrength;

    // ---- 3. Screen blend (linear light) -------------------------------------
    float3 result = 1.0 - (1.0 - center) * (1.0 - glow);

    // ---- 4. Clamp to local extents (prevents hue shift) --------------------
    float3 minN = min(center, min(min(s1, s2), min(s3, s4)));
    float3 maxN = max(center, max(max(s1, s2), max(s3, s4)));
    result = clamp(result, minN, maxN);

    // ---- 5. Return to gamma space and store ---------------------------------
    OutputTex[pos] = float4(sqrt(max(result, 0.0)), 1.0);
}