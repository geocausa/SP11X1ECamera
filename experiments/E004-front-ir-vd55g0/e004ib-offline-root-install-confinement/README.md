# E004ib — fail-closed path and manifest preflight for disposable camera-stack package roots

OFFLINE ONLY PASS on SP11 ARM64 Golden, 2026-09-20. This stage repairs a
maintainability/safety problem in the original bounded scratch-root camera
installer and uninstaller. Previously each script rejected literal root /,
but could still accept symlink aliases for /, paths containing parent traversal,
a preexisting usr symlink pointing outside the disposable root, or forged
prior managed manifests containing path escapes. Those cases could allow
the shell tar/rm operations outside their intended destination.

The new src/sp11-camera-stack/offline-root-guard.py is invoked by the
MAINTAINED install-staged-root.sh and uninstall-root.sh before either mutates
the destination. It allows only canonical, unprivileged, user-owned scratch
roots strictly underneath /tmp. It rejects noncanonical/symlink path
ancestors, package usr symlinks or nonregular/special files, unexpected
package files absent from the package manifest, unsafe/duplicate/out-of-root
manifest entries, dangerous existing managed file or directory symlinks,
and unsafe prior managed state entries. The existing E004dw 51-file
canonical full-stack manifest passes the new approved-member SYNTAX check.
Actual package content/checksum verification is still the original
installer's responsibility.

On SP11, test_guard.py exercises 24 path/manifest/symlink negative
scenarios and invokes the actual maintained offline uninstall-root.sh
on a disposable synthetic one-file managed scratch root. The expected file
is removed; unrelated scratch and outside sentinels remain unchanged.
The original pinned full stack package WAS NOT regenerated/reinstalled,
so this is NOT a new running-camera or positive production install test.
It does not supersede E004dx's original positive full-package lifecycle.

The preflight is NOT race-free against a concurrent adversary changing
directory entries between validation and later shell operations. It is
NOT a privilege boundary or general sandbox; do not run these
disposable-root tools as root or against shared attacker-controlled trees.
Separate live install tools are unchanged/unapproved by this patch.
Protected Golden filesystem/boot/kernel, camera and PAM remain unchanged.
No SecurePD signing, native IR illumination, optical safety or biometric
authentication is claimed.

Reproduce unprivileged on protected SP11 Golden:

    python3 experiments/E004-front-ir-vd55g0/e004ib-offline-root-install-confinement/verify_guard.py
    python3 experiments/E004-front-ir-vd55g0/e004ib-offline-root-install-confinement/verify_result.py
