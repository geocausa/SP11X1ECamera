# E003i-DW — IQ producer with live CQ residual Demux/BLS

Status: **PASS (offline differential on preserved DT live input; live mode intentionally disabled).**

DW is a narrow fork of DS. The existing request-local native trigger, Windows-valid AWB HOLD_PREVIOUS behavior, dynamic LSC/Tintless state, template-free capsule framing, GTM/static payloads and V4L2 control shim are unchanged.

The single new input is CQ's per-generation `isp_gain`. For R5<-G2 and R6<-G3, `Composer.compose()` passes that float to DV and replaces only Demux/BLS module values for Titan680 registers `0x3b70` and `0x3b74`. Every other module value and DMI payload remains on the existing DS path.

DW intentionally refuses CLI live mode. DX must first provide an exact generation-tagged parent-AEC -> producer gain feed. This prevents accidental live submission using a guessed/default ISP gain.

The offline gate replays the preserved successful DT G1..G3 pairs twice: once through DS and once through DW with the exact CQ ISP-gain bits recovered from the same DT statistics using the native AEC->CQ chain. It requires identical AWB/LSC results and capsule differences confined to the two four-byte Demux/BLS fields.
