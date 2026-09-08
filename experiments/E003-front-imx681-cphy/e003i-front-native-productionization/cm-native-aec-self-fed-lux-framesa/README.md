# E003i CM — native self-fed Lux + FrameSA recurrence

Status: **PASS (native/offline)**.

CM removes two more per-request abstractions from CL. Ordinary front requests no longer accept caller-supplied Lux or a caller-supplied FrameSA candidate. The request boundary is now `frame_id + measured_luma + seven still-open analyzer value/confidence pairs`.

For request F, CM uses the internal Lux present at request entry, evaluates the BG/BK FrameSA target curve, publishes exact FrameSA `AdjRatio = float32(target / measured_luma)` with confidence `0.001f`, and feeds that pair into CE. Analyzer source S1 remains CL's retained `F-3.S1`.

After the current target/convergence/T681 work is complete, CM derives the BI/BJ `log1.03` coordinate from the same `F-3.S1`, runs BK/AB Algorithm001, and updates the internal Lux for the next request. This preserves BH's proven order: current FrameSA/ADRC work sees entry Lux; Algorithm001 writes the next Lux afterwards.

The composed verifier keeps the seven still-open analyzer publications inside CL's already-proven ordinary arbitration domain (`0.72..1.45`) while deliberately retaining AB-realistic measured luma (`0.55..2.75`). That matters because BG FrameSA target is `30..55`, so FrameSA AdjRatio can be numerically large in real low-luma scenes; its exact `0.001f` confidence is what keeps that point appropriately weak in the final method-11 aggregation. The earlier scratch verifier incorrectly randomized those seven analyzer values as `5..50`, which produced out-of-table synthetic exposures and correctly tripped CH/T681; no native recurrence code changed for this correction.

The Algorithm001 blend coefficient remains an initialization seam. Captured ordinary front runs prove alpha=0, but CM does not promote that capture-specific fact into an unsupported global constant. The warm-up exposure-history seam also remains explicit.

No live camera, module load, sensor write, MMIO, Windows boot or reboot is used.
