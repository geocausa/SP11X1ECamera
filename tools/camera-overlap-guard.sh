#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"
require_clean=0; require_golden=0; require_no_camera_process=0
expect_head=""; expect_origin=""; stage_free=""
while (($#)); do
  case "$1" in
    --require-clean-tracked) require_clean=1; shift ;;
    --require-golden) require_golden=1; shift ;;
    --require-no-camera-process) require_no_camera_process=1; shift ;;
    --expect-head) expect_head="${2:?missing SHA}"; shift 2 ;;
    --expect-origin) expect_origin="${2:?missing SHA}"; shift 2 ;;
    --stage-free) stage_free="${2:?missing stage prefix}"; shift 2 ;;
    -h|--help) echo "camera-overlap-guard: read-only concurrency/Golden preflight"; exit 0 ;;
    *) echo "OVERLAP_GUARD=FAIL unknown option: $1" >&2; exit 2 ;;
  esac
done
branch="$(git branch --show-current)"
head="$(git rev-parse HEAD)"
upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
origin=""; [[ -z "$upstream" ]] || origin="$(git rev-parse "$upstream" 2>/dev/null || true)"
tracked_dirty="$(git status --porcelain=v1 -uno | wc -l | tr -d ' ')"
untracked="$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')"
boot_id="$(cat /proc/sys/kernel/random/boot_id 2>/dev/null || true)"
kernel="$(uname -r 2>/dev/null || true)"
cmdline="$(cat /proc/cmdline 2>/dev/null || true)"
grubenv="$(grub-editenv list 2>/dev/null || true)"
saved_entry="$(printf '%s\n' "$grubenv" | sed -n 's/^saved_entry=//p' | head -1)"
next_entry="$(printf '%s\n' "$grubenv" | sed -n 's/^next_entry=//p' | head -1)"
nodes="$(compgen -G '/dev/video*' || true; compgen -G '/dev/media*' || true)"
mods="$(lsmod 2>/dev/null | awk '$1 ~ /^(qcom_camss|imx681|ov13858)$/ {print $1}' || true)"
procs="$(ps -eo pid=,cmd= | grep -E 'libcamera|v4l2-ctl|ffmpeg|gst-launch|e003i-[a-z0-9-]*native-aec|camera-e003|make-(nine|eleven|twelve|fifteen|eighteen|twentyone|twentyfour|twentyseven)-frame|live-iq-producer.py' | grep -v -E 'grep -E|camera-overlap-guard' || true)"
printf 'OVERLAP_GUARD branch=%s head=%s upstream=%s origin=%s tracked_dirty=%s untracked=%s\n' "$branch" "$head" "${upstream:-none}" "${origin:-none}" "$tracked_dirty" "$untracked"
printf 'OVERLAP_GUARD boot_id=%s kernel=%s saved_entry=%s next_entry=%s nodes=%s modules=%s active_processes=%s\n' "${boot_id:-unknown}" "${kernel:-unknown}" "${saved_entry:-unknown}" "${next_entry:-}" "$( [[ -n "$nodes" ]] && echo yes || echo no )" "$( [[ -n "$mods" ]] && echo "$mods" | tr '\n' ',' || echo none )" "$( [[ -n "$procs" ]] && echo yes || echo no )"
fail=0
[[ -z "$expect_head" || "$head" == "$expect_head" ]] || { echo "OVERLAP_GUARD=FAIL expected HEAD $expect_head, got $head" >&2; fail=1; }
[[ -z "$expect_origin" || "$origin" == "$expect_origin" ]] || { echo "OVERLAP_GUARD=FAIL expected origin $expect_origin, got ${origin:-none}" >&2; fail=1; }
(( ! require_clean )) || [[ "$tracked_dirty" == 0 ]] || { echo "OVERLAP_GUARD=FAIL tracked tree is dirty" >&2; fail=1; }
if ((require_golden)); then
  [[ "$cmdline" == *"/boot/sp11-7.1.5-audio-fullio-v19c/"* && "$saved_entry" == "sp11-audio-fullio-v19c" && -z "$next_entry" && -z "$nodes" && -z "$mods" ]] || { echo "OVERLAP_GUARD=FAIL protected Golden invariant not satisfied" >&2; fail=1; }
fi
(( ! require_no_camera_process )) || [[ -z "$procs" ]] || { echo "OVERLAP_GUARD=FAIL active camera/build process detected" >&2; printf '%s\n' "$procs" >&2; fail=1; }
if [[ -n "$stage_free" ]]; then
  base_stage="experiments/E003-front-imx681-cphy/e003i-front-native-productionization"
  hits="$(find "$base_stage" -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | grep -E "^${stage_free}-" || true)"
  [[ -z "$hits" ]] || { echo "OVERLAP_GUARD=FAIL stage prefix '$stage_free' already exists: $hits" >&2; fail=1; }
fi
((fail==0)) || exit 1
echo OVERLAP_GUARD=PASS
