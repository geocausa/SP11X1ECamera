# E003i-DS — live IQ producer with Windows AWB hold semantics

Status: **PASS (offline producer integration; no camera runtime).**

DS is a minimal fork of AE's already-proven live IQ producer. It changes only the native trigger source from AD to DR and interprets DR return code 1 as the DQ-proven Windows no-update condition.

For an ordinary positive-weight AWB frame, DS executes the original AE path unchanged: fresh AGW XY -> startup temporal 60/40 -> final CCT -> dynamic LSC -> template-free R5/R6 capsule.

For zero aggregate AGW weight, DS:
1. preserves the current previous XY exactly;
2. derives CCT from that held XY with the already-proven P03 mapping;
3. does not advance the previous-XY state;
4. continues using the valid request-local AEC Lux for LSC selection;
5. records `awb_hold_previous=true` in evidence.

This mirrors Windows: CSAAGWV1 emits a zero no-update target and CAWBMain keeps previous AWB gains/decision state. It does not temporal-blend a fabricated zero target.

No kernel ABI, V4L2 ingress, IQ capsule format, LSC backend, request mapping or camera helper behavior changes here.
