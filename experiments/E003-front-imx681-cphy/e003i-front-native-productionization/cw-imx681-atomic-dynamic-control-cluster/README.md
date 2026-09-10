# E003i CW — atomic dynamic IMX681 control cluster

Status: **PASS offline/static + Golden W=1 module build; full parent-backed acceptance pending.**

CW fixes the final control-transport atomicity seam found while joining CV to the already-live-proven AM sensor transaction. CV can legitimately request a larger FLL together with a correspondingly larger exposure. AM keeps VBLANK separate from the exposure/gain cluster so `__v4l2_ctrl_modify_range(exposure)` cannot clobber an in-flight exposure, but that topology means a powered live update can invoke the hardware callback once for VBLANK and again for the exposure/gain cluster. Two individually group-held transactions are not equivalent to one request-local four-field publication at a frame boundary.

CW preserves AM's exact `imx681_apply_request_controls()` body and changes only V4L2 control topology/validation:

- VBLANK, exposure, analogue gain and digital gain are again one four-control cluster with VBLANK as master;
- `__v4l2_ctrl_modify_range()` is removed from the callback entirely;
- exposure advertises the sensor-wide 24-bit hardware-safe maximum;
- `.try_ctrl` validates the true request-local relation `exposure <= even(FLL - 4)` using the cluster's pending values;
- a changed cluster therefore reaches `.s_ctrl` exactly once and emits exactly one AM group-held transaction.

## Why this does not reintroduce AL

AL proved the older four-control design failed because `__v4l2_ctrl_modify_range()` itself calls `cur_to_new(exposure)` while the cluster is inside `.s_ctrl`, overwriting the caller's pending exposure before V4L2 commits it. CW has no range mutation at all. Linux 7.1.5 first installs all caller-provided values into the cluster, fills omitted peers from current state, calls `try_ctrl`, then calls `s_ctrl`, and only after success commits `new` to `current`.

`v4l2_ctrl_new_std()` does not call `try_ctrl` while controls are being constructed, so the validator cannot observe a half-created four-pointer cluster.

## Metadata tradeoff

The exposure control's advertised `maximum` is now the sensor-wide safe ceiling rather than a value that shrinks/grows with the current VBLANK. Hardware safety is not relaxed: `try_ctrl` rejects any tuple whose pending exposure exceeds `even(height + pending_vblank - 4)`. This deliberately trades dynamic query metadata for transaction atomicity while preserving the actual acceptance rule.

The default AM/AP tuple remains valid, and every current CV tuple (`FLL=3562`, exposure `3554`) passes the relation. Boundary `FLL=3562/exposure=3560` is rejected.

## Sensor transaction and parity

The AM group-held CCI body is source-exact in CW: hold `0x0104=1`, FLL, coarse exposure, analogue gain, global digital gain, then unconditional hold release `0x0104=0`. AP already proved that exact body live on SP11. CW does not repeat the live write.

`prove-cw.py` maps every CV control tuple through the retained Windows `FillExposureSettings` oracle and verifies the same 10 dynamic register bytes. It also runs a 50,000-case valid/invalid FLL/exposure relation corpus and builds the module with `W=1` against the configured Golden kernel. Current vermagic remains `7.1.5-sp11-render-parity-v4+ ... aarch64`.

## Safety boundary

CW has not been loaded. No camera device was opened, no STREAMON occurred, and no sensor write was made. The final externally numbered optical latch/effect frame remains unclaimed; AW already warns that naively adding AV's `maxPipeline=2` after the KMD apply coordinate would double-count scheduling.
