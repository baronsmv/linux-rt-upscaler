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
    if echo "$hlsl" | grep -q "fsr"
        # FSR shader
        dxc -spirv "$hlsl" \
            -Fo "$spv" \
            -T cs_6_2 \
            -E main \
            -fvk-auto-shift-bindings \
            -fvk-t-shift 1024 0 \
            -fvk-u-shift 2048 0 \
            -fvk-s-shift 3072 0 \
            -D SAMPLE_EASU=1 \
            -D A_GPU=1 \
            -D A_HLSL=1 \
            -D A_HLSL_6_2=1 \
            -D A_NO_16_BIT_CAST=1 \
            -D WIDTH=64 \
            -D HEIGHT=1 \
            -D DEPTH=1 \
            -enable-16bit-types \
            -I (dirname "$hlsl")
    else
        dxc -spirv "$hlsl" \
            -Fo "$spv" \
            -T cs_6_0 \
            -E main \
            -fvk-auto-shift-bindings \
            -fvk-t-shift 1024 0 \
            -fvk-u-shift 2048 0 \
            -fvk-s-shift 3072 0 \
            -fvk-use-dx-layout \
            -fvk-use-scalar-layout
    end
end

for hlsl in (
    find "$project_dir" \
        -mindepth 3 \
        -type f \
        -not -path '*/[@.]*' \
        -name '*.hlsl' \
    | grep "$argv"
)
    echo "Converting '$hlsl'..."
    hlsl_to_spv "$hlsl"
end
