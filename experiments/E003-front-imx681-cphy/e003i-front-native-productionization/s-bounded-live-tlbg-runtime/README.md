# E003i-S — bounded live TL_BG runtime package

Status: **prepared and unarmed**.

This package is the first bounded runtime composition of E003i-R. It preserves the accepted 0076 six-frame QC10C buffer order and front-only DT/sensor assets while replacing the old captured-IQ CAMSS module with the reconciled production module.

Runtime contract:

- unique one-shot boot; persistent Golden remains `sp11-audio-fullio-v19c`;
- hardened `clk_ignore_unused pd_ignore_unused` and camera-module blacklist on boot;
- load reconciled CAMSS without the obsolete `e003h_pix_runtime_arm` parameter;
- exact oracle R4 is submitted before STREAMON;
- exact oracle R5 is submitted after DQBUF0 and R6 after DQBUF1, both through the same live V4L2 fd;
- after each DQBUF, read/save the generation-tagged `X1E Front TL_BG Snapshot` compound control;
- allow latest-snapshot generation skips during intermediate reads, but require bounded final generation 6;
- one helper invocation only; no same-boot retry; unexpected live failure pins state until mandatory Golden reboot.

After return to Golden, the six saved TL_BG controls are parsed offline with the accepted Titan680 stage-N parser. Runtime success does not establish a request-number delay; `source_seq` remains a hardware/source completion generation only.
