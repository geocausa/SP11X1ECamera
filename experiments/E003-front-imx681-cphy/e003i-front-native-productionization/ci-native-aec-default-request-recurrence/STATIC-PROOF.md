# Static proof

Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Exposure recurrence

AX proves normal request F consumes retained post-T681 exposure history from F-1 and that post-convergence T681 result `+0x18` becomes rich record `+0x20`, then the next history record. CH implements and verifies the final T681 retained qword.

CI retains only the Short/Long/Safe history subset already proven sufficient by BT/BU/CG; F-3 needs Safe only.

## Predictive-gain recurrence

BA names internal convergence field `+0xd8` `PredGain` and reconstructs its policy-0 update behavior. The normal recurrence is byte-for-byte:

- no-history initialization: `0x1803b4718` loads `1.0f`, `0x1803b4720` stores it to convergence `+0xd8`;
- history path: `0x1803b479c` loads history `+0x178`, `0x1803b47a0` stores it to convergence `+0xd8`;
- `PopulateOutput`: `0x1803ce040` loads convergence `+0xd8`, `0x1803ce044` stores output `+0x70`;
- `runEndOfFrame`: `0x1803bd440` loads compact output `+0x70`, `0x1803bd448` stores controller history `+0x1220`;
- history base is `+0x10a8`, and `0x10a8 + 0x178 = 0x1220`.

CG already exposes the resulting scalar as `e003i_conv_output.pred_gain`, so CI persists that exact native value rather than recomputing it.

## Current-target representation

`RunConvProcesss` preserves its x1 request object in x23. The target-log conversion reads x23 `+0x10,+0x18,+0x20`, i.e. the raw metering qwords copied by BF. The pre-convergence arbitration pointer at request `+0x08` is a distinct representation and was eliminated from the ordinary public convergence state by BR through BU. Thus CF raw target qwords are the correct public inputs to CG.
