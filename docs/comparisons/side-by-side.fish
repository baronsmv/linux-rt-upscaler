#!/usr/bin/env fish

set w_start $argv[5]  # left edge (%)
set w_end   $argv[6]  # right edge (%)
set h_start $argv[7]  # top edge (%)
set h_end   $argv[8]  # bottom edge (%)

set resize 400   # enlargement after cropping

# White panel settings
set panel_height 120   # height of the white panel in pixels
set text_pointsize 80 # font size for the caption

# Check that at least two files are provided
if test (count $argv) -lt 2
    echo "Usage: $argv[0] <image1> <image2> [text1] [text2]"
    exit 1
end

# Validate the two input files
for f in $argv[1..2]
    if not test -f "$f"
        echo "File '$f' doesn't exist or is invalid."
        exit 1
    end
end

# Set caption texts (default or user-supplied)
set text1 "Image 1"
set text2 "Image 2"
if test (count $argv) -eq 8
    set text1 $argv[3]
    set text2 $argv[4]
else if test (count $argv) -ne 2
    echo "Please provide either 2 files or 2 files + 2 texts + 4 crop limits."
    exit 1
end

cd (dirname "$argv[1]")

# Get dimensions of the upscaled image (second)
set w_upscaled (magick identify -format "%w" "$argv[2]")
set h_upscaled (magick identify -format "%h" "$argv[2]")

set x_start (math "round($w_upscaled * $w_start / 100)")
set x_end   (math "round($w_upscaled * $w_end / 100)")
set y_start (math "round($h_upscaled * $h_start / 100)")
set y_end   (math "round($h_upscaled * $h_end / 100)")
set width   (math "$x_end - $x_start")
set height  (math "$y_end - $y_start")
set geometry "$width"x"$height"+"$x_start"+"$y_start"

# Create a safe filename from the percentages
set output "w$w_start-$w_end"_h"$h_start-$h_end"_(math "$resize / 100")x
set first_output "$output"_(basename "$argv[1]")
set second_output "$output"_(basename "$argv[2]")

# Process first image: resize to match second, crop, scale, then add white panel with text
magick "$argv[1]" \
    -resize "$w_upscaled"x"$h_upscaled"\! \
    -crop "$geometry" +repage -resize "$resize"% \
    -gravity south -background white -splice 0x"$panel_height" \
    -gravity south -pointsize $text_pointsize -fill black -annotate +0+10 "$text1" \
    "$first_output"

# Process second image: crop, scale, then add white panel with text
magick "$argv[2]" \
    -crop "$geometry" +repage -resize "$resize"% \
    -gravity south -background white -splice 0x"$panel_height" \
    -gravity south -pointsize $text_pointsize -fill black -annotate +0+10 "$text2" \
    "$second_output"

# Combine side-by-side
magick "$first_output" "$second_output" \
    +append "$output"_comparison.png

echo "Done. Comparison image: $output"_comparison.png
