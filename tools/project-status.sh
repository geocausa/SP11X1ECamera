#!/usr/bin/env bash
set -u
repo="$(cd "$(dirname "$0")/.." && pwd)"
printf '== SP11 camera project ==\n'
printf 'repo: %s\n' "$repo"
cd "$repo"
printf 'git:  '; git status --short --branch 2>/dev/null || true
printf 'head: '; git rev-parse --short HEAD 2>/dev/null || echo '(no commit)'

printf '\n== live Linux ==\n'
uname -a 2>/dev/null || true
printf 'cmdline: '; cat /proc/cmdline 2>/dev/null || true; echo
printf 'video nodes: '; compgen -G '/dev/video*' | tr '\n' ' '; echo
printf 'media nodes: '; compgen -G '/dev/media*' | tr '\n' ' '; echo
k="$(uname -r 2>/dev/null || true)"
if [ -n "$k" ] && [ -d "/lib/modules/$k" ]; then
  printf 'module build: '; readlink -f "/lib/modules/$k/build" 2>/dev/null || echo '(none)'
  printf 'module source: '; readlink -f "/lib/modules/$k/source" 2>/dev/null || echo '(none)'
  printf 'qcom-camss: '; find "/lib/modules/$k" -name 'qcom-camss.ko*' -print -quit 2>/dev/null || true
  printf 'i2c-qcom-cci: '; find "/lib/modules/$k" -name 'i2c-qcom-cci.ko*' -print -quit 2>/dev/null || true
fi
printf '\n== camera dmesg summary ==\n'
sudo -n dmesg 2>/dev/null | grep -Ei 'camera|camss|csiphy|csid|vfe|cci|videocc' | tail -60 || true
printf '\n== durable state ==\n'
grep -E '^(state_id|phase|current_experiment|next_experiment|next_action):' state/project.yaml || true
