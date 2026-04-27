#!/usr/bin/env python3
"""
Convert an Anime4K mpv shader to Vulkan-compatible GLSL compute shaders.

Anime4K multi‑pass shaders:
- Each pass starts with a //!DESC line.
- Inputs are declared with //!BIND <tex>
- Output is //!SAVE <tex>
- The main function is vec4 hook().

The script generates:
- One compute shader per pass (non‑tile) with Vulkan layout qualifiers.
- Optionally tile‑based variants that use push constants, array textures and bounds checks.
- A model.json file describing the pipeline (same format as the CuNNy converter).
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
    """Conversion options."""

    # Whether to generate tile‑mode variants.
    tile: bool = False
    # Compute shader local size (matches CuNNy and most hardware).
    local_size: Tuple[int, int, int] = (8, 8, 1)


# ----------------------------------------------------------------------
# Data structures for passes
# ----------------------------------------------------------------------


@dataclass
class PassInfo:
    """All information about a single shader pass."""

    desc: str  # Description line (after //!DESC)
    bindings: List[str]  # Input texture names in order
    save: str  # Output texture name
    width_expr: Optional[str]  # //!WIDTH directive
    height_expr: Optional[str]  # //!HEIGHT directive
    components: int  # //!COMPONENTS (default 4)
    defines: List[str]  # #define lines before hook()
    body: str  # Code inside vec4 hook() (without braces)
    when: Optional[str] = None  # //!WHEN directive (ignored for simplicity)

    @property
    def is_final(self) -> bool:
        """The final pass writes to MAIN (the output)."""
        return self.save == "MAIN"

    @property
    def is_d2s(self) -> bool:
        """True if this is a depth‑to‑space pass (usually the final one)."""
        return "Depth-to-Space" in self.desc

    @property
    def input_names(self) -> List[str]:
        return self.bindings

    @property
    def output_name(self) -> str:
        return self.save


# ----------------------------------------------------------------------
# Parsing the mpv shader file
# ----------------------------------------------------------------------


class Anime4KParser:
    """Parses the Anime4K mpv shader into a list of PassInfo objects."""

    def __init__(self, content: str):
        self.content = content
        self.passes: List[PassInfo] = []
        self._parse()

    def _parse(self) -> None:
        # Split on //!DESC lines; the first block before any DESC is discarded.
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

            # Find the hook function and attributes
            body_start = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("//!BIND"):
                    bindings.append(stripped.split(maxsplit=1)[1].strip())
                elif stripped.startswith("//!SAVE"):
                    save = stripped.split(maxsplit=1)[1].strip()
                elif stripped.startswith("//!WIDTH"):
                    width_expr = stripped[len("//!WIDTH") :].strip()
                elif stripped.startswith("//!HEIGHT"):
                    height_expr = stripped[len("//!HEIGHT") :].strip()
                elif stripped.startswith("//!COMPONENTS"):
                    components = int(stripped.split()[-1])
                elif stripped.startswith("//!WHEN"):
                    when = stripped[len("//!WHEN") :].strip()
                elif stripped.startswith("#define"):
                    defines.append(stripped)
                elif "vec4 hook()" in stripped:
                    body_start = i
                    break

            # Extract the body of hook()
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
# GLSL code generation helpers
# ----------------------------------------------------------------------


def tex_name_safe(name: str) -> str:
    """Transform a texture name into a valid GLSL variable."""
    return name.replace(".", "_").replace("-", "_")


def texture_binding_number(base: int, index: int) -> int:
    """Compute binding index for input textures (starting from `base`)."""
    return base + index


def replace_sampling_calls(
    body: str, tex_mappings: Dict[str, str], array_mode: bool, point_sampler: str
) -> str:
    """
    Replace mpv sampling macros with GLSL texture calls.
    tex_mappings: name -> sampler variable
    """
    # Pattern: <name>_texOff(vec2(x, y))
    # e.g., MAIN_texOff(vec2(-1.0, -1.0))
    # or conv2d_tf_texOff(vec2(x, y))

    for orig_name, sampler_var in tex_mappings.items():
        macro = f"{orig_name}_texOff"
        if array_mode:
            replacement = f"texture(sampler2DArray({sampler_var}, {point_sampler}), vec3(pos + vec2(\\1, \\2) * vec2(ubo.in_dx, ubo.in_dy), tile.inputLayer))"
        else:
            replacement = f"texture(sampler2D({sampler_var}, {point_sampler}), pos + vec2(\\1, \\2) * vec2(ubo.in_dx, ubo.in_dy))"
        body = re.sub(
            rf"{re.escape(macro)}\s*\(\s*vec2\s*\(\s*([^)]+)\s*,\s*([^)]+)\s*\)\s*\)",
            replacement,
            body,
        )

    # Also handle the non‑offset lookups used in depth‑to‑space:
    # pattern: <name>_tex(coord)
    for orig_name, sampler_var in tex_mappings.items():
        macro = f"{orig_name}_tex"
        if array_mode:
            replacement = f"texture(sampler2DArray({sampler_var}, {point_sampler}), vec3(\\1, tile.inputLayer))"
        else:
            replacement = f"texture(sampler2D({sampler_var}, {point_sampler}), \\1)"
        body = re.sub(rf"{re.escape(macro)}\s*\(\s*([^)]+)\s*\)", replacement, body)

    # Replace the built-in pos macros used only in the final D2S pass
    # e.g., conv2d_last_tf_pos -> pos  (since we already compute pos)
    for orig_name in tex_mappings:
        body = body.replace(f"{orig_name}_pos", "pos")
        body = body.replace(f"{orig_name}_pt", "vec2(ubo.in_dx, ubo.in_dy)")
        body = body.replace(f"{orig_name}_size", "vec2(ubo.in_width, ubo.in_height)")

    return body


def generate_common_header() -> str:
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


def generate_push_constant_block() -> str:
    return """layout(push_constant) uniform TileParams {
    uint inputLayer;
    uvec2 dstOffset;
    uint fullOutWidth;
    uint fullOutHeight;
    uint margin;
    uvec2 tileOutExtent;
} tile;
"""


def generate_intermediate_pass(pass_info: PassInfo, tile_mode: bool) -> str:
    """Generate a GLSL compute shader for an intermediate convolution pass."""
    tex_mappings = {}
    bindings_start = 3  # after ubo (0), pointSampler (1), linearSampler (2)
    lines = []

    # Header and declarations
    lines.append(generate_common_header())
    if tile_mode:
        lines.append(generate_push_constant_block())

    # Input texture declarations
    for idx, name in enumerate(pass_info.bindings):
        binding = bindings_start + idx
        safe = tex_name_safe(name)
        if tile_mode:
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform sampler2DArray tex_{safe};"
            )
        else:
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform sampler2D tex_{safe};"
            )
        tex_mappings[name] = f"tex_{safe}"

    # Output image
    out_binding = bindings_start + len(pass_info.bindings)
    out_safe = tex_name_safe(pass_info.save) if pass_info.save != "MAIN" else "output"
    if tile_mode and pass_info.save != "MAIN":
        lines.append(
            f"layout(set = 0, binding = {out_binding}, rgba8) uniform image2DArray img_{out_safe};"
        )
    else:
        lines.append(
            f"layout(set = 0, binding = {out_binding}, rgba8) uniform image2D img_{out_safe};"
        )

    lines.append("")
    # Defines
    for d in pass_info.defines:
        lines.append(d)
    lines.append("")

    # Main function
    lines.append("void main() {")
    if tile_mode:
        lines.append(
            "    // Tile mode: process interior region only, using expanded tile size."
        )
        lines.append(
            "    // in_width/in_height is the expanded tile size (includes margin)."
        )
        lines.append("    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append("    ivec2 valid_xy = interior_xy + ivec2(tile.margin);")
        lines.append(
            "    vec2 pos = (vec2(valid_xy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);"
        )
    else:
        lines.append("    ivec2 gxy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append("    vec2 pos = (vec2(gxy) + 0.5) * vec2(ubo.in_dx, ubo.in_dy);")

    # Body with sampling replacements
    body = replace_sampling_calls(
        pass_info.body, tex_mappings, tile_mode, "pointSampler"
    )
    lines.append(body)

    # Write output (assuming the body computes a vec4 variable named 'result'
    # In the original code, the result is returned, so we need to make it explicit.
    # The original body ends with 'return result;' we replace that with imageStore.
    # We'll add a line that captures the result and stores it.
    # For simplicity, we assume the original body last statement is 'return result;'
    # We'll replace it inside the body before appending.
    # We'll handle this by post-processing the body: replace 'return result;' with nothing
    # and then store.
    lines.append(
        f'    imageStore(img_{out_safe}, {"ivec3(valid_xy, 0)" if tile_mode else "gxy"}, result);'
    )
    lines.append("}")

    final_body = "\n".join(lines)
    # replace the return statement
    final_body = final_body.replace(
        "return result;", ""
    )  # already removed in body replacement?
    # We also need to ensure we've stored 'result'. The original code does 'return result;'
    # So we'll do the store ourselves. We'll remove any trailing return.
    # This is a bit fragile; we'll instead use a simple approach:
    # In the body replacement, we'll change 'return result;' to nothing, and then add the store.
    return final_body


def generate_d2s_pass(pass_info: PassInfo, tile_mode: bool) -> str:
    """Generate the final depth‑to‑space pass.

    This pass reads the feature maps and the original image, performs the shuffle,
    and adds the low‑res residual.
    """
    tex_mappings = {}
    bindings_start = 3
    lines = []

    lines.append(generate_common_header())
    if tile_mode:
        lines.append(generate_push_constant_block())

    # We need to separate the feature maps (conv2d_last_tf*) and the original image (MAIN).
    # The MAIN binding is always present and is the low‑res image.
    main_tex = None
    feature_bindings = []
    for name in pass_info.bindings:
        if name == "MAIN":
            main_tex = name
        else:
            feature_bindings.append(name)

    if not main_tex:
        raise ValueError("Final pass missing MAIN binding")

    # Declare feature inputs as samplers (with array if tile)
    for idx, name in enumerate(feature_bindings):
        binding = bindings_start + idx
        safe = tex_name_safe(name)
        if tile_mode:
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform sampler2DArray tex_{safe};"
            )
        else:
            lines.append(
                f"layout(set = 0, binding = {binding}) uniform sampler2D tex_{safe};"
            )
        tex_mappings[name] = f"tex_{safe}"

    # MAIN (original image) always as sampler2D (even in tile mode, because it's the full low‑res image)
    main_binding = bindings_start + len(feature_bindings)
    safe_main = tex_name_safe(main_tex)
    lines.append(
        f"layout(set = 0, binding = {main_binding}) uniform sampler2D tex_{safe_main};"
    )
    tex_mappings[main_tex] = f"tex_{safe_main}"

    # Output image (2D)
    out_binding = main_binding + 1
    lines.append(
        f"layout(set = 0, binding = {out_binding}, rgba8) uniform image2D img_output;"
    )

    lines.append("")
    for d in pass_info.defines:
        lines.append(d)
    lines.append("")

    lines.append("void main() {")
    if tile_mode:
        lines.append("    ivec2 interior_xy = ivec2(gl_GlobalInvocationID.xy);")
        lines.append(
            "    ivec2 base_output_xy = (interior_xy * 2) + ivec2(tile.dstOffset);"
        )
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

    # Convert the body: replace sampling macros and pos/pt/size references
    body = replace_sampling_calls(
        pass_info.body, tex_mappings, tile_mode, "pointSampler"
    )

    # Drop the original body lines and write our own implementation.
    # We'll use a prebuilt function.
    lines.append("")
    lines.append("    // Depth‑to‑Space shuffle + residual add")
    lines.append(f"    vec2 f0 = fract(pos * vec2(ubo.in_width, ubo.in_height));")
    lines.append(f"    ivec2 i0 = ivec2(f0 * 2.0);")

    # We'll generate sampling for each feature map
    if tile_mode:
        idx = 0
        for name in feature_bindings:
            safe = tex_name_safe(name)
            lines.append(
                f"    float c{idx} = texture(sampler2DArray(tex_{safe}, pointSampler), vec3((vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos, tile.inputLayer))[i0.y * 2 + i0.x];"
            )
            idx += 1
        # For the last channel(s) reuse c2 as c3 if only one map? We need to follow original logic.
        # We'll mimic the original's handling: if only one feature map, c0=c1=c2=c3.
    else:
        idx = 0
        for name in feature_bindings:
            safe = tex_name_safe(name)
            lines.append(
                f"    float c{idx} = texture(sampler2D(tex_{safe}, pointSampler), (vec2(0.5) - f0) * vec2(ubo.in_dx, ubo.in_dy) + pos)[i0.y * 2 + i0.x];"
            )
            idx += 1

    # Now emulate the original code that sets c2 = c1 etc. depending on the number of maps.
    # In the examples provided:
    # - CNN(S) has only one conv2d_last_tf: its body does c1=c0; c2=c1; c3=c2.
    # - UL has three, and c3 = c2.
    # We'll handle both cases.
    num_features = len(feature_bindings)
    if num_features == 1:
        lines.append("    float c1 = c0;")
        lines.append("    float c2 = c1;")
        lines.append("    float c3 = c2;")
    elif num_features == 2:
        lines.append("    float c2 = c1;")
        lines.append("    float c3 = c2;")
    elif num_features == 3:
        # The original UL uses c3 = c2.
        lines.append("    float c3 = c2;")
    # else: assume 4 or more (rare)

    # Residual add
    if tile_mode:
        lines.append(
            "    ivec2 maxOut = ivec2(tile.dstOffset) + ivec2(tile.tileOutExtent);"
        )
        for offx, offy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            c_idx = offy * 2 + offx
            lines.append(
                f"    if ((base_output_xy.x + {offx}) < maxOut.x && (base_output_xy.y + {offy}) < maxOut.y) {{"
            )
            lines.append(
                f"        vec3 rgb = texture(sampler2D(tex_{safe_main}, linearSampler), (vec2(base_output_xy) + vec2({offx+0.5}, {offy+0.5})) * full_opt).rgb;"
            )
            lines.append(
                f"        imageStore(img_output, ivec2(base_output_xy) + ivec2({offx}, {offy}), vec4(rgb + c{c_idx}, 1.0));"
            )
            lines.append("    }")
    else:
        for offx, offy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            c_idx = offy * 2 + offx
            lines.append(
                f"    vec3 rgb = texture(sampler2D(tex_{safe_main}, linearSampler), (vec2(gxy) + vec2({offx+0.5}, {offy+0.5})) * full_opt).rgb;"
            )
            lines.append(
                f"    imageStore(img_output, gxy + ivec2({offx}, {offy}), vec4(rgb + c{c_idx}, 1.0));"
            )

    lines.append("}")
    return "\n".join(lines)


def generate_pass(pass_info: PassInfo, tile_mode: bool) -> str:
    """Dispatcher: generate the appropriate compute shader."""
    if pass_info.is_final or pass_info.is_d2s:
        # For the final pass we use the specialised depth‑to‑space generator
        return generate_d2s_pass(pass_info, tile_mode)
    else:
        return generate_intermediate_pass(pass_info, tile_mode)


# ----------------------------------------------------------------------
# Model.json builder
# ----------------------------------------------------------------------


def build_model_json(passes: List[PassInfo]) -> Dict:
    """Create the model.json descriptor."""
    srv_uav = []
    # We'll assume samplers: all passes use point, final also linear.
    samplers = []
    for p in passes:
        inputs = [name.lower() if name != "MAIN" else "input" for name in p.input_names]
        outputs = [p.save.lower() if p.save != "MAIN" else "output"]
        srv_uav.append([inputs, outputs])
        if p.is_final:
            samplers.append(["point", "linear"])
        else:
            samplers.append(["point"])

    # Count the number of unique intermediate textures (by name) for 'num_textures'
    all_tex = set()
    for p in passes:
        all_tex.update(p.input_names)
        all_tex.add(p.save)
    num_textures = len(all_tex - {"MAIN"})  # exclude the special MAIN

    return {
        "name": None,  # filled later
        "passes": len(passes),
        "num_textures": num_textures,
        "srv_uav": srv_uav,
        "samplers": samplers,
    }


# ----------------------------------------------------------------------
# Main script
# ----------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Convert Anime4K mpv shader to Vulkan compute shaders."
    )
    parser.add_argument("shader_path", help="Path to the .glsl shader file")
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

    # Parse
    shader_parser = Anime4KParser(content)
    if not shader_parser.passes:
        print("No passes found!")
        return

    # Setup output directory
    shader_dir = os.path.dirname(shader_path)
    shader_name = os.path.splitext(os.path.basename(shader_path))[0]
    output_dir = os.path.join(shader_dir, shader_name)
    os.makedirs(output_dir, exist_ok=True)

    # Generate model.json
    model = build_model_json(shader_parser.passes)
    model["name"] = shader_name
    with open(os.path.join(output_dir, "model.json"), "w") as f:
        json.dump(model, f, indent=2)

    # Generate passes
    for i, pinfo in enumerate(shader_parser.passes, 1):
        # Non‑tile
        glsl_code = generate_pass(pinfo, tile_mode=False)
        out_path = os.path.join(output_dir, f"Pass{i}.glsl")
        with open(out_path, "w") as f:
            f.write(glsl_code)
        print(f"Written {out_path}")

        # Tile variant if requested
        if args.tile:
            glsl_tile = generate_pass(pinfo, tile_mode=True)
            out_tile_path = os.path.join(output_dir, f"Pass{i}_tile.glsl")
            with open(out_tile_path, "w") as f:
                f.write(glsl_tile)
            print(f"Written {out_tile_path}")

    print(f"Done. Output in {output_dir}")


if __name__ == "__main__":
    main()
