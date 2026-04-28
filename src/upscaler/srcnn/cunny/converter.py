#!/usr/bin/env python3
"""
Convert a Magpie CuNNy shader to Vulkan-compatible HLSL compute shader format.

Features:
- Detects number of passes and textures automatically.
- Parses //!IN and //!OUT lines to build srv_uav list.
- Replaces tabs with 4 spaces.
- Inserts blank lines between logical sections.
- Groups bias lines together and combines max + simple assignments.
- Handles scalar multiplications (r += V4(...) * s) and min16float declarations.
- Outputs to a folder named after the shader (without extension) at the same level.
- Adds "name": "shader_name" to model.json.
- Easy configuration via a Config dataclass.
- Supports tile-aware (cache) and offset-write (no cache) variants.
"""

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any


@dataclass
class Config:
    """Configuration options for the converter."""

    replace_tabs: bool = True
    tabs_to_spaces: int = 4
    separate_sections: bool = True
    combine_bias_max: bool = True  # group bias lines and combine max+assign
    use_min16float: bool = True
    num_threads: Tuple[int, int, int] = (8, 8, 1)
    entry_point: str = "main"
    output_texture_prefix: str = "T"
    input_texture_prefix: str = "T"
    special_input: str = "INPUT"
    special_output: str = "OUTPUT"
    tile: bool = False  # generate tile-mode shader


@dataclass
class PassInfo:
    """Information about a single rendering pass."""

    pass_num: int
    pre_lines: List[str]
    body: str
    in_textures: List[str]
    out_textures: List[str]


@dataclass
class SamplerInfo:
    """Sampler declaration with its filter type."""

    name: str
    filter_type: str  # 'point' or 'linear'


class ShaderParser:
    """Parses the original Magpie shader and extracts passes, samplers, texture indices."""

    def __init__(self, content: str) -> None:
        self.content = content
        self.samplers: List[SamplerInfo] = []
        self.sampler_order: List[str] = []
        self.max_texture_index: int = -1
        self.passes: List[PassInfo] = []
        self._parse()

    def _parse(self) -> None:
        self._parse_samplers()
        self._parse_texture_indices()
        self._parse_passes()

    def _parse_samplers(self) -> None:
        """Extract sampler names and their filter types."""
        lines = self.content.splitlines()
        i = 0
        while i < len(lines):
            if lines[i].strip().startswith("//!SAMPLER"):
                filter_type = None
                if i + 1 < len(lines) and "//!FILTER" in lines[i + 1]:
                    m = re.search(r"//!FILTER\s+(\w+)", lines[i + 1])
                    if m:
                        filter_type = m.group(1).lower()
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith(
                    "SamplerState"
                ):
                    j += 1
                if j < len(lines):
                    m = re.search(r"SamplerState\s+(\w+)\s*;", lines[j])
                    if m:
                        name = m.group(1)
                        self.samplers.append(SamplerInfo(name, filter_type or "point"))
                        self.sampler_order.append(name)
                i = j + 1
            else:
                i += 1

    def _parse_texture_indices(self) -> None:
        """Find the highest index of textures named T<number>."""
        pattern = r"Texture2D\s+T(\d+)\s*;"
        matches = re.findall(pattern, self.content)
        if matches:
            self.max_texture_index = max(int(m) for m in matches)

    def _parse_passes(self) -> None:
        """Extract all passes using regex."""
        pattern = r"//!PASS\s+(\d+)\n(.*?)void\s+Pass\1\s*\([^)]*\)\s*\{(.*?)\n\}"
        matches = re.findall(pattern, self.content, re.DOTALL)
        for pass_num_str, pre, body in matches:
            pass_num = int(pass_num_str)
            pre_lines = pre.strip().splitlines()
            in_textures, out_textures = self._extract_in_out(pre_lines)
            self.passes.append(
                PassInfo(
                    pass_num=pass_num,
                    pre_lines=pre_lines,
                    body=body.rstrip(),
                    in_textures=in_textures,
                    out_textures=out_textures,
                )
            )

    @staticmethod
    def _extract_in_out(pre_lines: List[str]) -> Tuple[List[str], List[str]]:
        """Extract //!IN and //!OUT lists from the pre-pass lines."""
        in_tex, out_tex = [], []
        for line in pre_lines:
            if line.startswith("//!IN"):
                parts = line.split(maxsplit=1)
                if len(parts) > 1:
                    in_tex = [x.strip() for x in parts[1].split(",")]
            elif line.startswith("//!OUT"):
                parts = line.split(maxsplit=1)
                if len(parts) > 1:
                    out_tex = [x.strip() for x in parts[1].split(",")]
        return in_tex, out_tex


class ModelJsonBuilder:
    """Constructs the model.json data from parsed information."""

    def __init__(
        self,
        config: Config,
        passes: List[PassInfo],
        num_textures: int,
        sampler_map: Dict[str, str],
    ) -> None:
        self.config = config
        self.passes = passes
        self.num_textures = num_textures
        self.sampler_map = sampler_map  # name -> filter_type

    def build(self) -> Dict[str, Any]:
        srv_uav = []
        samplers_per_pass = []

        point_filter = self._get_filter("point") or "point"
        linear_filter = self._get_filter("linear") or "linear"

        for idx, pinfo in enumerate(self.passes):
            # Convert texture names to lower case for JSON (input -> "input", T0 -> "t0")
            srv = [
                t.lower() if t != self.config.special_input else "input"
                for t in pinfo.in_textures
            ]
            uav = [
                t.lower() if t != self.config.special_output else "output"
                for t in pinfo.out_textures
            ]
            srv_uav.append([srv, uav])

            # Samplers for this pass: all passes use point, last pass also uses linear
            if idx == len(self.passes) - 1:
                samplers_per_pass.append([point_filter, linear_filter])
            else:
                samplers_per_pass.append([point_filter])

        return {
            "name": None,  # will be filled later with the shader name
            "passes": len(self.passes),
            "num_textures": self.num_textures,
            "srv_uav": srv_uav,
            "samplers": samplers_per_pass,
            "depth": "rgba8",
        }

    def _get_filter(self, filter_type: str) -> Optional[str]:
        """Return the first sampler name with the given filter type, or None."""
        for name, ftype in self.sampler_map.items():
            if ftype == filter_type:
                return ftype  # actually the filter string, not the name
        return None


class HlslGenerator:
    """Generates the final HLSL source for a single pass."""

    def __init__(self, config: Config, model_name: str) -> None:
        self.config = config
        self.model_name = model_name

    @staticmethod
    def common_header(tile: bool) -> str:
        header = """// -----------------------------------------------------------------------------
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

"""
        if tile:
            header += """// -----------------------------------------------------------------------------
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

"""

        header += """float2 GetInputPt() { return float2(in_dx, in_dy); }
float2 GetOutputPt() { return float2(out_dx, out_dy); }
uint2 GetInputSize() { return uint2(in_width, in_height); }
uint2 GetOutputSize() { return uint2(out_width, out_height); }

"""
        if tile:
            header += "#define O(t, x, y) t.SampleLevel(SP, float3(pos + float2(x, y) * pt, tileParams.inputLayer), 0)"
        else:
            header += "#define O(t, x, y) t.SampleLevel(SP, pos + float2(x, y) * pt, 0)"

        header += """
#define V4 min16float4
#define M4 min16float4x4
#define V3 min16float3
#define M3x4 min16float3x4
"""
        return header

    def generate(
        self,
        pass_info: PassInfo,
        sampler_order: List[str],
        total_passes: int,
        original_license: str = "",
    ) -> str:
        pass_num = pass_info.pass_num
        in_textures = pass_info.in_textures
        out_textures = pass_info.out_textures
        pre_lines = pass_info.pre_lines
        body = pass_info.body
        is_final = self.config.special_output in out_textures
        tile = self.config.tile

        # Texture declarations with registers
        tex_decl_lines = self._build_texture_declarations(
            in_textures, out_textures, is_final, tile
        )

        # Sampler declarations
        sampler_lines = [
            f"SamplerState {name} : register(s{idx});"
            for idx, name in enumerate(sampler_order)
        ]

        # L macros from pre_lines
        l_macros = [line for line in pre_lines if line.strip().startswith("#define L")]

        # Extract computation core from the body
        core_lines = self._extract_core_lines(body)

        # Reformat if requested
        if self.config.separate_sections:
            core_lines = self._reformat_body(core_lines)

        # Apply tile/offset specific rewrites
        if tile:
            if is_final:
                # --- Final pass: convert to tile-mode with bounds checks ---

                # 1. Replace fpos calculation to use full_opt
                core_lines = [
                    re.sub(
                        r"float2 fpos = \(float2\(gxy\) \+ 0\.5\) \* opt;",
                        "float2 fpos = (float2(globalOutXY) + 0.5) * full_opt;",
                        line,
                    )
                    for line in core_lines
                ]

                # 2. Wrap each OUTPUT assignment with bounds check,
                #    change gxy -> globalOutXY, and add uint3 + outputLayer.
                new_core = []
                for line in core_lines:
                    # Match original: OUTPUT[gxy + int2(X, Y)] = ...;
                    m = re.match(
                        r"(\s*)OUTPUT\[gxy\s*\+\s*int2\((\d+),\s*(\d+)\)\]\s*=\s*(.+);",
                        line,
                    )
                    if m:
                        indent, off_x, off_y, rhs = m.groups()
                        cond_x = (
                            f"globalOutXY.x + {off_x} < maxOut.x"
                            if off_x != "0"
                            else "globalOutXY.x < maxOut.x"
                        )
                        cond_y = (
                            f"globalOutXY.y + {off_y} < maxOut.y"
                            if off_y != "0"
                            else "globalOutXY.y < maxOut.y"
                        )
                        cond = f"{cond_x} && {cond_y}"
                        new_core.append(f"{indent}if ({cond})")
                        new_core.append(
                            f"{indent}    OUTPUT[globalOutXY + int2({off_x}, {off_y})] = {rhs};"
                        )
                    else:
                        new_core.append(line)
                core_lines = new_core

                # 3. Convert INPUT.SampleLevel to array texture:
                #    - change * opt to * full_opt
                #    - wrap coordinate in float3(..., tileParams.inputLayer)
                core_lines = [
                    re.sub(
                        r"INPUT\.SampleLevel\(SL,\s*(fpos\s*\+\s*float2\([^)]+\))\s*\*\s*opt\s*,\s*0\)",
                        r"INPUT.SampleLevel(SL, float3(\1 * full_opt, 0), 0)",
                        line,
                    )
                    for line in core_lines
                ]
                # Also catch cases where opt was already replaced
                core_lines = [
                    re.sub(
                        r"INPUT\.SampleLevel\(SL,\s*(fpos\s*\+\s*float2\([^)]+\)\s*\*\s*full_opt)\s*,\s*0\)",
                        r"INPUT.SampleLevel(SL, float3(\1, tileParams.inputLayer), 0)",
                        line,
                    )
                    for line in core_lines
                ]

            else:
                # --- Intermediate passes: write to inputLayer (not outputLayer) ---
                core_lines = [
                    re.sub(
                        r"(T\d+)\[(\w+)\]",
                        r"\1[uint3(\2, tileParams.inputLayer)]",
                        line,
                    )
                    for line in core_lines
                ]

        entry = self._build_entry(is_final, tile)
        separator = f"// {"=" * 77}"

        # Assemble everything
        lines = [
            f"// {self.model_name} - Pass {pass_num} of {total_passes} - https://github.com/funnyplanter/CuNNy",
            "// Generated for linux-rt-upscaler - https://github.com/baronsmv/linux-rt-upscaler",
            "//",
            "// Compile with:",
            "// dxc -T cs_6_0 -E main -spirv <this_file> \\",
            "//     -fvk-auto-shift-bindings \\",
            "//     -fvk-t-shift 1024 0 \\",
            "//     -fvk-u-shift 2048 0 \\",
            "//     -fvk-s-shift 3072 0 \\",
            "//     -fvk-use-dx-layout \\",
            "//     -fvk-use-scalar-layout \\",
            "//     -Fo <output.spv>",
            "//",
            separator,
            "//",
        ]
        if original_license:
            for lic_line in original_license.strip().splitlines():
                lines.append(f"// {lic_line}")
            lines.extend(["//", separator, ""])

        lines.extend(
            [
                self.common_header(tile).strip(),
                "",
                *tex_decl_lines,
                "",
                *sampler_lines,
                "",
                *l_macros,
                "",
                entry,
            ]
        )
        # Indent core lines by 4 spaces
        for line in core_lines:
            if line.strip() == "":
                lines.append("")
            else:
                lines.append("    " + line)
        lines.append("}")

        full_shader = "\n".join(lines)
        if self.config.replace_tabs:
            full_shader = full_shader.expandtabs(self.config.tabs_to_spaces)
        return full_shader

    def _build_texture_declarations(
        self,
        in_textures: List[str],
        out_textures: List[str],
        is_final: bool,
        tile: bool,
    ) -> List[str]:
        """Return SRV and UAV declaration lines with registers."""
        lines = []
        suffix = "Array" if tile else ""
        # Input textures: for tile modes, use arrays for all passes
        for idx, tex in enumerate(in_textures):
            lines.append(f"Texture2D{suffix}<float4> {tex} : register(t{idx});")
        if in_textures and out_textures:
            lines.append("")
        # Output textures
        for idx, tex in enumerate(out_textures):
            # In tile mode, output is always an array (except for final pass)
            suffix = "Array" if tile and not is_final else ""
            lines.append(
                f'[[vk::image_format("rgba8")]] RWTexture2D{suffix}<float4> {tex} : register(u{idx});'
            )
        return lines

    def _build_entry(self, is_final: bool, tile: bool) -> str:
        nt = self.config.num_threads
        if is_final:
            # Final pass: 2x2 output pixels per thread
            if tile:
                # Tile mode final pass uses interior_id + validOffset to compute coordinates
                return f"""[numthreads({nt[0]},{nt[1]},{nt[2]})]
void {self.config.entry_point}(uint3 id : SV_DispatchThreadID)
{{
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
"""
            else:
                return f"""[numthreads({nt[0]},{nt[1]},{nt[2]})]
void {self.config.entry_point}(uint3 id : SV_DispatchThreadID)
{{
    // -----------------------------------------------------------------------------
    //  Coordinate mapping for the final shuffle pass (full-frame)
    //
    //    The last pass upsamples by 2x using a 2x2 output quad per thread.
    //    The dispatch grid covers the *low-resolution* feature map (1:1),
    //    and each thread writes 4 pixels into the full-size output.
    // -----------------------------------------------------------------------------
    
    // (1) texel size of the low-res feature map (same as in_width/in_height)
    float2 pt = float2(GetInputPt());
    
    // (2) gxy is the *low-res* pixel coordinate of this thread.
    //     Multiply by 2 to get the top-left of the 2x2 upscaled quad.
    uint2 gxy = id.xy * 2;
    
    // (3) Sampling position (centre of low-res pixel).
    float2 pos = ((gxy >> 1) + 0.5) * pt;
    //     (gxy >> 1) recovers the original id.xy.
"""
        else:
            # Intermediate passes: 1x1 output per thread
            return f"""[numthreads({nt[0]},{nt[1]},{nt[2]})]
void {self.config.entry_point}(uint3 id : SV_DispatchThreadID)
{{
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
"""

    def _extract_core_lines(self, body: str) -> List[str]:
        """
        Strip the original function prologue and return the computation lines.
        Finds the first line after 'float2 pos = ...' and takes everything after it.
        """
        lines = body.splitlines()
        # Find the line that sets 'pos' (prologue end)
        pos_idx = -1
        for i, line in enumerate(lines):
            if "pos =" in line and "float2" in line:
                pos_idx = i
                break
        if pos_idx == -1:
            # Fallback: find first declaration line (min16float, V4, V3)
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                if (
                    stripped.startswith("min16float")
                    or stripped.startswith("V4")
                    or stripped.startswith("V3")
                ):
                    pos_idx = i - 1  # start from this line
                    break
        if pos_idx >= 0 and pos_idx + 1 < len(lines):
            core = lines[pos_idx + 1 :]
        else:
            core = lines  # fallback

        # Remove any leading/trailing whitespace
        return [line.strip() for line in core]

    @staticmethod
    def _classify_line(line: str) -> str:
        """Return the type of a line."""
        stripped = line.lstrip()
        # Declarations
        if (
            stripped.startswith("min16float")
            or stripped.startswith("V4")
            or stripped.startswith("V3")
            or stripped.startswith("float")
        ):
            return "decl"
        # s-assignments (L calls)
        if "= L" in line:
            return "s_assign"
        # Matrix multiplication
        if "+= mul" in line:
            return "mul"
        # Scalar multiplication: rX += V4(...) * sY
        if re.search(r"r\d+\s*\+=\s*V4\(.*\)\s*\*\s*\w+", line):
            return "mul_scalar"
        # Bias (vector addition without multiplication)
        if re.search(r"r\d+\s*\+=\s*V4\(", line) and "*" not in line:
            return "bias"
        # Max operation
        if re.match(r"^r\d+\s*=\s*max\(r\d+,\s*0\.0\);$", stripped):
            return "max"
        # Simple assignment: T... = r...;
        if re.match(r"^(T\d+|OUTPUT)\[.*\]\s*=\s*r\d+;\s*$", stripped):
            return "assign_simple"
        # Any other output-like line (complex)
        if (
            stripped.startswith("T")
            or "OUTPUT" in line
            or "SampleLevel" in line
            or "saturate" in line
        ):
            return "assign_complex"
        return "other"

    def _get_s_var(self, line: str, typ: str) -> Optional[str]:
        """Extract the s-variable name from a mul or mul_scalar line."""
        if typ == "mul":
            m = re.search(r"mul\((\w+),", line)
            return m.group(1) if m else None
        if typ == "mul_scalar":
            # rX += V4(...) * sY
            m = re.search(r"\*\s*(\w+)", line)
            return m.group(1) if m else None
        return None

    def _split_into_blocks(self, lines: List[str]) -> List[Tuple[str, List[str]]]:
        """Split lines into blocks based on type, with mul groups split by s variable."""
        blocks = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            typ = self._classify_line(line)

            if typ in ("mul", "mul_scalar"):
                # Group mul lines by the s variable
                block = []
                last_s = None
                while i < n and self._classify_line(lines[i]) in ("mul", "mul_scalar"):
                    line = lines[i]
                    s_var = self._get_s_var(line, self._classify_line(line))
                    if s_var != last_s and block:
                        blocks.append(("mul_group", block))
                        block = []
                    block.append(line)
                    last_s = s_var
                    i += 1
                if block:
                    blocks.append(("mul_group", block))

            else:
                # For all other types, group consecutive lines of the same type
                block = []
                while i < n and self._classify_line(lines[i]) == typ:
                    block.append(lines[i])
                    i += 1
                blocks.append((typ, block))

        return blocks

    def _compact_tail(
        self, blocks: List[Tuple[str, List[str]]]
    ) -> List[Tuple[str, List[str]]]:
        """
        Find the tail region (from the first non-decl/s_assign/mul_group block onward)
        and replace it with a compact block if it consists only of bias, max, and assign lines.
        """
        if not self.config.combine_bias_max:
            return blocks

        # Find start index of the tail
        tail_start = 0
        for idx, (btype, _) in enumerate(blocks):
            if btype not in ("decl", "s_assign", "mul_group"):
                tail_start = idx
                break
        else:
            return blocks  # no tail

        # Collect all lines from the tail
        tail_lines = []
        tail_block_indices = []
        for idx in range(tail_start, len(blocks)):
            btype, blines = blocks[idx]
            if btype == "line":
                # Each line is its own block; we can merge them
                for line in blines:
                    tail_lines.append(line)
                    tail_block_indices.append(idx)
            else:
                # If we encounter a block that is not a line block, we cannot compact beyond it
                # So we stop at the previous block.
                break

        if not tail_lines:
            return blocks

        # Classify each line in tail
        line_types = [self._classify_line(line) for line in tail_lines]
        # Check if all are bias, max, assign_simple, assign_complex
        allowed = {"bias", "max", "assign_simple", "assign_complex"}
        if not all(t in allowed for t in line_types):
            return blocks  # cannot compact

        # Extract register numbers
        reg_data = {}  # reg -> {"bias": line, "max": line, "assign": (line, is_simple)}
        reg_order = []

        for line, typ in zip(tail_lines, line_types):
            # Extract register number
            m_reg = re.search(r"r(\d+)", line)
            if not m_reg:
                # Should not happen for these types, but skip
                continue
            reg = int(m_reg.group(1))
            if reg not in reg_order:
                reg_order.append(reg)

            if typ == "bias":
                reg_data.setdefault(reg, {})["bias"] = line
            elif typ == "max":
                reg_data.setdefault(reg, {})["max"] = line
            elif typ == "assign_simple":
                reg_data.setdefault(reg, {})["assign"] = (line, True)
            elif typ == "assign_complex":
                reg_data.setdefault(reg, {})["assign"] = (line, False)

        # Build compact lines
        compact_lines = []

        # Bias block (if any)
        bias_lines = []
        for reg in reg_order:
            if "bias" in reg_data.get(reg, {}):
                bias_lines.append(reg_data[reg]["bias"])
        if bias_lines:
            compact_lines.extend(bias_lines)
            compact_lines.append("")  # blank line after biases

        # Assignments block
        assign_lines = []
        for reg in reg_order:
            data = reg_data.get(reg, {})
            assign = data.get("assign")
            if assign:
                line, is_simple = assign
                if is_simple:
                    # Combine with max if present
                    if "max" in data:
                        # Replace '= rX;' with '= max(rX, 0.0);'
                        new_line = re.sub(r"= r\d+;", f"= max(r{reg}, 0.0);", line)
                    else:
                        new_line = line
                    assign_lines.append(new_line)
                else:
                    # Complex assignment: output max first (if any) then the assign
                    if "max" in data:
                        assign_lines.append(data["max"])
                    assign_lines.append(line)
            else:
                # No assign? Then just output max if present (should be rare)
                if "max" in data:
                    assign_lines.append(data["max"])
        if assign_lines:
            compact_lines.extend(assign_lines)

        # Replace the tail blocks with a single new block
        new_blocks = blocks[:tail_start]
        if compact_lines:
            new_blocks.append(("compact", compact_lines))
        # Append any blocks after the tail that we didn't include (should be none because we broke at first non-line)
        # But in case there were blocks after, we add them
        if tail_block_indices:
            last_idx = tail_block_indices[-1]
            if last_idx + 1 < len(blocks):
                new_blocks.extend(blocks[last_idx + 1 :])

        return new_blocks

    def _blocks_to_lines(self, blocks: List[Tuple[str, List[str]]]) -> List[str]:
        """Convert blocks back to a flat list of lines, with a blank line between blocks."""
        lines = []
        for i, (_, blines) in enumerate(blocks):
            if i > 0:
                lines.append("")  # blank line between blocks
            lines.extend(blines)
        return lines

    def _reformat_body(self, core_lines: List[str]) -> List[str]:
        """Reformat the core lines: group into blocks and compact the tail."""
        if not core_lines:
            return []

        # Split into blocks
        blocks = self._split_into_blocks(core_lines)

        # Compact the tail if possible
        blocks = self._compact_tail(blocks)

        # Convert blocks back to lines with blank lines between blocks
        return self._blocks_to_lines(blocks)


def extract_license(content: str, start: int = 2) -> str:
    lines = content.splitlines()[start:]  # Ignore title
    license_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("//"):
            license_lines.append(stripped[2:].strip())
        elif license_lines and not stripped:
            break  # end of comment block
        else:
            break
    return "\n".join(license_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Magpie CuNNy shader to Vulkan compute shader format."
    )
    parser.add_argument("shader_path", help="Path to the original .hlsl shader file")
    parser.add_argument(
        "-t",
        "--tile",
        action="store_true",
        help="Generate tile-mode shader (compatible with both direct and cached tile processors)",
    )
    args = parser.parse_args()

    shader_path = args.shader_path
    if not os.path.isfile(shader_path):
        print(f"Error: {shader_path} not found.")
        return

    with open(shader_path, "r") as f:
        content = f.read()

    # Parse the shader
    parser = ShaderParser(content)
    if not parser.passes:
        print("No passes found in the shader.")
        return

    # Configuration
    config = Config(tile=args.tile)

    # Build model.json data
    sampler_map = {s.name: s.filter_type for s in parser.samplers}
    model_builder = ModelJsonBuilder(
        config,
        parser.passes,
        num_textures=(
            parser.max_texture_index + 1 if parser.max_texture_index >= 0 else 0
        ),
        sampler_map=sampler_map,
    )
    model_data = model_builder.build()

    # Output folder
    shader_dir = os.path.dirname(shader_path)
    shader_basename = os.path.splitext(os.path.basename(shader_path))[0]
    output_dir = os.path.join(shader_dir, shader_basename)
    os.makedirs(output_dir, exist_ok=True)

    # Write model.json with the shader name
    model_data["name"] = shader_basename
    with open(os.path.join(output_dir, "model.json"), "w") as f:
        json.dump(model_data, f, indent=2)

    # Generate per-pass HLSL files
    hlsl_gen = HlslGenerator(config, model_name=shader_basename)
    sampler_order = [s.name for s in parser.samplers]

    suffix = "_tile" if config.tile else ""
    total_passes = len(parser.passes)

    for pinfo in parser.passes:
        hlsl = hlsl_gen.generate(
            pinfo,
            sampler_order,
            total_passes,
            extract_license(content),
        )
        out_path = os.path.join(output_dir, f"Pass{pinfo.pass_num}{suffix}.hlsl")
        with open(out_path, "w") as f:
            f.write(hlsl)
        print(f"Written {out_path}")

    print(f"Done. Output in {output_dir}")


if __name__ == "__main__":
    main()
