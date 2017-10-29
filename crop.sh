#!/usr/bin/env bash

dir="$1"
cd $dir

for file in *; do
    filename=$(basename "$file")
    name="${filename%%.*}"

    result="${name}_%04d.jpeg"

    convert -crop 400x325 $file $result
    cp -v $result ../images
done

cd ..
python crop_swatches.py
