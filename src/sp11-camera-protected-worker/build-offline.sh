#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel)"
OUT=${1:-/tmp/sp11-camera-protected-worker-build}
ORACLE=${SP11_CAMERA_WORKER_ORACLE:-$REPO/experiments/E004-front-ir-vd55g0/e004dh-swab-exact-offline-port/oracle/windows-sync-oracle}
INPUT="$ORACLE/input-644x604-nv12.bin"
WINDOWS="$ORACLE/windows-trustlet-sync-swasf-644x604-stable.bin"
[ "$(sha256sum "$INPUT"|awk '{print $1}')" = 1dbcc3b8f460565acd80b5efda6a8ef9457768ab2c977f91e2754c4f54abdb3d ] || { echo oracle_input_drift >&2; exit 1; }
[ "$(sha256sum "$WINDOWS"|awk '{print $1}')" = 9ef2dc6179d6151910ff524e4821328ffddfdd151996463c08b904673688ccbf ] || { echo windows_oracle_drift >&2; exit 1; }
rm -rf "$OUT"; mkdir -p "$OUT"
CORE=(sp11-securepd-camera-wire.c sp11-parity-worker.c sp11-swabf-reference.c sp11-swasf-reference.c sp11-swasf-windows-tuning.c sp11-swasf-helpers.c sp11-swasf-c230.c sp11-swasf-c3e8.c sp11-swasf-cd90.c)
clang -std=c11 -O2 -Wall -Wextra -Werror -I"$ROOT" "${CORE[@]/#/$ROOT/}" "$ROOT/test_camera_wire.c" -o "$OUT/wire-vectors"
"$OUT/wire-vectors" | tee "$OUT/WIRE-VECTORS.txt"
clang -std=c11 -O2 -Wall -Wextra -Werror -I"$ROOT" "${CORE[@]/#/$ROOT/}" "$ROOT/test_camera_wire_fullframe.c" -o "$OUT/wire-full"
"$OUT/wire-full" "$INPUT" "$WINDOWS" | tee "$OUT/FULLFRAME-DIFFERENTIAL.txt"
clang -std=c11 -O2 -Wall -Wextra -Werror -I"$ROOT" "$ROOT/sp11-loadalgo-camera-proxy.c" "${CORE[@]/#/$ROOT/}" "$ROOT/test_proxy_contract.c" -o "$OUT/proxy-contract"
"$OUT/proxy-contract" | tee "$OUT/PROXY-CONTRACT.txt"
NATIVE=(sp11-securepd-native-binding.c sp11-securepd-camera-wire.c sp11-parity-worker.c sp11-swabf-reference.c sp11-swasf-reference.c sp11-swasf-windows-tuning.c sp11-swasf-helpers.c sp11-swasf-c230.c sp11-swasf-c3e8.c sp11-swasf-cd90.c)
for f in "${NATIVE[@]}"; do
  clang --target=hexagon -mcpu=hexagonv73 -O2 -ffreestanding -fno-builtin -fno-pic -fno-pie -Wall -Wextra -Werror -I"$ROOT" -c "$ROOT/$f" -o "$OUT/${f%.c}.o"
done
ld.lld -m hexagonelf -r $(printf '%s\n' "$OUT"/*.o | sort) -o "$OUT/sp11-camera-protected-worker.hexagon-v73.o"
llvm-nm -u "$OUT/sp11-camera-protected-worker.hexagon-v73.o" | sort > "$OUT/UNRESOLVED.txt"
cat > "$OUT/EXPECTED-UNRESOLVED.txt" <<'EOT'
         U dsc_verify_buffer
         U get_secure_channel_handle
         U qurt_sleep
         U secure_pd_mapping_create_64
         U secure_pd_mapping_delete_64
         U secure_pd_mb_delete
         U secure_pd_mb_get
         U secure_pd_mb_receive
         U secure_pd_mb_send
         U secure_pd_thread_create
EOT
cmp "$OUT/UNRESOLVED.txt" "$OUT/EXPECTED-UNRESOLVED.txt"
[ "$(sha256sum "$OUT/sp11-camera-protected-worker.hexagon-v73.o"|awk '{print $1}')" = 4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48 ] || { echo native_object_drift >&2; exit 1; }
llvm-nm --defined-only "$OUT/sp11-camera-protected-worker.hexagon-v73.o" | grep -q ' algo_main$'
llvm-nm --defined-only "$OUT/sp11-camera-protected-worker.hexagon-v73.o" | grep -q ' sp11_securepd_camera_worker_thread$'
printf 'SP11_CAMERA_PROTECTED_WORKER_OFFLINE=PASS SIGNED=NO ADMITTED=NO RUNTIME=NO\n'
sha256sum "$OUT/sp11-camera-protected-worker.hexagon-v73.o"
