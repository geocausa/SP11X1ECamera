# E003h 0055 runtime result — Linux CAMNOC RT is live at XO rate, Windows uses 300 MHz

The single authorized 0055 telemetry run executed exactly once with **zero camera programming delta** and returned immediately to FullIO Golden. There was no retry.

## Decisive same-machine hardware result

Windows stock `Surface Camera Front` streaming programs CAM_CC CAMNOC RT to `CFG=0x00000203` with branch bit0 enabled. The Windows measurement was repeated identically. X1E80100 clock-source data decodes this as **300 MHz**.

Linux 0055, using the frozen healthy-CSID 0054 camera path, also enables the CAMNOC RT branch, but throughout the live interval its RCG remains `CFG=0x00000000`. X1E's parent map selects `P_BI_TCXO` for source 0 and the RCG divisor is zero, so Linux runs the active CAMNOC RT branch at **19.2 MHz**. No live 300 MHz state was observed across 1,285 samples.

RT-CDM still completed FIFO sequence 25 with `faulted=0`, CSID behavior remained the frozen 0054 path, and QC10C output remained absent. Therefore this is a concrete infrastructure parity mismatch, not a transport failure. Its causality for the VFE1 Epoch0 stall is not yet proven.

The next bounded gate is a front/X1E-only 300 MHz CAMNOC RT request through the Linux common clock framework, with all sensor/CSID/VFE programming otherwise frozen. If VFE1 Epoch0 appears, the underclock was causal; if not, retain the parity correction but close it as noncausal.

**0055 authorization is consumed. No 0055 rerun is permitted.**
