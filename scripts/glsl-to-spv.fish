#!/usr/bin/env fish

# ===================================================================
# Convert GLSL to SPV
# ===================================================================

set root_dir (dirname (dirname (status --current-filename)))
set project_dir "$root_dir/src/upscaler"

if not test (which glslc)
    echo "'glslc' must be installed or in PATH."
    return
end

function glsl_to_spv -a glsl
    set spv (echo "$glsl" | sed 's/\.glsl/\.spv/')
    glslc -fshader-stage=compute "$glsl" -o "$spv"
end

for glsl in (
    find "$project_dir" \
        -mindepth 3 \
        -type f \
        -not -path '*/[@.]*' \
        -name '*.glsl'
)
    echo "Converting '$glsl'..."
    glsl_to_spv "$glsl"
end
