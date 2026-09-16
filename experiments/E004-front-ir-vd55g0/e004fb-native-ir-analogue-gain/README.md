# E004fb: standard non-unity analogue gain and reliable evidence

Request analogue gain code 16 (2x), exposure 1000 lines and digital gain 256
through the existing standard V4L2 controls, then capture 16 complete consecutive
R10_CSI2P frames through stock cam. Require the sensor's before-stop applied
status to match all three values. No other mode, DT, transport or power changes.

Driver changes only correct two stale diagnostic pixel-rate literals to use the
same 137.6 MHz constant as the control, and label the firmware digest as expected
rather than implying a kernel-computed digest. The builder still checks its SHA.

Replace line-count dmesg slicing with a raw-timestamp boundary tied to the boot
identity. Preserve multiline messages and fail if the boot changes. A regression
fixture specifically covers ring rollover with fewer lines after the operation,
which made E004fa's old collector lose all sensor logs. Missing status evidence
is classified separately from a confirmed health/power failure.

One stream attempt, bounded timeout, watchdog return, confirmed stop/autosuspend,
Golden return and retirement. No same-boot retry. Selection queries and stock
libcamera discovery remain gates. This is not a scene-quality or processed-output
claim, and all sensor GPIO outputs remain disabled.

## Result

PASS: stock cam delivered all 16 consecutive complete frames; the applied
status confirmed exposure 1000, analogue code 16 (2x), digital code 256, and
137.6 MHz timing. Four selection targets passed. The timestamp collector
retained initialization/start/stop evidence directly, with no kernel fault
or warning. Autosuspend passed; Golden returned and the identity was retired.
Pixels span 55–94, mostly close to black. Useful scene imagery and processed
output remain unproven.
