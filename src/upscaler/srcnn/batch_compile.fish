#!/usr/bin/env fish

set dir (dirname (status --current-filename))
set cnn_dir "$dir/cunny"
set models 3x12 4x12 4x16 4x24 4x32 8x32 fast faster veryfast

if not test (which dxc)
    echo "'dxc' must be installed or in PATH."
    return
end

function to_spv -a hlsl
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

for model in $models
    set original_model "$cnn_dir/.originals/CuNNy-$model-NVL"
    set model_dir "$cnn_dir/$model"

    if test -d "$model_dir"
        rm -r "$model_dir"
    end

    "$cnn_dir/converter.py" "$original_model.hlsl"
    "$cnn_dir/converter.py" -m tile "$original_model.hlsl"
    "$cnn_dir/converter.py" -m cache "$original_model.hlsl"

    mv "$original_model" "$model_dir"
end

for hlsl in (find (dirname "$dir") -mindepth 1 -type f -not -path '*/[@.]*' -name '*.hlsl')
    to_spv "$hlsl"
end
