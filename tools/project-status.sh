#!/usr/bin/env bash
set -u
repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"
echo '== SP11 camera project =='
printf 'repo: %s\n' "$repo"
printf 'branch: '; git branch --show-current 2>/dev/null || true
printf 'head:   '; git rev-parse HEAD 2>/dev/null || true
printf 'origin: '; git rev-parse '@{u}' 2>/dev/null || echo '(no upstream)'
printf 'tracked changes: '; git status --porcelain=v1 -uno | wc -l
printf 'untracked files:  '; git ls-files --others --exclude-standard | wc -l
echo; echo '== overlap/live-state summary =='
"$repo/tools/camera-overlap-guard.sh" || true
echo; echo '== durable frontier =='
grep -E '^(updated|state_id|phase|status|current_experiment|current_gate|next_experiment):' state/project.yaml | head -20 || true
echo 'handoff: HANDOFF.md'
echo; echo '== recent camera commits =='
git log --oneline -12 2>/dev/null || true
