# E003h same-machine Windows MIPI/CSIPHY lifecycle oracle

Date: 2026-08-28

This closes the remaining E003h lifecycle-placement question using Windows on the exact SP11. The raw KD log is preserved byte-for-byte and parsed by `extract_mipi_order.py`.

## Exact evidence

- raw KD log: `E003H_MIPI_ORDER_20260828.log`
- bytes: `8600`
- SHA-256: `09a9b0aa11c677563dee521b14157d76eaecebe9971491a8156b82020bbef224`
- exact `qccammipicsi8380.sys` SHA-256: `033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407`
- exact ISP SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- exact front-sensor KMD SHA-256: `80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`

The same corrected front-only WinRT holder used by the prior lifecycle oracle was run four independent times. Every run selected `Surface Camera Front`, returned `StartAsync=Success`, and completed normal `StopAsync()`.

## Static MIPI anchors

Static disassembly of the SHA-pinned MIPI KMD maps its private-control CSIPHY cases to:

- STOP case entry: RVA `0x1e70`;
- successful STOP continuation after the hardware-stop helper: RVA `0x2024`;
- START case entry: RVA `0x2068`;
- successful START completion after all start helpers: RVA `0x2398`.

The current-boot live image base was `0xfffff803488e0000`; KD disassembly at all four relocated addresses matched the static instructions before breakpoints were armed.

## Four-cycle result

Start is completely stable in all four runs:

**ISP_START_DONE -> MIPI_START_ENTER -> MIPI_START_DONE -> SENSOR_STREAM_ON_APPLY**

Stop is a partial order, not one total order. All four runs prove:

- `ISP_STOP_DONE` occurs before sensor stream-off;
- `ISP_STOP_DONE` occurs before MIPI stop entry;
- `MIPI_STOP_ENTER` occurs before `MIPI_STOP_DONE`.

But Windows schedules sensor stream-off independently relative to the MIPI stop interval. Across the four runs it appeared:

1. before MIPI stop entry;
2. between MIPI stop entry and completion;
3. between MIPI stop entry and completion;
4. after MIPI stop completion.

Therefore **there is no Windows-proven ordering dependency between sensor-off and CSIPHY-stop after ISP teardown**. Do not invent one.

## Linux consequence

E003h `0010-x1e-windows-stop-order.patch` changes X1E host teardown to CSID before VFE and then leaves the existing CSIPHY -> sensor tail. That tail is now an observed-valid serialization of the Windows partial order (cycle 4), so `0010` does not need to be changed. However, documentation must not claim Windows requires CSIPHY-before-sensor on stop.

The proven lifecycle boundary is now closed. Remaining E003h blockers are the Windows-path CSID1 IPP and VFE1 PIX/ISP implementation gaps.
