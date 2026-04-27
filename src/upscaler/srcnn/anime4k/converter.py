#!/usr/bin/env python3
"""
Convert an Anime4K mpv shader to Vulkan GLSL compute shaders and model.json.

Features:
- Parses multi‑pass shaders with //!DESC, //!BIND, //!SAVE, etc.
- Generates one .glsl compute shader per pass (full‑frame).
- Optionally generates tile‑mode variants (push constants + array textures).
- Robust handling of missing //!SAVE (implicit MAIN writes).
- Detects depth‑to‑space passes by description and uses a specialised generator.
- Produces a model.json exactly as the CuNNy converter.

Usage:
    python converter.py <shader.glsl> [--tile]
"""

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------


@dataclass
class Config:
    tile: bool = False
    local_size: Tuple[int, int, int] = (8, 8, 1)


# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------


@dataclass
class PassInfo:
    desc: str
    bindings: List[str]
    save: Optional[str]  # None if no //!SAVE directive
    width_expr: Optional[str]
    height_expr: Optional[str]
    components: int
    defines: List[str]
    body: str
    when: Optional[str] = None

    @property
    def is_d2s(self) -> bool:
        """True if this pass performs depth‑to‑space (pixel shuffle)."""
        return "Depth-to-Space" in self.desc


# ----------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------


class Anime4KParser:
    def __init__(self, content: str):
        self.content = content
        self.passes: List[PassInfo] = []
        self._parse()

    def _parse(self) -> None:
        blocks = re.split(r"^//!DESC\s+", self.content, flags=re.MULTILINE)[1:]
        for block in blocks:
            lines = block.splitlines()
            desc = lines[0].strip()

            bindings = []
            save = None
            width_expr = None
            height_expr = None
            components = 4
            defines = []
            when = None

            body_start = 0
            for i, line in enumerate(lines):
                s = line.strip()
                if s.startswith("//!BIND"):
                    bindings.append(s.split(maxsplit=1)[1].strip())
                elif s.startswith("//!SAVE"):
                    save = s.split(maxsplit=1)[1].strip()
                elif s.startswith("//!WIDTH"):
                    width_expr = s[len("//!WIDTH") :].strip()
                elif s.startswith("//!HEIGHT"):
                    height_expr = s[len("//!HEIGHT") :].strip()
                elif s.startswith("//!COMPONENTS"):
                    components = int(s.split()[-1])
                elif s.startswith("//!WHEN"):
                    when = s[len("//!WHEN") :].strip()
                elif s.startswith("#define"):
                    defines.append(s)
                elif "vec4 hook()" in s:
                    body_start = i
                    break

            # Extract hook body
            brace_count = 0
            body_lines = []
            for line in lines[body_start:]:
                brace_count += line.count("{")
                brace_count -= line.count("}")
                body_lines.append(line)
                if brace_count == 0:
                    break
            full_body = "\n".join(body_lines)
            inner_body = full_body.split("{", 1)[1].rsplit("}", 1)[0].strip()

            self.passes.append(
                PassInfo(
                    desc=desc,
                    bindings=bindings,
                    save=save,
                    width_expr=width_expr,
                    height_expr=height_expr,
                    components=components,
                    defines=defines,
                    body=inner_body,
                    when=when,
                )
            )


# ----------------------------------------------------------------------
# GLSL generation helpers
# ----------------------------------------------------------------------


def tex_name_safe(name: str) -> str:
    return name.replace(".", "_").replace("-", "_")


def replace_sampling_calls(
    body: str, tex_mappings: Dict[str, str], array_mode: bool, point_sampler: str
) -> str:
    """Replace mpv sampling macros with GLSL texture calls."""
    # texOff(vec2(x,y))
    for orig, sampler in tex_mappings.items():
        macro = f"{orig}_texOff"
        if array_mode:
            repl = f"texture(sampler2DArray({sampler}, {point_sampler}), vec3(pos + vec2(\\1, \\2) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))"
        else:
            repl = f"texture(sampler2D({sampler}, {point_sampler}), pos + vec2(\\1, \\2) * vec2(ubo.in_dx, ubo.in_dy))"
        body = re.sub(
            rf"{re.escape(macro)}\s*\(\s*vec2\s*\(\s*([^)]+)\s*,\s*([^)]+)\s*\)\s*\)",
            repl,
            body,
        )

    # tex(coord)
    for orig, sampler in tex_mappings.items():
        macro = f"{orig}_tex"
        if array_mode:
            repl = f"texture(sampler2DArray({sampler}, {point_sampler}), vec3(\\1, tile.inputLayer))"
        else:
            repl = f"texture(sampler2D({sampler}, {point_sampler}), \\1)"
        body = re.sub(rf"{re.escape(macro)}\s*\(\s*([^)]+)\s*\)", repl, body)

    # built-in macros
    for orig in tex_mappings:
        body = body.replace(f"{orig}_pos", "pos")
        body = body.replace(f"{orig}_pt", "vec2(ubo.in_dx, ubo.in_dy)")
        body = body.replace(f"{orig}_size", "vec2(ubo.in_width, ubo.in_height)")

    return body


def common_header() -> str:
    return """#version 450

layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

layout(set = 0, binding = 0) uniform Constants {
    float in_width;
    float in_height;
    float out_width;
    float out_height;
    float in_dx;
    float in_dy;
    float out_dx;
    float out_dy;
} ubo;

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;
"""


def push_constant_block() -> str:
    return """layout(push_constant) uniform TileParams {
    uint inputLayer;
    uvec2 dstOffset;
    uint fullOutWidth;
    uint fullOutHeight;
    uint margin;
    uvec2 tileOutExtent;
} tile;
"""


def generate_intermediate_pass(pinfo: PassInfo, out_name: str, tile_mode: bool) -> str:
    """Regular convolution / utility pass (may also be the final pass if not D2S)."""
    tex_mappings = {}
    bind_start = 3
    lines = []

    lines.append(common_header())
    if tile_mode:
        lines.append(push_constant_block())

    # Input textures
    for idx, name in enumerate(pinfo.bindings):
        binding = bind_start + idx
        safe = tex_name_safe(name)
        stype = "sampler2DArray" if tile_mode else "sampler2D"
        lines.append(
            f"layout(set = 0, binding = {binding}) uniform {stype} tex_{safe};"
        )
        tex_mappings[name] = f"tex_{safe}"

    # Output image: for tile mode, intermediate passes use array; final output uses 2D
    out_binding = bind_start + len(pinfo.bindings)
    out_safe = tex_name_safe(out_name)
    if tile_mode and out_name != "output":
        stype_out = "image2DArray"
    else:
        stype_out = "image2D"
    lines.append(
        f"layout(set = 0, binding = {out_binding}, rgba8) uniform {stype_out} img_{out_safe};"
    )

    lines.append("")
    for d in pinfo.defines:
        lines.append(d)
    lines.append("")

    # Main function
    lines.append("void main() {")
    if tile_mode:
        lines.append("    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append("    ivec2 valid_xy = interior_xy + ivec2(tile.margin);")
        lines.append(
            "    vec2 pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
        )
    else:
        lines.append("    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append("    vec2 pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);")

    body = replace_sampling_calls(pinfo.body, tex_mappings, tile_mode, "pointSampler")
    # Remove any 'return result;' – we will write to the image directly.
    body = re.sub(r"\breturn\s+result\s*;\s*$", "", body, flags=re.MULTILINE).rstrip()
    lines.append(body)

    if tile_mode:
        lines.append(f"    imageStore(img_{out_safe}, ivec3(valid_xy, 0), result);")
    else:
        lines.append(f"    imageStore(img_{out_safe}, gxy, result);")

    lines.append("}")
    return "\n".join(lines)


def generate_d2s_pass(pinfo: PassInfo, out_name: str, tile_mode: bool) -> str:
    """Specialised generator for depth‑to‑space (pixel shuffle) + residual add."""
    tex_mappings = {}
    bind_start = 3
    lines = []

    lines.append(common_header())
    if tile_mode:
        lines.append(push_constant_block())

    # Separate MAIN (original image) from feature maps
    main_tex = None
    feature_bindings = []
    for name in pinfo.bindings:
        if name == "MAIN":
            main_tex = name
        else:
            feature_bindings.append(name)

    if not main_tex:
        raise ValueError("Depth‑to‑space pass missing MAIN binding (original image)")

    # Feature samplers
    for idx, name in enumerate(feature_bindings):
        binding = bind_start + idx
        safe = tex_name_safe(name)
        stype = "sampler2DArray" if tile_mode else "sampler2D"
        lines.append(
            f"layout(set = 0, binding = {binding}) uniform {stype} tex_{safe};"
        )
        tex_mappings[name] = f"tex_{safe}"

    # MAIN (original) always 2D (full frame even in tile mode)
    main_binding = bind_start + len(feature_bindings)
    safe_main = tex_name_safe(main_tex)
    lines.append(
        f"layout(set = 0, binding = {main_binding}) uniform sampler2D tex_{safe_main};"
    )
    tex_mappings[main_tex] = f"tex_{safe_main}"

    # Output image (always 2D)
    out_binding = main_binding + 1
    lines.append(
        f"layout(set = 0, binding = {out_binding}, rgba8) uniform image2D img_output;"
    )

    lines.append("")
    for d in pinfo.defines:
        lines.append(d)
    lines.append("")

    lines.append("void main() {")
    if tile_mode:
        lines.append("    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append("    ivec2 base_out = (interior_xy * 2) + ivec2(tile.dstOffset);")
        lines.append(
            "    vec2 pos = (vec2(interior_xy + tile.margin) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
        )
        lines.append(
            "    vec2 full_opt = vec2(1.0 / tile.fullOutWidth, 1.0 / tile.fullOutHeight);"
        )
    else:
        lines.append("    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy) * 2;")
        lines.append(
            "    vec2 pos = ((vec2(gxy) / 2.0) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
        )
        lines.append("    vec2 full_opt = vec2(ubo.out_dx, ubo.out_dy);")

    # Depth‑to‑Space shuffle
    lines.append("    vec2 f0 = fract(pos * vec2(ubo.in_width, ubo.in_height));")
    lines.append("    ivec2 i0 = ivec2(f0 * 2.0);")
    for idx, name in enumerate(feature_bindings):
        safe = tex_name_safe(name)
        if tile_mode:
            lines.append(
                f"    float c{idx} = texture(sampler2DArray(tex_{safe}, pointSampler), vec3((vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos, tile.inputLayer))[i0.y * 2 + i0.x];"
            )
        else:
            lines.append(
                f"    float c{idx} = texture(sampler2D(tex_{safe}, pointSampler), (vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos)[i0.y * 2 + i0.x];"
            )

    # Replicate channels if fewer than 4 feature maps
    nf = len(feature_bindings)
    if nf == 1:
        lines.append("    float c1 = c0; float c2 = c0; float c3 = c0;")
    elif nf == 2:
        lines.append("    float c2 = c1; float c3 = c1;")
    elif nf == 3:
        lines.append("    float c3 = c2;")
    # if nf >= 4 we already have c0..c3

    # Write 2x2 block
    offsets = [(0, 0, 0), (1, 0, 1), (0, 1, 2), (1, 1, 3)]
    for ox, oy, ci in offsets:
        if tile_mode:
            lines.append(
                f"    if ((base_out.x + {ox}) < int(tile.dstOffset.x + tile.tileOutExtent.x) && (base_out.y + {oy}) < int(tile.dstOffset.y + tile.tileOutExtent.y)) {{"
            )
            lines.append(
                f"        vec3 rgb = texture(sampler2D(tex_{safe_main}, linearSampler), (vec2(base_out) + vec2({ox+0.5}, {oy+0.5})) * full_opt).rgb;"
            )
            lines.append(
                f"        imageStore(img_output, ivec2(base_out) + ivec2({ox}, {oy}), vec4(rgb + c{ci}, 1.0));"
            )
            lines.append("    }")
        else:
            lines.append(
                f"    vec3 rgb = texture(sampler2D(tex_{safe_main}, linearSampler), (vec2(gxy) + vec2({ox+0.5}, {oy+0.5})) * full_opt).rgb;"
            )
            lines.append(
                f"    imageStore(img_output, gxy + ivec2({ox}, {oy}), vec4(rgb + c{ci}, 1.0));"
            )

    lines.append("}")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# Model.json builder (with implicit MAIN handling)
# ----------------------------------------------------------------------


def build_model_json(passes: List[PassInfo]) -> Dict:
    """
    Build the model.json descriptor, resolving implicit MAIN flows.
    """
    srv_uav = []
    sampler_list = []
    prev_output = "input"
    all_tex_names = set()

    total_passes = len(passes)
    for idx, p in enumerate(passes):
        is_last = idx == total_passes - 1

        # Replace any "MAIN" binding with the previous output name
        inputs = [
            prev_output if name == "MAIN" else name.lower() for name in p.bindings
        ]

        # Determine output name
        if p.save is None:
            out_name = f"pass_{idx}_out"
            if is_last:
                out_name = "output"
        elif p.save == "MAIN" and is_last:
            out_name = "output"
        else:
            out_name = p.save.lower()

        srv_uav.append([inputs, [out_name]])
        sampler_list.append(["point", "linear"] if is_last else ["point"])

        all_tex_names.update(inputs)
        all_tex_names.add(out_name)
        prev_output = out_name

    num_textures = len(all_tex_names - {"input", "output"})

    return {
        "name": None,
        "passes": total_passes,
        "num_textures": num_textures,
        "srv_uav": srv_uav,
        "samplers": sampler_list,
    }


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Anime4K mpv to Vulkan compute converter."
    )
    parser.add_argument("shader_path", help="Path to .glsl shader file")
    parser.add_argument(
        "-t", "--tile", action="store_true", help="Generate tile‑mode variants"
    )
    args = parser.parse_args()

    shader_path = args.shader_path
    if not os.path.isfile(shader_path):
        print(f"Error: {shader_path} not found.")
        return

    with open(shader_path, "r", encoding="utf-8") as f:
        content = f.read()

    shader_parser = Anime4KParser(content)
    passes = shader_parser.passes
    if not passes:
        print("No passes found.")
        return

    # Prepare output directory
    shader_dir = os.path.dirname(shader_path)
    shader_name = os.path.splitext(os.path.basename(shader_path))[0]
    output_dir = os.path.join(shader_dir, shader_name)
    os.makedirs(output_dir, exist_ok=True)

    # Build model.json
    model = build_model_json(passes)
    model["name"] = shader_name
    with open(os.path.join(output_dir, "model.json"), "w") as f:
        json.dump(model, f, indent=2)

    # Generate shaders
    tile_modes = [False, True] if args.tile else [False]
    total_passes = len(passes)

    for pass_idx, pinfo in enumerate(passes):
        is_last = pass_idx == total_passes - 1

        # Determine output name (consistent with build_model_json)
        if pinfo.save is None:
            out_name = f"pass_{pass_idx}_out"
            if is_last:
                out_name = "output"
        elif pinfo.save == "MAIN" and is_last:
            out_name = "output"
        else:
            out_name = pinfo.save

        for tile in tile_modes:
            suffix = "_tile" if tile else ""

            if pinfo.is_d2s:
                # Only genuine depth‑to‑space passes use the specialised generator
                code = generate_d2s_pass(pinfo, out_name, tile)
            else:
                # All other passes (including the final pass for non‑D2S shaders)
                code = generate_intermediate_pass(pinfo, out_name, tile)

            out_file = os.path.join(output_dir, f"Pass{pass_idx+1}{suffix}.glsl")
            with open(out_file, "w") as f:
                f.write(code)
            print(f"Written {out_file}")

    print(f"Done. Output in {output_dir}")


if __name__ == "__main__":
    main()
