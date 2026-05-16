#!/usr/bin/env fish

# ===================================================================
# Generate Flatpak dependency JSON
# ===================================================================

set root_dir (dirname (dirname (status --current-filename)))
cd "$root_dir"

if not test -f flatpak-pip-generator.py
    wget https://raw.githubusercontent.com/flatpak/flatpak-builder-tools/master/pip/flatpak-pip-generator.py
    chmod +x flatpak-pip-generator.py
end

uv run python3 flatpak-pip-generator.py \
    --runtime='org.kde.Sdk//6.10' \
    --output python-dependencies \
    pybind11 numpy pillow platformdirs psutil pyyaml screeninfo xcffib