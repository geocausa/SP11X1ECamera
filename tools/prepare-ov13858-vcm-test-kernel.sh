#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Stage and compile the upstream DW9800K vddio RFC in a throwaway worktree.
# Does NOT install a kernel, change GRUB, alter /boot, or touch a Golden image.
set -euo pipefail

usage() {
  echo "Usage: $0 <local-linux-git-clone> <new-scratch-directory> [kernel-commit] [--full-kernel]" >&2
  echo "Only an isolated worktree/out tree is modified. 'full-kernel' builds Image/dtbs/modules, NOT an installable SP11 camera system." >&2
  exit 2
}
[[ $# -ge 2 && $# -le 4 ]] || usage

repo=$(realpath "$1")
scratch=$(realpath -m "$2")
ref=${3:-c44104f3642da720164042623e4832836aefdd8e}
full=${4:-}
[[ -z "$full" || "$full" == "--full-kernel" ]] || usage
[[ "$ref" != "--full-kernel" ]] || usage
[[ ! -e "$scratch" ]] || { echo "Refusing to replace existing scratch directory" >&2; exit 1; }
[[ "$scratch" != /boot* && "$scratch" != /lib/modules* && "$scratch" != /usr* ]] || {
  echo "Refusing system/kernel installation paths" >&2; exit 1;
}
command -v git >/dev/null
command -v make >/dev/null

# Native ARM64 GCC is a supported alternative on the SP11 itself.
# Prefer LLVM where available, otherwise require native ARM64 GCC.
if command -v clang >/dev/null; then
  compiler_args=(LLVM=1)
  compiler_name=clang
else
  [[ "$(uname -m)" == "aarch64" ]] || {
    echo "No clang: GCC fallback is only supported for native ARM64 hosts" >&2
    exit 1
  }
  command -v gcc >/dev/null || { echo "Missing native ARM64 GCC" >&2; exit 1; }
  compiler_args=()
  compiler_name=gcc
fi
echo "Using $compiler_name for an isolated ARM64 build"
git -C "$repo" rev-parse --is-inside-work-tree >/dev/null
rev=$(git -C "$repo" rev-parse --verify "$ref^{commit}")
driver=$(git -C "$repo" rev-parse "$rev:drivers/media/i2c/dw9719.c")
binding=$(git -C "$repo" rev-parse "$rev:Documentation/devicetree/bindings/media/i2c/dongwoon,dw9719.yaml")
[[ "$driver" == 5d5da0439dba01e5d9c458e6c357d579b5c54157 ]] || {
  echo "Upstream driver has changed: must rebase/review RFC" >&2; exit 1;
}
[[ "$binding" == 8e8d62436e0d0c4f9af9e52262b23881abd37cec ]] || {
  echo "Upstream DT binding has changed: must rebase/review RFC" >&2; exit 1;
}
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
patch="$here/patches/ov13858-dw9800k-l6m-vddio/0001-media-i2c-dw9719-support-optional-vddio-supply.patch"
[[ -r "$patch" ]] || { echo "Missing RFC patch: $patch" >&2; exit 1; }

mkdir -p "$scratch"
src="$scratch/source"
out="$scratch/out"
git -C "$repo" worktree add --detach "$src" "$rev"
git -C "$src" apply --check "$patch"
git -C "$src" apply "$patch"
echo "Applied RFC patch in disposable worktree at $src"

make -C "$src" O="$out" ARCH=arm64 "${compiler_args[@]}" defconfig
"$src/scripts/config" --file "$out/.config" -e MEDIA_SUPPORT -e VIDEO_DEV -e VIDEO_DW9719
make -C "$src" O="$out" ARCH=arm64 "${compiler_args[@]}" olddefconfig
make -C "$src" O="$out" ARCH=arm64 "${compiler_args[@]}" -j2 drivers/media/i2c/dw9719.o
echo "Driver object compilation complete (NOT a board/hardware test)."

if [[ "$full" == "--full-kernel" ]]; then
  echo "Building kernel artefacts only; no modules_install or /boot writes."
  make -C "$src" O="$out" ARCH=arm64 "${compiler_args[@]}" -j2 Image dtbs modules
fi

printf 'source_commit=%s\npatch_sha256=%s\nsource_dir=%s\nbuild_dir=%s\n' \
  "$rev" "$(sha256sum "$patch" | cut -d' ' -f1)" "$src" "$out" \
  > "$scratch/BUILD_MANIFEST.txt"
echo "Build manifest: $scratch/BUILD_MANIFEST.txt"
echo "NO camera board graph or regulator parent DTS has been installed; hardware status remains UNTESTED."
