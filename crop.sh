#!/usr/bin/env bash

cd images
for file in *; do
    filename=$(basename "$file")
    name="${filename%%.*}"

    convert -crop 400x325 $file "${name}_%04d.jpeg"
done

cd ..
python crop_swatches.py
