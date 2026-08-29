# External diagnostic handoff: SP11 IMX681 zero-packet boundary

Date: 2026-08-29
SP11X1ECamera base: `8489b72ab1d0442a09b1ff02bfd3180941fb74b8` (`E003h`)
Observed external kernel branch: `ooaklee/linux_ms_dev_kit-sp11` `sp11/integration-7.2.x-ooaklee-karsies-wq-cams` at `347eb9702bf18f2d81e4e29767a416172acbfe66`

## Scope

This note is deliberately **diagnostic-only**. It is intended to help another
SP11 Linux bring-up localize a `MODE_SELECT=1` / `CSID TOTAL_PKTS=0` failure
without importing SP11X1ECamera's Windows-parity ISP architecture into a Linux
RDI experiment.

No patch in this note is proposed for the external tree. In particular, do not
copy RT-CDM, VFE1 PIX/FULL, QC10C/UBWC, IPP, sensor-rate interpretation, or
Windows ISP command-buffer programming into an RDI capture path merely to make
it look more Windows-like.

## Same-machine Windows facts safe to use as diagnostic constraints

These are dynamically observed on the exact SP11 used by SP11X1ECamera unless
explicitly marked otherwise.

1. The front physical/receiver route is:

   `IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1`

   CCI ownership is CCI1/master1 and the sensor is a one-trio C-PHY device.

2. During a normal Windows front-camera session, CSID1 receiver state is:

   - `RX_CFG0 = 0x11300000`
   - `RX_CFG1 = 0x00000001`

   The stable `RX_CFG0` encodes the CSIPHY2 selection, C-PHY type, one active
   trio, and the observed bit-28 field. This is a receiver-state comparison
   point, not a requirement to use Windows' downstream ISP path.

3. Same-machine lifecycle placement is receiver-before-transmitter:

   `CDM -> IFE -> initial config packets -> CSID -> sensor MODE_SELECT=1`

   At the outer camera lifecycle level this is `ISP -> MIPI/CSIPHY -> sensor`.
   Therefore a diagnostic intended to distinguish "sensor never emits" from
   "receiver never sees symbols" should sample the sensor and receiver while
   **both are still powered and before downstream teardown begins**.

4. Stop-time sensor reachability is not a reliable timestamp for when a stream
   failed. Windows tears the ISP side down first and schedules sensor-off and
   MIPI-stop later without a fixed relative order. A sensor NACK observed only
   after receiver teardown must not be used to claim that the sensor was
   unreachable during the active interval.

5. Windows' active downstream route is CSID1 IPP into VFE1 PIX/FULL, not Linux
   VFE680 RDI. A successful Linux RDI frame is useful transport evidence but is
   not Windows parity. Conversely, absence of Windows-style IPP/VFE1/RT-CDM in
   an RDI experiment cannot explain `TOTAL_PKTS=0`, because packet arrival is
   upstream of that processing architecture.

## Sensor-mode boundary: preserve bytes, do not mix interpretations

The exact installed Windows/QTI package used by SP11X1ECamera contains a
3840x2640 RAW10 mode with line length 6752, frame length 3554, and PLL2 bytes
`03 01 77`. SP11X1ECamera's E003e experiment historically derived a 1.2 GHz
V4L2 link value from that tuple.

The external `347eb970` experiment instead targets the distinct
Karsies-derived 3844x2640 / 969.6 Msymbol/s Linux mode and intentionally
restores only the sparse PLL overrides proven on that working reference.

**Do not combine the two modes.** The Windows register bytes are useful oracle
evidence, but importing their geometry, PLL tuple, or a derived rate into the
969.6-mode experiment would destroy the value of the bounded A/B test. Rate
semantics should be re-correlated from direct evidence before being shared
across modes.

## Non-invasive decision tree for the current zero-packet experiment

Keep the current `347eb970` configuration fixed and collect one coherent
active-window observation after at least one expected frame interval:

- sensor `MODE_SELECT` readback;
- sensor frame/progress indication if the register is meaningful on this
  silicon/state;
- already-existing CSID `TOTAL_PKTS`, RX/error IRQ, ECC and CRC counters;
- read-only CSIPHY2 status only through a path already known safe while the PHY
  clocks/power are active. Do not add speculative MMIO reads after power-off.

Interpretation:

- Sensor shows no progress and CSID remains zero: stay sensor/PLL/mode-side.
- Sensor shows progress but CSID remains zero with no protocol errors: focus on
  the transmitter-to-CSIPHY electrical/rate/receiver boundary.
- CSID packet count rises: move downstream to CSID decode/crop/RDI/VFE.
- Stop-time sensor NACK only: do not move the failure boundary earlier without
  an active-window observation.

The point is to change **observation**, not configuration. One unknown per
experiment keeps both projects useful to each other even though their end
architectures differ.

## Windows-parity material that is intentionally out of scope here

SP11X1ECamera E003h has additionally reconstructed CSID1 IPP 3840x2160,
VFE1 FULL 2560x1440 QC10C/TP10-UBWC, DS4/DS16/statistics clients, RT_CDM1
resources/lifecycle, IFE startup CDM streams and DMI payloads. Those findings
belong to the native Windows-parity path. They should not be added to a
zero-packet RDI experiment: they are downstream of the current failure boundary
and would add variables without helping packet reception.

## Source pointers

Within SP11X1ECamera at the base above:

- `PROJECT_STATE.md`
- `docs/runbooks/2026-08-28-e003h-windows-parity-static.md`
- `docs/runbooks/2026-08-28-e003g-route-resolved.md`
- `experiments/E003-front-imx681-cphy/e003e-mode0-standby/`

This handoff is intentionally a water bottle, not a merge strategy.
