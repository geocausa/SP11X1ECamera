# E003i-HF — stable front-IMX681 source bundle

Status: **PASS OFFLINE / no camera runtime.**

HF creates `src/front-imx681/`, the first stable source surface that no longer requires reconstructing the final CAMSS or capture-helper source through a long experiment chain just to inspect or build them.

The bundle preserves 82 authority files with SHA256 provenance. The final R27 CAMSS source, HC capture helper, CW IMX681 driver, 32 native AEC source/header files, continuous scheduler, gain feed, cap-release policy and GM IQ producer are all pinned. The C helper builds from the bundle to the **exact accepted HC binary hash**, and both kernel modules build cleanly with the protected SP11 kernel vermagic.

No camera device is opened and no runtime behavior is changed. The post-G3 native feedback path remains fail-closed pending HD's brighter-real-scene condition.

One deliberate gap remains: the GM IQ producer source is byte-identical but still imports 16 experiment-local modules/assets. HG should relocate those dependencies into the stable tree and prove R5..R27 capsule output remains byte-exact before any production launcher/package work.
