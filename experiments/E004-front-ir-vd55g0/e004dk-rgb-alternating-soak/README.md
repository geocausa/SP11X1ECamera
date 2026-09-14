# E004dk — bounded repeated alternating rear/front RGB soak

Status: **PREPARED / OFFLINE ONLY**.

Parent authority is Camera IJ: exact unified IB DTB plus pinned production CAMSS, IMX681 and OV13858 binaries. E004dk targets the one remaining RGB integration blocker in IJ: repeated alternating same-boot switching.

The planned single one-shot candidate runs exactly six production legs with no retry:

`rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral`.

Each rear leg captures eight normal 4076x2806 RAW10 frames; leg 1 also rechecks the accepted exact color-bar hash. Each front leg runs the accepted production R27 launcher with post-G3 policy `shadow` and 27 frames. Every source must reach runtime suspend before its route is neutralized. All four mutable links must be neutral before enabling the next target. Final state is neutral before reboot to protected Golden.

The candidate reuses exact accepted artifacts by hash; it does not rebuild alternate camera binaries. Linux SecureISP and VD55G0 are not involved in this RGB soak.

No candidate is installed or armed by this prep checkpoint.
