# Roadmap

## Canonical request-to-hardware slice map

Before interpreting a Windows video pin or reverse-engineered event
as a Linux driver requirement, read
[CAMERA-STACK-PORT-MAP.md](CAMERA-STACK-PORT-MAP.md). It pins the
Windows request → AVStream → platform/sensor/ISP → physical CSI/VFE
relationships and corresponding clean Linux L0–L6 owners, marks
observed versus static versus conjectured facts, separates mandatory
native capture/control from optional Windows AI effects, and protects
the accepted front/rear RAW paths. Run the source/INF/scalar gate:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/verify-camera-stack-port-map.py
~~~

## Phase A — Oracle map

- Identify exact devices/packages: **done**.
- Decode board resource ordering, CCI/I2C identity, MCLK, GPIO/reset and CSI link mode.
- E004nz now source-pins the OEM AVStream camera engine, profile/configuration packet handoff and start/stop indirect dispatch: [E004nz callgraph](../experiments/E004-front-ir-vd55g0/e004nz-avstream-profile-control-static/README.md). Next: trace helper RVA `0x20DA8` to its platform/ISP/sensor recipient and decode only the required hardware request ABI. **Numeric command selectors remain unidentified**; do not port them or infer the registered Device MFT ran in a given session.
- Trace Windows only where static packages are insufficient; compare manual rear VideoRecord versus preview/photo and front→rear→front in a bounded non-image session.

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
