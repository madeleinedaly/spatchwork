#!/usr/bin/env bash

function rand() {
    local min="$1"
    local max="$2"

    echo "$(((RANDOM % max) + min))"
}

# https://stackoverflow.com/a/12278644
function gen() {
    local sx1=$(rand 1 width)
    local sy1=$(rand 1 height)
    local dx1="$((sx1 - $(rand 1 7)))"
    local dy1="$((sy1 - $(rand 1 7)))"

    local sx2="$((dx1 - $(rand 1 7)))"
    local sy2=$(rand 1 height)
    local dx2="$((sx2 - $(rand 1 7)))"
    local dy2="$((sy2 - $(rand 1 7)))"

    local sx3=$(rand 1 width)
    local sy3=$(rand 1 height)
    local dx3="$((sx3 - $(rand 1 7)))"
    local dy3="$((sy3 - $(rand 1 7)))"

    local sx4="$((sx3 - $(rand 1 7)))"
    local sy4=$(rand 1 height)
    local dx4="$((sx4 - $(rand 1 7)))"
    local dy4="$((sy4 - $(rand 1 7)))"

    echo "$sx1,$sy1 $dx1,$dy1   $sx2,$sy2 $dx2,$dy2   $sx3,$sy3 $dx3,$dy3   $sx4,$sy4 $dx4,$dy4"
}

function tilt() {
    local sha1=$(echo $src $RANDOM | sha1sum | awk '{print $1}')
    local dest=$(printf "%s_%s.png" "$name" "$sha1")

    local xform=$(gen)
    local delta=$(rand 1 359)

    IFS='%'
    convert                           \
        $src                          \
        -rotate $delta                \
        -alpha Set                    \
        -virtual-pixel transparent    \
        -distort perspective $xform   \
        $dest &

    unset IFS
}

read -r src width height <<< $(convert "$1" -format "%f %w %h" info:)

name="${src%.*}"
default_max_transforms=16

for i in $(seq "${2:-$default_max_transforms}"); do
    tilt &
done
