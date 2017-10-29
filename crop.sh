#!/usr/bin/env bash

dir="$1"
cd $dir

for file in *; do
    local filename=$(basename "$file")
    local name="${filename%%.*}"

    local result="${name}_%04d.jpeg"

    convert -crop 400x325 $file $result
    cp -v $result ../images
done

cd ..
python crop_swatches.py
