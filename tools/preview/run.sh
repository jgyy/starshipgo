#!/bin/bash
# usage: tools/preview/run.sh out.png model1.glb model2.glb ...
# Set GODOT to the godot binary (default: godot). Uses xvfb + software Vulkan when no display.
GODOT=${GODOT:-godot}
OUT=$(realpath -m "$1"); shift
FILES=()
for f in "$@"; do FILES+=("$(realpath "$f")"); done
DIR="$(cd "$(dirname "$0")" && pwd)"
RES=${RES:-1600x900}
xvfb-run -a -s "-screen 0 1920x1080x24" $GODOT --path "$DIR" --rendering-driver vulkan --resolution $RES -s res://preview.gd -- "$OUT" "${FILES[@]}" 2>&1 | grep -v -E "ALSA|audio|dummy|^$"
