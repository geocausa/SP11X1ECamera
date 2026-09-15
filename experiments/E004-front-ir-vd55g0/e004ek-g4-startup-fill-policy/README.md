# E004ek — guarded G4/request7 startup-fill policy

E004ei proved pure shadow becomes causally invalid at G7 because corrected Linux G4 is the first capped tuple and is suppressed. E004ej then proved Windows requests 7..9 sit on the stable preview-cap plateau, and that Windows request7 plus Linux G4 cap quantize to the exact same IMX681 tuple.

This experiment adds a disabled-by-default `g4-startup-fill-shadow` policy. It allows exactly one G4/request7 physical write only when every provenance, cap, retained-exposure, pipeline and IMX681 control field matches the proved tuple. It does not consume the later cap-release latch. Every later source remains shadow-only in this policy, so G7+ statistics can be observed causally without authorizing a second post-G3 write.

Existing `shadow` and `cap-release-one-shot` behavior is unchanged.

Offline verification passes with strict one-field mutation rejection and compatibility checks for the existing `shadow` and `cap-release-one-shot` modes. The guarded userspace capture builds deterministically as `4735e81c25c3feff6f595480296e54da358622603c5e711cdabff3caddcd9934`. Rebuilding the full hardware authority leaves all kernel modules and the unified DTB byte-exact; the hardware manifest changes only because that userspace capture binary is included, to `ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c`.

## Package promotion

The committed guarded build stages and verifies as front-package manifest `fef87066248193c1622671c519095ebaf7ca43d3348535d52a63a9e57bde3f17` and full-stack manifest `3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71`. The disposable-root lifecycle passes clean install, integrity verification, deliberate capture-binary tamper rejection, managed reinstall, clean uninstall and unrelated-sentinel preservation. The live installer is pinned to this exact full-stack manifest. No live camera activation has occurred in E004ek itself.
