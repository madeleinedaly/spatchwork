#!/usr/bin/env bash

function rand() {
    local default_min=5
    local default_max=23

    if [ $# -eq 1 ]; then
        local min=$default_min
        local max="$1"
    elif [ $# -eq 2 ]; then
        local min="$1"
        local max="$2"
    else
        local min=$default_min
        local max=$default_max
    fi

    echo "$(((RANDOM % max) + 1))"
}

function gen() {
    # 7,40 4,30   4,124 4,123   85,122 100,123   85,2 100,30
    # https://stackoverflow.com/a/12278644

    local sx1=$(rand width)
    local sy1=$(rand height)
    local dx1="$((sx1 - $(rand 9)))"
    local dy1="$((sy1 - $(rand 9)))"

    local sx2="$((dx1 - $(rand 9)))"
    local sy2=$(rand height)
    local dx2="$((sx2 - $(rand 9)))"
    local dy2="$((sy2 - $(rand 9)))"

    local sx3=$(rand width)
    local sy3=$(rand height)
    local dx3="$((sx3 - $(rand 9)))"
    local dy3="$((sy3 - $(rand 9)))"

    local sx4="$((sx3 - $(rand 9)))"
    local sy4=$(rand height)
    local dx4="$((sx4 - $(rand 9)))"
    local dy4="$((sy4 - $(rand 9)))"

    echo "$sx1,$sy1 $dx1,$dy1   $sx2,$sy2 $dx2,$dy2   $sx3,$sy3 $dx3,$dy3   $sx4,$sy4 $dx4,$dy4"
}

read -r src width height <<< $(convert "$1" -format "%f %w %h" info:)

name="${src%.*}"
default_max_transforms=16

for i in $(seq "${2:-$default_max_transforms}"); do
    sha1=$(echo $src $RANDOM | sha1sum | awk '{print $1}')
    dest=$(printf "%s_%s.png" "$name" "$sha1")
    xform=$(gen)

    IFS='%'

    convert                           \
        $src                          \
        -alpha Set                    \
        -virtual-pixel transparent    \
        -distort perspective $xform   \
        $dest &

    unset IFS
done

wait
