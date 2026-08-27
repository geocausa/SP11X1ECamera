# Runtime kitchen audit

The archived v19c DTB in `01-audio-main-promote-v18/deploy/native-audio-v19c/` is byte-identical to the currently deployed Golden DTB:

`2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`.

The adjacent `.dts` is a decompiled/archival representation and recompiles semantically, but not byte-identically due to DT serialization/string-table details. The DTB—not a fresh generic source build—is the runtime anchor.

Compiling untouched Golden maintained source as `x1e80100-microsoft-denali-oled.dtb` produces a different board state. The semantic differences include:

- FullIO TX DMIC capture route missing;
- v19c sound-card model absent;
- touch/QSPI enablement and GSI DMA differences.

Therefore no E002k-D runtime candidate may substitute a generic maintained-source DTB for v19c until those non-camera changes are reconciled.
