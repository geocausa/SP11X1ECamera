#!/usr/bin/env bash
set -Eeuo pipefail
D=/var/lib/sp11-camera-e004md
[[ "$EUID" == 0 ]]
case "${1:-}" in
 front) key=front_rdi_video_device; route=front-rdi-only;;
 rear) key=rear_video_device; route=rear-only;;
 *) exit 2;;
esac
exec 9>"$D/session.lock"
/usr/bin/flock -n 9 || exit 75
/usr/bin/sha256sum -c "$D/SESSION-ASSETS.sha256" >/dev/null
source_node=$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$D/output/UNIFIED.json" "$key")
media=$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["media"])' "$D/output/UNIFIED.json")
media-ctl -d "$media" -p > "$D/output/$1-SERVICE-GRAPH.txt"
/usr/bin/python3 "$D/route-state.py" "$D/output/$1-SERVICE-GRAPH.txt" --expect "$route"
exec "$D/bridge/$1-direct-publisher" --source "$source_node" continuous
