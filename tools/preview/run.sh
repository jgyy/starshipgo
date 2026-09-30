#!/bin/bash
# usage: tools/preview/run.sh out.png model1.glb model2.glb ...
# Set GODOT to the godot binary (default: godot). Uses xvfb + software Vulkan when there is no display.
set -o pipefail
if [ "$#" -lt 2 ]; then
    echo "usage: $0 out.png model1.glb [model2.glb ...]" >&2
    exit 2
fi
GODOT=${GODOT:-godot}
OUT=$(realpath -m "$1"); shift
FILES=()
for f in "$@"; do
    [ -f "$f" ] || { echo "no such file: $f" >&2; exit 2; }
    FILES+=("$(realpath "$f")")
done
DIR="$(cd "$(dirname "$0")" && pwd)"
RES=${RES:-1600x900}
RUN=()
if [ -z "$DISPLAY" ]; then RUN=(xvfb-run -a -s "-screen 0 1920x1080x24"); fi
"${RUN[@]}" $GODOT --path "$DIR" --rendering-driver vulkan --resolution $RES -s res://preview.gd -- "$OUT" "${FILES[@]}" 2>&1 | grep -v -E "ALSA|audio|dummy|^$"
status=${PIPESTATUS[0]}
[ -f "$OUT" ] || { echo "preview was not written" >&2; exit 1; }
exit $status
