#!/usr/bin/env fish

# ===================================================================
# Convert HLSL to SPV
# ===================================================================

set root_dir (dirname (dirname (status --current-filename)))
set project_dir "$root_dir/src/upscaler"

if not test (which dxc)
    echo "'dxc' must be installed or in PATH."
    return
end

function hlsl_to_spv -a hlsl
    set spv (echo "$hlsl" | sed 's/\.hlsl/\.spv/')
    dxc -T cs_6_0 -E main -spirv "$hlsl" \
        -fvk-auto-shift-bindings \
        -fvk-t-shift 1024 0 \
        -fvk-u-shift 2048 0 \
        -fvk-s-shift 3072 0 \
        -fvk-use-dx-layout \
        -fvk-use-scalar-layout \
        -Fo "$spv"
end

for hlsl in (
    find "$project_dir" \
        -mindepth 3 \
        -type f \
        -not -path '*/[@.]*' \
        -name '*.hlsl'
)
    echo "Converting '$hlsl'..."
    hlsl_to_spv "$hlsl"
end
