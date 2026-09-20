# E004jd — make front RGB production package R4-complete

2026-09-20. Parent `3741394`. Source-only, offline production packaging
correction after E004ja exposed the accepted front launcher's otherwise
missing Git-ignored 41,088-byte R4 bootstrap. E004jc independently
proved the exact same bootstrap capsule as a root-private sidecar and
captured **eight actual rear Bayer10 frames followed by 27 real front
QC10C frames with the new mapped-DMA guard active**, in one bounded
candidate boot. The candidate returned safely to protected Golden
and all camera images and temporary boot artifacts were retired.

## Production source correction

`src/front-imx681/stage-package.sh` preserves its Git-archive
boundary but now requires the **local original, derived** R4 bootstrap
to be a regular non-symlink file of **41,088 bytes** and SHA-256
`1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa`.
Its committed `r4-bootstrap.json` must agree on size, checksum and
derived-not-raw provenance. The one file is separately copied with
mode 0600 into the transient front package before computing the
front manifest. The original ignored source remains uncommitted and
is **not** exported as an artifact or installed into Golden.

`src/sp11-camera-stack/stage-full-package.sh` verifies that
the resulting unified package contains the required R4 under both
manifests, using the new strict `verify-package.py --require-r4`
mode. The verifier confirms byte hash, file size, mode, metadata,
absence of symlinks, and a complete unique-path full package
manifest, in addition to the original canonical module and DTB
authority. The legacy non-strict verifier is retained for examining
historical 50-file packages, *not* for production release gating.

The protected Golden kernel/DTB/initrd, GRUB saved boot default,
SecurePD signing, IR emitter, camera drivers and camera services
are untouched. A verified package is staged offline only.

## Actual fresh SP11 offline result

The accepted hardware authority was rebuilt from the pinned Golden-v4
Kbuild source/header frontend; the freshly staged camera package
contains exactly **51** files in the unified manifest and **43**
in the front manifest. The new package manifest SHA-256 is
`3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71`;
the front manifest SHA-256 is
`fef87066248193c1622671c519095ebaf7ca43d3348535d52a63a9e57bde3f17`.
The standard accepted kernel module and unified DTB checks still pass.
The packaged launcher, invoked only with archived `--topology-file`,
returned `execute=false` and the expected QC10C source and R4 hash.
No output directory, device node or camera process was opened.
Eight negative/positive offline tests pass on this staged package,
including failures for missing/corrupt R4, unlisted package files and
symlinks. No physical camera regression or user-facing endpoint is
claimed by this packaging change.

Reproduce offline using a disposable, source-built package:

```sh
SP11_R4_PACKAGE_FIXTURE=/tmp/sp11-e004jd-pinned-r4-production-package-20260920/package \
  python3 -m unittest discover \
    -s experiments/E004-front-ir-vd55g0/e004jd-production-r4-package \
    -p test_r4_release.py -v
```

**Remaining end-user gates:** stable live rear Bayer-to-calibrated
NV12-to-app endpoint; separately validated front QC10C decode or true
safe linear ISP NV12 mode followed by front app endpoint. The
physical bounded 27-frame mapped-DMA guard passed in E004jc, but the
new guard driver has NOT been made Golden's default.
