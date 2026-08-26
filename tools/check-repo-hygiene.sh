#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bad_re='\.(sys|dll|cat|mbn|elf|bin|etl|dmp|pcap|pcapng)$'
if git ls-files | grep -Ei "$bad_re"; then
  echo 'ERROR: proprietary/raw binary type is tracked.' >&2
  exit 1
fi
if git grep -nEi '(gho_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)' -- ':!tools/check-repo-hygiene.sh' >/tmp/sp11camera-hygiene.$$ 2>/dev/null; then
  cat /tmp/sp11camera-hygiene.$$
  rm -f /tmp/sp11camera-hygiene.$$
  echo 'ERROR: possible credential-like material found.' >&2
  exit 1
fi
rm -f /tmp/sp11camera-hygiene.$$
echo 'repository hygiene: OK'
