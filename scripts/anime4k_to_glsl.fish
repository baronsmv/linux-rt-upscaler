#!/usr/bin/env fish

# ===================================================================
# Convert CuNNy Magpie to agnostic HLSL
# ===================================================================

set root_dir (dirname (dirname (status --current-filename)))
set project_dir "$dir/src/upscaler"
set anime4k_dir "$dir/srcnn/anime4k"
set models (ls "$anime4k_dir/.originals")

for model in $models
    set original_model "$anime4k_dir/.originals/$model"
    set model_subdir (
        echo "$original_model" \
            | sed 's|_|/|1; s|_|/|1' \
            | tr '[:upper:]' '[:lower:]'
        )
    set model_dir "$anime4k_dir/$model_subdir"

    if test -d "$model_dir"
        rm -r "$model_dir"
    end

    "$anime4k_dir/converter.py" "$original_model.hlsl"
    "$anime4k_dir/converter.py" -t "$original_model.hlsl"

    mv "$original_model" "$model_dir"
end