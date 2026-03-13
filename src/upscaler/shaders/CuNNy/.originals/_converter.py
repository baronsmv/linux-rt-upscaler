#!/usr/bin/env python3

"""
A fast implementation of a parser.
As is, it's only used to divide 8x32 into 10 passes.
"""

import json
import os
import re


def convert_magpie_to_srcnn(original_shader_path, output_dir):
    with open(original_shader_path, "r") as f:
        shader = f.read()

    # Split into passes using the //!PASS markers
    pass_pattern = (
        r"//!PASS (\d+)\n.*?void Pass\d+\(uint2 blockStart, uint3 tid\) \{(.*?)\n\}"
    )
    passes = re.findall(pass_pattern, shader, re.DOTALL)

    # Template for the common header
    common_header = """cbuffer Constants : register(b0) {{
    uint in_width;
    uint in_height;
    uint out_width;
    uint out_height;
    float in_dx;
    float in_dy;
    float out_dx;
    float out_dy;
}};

SamplerState SP : register(s0);
SamplerState SL : register(s1);

float2 GetInputPt() {{ return float2(in_dx, in_dy); }}
float2 GetOutputPt() {{ return float2(out_dx, out_dy); }}
uint2 GetInputSize() {{ return uint2(in_width, in_height); }}
uint2 GetOutputSize() {{ return uint2(out_width, out_height); }}

#define O(t, x, y) t.SampleLevel(SP, pos + float2(x, y) * pt, 0)
#define V4 min16float4
#define M4 min16float4x4
#define V3 min16float3
#define M3x4 min16float3x4
"""

    os.makedirs(output_dir, exist_ok=True)

    # Prepare model.json data
    srv_uav = []
    samplers = []

    # Pass 1
    srv_uav.append([["input"], [f"t{i}" for i in range(8)]])
    samplers.append(["point"])

    # Passes 2-9 alternate
    for i in range(2, 10):
        if i % 2 == 0:  # even passes: input T0..T7, output T8..T15
            srv = [f"t{j}" for j in range(8)]
            uav = [f"t{j}" for j in range(8, 16)]
        else:  # odd passes: input T8..T15, output T0..T7
            srv = [f"t{j}" for j in range(8, 16)]
            uav = [f"t{j}" for j in range(8)]
        srv_uav.append([srv, uav])
        samplers.append(["point"])

    # Pass 10
    srv_uav.append([["input"] + [f"t{i}" for i in range(8)], ["output"]])
    samplers.append(["point", "linear"])

    model_json = {
        "passes": 10,
        "num_textures": 16,
        "srv_uav": srv_uav,
        "samplers": samplers,
    }
    with open(os.path.join(output_dir, "model.json"), "w") as f:
        json.dump(model_json, f, indent=2)

    # Process each pass
    for idx, (pass_num, body) in enumerate(passes, 1):
        pass_num = int(pass_num)
        body = body.strip()

        # Determine input and output textures for this pass (for register declarations)
        srv_list = srv_uav[pass_num - 1][0]
        uav_list = srv_uav[pass_num - 1][1]

        # Generate texture declarations
        tex_decl = ""
        for i, name in enumerate(srv_list):
            if name == "input":
                tex_decl += f"Texture2D<float4> INPUT : register(t{i});\n"
            else:
                tex_decl += f"Texture2D<float4> T{name[1:]} : register(t{i});\n"  # name like "t0"
        for i, name in enumerate(uav_list):
            if name == "output":
                tex_decl += f"RWTexture2D<float4> OUTPUT : register(u{i});\n"
            else:
                tex_decl += f"RWTexture2D<float4> T{name[1:]} : register(u{i});\n"

        # Replace function signature and gxy calculation
        # For passes 1-9, gxy = id.xy
        # For pass 10, gxy = id.xy * 2
        if pass_num == 10:
            entry = """[numthreads(8,8,1)]
void CSMain(uint3 id : SV_DispatchThreadID)
{
    float2 pt = float2(GetInputPt());
    float2 opt = float2(GetOutputPt());
    uint2 gxy = id.xy * 2;
"""
            # In pass 10, they also use opt for the final sample
        else:
            entry = """[numthreads(8,8,1)]
void CSMain(uint3 id : SV_DispatchThreadID)
{
    float2 pt = float2(GetInputPt());
    uint2 gxy = id.xy;
"""
        full_shader = common_header + tex_decl + "\n" + entry + body + "\n}"

        # Write to file
        out_path = os.path.join(output_dir, f"Pass{pass_num}.hlsl")
        with open(out_path, "w") as f:
            f.write(full_shader)


if __name__ == "__main__":
    convert_magpie_to_srcnn("original.hlsl", "CuNNy-0008672")
