#!/usr/bin/env fish

# ===================================================================
# Convert Anime4k MPV to agnostic GLSL
# ===================================================================

set root_dir (dirname (dirname (status --current-filename)))
set project_dir "$root_dir/src/upscaler"
set anime4k_dir "$project_dir/srcnn/anime4k"
set models (ls "$anime4k_dir/.originals" | sed 's/.glsl$//')

for model in $models
    set original_model "$anime4k_dir/.originals/$model"
    set model_subdir (
        echo "$model" \
            | sed 's|^Anime4K_||; s|_|/|1' \
            | tr '[:upper:]' '[:lower:]'
        )
    set model_dir "$anime4k_dir/$model_subdir"

    if test -d "$model_dir"
        rm -r "$model_dir"
    end

    "$anime4k_dir/converter.py" "$original_model.glsl"
    "$anime4k_dir/converter.py" -t "$original_model.glsl"

    mkdir -p (dirname "$model_dir")
    mv "$original_model" "$model_dir"
end