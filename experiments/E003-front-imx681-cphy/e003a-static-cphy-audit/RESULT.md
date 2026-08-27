# E003a static C-PHY audit result

Date: 2026-08-27

## Archived series

The exact nine-patch Qualcomm CAMSS C-PHY v9 resend used for this audit is retained under `upstream-v9/`.

- series dates: 2026-07-29
- mbox SHA-256: `d0aa8c7883bcaf60a078e833859f3b6264dc1f73a76f8e0625c60bddb5315659`
- patches: `0001.patch` through `0009.patch`

## Golden replay result

Against the true Golden source anchor `.golden-v33-repro/src`:

- patches 1-3 apply successfully (context offsets only);
- patch 4 first conflicts in Golden's older CSID API and requires a semantic adaptation;
- after adapting patch 4, patch 5 reaches a further context conflict in `camss-csiphy-3ph-1-0.c`;
- the generic series is therefore not a literal drop-in for this Golden tree.

The replay logs are retained as `CPHY-V9-REPLAY.log` and `CPHY-V9-SEMANTIC-REPLAY.log`.

## X1E80100 hard blocker found in the series

Patch 5 explicitly selects `lane_regs_x1e80100` for D-PHY, but for `CAMSS_X1E80100` + `V4L2_MBUS_CSI2_CPHY` it sets:

`lane_regs = NULL` and `lane_array_size = 0`.

The same patch adds a runtime `WARN_ONCE(..., "Missing lane_regs definition!")` when no table is selected.

Patch 6 adds a C-PHY electrical table only for SDM845 (`lane_regs_sdm845_3ph`). It does not add an X1E80100 C-PHY table. Patches 7-9 adjust generic Gen2 programming, C-PHY clock/rate calculations, and endpoint acceptance, but do not close the X1E electrical-table gap.

## Conclusion

The v9 series is useful as the generic C-PHY plumbing reference, but must not be enabled on SP11/X1E80100 by itself. A Windows-derived X1E-specific C-PHY electrical program is required before first C-PHY streaming.

That missing evidence is now supplied separately by `../e003a-windows-oracle/`, which captured two independent live IMX681 CSIPHY2 snapshots plus idle/post-stop state.

## Runtime boundary

No E003a static-audit action powered the front sensor or issued a CCI transaction. Front runtime work begins only in the separately gated E003b identity experiment.
