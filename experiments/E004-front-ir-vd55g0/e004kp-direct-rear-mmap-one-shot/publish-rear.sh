#!/usr/bin/env bash
set +e
timeout --foreground --signal=TERM --kill-after=3s 220s /var/lib/sp11-camera-e004kp/bridge/rear-direct-publisher --source "$1" 2400 > "$2/REAR-DIRECT-PUBLISHER-STDOUT.txt" 2> "$2/REAR-DIRECT-PUBLISHER.json"
rc=$?
printf 'PUBLISHER_END_NS=%s\n' "$(date +%s%N)" > "$2/REAR-4K-PUBLISHER-DONE.txt"
exit "$rc"
