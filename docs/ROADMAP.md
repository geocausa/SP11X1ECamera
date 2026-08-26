# Roadmap

## Phase A — Oracle map

- Identify exact devices/packages: **done**.
- Decode board resource ordering, CCI/I2C identity, MCLK, GPIO/reset and CSI link mode.
- Trace Windows only where static packages are insufficient.

## Phase B — Common Qualcomm path

- Align the camera branch with the appropriate X1E80100 CAMSS/CCI/CSI-PHY upstream state.
- Add Denali common camera DT resources without sensors first where possible.
- Prove media graph / test-pattern path before blaming a sensor.

## Phase C — Rear OV13858

First physical sensor target because Linux already has an OV13858 driver and it is the lowest-risk way to prove the common transport path.

Milestones: power -> identify -> CSI lock/SOF -> RAW capture -> stable repeated stream -> controls.

## Phase D — Front IMX681

Audit existing Linux IMX681 work against SP11 Windows traces. Establish D-PHY vs C-PHY from the oracle, not community assumption. Bring up transport and controls.

## Phase E — IR VD55G0

Adapt only genuinely reusable VD55G1 concepts. Treat VD55G0 and the illuminator/privacy/security path as its own evidence-driven target. Default unsafe/unproven illumination paths to off.

## Phase F — Image pipeline

After stable RAW capture: libcamera pipeline, debayer/colour/exposure/AWB, Qualcomm ISP integration where appropriate, Windows image-quality comparison, then HDR/multiframe/noise/tone-mapping parity as separate work.
