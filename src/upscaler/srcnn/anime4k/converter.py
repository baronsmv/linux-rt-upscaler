#!/usr/bin/env python3
"""
Anime4K mpv shader -> Vulkan GLSL compute shaders + model.json

This script converts a traditional mpv-compatible Anime4K GLSL file
(containing //!DESC, //!BIND, //!SAVE, ...) into a set of GLSL compute
shaders with explicit Vulkan bindings and a corresponding model.json
that the SRCNN pipeline can use.

Features:
  - Parses multi-pass mpv shaders (//!DESC).
  - Translates mpv-specific texture macros (*_texOff, *_tex, *_pos, ...)
    into standard Vulkan GLSL texture() calls.
  - Supports tile-mode (2D array textures + push-constant block) and
    full-frame (plain 2D textures).
  - Resolves #define aliases and removes unused helpers.
  - Generates proper depth-to-space (final shuffle) passes.
  - Outputs model.json matching the CuNNy-compatible pipeline.
  - Uses binding numbers compatible with the SRCNN framework:
      • Constant buffer    -> binding 0
      • Sampled textures   -> binding 1024 + offset
      • Storage image      -> binding 2048
      • Samplers           -> binding 3072 (point), 3073 (linear)
"""

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ----------------------------------------------------------------------
# Binding offsets as required by the SRCNN Vulkan pipeline
# ----------------------------------------------------------------------
CB_BINDING = 0
SRV_BINDING_START = 1024
UAV_BINDING = 2048
SAMPLER_POINT_BINDING = 3072
SAMPLER_LINEAR_BINDING = 3073


# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass
class PassInfo:
    """All information extracted from one mpv shader pass."""

    desc: str  # description from //!DESC
    bindings: List[str] = field(
        default_factory=list
    )  # texture names in order (first = MAIN)
    save: Optional[str] = None  # output texture name (//!SAVE)
    width_expr: Optional[str] = None  # optional //!WIDTH expression
    height_expr: Optional[str] = None
    components: int = 4  # number of channels (always 4)
    defines: List[str] = field(default_factory=list)  # #define lines (macro aliases)
    prologue: str = ""  # GLSL code before the hook() function
    body: str = ""  # contents of vec4 hook() { ... }
    when: Optional[str] = None  # unused //!WHEN clause

    @property
    def is_d2s(self) -> bool:
        """Returns True if this is the depth-to-space (final shuffle) pass."""
        return "Depth-to-Space" in self.desc


# ----------------------------------------------------------------------
# Parser: extract passes from the original mpv shader
# ----------------------------------------------------------------------
class Anime4KParser:
    """Splits the input mpv shader into individual passes."""

    def __init__(self, content: str):
        self.passes: List[PassInfo] = []
        self.license: str = ""
        self._parse(content)

    def _parse(self, content: str) -> None:
        first_desc = content.find("//!DESC")
        if first_desc != -1:
            self.license = self._extract_license(content[:first_desc])

        # Split on //!DESC to obtain blocks for each pass
        blocks = re.split(r"^//!DESC\s+", content, flags=re.MULTILINE)[1:]
        for block in blocks:
            if "vec4 hook()" not in block:
                continue
            pinfo = self._parse_pass_block(block)
            if pinfo:
                self.passes.append(pinfo)

    @staticmethod
    def _extract_license(head: str) -> str:
        """Extract a comment-style license block from the file header."""
        lines = []
        for line in head.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("//"):
                stripped = stripped[2:].strip()
            lines.append(stripped)
        return "\n".join(lines)

    def _parse_pass_block(self, block: str) -> Optional[PassInfo]:
        lines = block.splitlines()
        desc = lines[0].strip()

        bindings = []
        save = None
        width_expr = None
        height_expr = None
        components = 4
        defines = []
        when = None

        hook_idx = None
        for i, line in enumerate(lines):
            if "vec4 hook()" in line:
                hook_idx = i
                break
        if hook_idx is None:
            return None

        # Parse metadata lines before hook()
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

        # Prologue = any non-metadata lines before hook()
        prologue_lines = [
            line
            for line in lines[1:hook_idx]
            if not line.strip().startswith("//!")
            and not line.strip().startswith("#define")
        ]
        prologue = "\n".join(prologue_lines).strip()

        # Extract body of hook() function
        body = self._extract_function_body(lines, hook_idx)

        return PassInfo(
            desc=desc,
            bindings=bindings,
            save=save,
            width_expr=width_expr,
            height_expr=height_expr,
            components=components,
            defines=defines,
            prologue=prologue,
            body=body,
            when=when,
        )

    @staticmethod
    def _extract_function_body(lines: List[str], start: int) -> str:
        """Extract everything inside the first { ... } after a function signature."""
        brace_count = 0
        body_lines = []
        for line in lines[start:]:
            brace_count += line.count("{")
            brace_count -= line.count("}")
            body_lines.append(line)
            if brace_count == 0:
                break
        full = "\n".join(body_lines)
        inner = full.split("{", 1)[1].rsplit("}", 1)[0].strip()
        return inner


# ----------------------------------------------------------------------
# Macro translation engine
# ----------------------------------------------------------------------
class MacroTranslator:
    """
    Translates mpv-specific texture macros into standard Vulkan GLSL
    ``texture()`` calls. Supports both 2D and 2D-array modes.
    """

    @staticmethod
    def safe_tex_name(name: str) -> str:
        return name.replace(".", "_").replace("-", "_")

    @staticmethod
    def replace_mpv_globals(code: str) -> str:
        """Replace mpv built-in variables with their Vulkan counterparts."""
        code = code.replace(
            "HOOKED_size", "vec2(float(ubo.in_width), float(ubo.in_height))"
        )
        code = code.replace("HOOKED_pt", "vec2(ubo.in_dx, ubo.in_dy)")
        code = code.replace("HOOKED_pos", "pos")
        code = code.replace("MAIN_pos", "pos")
        return code

    @staticmethod
    def replace_texture_macros(
        code: str,
        tex_mappings: Dict[str, str],
        point_sampler: str,
        array_mode: bool,
    ) -> str:
        """
        Recursively replace ``*_texOff(...)`` and ``*_tex(...)`` with
        ``texture(sampler2D(...)`` (or ``sampler2DArray``).
        """
        # We must work iteratively because replacements may change the string.
        # A simple loop with a regex based approach is used for clarity.
        for base, sampler_name in tex_mappings.items():
            # ---- *_texOff(offset) ----
            code = MacroTranslator._replace_pattern(
                code,
                rf"{re.escape(base)}_texOff\s*\(",
                sampler_name,
                point_sampler,
                array_mode,
                offset_mode=True,
            )
            # ---- *_tex(coordinate) ----
            code = MacroTranslator._replace_pattern(
                code,
                rf"{re.escape(base)}_tex\s*\(",
                sampler_name,
                point_sampler,
                array_mode,
                offset_mode=False,
            )
            # Replace position / size macros
            code = code.replace(f"{base}_pos", "pos")
            code = code.replace(f"{base}_pt", "vec2(ubo.in_dx, ubo.in_dy)")
            code = code.replace(f"{base}_size", "vec2(ubo.in_width, ubo.in_height)")
        return code

    @staticmethod
    def _replace_pattern(
        code: str,
        pattern: str,
        sampler: str,
        point_sampler: str,
        array_mode: bool,
        offset_mode: bool,
    ) -> str:
        """Replace one occurrence of the pattern, return full code after replacement."""
        while True:
            match = re.search(pattern, code)
            if not match:
                break
            # Find the matching closing parenthesis
            start = match.end()
            depth = 1
            idx = start
            while idx < len(code) and depth > 0:
                if code[idx] == "(":
                    depth += 1
                elif code[idx] == ")":
                    depth -= 1
                idx += 1
            if depth != 0:
                break  # malformed - skip
            arg = code[start : idx - 1].strip()
            if offset_mode:
                coord2d = f"pos + ({arg}) * vec2(ubo.in_dx, ubo.in_dy)"
            else:
                coord2d = arg
            if array_mode:
                replacement = (
                    f"texture(sampler2DArray({sampler}, {point_sampler}), "
                    f"vec3({coord2d}, tile.inputLayer))"
                )
            else:
                replacement = (
                    f"texture(sampler2D({sampler}, {point_sampler}), {coord2d})"
                )
            code = code[: match.start()] + replacement + code[idx:]
        return code

    @staticmethod
    def resolve_defines_as_aliases(
        defines: List[str], tex_mappings: Dict[str, str]
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Convert ``#define ALIAS BASE_tex`` lines into extra texture mappings.
        Returns a list of remaining defines and the extra mappings.
        """
        remaining = []
        extra = {}
        for d in defines:
            m = re.match(r"#define\s+(\w+)\s+(\w+)_tex\s*$", d)
            if m:
                alias_full = m.group(1)
                original_base = m.group(2)
                if original_base in tex_mappings:
                    # Extract the prefix of the alias (strip _tex suffix)
                    alias_base = (
                        alias_full[:-4] if alias_full.endswith("_tex") else alias_full
                    )
                    extra[alias_base] = tex_mappings[original_base]
                    continue
            remaining.append(d)
        return remaining, extra


# ----------------------------------------------------------------------
# Shader code generators
# ----------------------------------------------------------------------
class ShaderGenerator:
    """Produces the final GLSL source for a single pass."""

    @staticmethod
    def _license_block(license_text: str) -> str:
        if not license_text:
            return ""
        return "\n".join(f"// {line}" for line in license_text.splitlines())

    @staticmethod
    def _header_comment(
        model_name: str,
        pass_index: int,
        total_passes: int,
        is_last: bool,
        tile_mode: bool,
        license_text: str,
    ) -> str:
        parts = [
            f"// {model_name} - Pass {pass_index + 1} of {total_passes} - https://github.com/bloc97/Anime4K",
            "// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler",
            "//",
            "// Compile with:",
            "//    glslc -fshader-stage=compute --target-env=vulkan1.2 <this_file> -o <output.spv>",
            "//",
            "// " + "-" * 77,
        ]
        lic = ShaderGenerator._license_block(license_text)
        if lic:
            parts.extend(["//", lic])
        parts.append(
            """//
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
//"""
        )
        if tile_mode:
            parts.append(
                """// -----------------------------------------------------------------------------
//  Push constants (only in tile-mode shaders)
//    layout(push_constant) uniform TileParams {
//        uvec2 dstOffset;       // output pixel offset in the full upscaled frame
//        uvec2 tileOutExtent;   // width & height of this tile’s output region
//        uint  fullOutWidth;    // upscaled frame width
//        uint  fullOutHeight;   // upscaled frame height
//        uint  inputLayer;      // array slice to read (0-based)
//        uint  margin;          // context margin (pixels in feature-map space)
//    } tile;
// -----------------------------------------------------------------------------
//"""
            )
        parts.append("// " + "=" * 77)
        return "\n".join(parts)

    @staticmethod
    def _common_header(tile_mode: bool) -> str:
        header = (
            """#version 450

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

layout(set = 0, binding = """
            + str(SAMPLER_POINT_BINDING)
            + """) uniform sampler pointSampler;

// global coordinate variable (replaces mpv's HOOKED_pos / MAIN_pos)
vec2 pos;
"""
        )
        if tile_mode:
            header += """
layout(push_constant) uniform TileParams {
    uvec2 dstOffset;
    uvec2 tileOutExtent;
    uvec2 fullOut;
    uint inputLayer;
    uint margin;
} tile;
"""
        return header

    @staticmethod
    def generate_intermediate_pass(
        pinfo: PassInfo,
        out_name: str,
        is_final: bool,
        tile_mode: bool,
        header_comment: str,
        intermediate_fmt: str = "rgba16f",
    ) -> str:
        """Generate a single intermediate (non-shuffle) compute pass."""
        tex_mappings: Dict[str, str] = {}
        lines = [header_comment, "", ShaderGenerator._common_header(tile_mode)]

        # Bind input textures
        for idx, name in enumerate(pinfo.bindings):
            binding = SRV_BINDING_START + idx
            safe = MacroTranslator.safe_tex_name(name)
            kind = "texture2DArray" if tile_mode else "texture2D"
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform {kind} tex_{safe};"
            )
            tex_mappings[name] = f"tex_{safe}"

        # Ensure MAIN is mapped to the first binding if not present
        if "MAIN" not in tex_mappings and pinfo.bindings:
            tex_mappings["MAIN"] = tex_mappings[pinfo.bindings[0]]

        # Output image
        out_safe = MacroTranslator.safe_tex_name(out_name)
        fmt = "rgba8" if is_final else intermediate_fmt
        out_kind = "image2DArray" if (tile_mode and not is_final) else "image2D"
        lines.append(
            f"layout(set = 0, binding = {UAV_BINDING}, {fmt}) uniform {out_kind} img_{out_safe};"
        )

        # Handle #define aliases
        filtered_defines, extra = MacroTranslator.resolve_defines_as_aliases(
            pinfo.defines, tex_mappings
        )
        tex_mappings.update(extra)

        # Emit defines and prologue after macro translation
        for d in filtered_defines:
            d_clean = MacroTranslator.replace_mpv_globals(d)
            d_clean = MacroTranslator.replace_texture_macros(
                d_clean, tex_mappings, "pointSampler", tile_mode
            )
            lines.append(d_clean)

        if pinfo.prologue:
            lines.append("")
            prologue = MacroTranslator.replace_mpv_globals(pinfo.prologue)
            prologue = MacroTranslator.replace_texture_macros(
                prologue, tex_mappings, "pointSampler", tile_mode
            )
            lines.append(prologue)

        # Hook function
        lines.append("")
        lines.append("vec4 hook() {")
        body = MacroTranslator.replace_mpv_globals(pinfo.body)
        body = MacroTranslator.replace_texture_macros(
            body, tex_mappings, "pointSampler", tile_mode
        )
        lines.append(body)
        lines.append("}")

        # Main entry point
        lines.append("")
        lines.append("void main() {")
        if tile_mode:
            lines.append("    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);")
            lines.append("    ivec2 valid_xy = interior_xy + ivec2(tile.margin);")
            lines.append(
                "    pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
            )
        else:
            lines.append("    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);")
            lines.append("    pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);")
        lines.append("    vec4 result = hook();")
        if tile_mode:
            if is_final:
                # Tile mode, final 2D output - needs tile offset
                lines.append(
                    f"    imageStore(img_{out_safe}, "
                    f"ivec2(valid_xy) + ivec2(tile.dstOffset), result);"
                )
            else:
                # Tile mode, intermediate 2D-array output
                lines.append(
                    f"    imageStore(img_{out_safe}, ivec3(valid_xy, tile.inputLayer), result);"
                )
        else:
            # Full-frame (2D image) - always use gxy
            lines.append(f"    imageStore(img_{out_safe}, gxy, result);")
        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def generate_d2s_pass(pinfo: PassInfo, tile_mode: bool, header_comment: str) -> str:
        """Generate the depth-to-space (final shuffle) pass."""
        # Separate feature maps from MAIN
        feature_bindings = [name for name in pinfo.bindings if name != "MAIN"]
        if not feature_bindings:
            raise ValueError(
                "Depth-to-space pass requires at least one feature map binding."
            )

        tex_mappings: Dict[str, str] = {}
        lines = [header_comment, "", ShaderGenerator._common_header(tile_mode)]
        # Add linear sampler (point sampler already in common header)
        lines.append(
            f"layout(set = 0, binding = {SAMPLER_LINEAR_BINDING}) uniform sampler linearSampler;"
        )

        # Feature map textures (2D array in tile mode, 2D otherwise)
        for idx, name in enumerate(feature_bindings):
            binding = SRV_BINDING_START + idx
            safe = MacroTranslator.safe_tex_name(name)
            kind = "texture2DArray" if tile_mode else "texture2D"
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform {kind} tex_{safe};"
            )
            tex_mappings[name] = f"tex_{safe}"

        # MAIN texture (always a plain 2D image sampled with linear filtering)
        main_binding = SRV_BINDING_START + len(feature_bindings)
        safe_main = MacroTranslator.safe_tex_name("MAIN")
        lines.append(
            f"layout(set = 0, binding = {main_binding}) uniform texture2D tex_{safe_main};"
        )
        tex_mappings["MAIN"] = f"tex_{safe_main}"

        # Output image
        lines.append(
            f"layout(set = 0, binding = {UAV_BINDING}, rgba8) uniform image2D img_output;"
        )

        # Resolve alias defines
        filtered_defines, extra = MacroTranslator.resolve_defines_as_aliases(
            pinfo.defines, tex_mappings
        )
        tex_mappings.update(extra)
        for d in filtered_defines:
            d_clean = MacroTranslator.replace_mpv_globals(d)
            d_clean = MacroTranslator.replace_texture_macros(
                d_clean, tex_mappings, "pointSampler", False
            )
            lines.append(d_clean)
        if pinfo.prologue:
            lines.append("")
            prologue = MacroTranslator.replace_mpv_globals(pinfo.prologue)
            lines.append(prologue)

        # Main function
        lines.append("")
        lines.append("void main() {")
        if tile_mode:
            lines.append("    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);")
            lines.append(
                "    ivec2 base_out = (interior_xy * 2) + ivec2(tile.dstOffset);"
            )
            lines.append(
                "    pos = (vec2(interior_xy + tile.margin) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
            )
            lines.append(
                "    vec2 full_opt = vec2(1.0 / tile.fullOut.x, 1.0 / tile.fullOut.y);"
            )
        else:
            lines.append("    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy) * 2;")
            lines.append(
                "    pos = ((vec2(gxy) / 2.0) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
            )
            lines.append("    vec2 full_opt = vec2(ubo.out_dx, ubo.out_dy);")

        lines.append("    vec2 f0 = fract(pos * vec2(ubo.in_width, ubo.in_height));")
        lines.append("    ivec2 i0 = ivec2(f0 * 2.0);")

        # Sample each feature map
        for idx, name in enumerate(feature_bindings):
            safe = MacroTranslator.safe_tex_name(name)
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

        # Fill missing channel coefficients (shaders expect 4 values)
        nf = len(feature_bindings)
        if nf == 1:
            lines.append("    float c1 = c0; float c2 = c0; float c3 = c0;")
        elif nf == 2:
            lines.append("    float c2 = c1; float c3 = c1;")
        elif nf == 3:
            lines.append("    float c3 = c2;")

        # 2x2 output quads
        offsets = [(0, 0, "c0"), (1, 0, "c1"), (0, 1, "c2"), (1, 1, "c3")]
        for ox, oy, cvar in offsets:
            if tile_mode:
                cond = (
                    f"    if ((base_out.x + {ox}) < int(tile.dstOffset.x + tile.tileOutExtent.x) && "
                    f"(base_out.y + {oy}) < int(tile.dstOffset.y + tile.tileOutExtent.y)) {{"
                )
                lines.append(cond)
                lines.append(
                    f"        vec3 rgb_{ox}_{oy} = texture(sampler2D(tex_{safe_main}, linearSampler), "
                    f"(vec2(base_out) + vec2({ox + 0.5}, {oy + 0.5})) * full_opt).rgb;"
                )
                lines.append(
                    f"        imageStore(img_output, ivec2(base_out) + ivec2({ox}, {oy}), "
                    f"vec4(rgb_{ox}_{oy} + {cvar}, 1.0));"
                )
                lines.append("    }")
            else:
                lines.append(
                    f"    vec3 rgb_{ox}_{oy} = texture(sampler2D(tex_{safe_main}, linearSampler), "
                    f"(vec2(gxy) + vec2({ox + 0.5}, {oy + 0.5})) * full_opt).rgb;"
                )
                lines.append(
                    f"    imageStore(img_output, gxy + ivec2({ox}, {oy}), "
                    f"vec4(rgb_{ox}_{oy} + {cvar}, 1.0));"
                )
        lines.append("}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# model.json builder
# ----------------------------------------------------------------------
class ModelJSONBuilder:
    """Creates the model.json dictionary from the parsed passes."""

    @staticmethod
    def build(passes: List[PassInfo], model_name: str, depth: str) -> Dict:
        srv_uav = []
        sampler_list = []
        prev_output = "input"
        all_tex = set()

        for idx, p in enumerate(passes):
            is_last = idx == len(passes) - 1
            # Collect inputs for this pass
            inputs = []
            for name in p.bindings:
                if name == "MAIN":
                    if is_last:
                        # For the final pass, MAIN is the original input - it should be the last SRV
                        continue
                    else:
                        inputs.append(prev_output)
                else:
                    inputs.append(name.lower())
            if is_last:
                inputs.append("input")  # original image is always the last SRV

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
            all_tex.update(inputs)
            all_tex.add(out_name)
            prev_output = out_name

        num_textures = len(all_tex - {"input", "output"})
        scale = next(
            (
                int(p[1:])
                for p in model_name.split("_")
                if p.startswith("x") and p[1:].isdigit()
            ),
            1,
        )
        return {
            "name": model_name,
            "scale": scale,
            "depth": depth,
            "passes": len(passes),
            "last_pass_upscale": "_GAN_" not in model_name,
            "num_textures": num_textures,
            "srv_uav": srv_uav,
            "samplers": sampler_list,
        }


# ----------------------------------------------------------------------
# CLI entry point
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Convert Anime4K mpv shader to Vulkan compute"
    )
    parser.add_argument("shader_path", help="Path to the original .glsl file")
    parser.add_argument(
        "-t", "--tile", action="store_true", help="Also generate tile-mode variants"
    )
    parser.add_argument(
        "-d",
        "--depth",
        choices=["rgba8", "rgba16"],
        default="rgba16",
        help="Intermediate texture format (default: rgba16)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.shader_path):
        print(f"Error: {args.shader_path} not found.")
        return

    with open(args.shader_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse
    parser_obj = Anime4KParser(content)
    passes = parser_obj.passes
    if not passes:
        print("No passes found in the shader file.")
        return

    shader_dir = os.path.dirname(args.shader_path)
    shader_name = os.path.splitext(os.path.basename(args.shader_path))[0]
    output_dir = os.path.join(shader_dir, shader_name)
    os.makedirs(output_dir, exist_ok=True)

    # model.json
    model = ModelJSONBuilder.build(passes, shader_name, args.depth)
    with open(os.path.join(output_dir, "model.json"), "w") as f:
        json.dump(model, f, indent=2)
    print(f"model.json written.")

    # Generate GLSL for each pass
    tile_modes = [False, True] if args.tile else [False]
    total = len(passes)
    intermediate_glsl = "rgba16f" if args.depth == "rgba16" else "rgba8"

    for idx, pinfo in enumerate(passes):
        is_last = idx == total - 1
        # Determine output name for this pass
        if pinfo.save is None:
            out_name = f"pass_{idx}_out"
            if is_last:
                out_name = "output"
        elif pinfo.save == "MAIN" and is_last:
            out_name = "output"
        else:
            out_name = pinfo.save

        for tile in tile_modes:
            suffix = "_tile" if tile else ""
            header = ShaderGenerator._header_comment(
                shader_name,
                idx,
                total,
                is_last=(is_last and not pinfo.is_d2s),
                tile_mode=tile,
                license_text=parser_obj.license,
            )
            if pinfo.is_d2s:
                code = ShaderGenerator.generate_d2s_pass(pinfo, tile, header)
            else:
                code = ShaderGenerator.generate_intermediate_pass(
                    pinfo,
                    out_name,
                    is_last,
                    tile,
                    header,
                    intermediate_fmt=intermediate_glsl,
                )
            out_file = os.path.join(output_dir, f"Pass{idx + 1}{suffix}.glsl")
            with open(out_file, "w") as f:
                f.write(code)
            print(f"Written {out_file}")

    print(f"\nDone. Output directory: {output_dir}")


if __name__ == "__main__":
    main()
