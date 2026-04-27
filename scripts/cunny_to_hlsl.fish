#!/usr/bin/env fish

# ===================================================================
# Convert CuNNy Magpie to agnostic HLSL
# ===================================================================

set root_dir (dirname (dirname (status --current-filename)))
set project_dir "$dir/src/upscaler"
set cunny_dir "$dir/srcnn/cunny"
set models 3x12 4x12 4x16 4x24 4x32 8x32 fast faster veryfast

for model in $models
    set original_model "$cunny_dir/.originals/CuNNy-$model-NVL"
    set model_dir "$cunny_dir/$model"

    if test -d "$model_dir"
        rm -r "$model_dir"
    end

    "$cunny_dir/converter.py" "$original_model.hlsl"
    "$cunny_dir/converter.py" -t "$original_model.hlsl"

    mv "$original_model" "$model_dir"
end