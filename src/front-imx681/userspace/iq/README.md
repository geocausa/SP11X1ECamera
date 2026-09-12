# Stable front-IMX681 IQ runtime

`live-iq-producer.py` is the production-consolidation form of the proven GM R5..R27 producer. HF froze the source, HG relocated its runtime path, and HH removed the runtime dependency on HG's raw/local authority cache.

The runtime now consumes `authority/authority.json`, a 250,690-byte clean decoded/derived authority file. It contains the normalized composer state, selected LSC/Tintless state, decoded GainAdj/AWB topology and the small CCT/AGW tables needed by the proven algorithms. It does **not** contain the proprietary IMX681 tuning blob, raw Windows trace, or raw request DMI slots.

HH physically hides all 80 former HG cache inputs and still reproduces R5..R27 23/23 byte-exact in two independent runs. A traced clean run opens no raw/local authority path, no project-local path outside this IQ tree, and no camera device.

`prepare-authority-cache.py` remains only as a historical/regeneration bridge for HG. `hh-cleanroom-authority-cache-reduction/build-clean-authority.py` regenerates the clean authority from the canonical reverse-engineering evidence. Neither is required by the shipped IQ runtime.

The clean authority is currently pinned to the proven SP11 unit/profile. Generalizing physical per-device calibration acquisition for other SP11 units is separate production work.
