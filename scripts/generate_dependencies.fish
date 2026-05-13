#!/usr/bin/env fish

# ===================================================================
# Generate Flatpak dependency JSON
# ===================================================================

set root_dir (dirname (dirname (status --current-filename)))
cd "$root_dir"

uv export \
    --format requirements-txt \
    --no-editable \
    --no-emit-project \
    > requirements.txt

pip install \
    --dry-run \
    --report python-dependencies.json \
    -r requirements.txt \
    --prefix /app

rm requirements.txt