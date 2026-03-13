#!/usr/bin/env python3

"""
Split/analyse Magpie‑style or Compushady‑style CuNNy models.
Currently it has many issues, so its output must be reviewed.

Usage:
  # Split a Magpie file into passes and generate config
  python split_magpie_model.py --split input.hlsl output_dir [--name MODEL_NAME]

  # Generate config from an existing directory of Compushady pass files
  python split_magpie_model.py --config pass_dir [--name MODEL_NAME]
"""

import argparse
import glob
import json
import os
import re
import sys


def name_to_logical(name, is_srv, pass_idx, max_idx):
    """
    Convert a shader resource name to a logical name used in the config.
    For SRVs:
      - Pass 1: the only SRV is assumed to be the original input -> "input".
      - Other passes: "InputN" -> "tN".
    For UAVs:
      - If name contains "OutputTex" (or "OUTPUT") -> "output".
      - Otherwise "OutputN" -> the corresponding intermediate texture.
    """
    name_lower = name.lower()
    if is_srv:
        if pass_idx == 0:
            # First pass: only SRV is the input
            return "input"
        else:
            # e.g. Input0 -> t0, Input1 -> t1
            m = re.search(r"input(\d+)", name_lower)
            if m:
                return f"t{m.group(1)}"
            # fallback: use the register index (we'll handle separately)
            return None
    else:
        # UAV
        if (
            "outputtex" in name_lower
            or "output" in name_lower
            and not re.search(r"output\d", name_lower)
        ):
            return "output"
        m = re.search(r"output(\d+)", name_lower)
        if m:
            return f"t{m.group(1)}"
        return None


# Magpie splitter (unchanged)
def parse_magpie_file(content):
    """Return list of passes from a Magpie file."""
    lines = content.splitlines()
    passes = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        m = re.match(r"//!PASS\s+(\d+)", line)
        if m:
            pass_num = int(m.group(1))
            desc = ""
            block_size = 8
            num_threads = 64
            inputs = []
            outputs = []
            j = i + 1
            while j < n:
                l = lines[j].strip()
                if l.startswith("//!DESC"):
                    desc = l.split(" ", 1)[-1] if " " in l else ""
                elif l.startswith("//!BLOCK_SIZE"):
                    try:
                        block_size = int(l.split()[-1])
                    except:
                        pass
                elif l.startswith("//!NUM_THREADS"):
                    try:
                        num_threads = int(l.split()[-1])
                    except:
                        pass
                elif l.startswith("//!IN"):
                    parts = l.split(" ", 1)
                    if len(parts) > 1:
                        names = [x.strip() for x in parts[1].split(",")]
                        inputs = [n.lower() for n in names]
                elif l.startswith("//!OUT"):
                    parts = l.split(" ", 1)
                    if len(parts) > 1:
                        names = [x.strip() for x in parts[1].split(",")]
                        outputs = [n.lower() for n in names]
                elif l.startswith("//!") or l == "":
                    pass
                else:
                    break
                j += 1
            code_start = j
            k = code_start
            while k < n and not lines[k].strip().startswith("//!PASS"):
                k += 1
            code_lines = lines[code_start:k]
            passes.append(
                {
                    "number": pass_num,
                    "desc": desc,
                    "block_size": block_size,
                    "num_threads": num_threads,
                    "inputs": inputs,
                    "outputs": outputs,
                    "code": code_lines,
                }
            )
            i = k
        else:
            i += 1
    return passes


def convert_pass_code(lines):
    """Strip Magpie directives from code lines."""
    return [line for line in lines if not line.strip().startswith("//!")]


def generate_config_from_passes(passes, model_name):
    """Build config dict from list of passes (from Magpie)."""
    all_tex = set()
    for p in passes:
        for name in p["inputs"]:
            if name.startswith("t") and name[1:].isdigit():
                all_tex.add(name)
        for name in p["outputs"]:
            if name.startswith("t") and name[1:].isdigit():
                all_tex.add(name)
    num_textures = 0
    for name in all_tex:
        idx = int(name[1:])
        if idx + 1 > num_textures:
            num_textures = idx + 1

    srv_uav = []
    for p in passes:
        srv = [name.lower() for name in p["inputs"]]
        uav = [name.lower() for name in p["outputs"]]
        srv_uav.append((srv, uav))

    # Sampler usage: assume all passes use point, last also linear if it has 'input'
    samplers = [["point"]] * len(passes)
    if passes and "input" in passes[-1]["inputs"]:
        samplers[-1] = ["point", "linear"]

    return {
        "name": model_name,
        "passes": len(passes),
        "num_textures": num_textures,
        "srv_uav": srv_uav,
        "samplers": samplers,
    }


def do_split(args):
    with open(args.input_file, "r") as f:
        content = f.read()
    passes = parse_magpie_file(content)
    if not passes:
        print("No passes found.")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    for p in passes:
        pass_num = p["number"]
        code = convert_pass_code(p["code"])
        filename = os.path.join(args.output_dir, f"Pass{pass_num}.hlsl")
        with open(filename, "w") as f:
            f.write("\n".join(code))
        print(f"Written {filename}")

    config = generate_config_from_passes(passes, args.name)
    config_file = os.path.join(args.output_dir, "model.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Written {config_file}")


# Config generator from existing pass directory
def parse_pass_file(filepath):
    """
    Parse a single Compushady HLSL pass file.
    Returns (srv_indices, uav_indices, sampler_count) where:
      - srv_indices: list of register indices (int) for input textures (tN)
      - uav_indices: list of register indices (int) for output textures (uN)
      - sampler_count: number of distinct sampler registers (sN)
    """
    srv_indices = []
    uav_indices = []
    samplers = set()
    with open(filepath, "r") as f:
        content = f.read()
    # Remove comments to avoid false positives
    content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)

    # Texture2D<...> name : register(tN)
    pattern_t = r"Texture2D<\s*\S+\s*>\s+\w+\s*:\s*register\s*\(\s*t(\d+)\s*\)"
    for match in re.finditer(pattern_t, content):
        idx = int(match.group(1))
        srv_indices.append(idx)

    # RWTexture2D<...> name : register(uN)
    pattern_u = r"RWTexture2D<\s*\S+\s*>\s+\w+\s*:\s*register\s*\(\s*u(\d+)\s*\)"
    for match in re.finditer(pattern_u, content):
        idx = int(match.group(1))
        uav_indices.append(idx)

    # SamplerState name : register(sN)
    pattern_s = r"SamplerState\s+\w+\s*:\s*register\s*\(\s*s(\d+)\s*\)"
    for match in re.finditer(pattern_s, content):
        samplers.add(int(match.group(1)))

    # Remove duplicates and sort (registers should be unique anyway)
    srv_indices = sorted(set(srv_indices))
    uav_indices = sorted(set(uav_indices))
    return srv_indices, uav_indices, len(samplers)


def generate_config_from_dir(directory, model_name):
    """Scan directory for Pass*.hlsl files and generate config."""
    files = glob.glob(os.path.join(directory, "Pass*.hlsl"))
    if not files:
        print(f"No Pass*.hlsl files found in {directory}")
        sys.exit(1)

    # Sort numerically by the number in the filename
    def pass_number(fname):
        m = re.search(r"Pass(\d+)\.hlsl", os.path.basename(fname))
        return int(m.group(1)) if m else 0

    files.sort(key=pass_number)

    passes_info = []
    max_tex_index = -1
    num_passes = len(files)

    for i, fpath in enumerate(files):
        srv_idxs, uav_idxs, sampler_count = parse_pass_file(fpath)

        # Build SRV logical names
        if i == 0:
            # First pass: only SRV is the original input
            srv_names = ["input"]
            # We don't add any texture index from input because it's not an intermediate texture
        else:
            srv_names = [f"t{idx}" for idx in srv_idxs]
            for idx in srv_idxs:
                if idx > max_tex_index:
                    max_tex_index = idx

        # Build UAV logical names
        if i == num_passes - 1:
            # Last pass: UAV is the final output
            uav_names = ["output"]
            # Do not add output to max_tex_index
        else:
            uav_names = [f"t{idx}" for idx in uav_idxs]
            for idx in uav_idxs:
                if idx > max_tex_index:
                    max_tex_index = idx

        # Sampler usage
        if sampler_count >= 2:
            sampler_usage = ["point", "linear"]
        else:
            sampler_usage = ["point"]

        passes_info.append(
            {"srv": srv_names, "uav": uav_names, "sampler": sampler_usage}
        )

    # Build final config
    srv_uav = [(p["srv"], p["uav"]) for p in passes_info]
    samplers = [p["sampler"] for p in passes_info]
    num_textures = max_tex_index + 1 if max_tex_index >= 0 else 0

    config = {
        "name": model_name,
        "passes": num_passes,
        "num_textures": num_textures,
        "srv_uav": srv_uav,
        "samplers": samplers,
    }
    return config


def do_config(args):
    config = generate_config_from_dir(args.pass_dir, args.name)
    out_path = os.path.join(args.pass_dir, "model.json")
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Written {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Split/analyse CuNNy models.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Split command
    split_parser = subparsers.add_parser(
        "split", help="Split a Magpie file into passes"
    )
    split_parser.add_argument("input_file", help="Path to the combined .hlsl file")
    split_parser.add_argument(
        "output_dir", help="Directory to write pass files and config"
    )
    split_parser.add_argument("--name", default="model", help="Model name")

    # Config command
    config_parser = subparsers.add_parser(
        "config", help="Generate config from existing pass files"
    )
    config_parser.add_argument("pass_dir", help="Directory containing Pass*.hlsl files")
    config_parser.add_argument("--name", default="model", help="Model name")

    args = parser.parse_args()

    if args.command == "split":
        do_split(args)
    elif args.command == "config":
        do_config(args)


if __name__ == "__main__":
    main()
