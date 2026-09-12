#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 install|rollback STAGE_ROOT TARGET_ROOT [--allow-real-root]" >&2
  exit 2
}

[ $# -ge 3 ] || usage
ACTION=$1
STAGE=$2
ROOT=$3
shift 3
ALLOW_REAL=0
[ $# -eq 0 ] || { [ $# -eq 1 ] && [ "$1" = '--allow-real-root' ] || usage; ALLOW_REAL=1; }

fail() { echo "FAIL: $*" >&2; exit 1; }
STAGE=$(realpath -m "$STAGE")
ROOT=$(realpath -m "$ROOT")
[ "$ROOT" != / ] || [ "$ALLOW_REAL" -eq 1 ] || fail 'TARGET_ROOT=/ requires --allow-real-root'
[ "$ACTION" = install ] || [ "$ACTION" = rollback ] || usage

PREFIX="$ROOT/usr/lib/sp11-front-imx681"
BINDIR="$ROOT/usr/bin"
STATE="$ROOT/var/lib/sp11-front-imx681"
RECEIPT="$STATE/current-install.env"
LOCK="$STATE/install.lock"
PKG_SHA=
if [ "$ACTION" = install ]; then
  [ -f "$STAGE/PACKAGE-MANIFEST.sha256" ] || fail 'package manifest missing'
  [ -d "$STAGE/usr/lib/sp11-front-imx681" ] || fail 'package prefix missing'
  [ -f "$STAGE/usr/bin/sp11-front-imx681" ] || fail 'launcher wrapper missing'
  [ -f "$STAGE/usr/bin/sp11-front-imx681-discover" ] || fail 'discover wrapper missing'
  (cd "$STAGE" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail 'package manifest verification failed'
  PKG_SHA=$(sha256sum "$STAGE/PACKAGE-MANIFEST.sha256" | awk '{print $1}')
fi
mkdir -p "$STATE"
exec 9>"$LOCK"
flock -n 9 || fail 'another install transaction holds the lock'

restore_backup() {
  local backup=$1
  rm -rf "$PREFIX"
  rm -f "$BINDIR/sp11-front-imx681" "$BINDIR/sp11-front-imx681-discover"
  if [ -d "$backup/usr/lib/sp11-front-imx681" ]; then
    mkdir -p "$ROOT/usr/lib"
    mv "$backup/usr/lib/sp11-front-imx681" "$PREFIX"
  fi
  for f in sp11-front-imx681 sp11-front-imx681-discover; do
    if [ -f "$backup/usr/bin/$f" ]; then
      mkdir -p "$BINDIR"
      mv "$backup/usr/bin/$f" "$BINDIR/$f"
    fi
  done
}

if [ "$ACTION" = rollback ]; then
  [ -f "$RECEIPT" ] || fail 'no install receipt to roll back'
  BACKUP_DIR=$(sed -n 's/^BACKUP_DIR=//p' "$RECEIPT")
  [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ] || fail 'receipt backup directory missing'
  restore_backup "$BACKUP_DIR"
  rm -f "$RECEIPT"
  printf 'STATUS=ROLLBACK_PASS\nTIME=%s\nRESTORED_FROM=%s\n' "$(date -Ins)" "$BACKUP_DIR" > "$STATE/last-rollback.env"
  echo "FRONT_IMX681_ROLLBACK=PASS ROOT=$ROOT"
  exit 0
fi

TMP_PREFIX="$ROOT/usr/lib/.sp11-front-imx681.new.$$"
TMP_BIN1="$BINDIR/.sp11-front-imx681.new.$$"
TMP_BIN2="$BINDIR/.sp11-front-imx681-discover.new.$$"
BACKUP="$STATE/backup-$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$ROOT/usr/lib" "$BINDIR" "$BACKUP/usr/lib" "$BACKUP/usr/bin"
rm -rf "$TMP_PREFIX"; rm -f "$TMP_BIN1" "$TMP_BIN2"
mkdir "$TMP_PREFIX"
cp -a "$STAGE/usr/lib/sp11-front-imx681/." "$TMP_PREFIX/"
cp -a "$STAGE/usr/bin/sp11-front-imx681" "$TMP_BIN1"
cp -a "$STAGE/usr/bin/sp11-front-imx681-discover" "$TMP_BIN2"
diff -qr "$STAGE/usr/lib/sp11-front-imx681" "$TMP_PREFIX" >/dev/null || fail 'staged prefix copy mismatch'
cmp -s "$STAGE/usr/bin/sp11-front-imx681" "$TMP_BIN1" || fail 'launcher wrapper copy mismatch'
cmp -s "$STAGE/usr/bin/sp11-front-imx681-discover" "$TMP_BIN2" || fail 'discover wrapper copy mismatch'

COMMITTED=0
rollback_on_error() {
  local rc=$?
  if [ "$COMMITTED" -eq 0 ]; then
    restore_backup "$BACKUP" || true
    rm -rf "$TMP_PREFIX"; rm -f "$TMP_BIN1" "$TMP_BIN2"
  fi
  exit "$rc"
}
trap rollback_on_error ERR

[ ! -e "$PREFIX" ] || mv "$PREFIX" "$BACKUP/usr/lib/sp11-front-imx681"
for f in sp11-front-imx681 sp11-front-imx681-discover; do
  [ ! -e "$BINDIR/$f" ] || mv "$BINDIR/$f" "$BACKUP/usr/bin/$f"
done
mv "$TMP_PREFIX" "$PREFIX"
mv "$TMP_BIN1" "$BINDIR/sp11-front-imx681"
mv "$TMP_BIN2" "$BINDIR/sp11-front-imx681-discover"
TMP_RECEIPT="$STATE/.current-install.env.$$"
printf 'STATUS=INSTALLED\nTIME=%s\nPACKAGE_MANIFEST_SHA256=%s\nBACKUP_DIR=%s\n' "$(date -Ins)" "$PKG_SHA" "$BACKUP" > "$TMP_RECEIPT"
mv "$TMP_RECEIPT" "$RECEIPT"
COMMITTED=1
trap - ERR
sync -f "$STATE" 2>/dev/null || true
echo "FRONT_IMX681_INSTALL=PASS ROOT=$ROOT PACKAGE_MANIFEST_SHA256=$PKG_SHA"
