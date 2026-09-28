# E009d — transient AF scalar equivalence, not live input proof

Status: **PRIVATE RETROSPECTIVE FIT; REQUEST SOURCE OPEN; NO RUNTIME**.
Parent E009c `fab157e51e0abc3be385bdb2bb594c12eb9470c6`.

In the pinned source `af_util_get_roi_default` RVA 0x628630, an AF zoom
factor greater than zero scales the loaded HAF fractions by its inverse
before truncation and centering. Using the selected rear 25% pair and
4064×2286 crop, an *illustrative* zoom factor 0.998 yields an AF rectangle
whose selector-1 bytes match the retained startup1 payload **300/300**.
The same candidate gives 250/300 for startup2/3; zoom 1.0 gives 300/300
for startup2/3 and 250/300 for startup1. The hardcoded startup0 remains
300/300 with either setting. Thus one request-scoped scalar change can
explain all observed ROI positions while preserving cell size.

**0.998 was selected after inspecting final DMI and is not an observed AF
input.** Alternate HAF fractions, AF ROI type/metadata, or transient sensor
geometry are not excluded. No driver constant, startup exception, or native
runtime call site is introduced. This fit is a diagnostic target for a
future request-stage observation, not independent predictive parity.

`audit-private.py` compiles the already committed E009b source-composed
candidate with these two scalar inputs in disposable directories on SP11.
It compares against the private original selector-1 bytes and emits only
aggregate counts. It neither exports captured data nor opens a camera.

Next distinguish the hypotheses by observing, for first normal and next
requests in one original rear session, the AF-selected ROI type/rectangle,
CAMIF dimensions, loaded HAF pair and AF zoom value before BAF mapping.
Do not repeat the generic E008y ETW capture without an AF-stage provider
schema or a safe, targeted logging path. Native rear ISP remains denied
pending the broader semantic seed and IRQ/DMA ownership gates.
