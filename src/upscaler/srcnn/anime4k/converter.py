#!/usr/bin/env python3
"""
Anime4K mpv shader → Vulkan GLSL compute shaders + model.json

Features:
- Detects multiple passes (//!DESC) and extracts hook() logic.
- Translates mpv texture macros (*_texOff, *_tex, *_pos, etc.).
- Handles tile‑mode (2D Arrays) and full‑frame (2D) textures.
- Resolves #define aliases.
- Correctly generates the depth‑to‑space (final shuffle) pass.
- Outputs model.json for the CuNNy‑compatible pipeline.
"""

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------


@dataclass
class PassInfo:
    desc: str
    bindings: List[str]  # texture names (1st = MAIN)
    save: Optional[str]
    width_expr: Optional[str]
    height_expr: Optional[str]
    components: int
    defines: List[str]
    prologue: str
    body: str
    when: Optional[str] = None

    @property
    def is_d2s(self) -> bool:
        return "Depth-to-Space" in self.desc


# ----------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------


class Anime4KParser:
    def __init__(self, content: str):
        self.passes: List[PassInfo] = []
        self._parse(content)

    def _parse(self, content: str) -> None:
        blocks = re.split(r"^//!DESC\s+", content, flags=re.MULTILINE)[1:]
        for block in blocks:
            lines = block.splitlines()
            desc = lines[0].strip()

            bindings, save, width_expr, height_expr, components, defines, when = (
                [],
                None,
                None,
                None,
                4,
                [],
                None,
            )

            hook_idx = None
            for i, line in enumerate(lines):
                if "vec4 hook()" in line:
                    hook_idx = i
                    break
            if hook_idx is None:
                continue

            for line in lines[1:hook_idx]:
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

            prologue_lines = [
                line
                for line in lines[1:hook_idx]
                if not line.strip().startswith("//!")
                and not line.strip().startswith("#define")
            ]
            prologue = "\n".join(prologue_lines).strip()

            brace_count = 0
            body_lines = []
            for line in lines[hook_idx:]:
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
                    prologue=prologue,
                    body=inner_body,
                    when=when,
                )
            )


# ----------------------------------------------------------------------
# Macro replacement engine
# ----------------------------------------------------------------------


def tex_name_safe(name: str) -> str:
    return name.replace(".", "_").replace("-", "_")


def replace_mpv_globals(code: str) -> str:
    code = code.replace("HOOKED_size", "vec2(ubo.in_width, ubo.in_height)")
    code = code.replace("HOOKED_pt", "vec2(ubo.in_dx, ubo.in_dy)")
    code = code.replace("HOOKED_pos", "pos")
    code = code.replace("MAIN_pos", "pos")
    return code


def replace_texture_macros(
    code: str, tex_mappings: Dict[str, str], point_sampler: str, array_mode: bool
) -> str:
    """
    Recursively replace mpv texture macros with GLSL texture() calls.
    When array_mode is True, textures are 2D arrays and coordinates
    become vec3(coord, tile.inputLayer).
    """
    for base, sampler in tex_mappings.items():
        # texOff
        prefix = f"{base}_texOff"
        pattern = re.compile(rf"{re.escape(prefix)}\s*\(")
        for match in pattern.finditer(code):
            start = match.end()
            depth = 1
            i = start
            while i < len(code) and depth > 0:
                if code[i] == "(":
                    depth += 1
                elif code[i] == ")":
                    depth -= 1
                i += 1
            if depth == 0:
                arg = code[start : i - 1].strip()
                coord2d = f"pos + ({arg}) * vec2(ubo.in_dx, ubo.in_dy)"
                if array_mode:
                    replacement = f"texture(sampler2DArray({sampler}, {point_sampler}), vec3({coord2d}, tile.inputLayer))"
                else:
                    replacement = (
                        f"texture(sampler2D({sampler}, {point_sampler}), {coord2d})"
                    )
                code = code[: match.start()] + replacement + code[i:]
                return replace_texture_macros(
                    code, tex_mappings, point_sampler, array_mode
                )

        # tex (without Off)
        prefix = f"{base}_tex"
        pattern = re.compile(rf"{re.escape(prefix)}\s*\(")
        for match in pattern.finditer(code):
            start = match.end()
            depth = 1
            i = start
            while i < len(code) and depth > 0:
                if code[i] == "(":
                    depth += 1
                elif code[i] == ")":
                    depth -= 1
                i += 1
            if depth == 0:
                arg = code[start : i - 1].strip()
                if array_mode:
                    replacement = f"texture(sampler2DArray({sampler}, {point_sampler}), vec3({arg}, tile.inputLayer))"
                else:
                    replacement = (
                        f"texture(sampler2D({sampler}, {point_sampler}), {arg})"
                    )
                code = code[: match.start()] + replacement + code[i:]
                return replace_texture_macros(
                    code, tex_mappings, point_sampler, array_mode
                )

        code = code.replace(f"{base}_pos", "pos")
        code = code.replace(f"{base}_pt", "vec2(ubo.in_dx, ubo.in_dy)")
        code = code.replace(f"{base}_size", "vec2(ubo.in_width, ubo.in_height)")
    return code


def resolve_defines_as_aliases(
    defines: List[str], tex_mappings: Dict[str, str]
) -> Tuple[List[str], Dict[str, str]]:
    new_defines = []
    extra_mappings = {}
    for d in defines:
        m = re.match(r"#define\s+(\w+)\s+(\w+)_tex\s*$", d)
        if m:
            alias_full = m.group(1)
            original_base = m.group(2)
            alias_base = alias_full[:-4] if alias_full.endswith("_tex") else alias_full
            if original_base in tex_mappings:
                extra_mappings[alias_base] = tex_mappings[original_base]
                continue
        new_defines.append(d)
    return new_defines, extra_mappings


# ----------------------------------------------------------------------
# Shader generation
# ----------------------------------------------------------------------


def common_header() -> str:
    return """#version 450

layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

layout(set = 0, binding = 0) uniform Constants {
    uint   in_width;
    uint   in_height;
    uint   out_width;
    uint   out_height;
    float  in_dx;
    float  in_dy;
    float  out_dx;
    float  out_dy;
} ubo;

layout(set = 0, binding = 1) uniform sampler pointSampler;
layout(set = 0, binding = 2) uniform sampler linearSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;
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


def generate_intermediate_pass(
    pinfo: PassInfo, out_name: str, is_final: bool, tile_mode: bool
) -> str:
    tex_mappings = {}
    bind_start = 3
    lines = []

    lines.append(common_header())
    if tile_mode:
        lines.append(push_constant_block())

    for idx, name in enumerate(pinfo.bindings):
        binding = bind_start + idx
        safe = tex_name_safe(name)
        if tile_mode:
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform texture2DArray tex_{safe};"
            )
        else:
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform texture2D tex_{safe};"
            )
        tex_mappings[name] = f"tex_{safe}"

    if "MAIN" not in tex_mappings and pinfo.bindings:
        tex_mappings["MAIN"] = tex_mappings[pinfo.bindings[0]]

    out_binding = bind_start + len(pinfo.bindings)
    out_safe = tex_name_safe(out_name) if out_name != "output" else "output"
    if tile_mode and not is_final:
        lines.append(
            f"layout(set = 0, binding = {out_binding}, rgba8) uniform image2DArray img_{out_safe};"
        )
    else:
        lines.append(
            f"layout(set = 0, binding = {out_binding}, rgba8) uniform image2D img_{out_safe};"
        )

    filtered_defines, extra_mappings = resolve_defines_as_aliases(
        pinfo.defines, tex_mappings
    )
    tex_mappings.update(extra_mappings)

    for d in filtered_defines:
        d_clean = replace_mpv_globals(d)
        d_clean = replace_texture_macros(
            d_clean, tex_mappings, "pointSampler", tile_mode
        )
        lines.append(d_clean)

    if pinfo.prologue:
        lines.append("")
        prologue = replace_mpv_globals(pinfo.prologue)
        prologue = replace_texture_macros(
            prologue, tex_mappings, "pointSampler", tile_mode
        )
        lines.append(prologue)

    lines.append("")
    lines.append("vec4 hook() {")
    body = replace_mpv_globals(pinfo.body)
    body = replace_texture_macros(body, tex_mappings, "pointSampler", tile_mode)
    lines.append(body)
    lines.append("}")

    lines.append("")
    lines.append("void main() {")
    if tile_mode:
        lines.append("    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append("    ivec2 valid_xy = interior_xy + ivec2(tile.margin);")
        lines.append("    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);")
    else:
        lines.append("    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append("    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);")

    lines.append("    vec4 result = hook();")
    if tile_mode:
        if is_final:
            lines.append(
                f"    imageStore(img_{out_safe}, ivec2(valid_xy) + ivec2(tile.dstOffset), result);"
            )
        else:
            lines.append(f"    imageStore(img_{out_safe}, ivec3(valid_xy, 0), result);")
    else:
        lines.append(f"    imageStore(img_{out_safe}, gxy, result);")
    lines.append("}")

    return "\n".join(lines)


def generate_d2s_pass(
    pinfo: PassInfo, out_name: str, is_final: bool, tile_mode: bool
) -> str:
    tex_mappings = {}
    bind_start = 3
    lines = []
    lines.append(common_header())
    if tile_mode:
        lines.append(push_constant_block())

    main_tex = None
    feature_bindings = []
    for name in pinfo.bindings:
        if name == "MAIN":
            main_tex = name
        else:
            feature_bindings.append(name)
    if not main_tex:
        raise ValueError("Depth‑to‑space pass missing MAIN binding")

    for idx, name in enumerate(feature_bindings):
        binding = bind_start + idx
        safe = tex_name_safe(name)
        if tile_mode:
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform texture2DArray tex_{safe};"
            )
        else:
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform texture2D tex_{safe};"
            )
        tex_mappings[name] = f"tex_{safe}"

    main_binding = bind_start + len(feature_bindings)
    safe_main = tex_name_safe(main_tex)
    lines.append(
        f"layout(set = 0, binding = {main_binding}) uniform texture2D tex_{safe_main};"
    )
    tex_mappings[main_tex] = f"tex_{safe_main}"

    out_binding = main_binding + 1
    lines.append(
        f"layout(set = 0, binding = {out_binding}, rgba8) uniform image2D img_output;"
    )

    filtered_defines, extra_mappings = resolve_defines_as_aliases(
        pinfo.defines, tex_mappings
    )
    tex_mappings.update(extra_mappings)
    for d in filtered_defines:
        d_clean = replace_mpv_globals(d)
        d_clean = replace_texture_macros(
            d_clean, tex_mappings, "pointSampler", False
        )  # MAIN is 2D
        lines.append(d_clean)
    if pinfo.prologue:
        lines.append("")
        prologue = replace_mpv_globals(pinfo.prologue)
        lines.append(prologue)

    lines.append("")
    lines.append("void main() {")
    if tile_mode:
        lines.append("    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append("    ivec2 base_out = (interior_xy * 2) + ivec2(tile.dstOffset);")
        lines.append(
            "    pos = (vec2(interior_xy + tile.margin) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
        )
        lines.append(
            "    vec2 full_opt = vec2(1.0 / tile.fullOutWidth, 1.0 / tile.fullOutHeight);"
        )
    else:
        lines.append("    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy) * 2;")
        lines.append(
            "    pos = ((vec2(gxy) / 2.0) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
        )
        lines.append("    vec2 full_opt = vec2(ubo.out_dx, ubo.out_dy);")

    lines.append("    vec2 f0 = fract(pos * vec2(ubo.in_width, ubo.in_height));")
    lines.append("    ivec2 i0 = ivec2(f0 * 2.0);")

    for idx, name in enumerate(feature_bindings):
        safe = tex_name_safe(name)
        if tile_mode:
            lines.append(
                f"    float c{idx} = texture(sampler2DArray(tex_{safe}, pointSampler), "
                f"vec3((vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos, tile.inputLayer))[i0.y * 2 + i0.x];"
            )
        else:
            lines.append(
                f"    float c{idx} = texture(sampler2D(tex_{safe}, pointSampler), "
                f"(vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos)[i0.y * 2 + i0.x];"
            )

    nf = len(feature_bindings)
    if nf == 1:
        lines.append("    float c1 = c0; float c2 = c0; float c3 = c0;")
    elif nf == 2:
        lines.append("    float c2 = c1; float c3 = c1;")
    elif nf == 3:
        lines.append("    float c3 = c2;")

    offsets = [(0, 0, "c0"), (1, 0, "c1"), (0, 1, "c2"), (1, 1, "c3")]
    for i, (ox, oy, cvar) in enumerate(offsets):
        if tile_mode:
            cond = (
                f"    if ((base_out.x + {ox}) < int(tile.dstOffset.x + tile.tileOutExtent.x) && "
                f"(base_out.y + {oy}) < int(tile.dstOffset.y + tile.tileOutExtent.y)) {{"
            )
            lines.append(cond)
            lines.append(
                f"        vec3 rgb_{i} = texture(sampler2D(tex_{safe_main}, linearSampler), "
                f"(vec2(base_out) + vec2({ox+0.5}, {oy+0.5})) * full_opt).rgb;"
            )
            lines.append(
                f"        imageStore(img_output, ivec2(base_out) + ivec2({ox}, {oy}), vec4(rgb_{i} + {cvar}, 1.0));"
            )
            lines.append("    }")
        else:
            lines.append(
                f"    vec3 rgb_{i} = texture(sampler2D(tex_{safe_main}, linearSampler), "
                f"(vec2(gxy) + vec2({ox+0.5}, {oy+0.5})) * full_opt).rgb;"
            )
            lines.append(
                f"    imageStore(img_output, gxy + ivec2({ox}, {oy}), vec4(rgb_{i} + {cvar}, 1.0));"
            )

    lines.append("}")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# model.json
# ----------------------------------------------------------------------


def build_model_json(passes: List[PassInfo]) -> Dict:
    srv_uav, sampler_list, prev_output, all_tex_names = [], [], "input", set()
    for idx, p in enumerate(passes):
        is_last = idx == len(passes) - 1
        inputs = [
            prev_output if name == "MAIN" else name.lower() for name in p.bindings
        ]
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
        "passes": len(passes),
        "num_textures": num_textures,
        "srv_uav": srv_uav,
        "samplers": sampler_list,
    }


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Anime4K mpv to Vulkan compute")
    parser.add_argument("shader_path", help="Path to .glsl file")
    parser.add_argument(
        "-t", "--tile", action="store_true", help="Generate tile‑mode variants"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.shader_path):
        print(f"Error: {args.shader_path} not found.")
        return

    with open(args.shader_path, "r", encoding="utf-8") as f:
        content = f.read()

    shader_parser = Anime4KParser(content)
    passes = shader_parser.passes
    if not passes:
        print("No passes found.")
        return

    shader_dir = os.path.dirname(args.shader_path)
    shader_name = os.path.splitext(os.path.basename(args.shader_path))[0]
    output_dir = os.path.join(shader_dir, shader_name)
    os.makedirs(output_dir, exist_ok=True)

    model = build_model_json(passes)
    model["name"] = shader_name
    with open(os.path.join(output_dir, "model.json"), "w") as f:
        json.dump(model, f, indent=2)

    tile_modes = [False, True] if args.tile else [False]
    for pass_idx, pinfo in enumerate(passes):
        is_last = pass_idx == len(passes) - 1
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
                code = generate_d2s_pass(pinfo, out_name, is_last, tile)
            else:
                code = generate_intermediate_pass(pinfo, out_name, is_last, tile)
            out_file = os.path.join(output_dir, f"Pass{pass_idx+1}{suffix}.glsl")
            with open(out_file, "w") as f:
                f.write(code)
            print(f"Written {out_file}")

    print(f"Done. Output in {output_dir}")


if __name__ == "__main__":
    main()
