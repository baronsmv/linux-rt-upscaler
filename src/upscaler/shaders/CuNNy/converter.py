#!/usr/bin/env python3
"""
Convert a Magpie CuNNy shader to Compushady compute shader format.

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
        """Extract //!IN and //!OUT lists from the pre‑pass lines."""
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
        }

    def _get_filter(self, filter_type: str) -> Optional[str]:
        """Return the first sampler name with the given filter type, or None."""
        for name, ftype in self.sampler_map.items():
            if ftype == filter_type:
                return ftype  # actually the filter string, not the name
        return None


class HlslGenerator:
    """Generates the final HLSL source for a single pass."""

    COMMON_HEADER = """cbuffer Constants : register(b0) {
    uint in_width;
    uint in_height;
    uint out_width;
    uint out_height;
    float in_dx;
    float in_dy;
    float out_dx;
    float out_dy;
};

float2 GetInputPt() { return float2(in_dx, in_dy); }
float2 GetOutputPt() { return float2(out_dx, out_dy); }
uint2 GetInputSize() { return uint2(in_width, in_height); }
uint2 GetOutputSize() { return uint2(out_width, out_height); }

#define O(t, x, y) t.SampleLevel(SP, pos + float2(x, y) * pt, 0)
#define V4 min16float4
#define M4 min16float4x4
#define V3 min16float3
#define M3x4 min16float3x4
"""

    def __init__(self, config: Config, model_name: str) -> None:
        self.config = config
        self.model_name = model_name

    def generate(self, pass_info: PassInfo, sampler_order: List[str]) -> str:
        pass_num = pass_info.pass_num
        in_textures = pass_info.in_textures
        out_textures = pass_info.out_textures
        pre_lines = pass_info.pre_lines
        body = pass_info.body
        is_final = self.config.special_output in out_textures

        # Texture declarations with registers
        tex_decl_lines = self._build_texture_declarations(in_textures, out_textures)

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

        # Build entry point
        entry = self._build_entry(is_final)

        # Assemble everything
        lines = [
            f"// {self.model_name} - Pass {pass_num}",
            "// Adapted for Compushady compute shader",
            "",
            self.COMMON_HEADER.strip(),
            "",
            *tex_decl_lines,
            "",
            *sampler_lines,
            "",
            *l_macros,
            "",
            entry,
        ]
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
        self, in_textures: List[str], out_textures: List[str]
    ) -> List[str]:
        """Return SRV and UAV declaration lines with registers."""
        srv_lines = [
            f"Texture2D<float4> {tex} : register(t{idx});"
            for idx, tex in enumerate(in_textures)
        ]
        uav_lines = [
            f"RWTexture2D<float4> {tex} : register(u{idx});"
            for idx, tex in enumerate(out_textures)
        ]
        if srv_lines and uav_lines:
            return srv_lines + [""] + uav_lines
        return srv_lines + uav_lines

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

    def _classify_line(self, line: str) -> str:
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
        Find the tail region (from the first non‑decl/s_assign/mul_group block onward)
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

        # Now we have a sequence of bias, max, assign lines. We'll group them by register.
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
        for i, (btype, blines) in enumerate(blocks):
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

    def _build_entry(self, is_final: bool) -> str:
        nt = self.config.num_threads
        if is_final:
            return f"""[numthreads({nt[0]},{nt[1]},{nt[2]})]
void {self.config.entry_point}(uint3 id : SV_DispatchThreadID)
{{
    float2 pt = float2(GetInputPt());
    uint2 gxy = id.xy * 2;
    float2 pos = ((gxy >> 1) + 0.5) * pt;
"""
        else:
            return f"""[numthreads({nt[0]},{nt[1]},{nt[2]})]
void {self.config.entry_point}(uint3 id : SV_DispatchThreadID)
{{
    float2 pt = float2(GetInputPt());
    uint2 gxy = id.xy;
    float2 pos = (gxy + 0.5) * pt;
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Magpie CuNNy shader to Compushady format."
    )
    parser.add_argument("shader_path", help="Path to the original .hlsl shader file")
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

    # Configuration (can be extended with command‑line overrides later)
    config = Config()

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

    # Generate per‑pass HLSL files
    hlsl_gen = HlslGenerator(config, model_name=shader_basename)
    sampler_order = [s.name for s in parser.samplers]
    for pinfo in parser.passes:
        hlsl = hlsl_gen.generate(pinfo, sampler_order)
        out_path = os.path.join(output_dir, f"Pass{pinfo.pass_num}.hlsl")
        with open(out_path, "w") as f:
            f.write(hlsl)
        print(f"Written {out_path}")

    print(f"Done. Output in {output_dir}")


if __name__ == "__main__":
    main()
