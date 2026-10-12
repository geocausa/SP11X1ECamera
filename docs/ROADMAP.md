## User reuse boundary, 2026-10-12

Use independently reverse-engineered Windows hardware behavior and functional
register transactions. Do not copy/extract Windows calibration data, vendor
tables, tuning payloads or blobs into the replacement. Public availability or
a GPL label alone does not establish admissible provenance. A source array
representing independently observed functional transactions is distinguished
from an extracted vendor table; review its derivation before runtime admission.

Compare our existing work and ooaklee component by component. Prefer matching
same-machine hardware evidence, correct interface/timing/power behavior and
maintainable source. Keep our qualified control/timing, allocator/completion/
reset/ownership work and independently measured or mathematically generated
calibration where applicable. No wholesale replacement or fresh calibration
restart. Directly extracted Windows factory tuning remains reference-only and
must not become replacement runtime data.

The reused ooaklee source comments declare independently transcribed MMIO/I2C
observations. Keep that declaration and original authorship; complete the
provenance review rather than treating it as proof. Its imported functional
sequence is a source candidate, not runtime admission or an extracted vendor
calibration profile. Hardware-ISP/NV12 and Windows parity remain the target.
This boundary governs future reuse decisions and supersedes ambiguous earlier
calibration-reuse language. No source/runtime/install changes accompany it.

## ooaklee reuse/comparison checkpoint, 2026-10-12

17 public source/DT/API files at validated64999b9f and current2cbd1ec3 are
byte-identical. Existing front RAW/RDI bring-up is a reusable implementation,
superseding E000's no-proven-community-stream snapshot. Author-reported capture
results are not our hardware qualification. Target remains hardware-ISP/NV12.
Public exact C-PHY admission accepts2.406Gsymbols/s/trio0; our2.400Gsymbol/s
mode is rejected by actual public configure. Do not mix the profiles or copy
the temporary D-PHY configure-field carrier as a settled generic C-PHY ABI.
Public16-bitFLL0x0340/bus-pixel metadata differ from our24-bit0x033d/timing.

Reused standalone sensor source under src/upstream/sensors/imx681-ooaklee:
unchanged public mode table, two isolated PM/group-hold error fixes, provenance
and immutable pins. GCC/Clang ASAN/UBSAN each1080 controls after3 original
counterexamples;36 profile+66submode+3DPHY controls;12 pin rejection cases.
AArch64 sensor module W=1/-Werror/modpost/link PASS,zero warnings,against
candidate17 source/config and pinned candidate16 symbols; not installed/loaded.
Patch replay exact. Local no-signoff checkpatch clean; standard check retains
the absent certification. No signoffs or upstream submission are claimed.
Evidence:docs/UPSTREAM-OOAKLEE-COMPARISON-20261012.json; detailed reuse decisions:
docs/UPSTREAM-OOAKLEE-COMPARISON-20261012.md.

NEXT bounded receiver lifecycle and CAMSS routing on a matching profile,
typed PHY configuration, sensor endpoint/timing/power graph qualification,
then fresh fully open RAW and clean stop/reopen. RAW does not require completing
processed ISP/CDM startup. Continue ISP/NV12 resource retirement separately,
reuse existing calibration. Both private startup consumers/all14 gates remain.
Golden, daily installation, original evidence and calibration preserved.
No capture/boot/module/service/DT/runtime or system-sleep changes in this stage.

> Current RGB driver status and next gates are in
> [NATIVE-RGB-ENGINEERING-AUDIT-20261007.md](NATIVE-RGB-ENGINEERING-AUDIT-20261007.md).
> The earlier statuses/plans below are historical, not current release readiness.

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
- E004oj source-locks the original conditional BF0x300D IFE resource STOP FLAG ZERO control write: selected zero-state register window = original base+0xC00, original BF switch table index13 branch writes zero at window+0x1200, therefore **original base+0x1E00**, independently E004nv's WM16 CFG0 offset. This is **NOT** proof of a live BF IRQ or safe WM16 DMA stop/retirement. Next prove active Windows rear selected mode and post-write bus/IRQ/WM16 drain before Linux runtime. [E004oj exact register-offset match](../experiments/E004-front-ir-vd55g0/e004oj-bf-resource-zero-register-offset-static/README.md).
- E004oi source-verifies TWO original mode-selected IFE resource callback entries, nonzero-state 0x1C0F0 and zero-state 0x1D830, stored in the exact field consumed by E004oh's bounded IFE 0x805 stop-resource loop. **Zero-state 0x1D830 explicitly recognizes BF resource0x300D**, but live Windows rear callback selection/BF event and WM16 physical retirement remain UNPROVEN. Next trace the 0x300D stop-flag-zero branch to actual VFE bus WM/IRQ/ack safe-stop and verify a live rear profile. [E004oi IFE BF resource callback](../experiments/E004-front-ir-vd55g0/e004oi-ife-resource-callback-bf-port-static/README.md).
- E004oh finds the *additional* original IFE/CSID/CDM stop-progress layers: IFE two 0x805 helpers including bounded per-resource callback 0x27278, **independent IFE event/stop progress**; CSID atomic pending work and worker state; CDM separate command event. **Neither software stop return nor CSID pending zero proves rear VFE WM16/other output DMA quiescence.** NEXT trace IFE per-resource function to physical register/IRQ/WM retirement. [E004oh multistage stop trace](../experiments/E004-front-ir-vd55g0/e004oh-isp-multistage-stop-progress-static/README.md).
- E004og identifies **three concrete original OEM core callback implementations**, each source-stored by its own original initializer and confirmed as an ARM64 PE function entry: CSID 0x211B0, IFE 0x22CD0, CDM 0x28480. Their 0x805 stop paths are distinct (IFE two helpers, CSID worker/event, CDM command-state/event). Next: trace physical stop/IRQ/WM/DMA acknowledgements and 0x809 separately, not pretend the original manager returning guarantees DMA quiescence. [E004og core implementations](../experiments/E004-front-ir-vd55g0/e004og-original-isp-three-core-callback-implementations-static/README.md).
- E004of traces the source-verified ISP **per-core interface producers**, not just their consumers: separate core-array allocation, indexed 0x30-byte records, dynamic descriptor lookup, 16-byte callable-pointer copying, and guarded manager use. NEXT identify actual first CDM/IFE/CSID callback bodies and register/IRQ/DMA effects before Linux runtime. [E004of core provenance](../experiments/E004-front-ir-vd55g0/e004of-isp-per-core-interface-provenance-static/README.md).
- E004oe verifies the six ISP-manager core calls against exact original OEM diagnostic hashes and code references: eligible `0x804` dispatch **CDM→IFE→CSID**; `0x805` dispatch **CSID→IFE→CDM**. Next trace lower callbacks, their request/return ABI and physical safe-stop completion; this **software call order** alone does not validate DMA drain or the live rear Windows profile. [E004oe six-stage trace](../experiments/E004-front-ir-vd55g0/e004oe-isp-manager-per-core-order-static/README.md).
- E004od source-verifies the previously unknown second ISP callback: a 16-record hardware-manager pool installs callback RVA `0x15D70`, which dispatches selectors `0x804`/`0x805` to distinct guarded per-core paths. Next trace the actual IFE/CSID/CDM receiving interfaces and per-profile DMA/IRQ/stop effects; **0x809 and live rear-session selection are still unresolved**. [E004od ISP manager](../experiments/E004-front-ir-vd55g0/e004od-isp-hw-manager-nested-start-stop-static/README.md).
- E004oc source-verifies the AVStream **nine-entry per-device-interface identity table** and seven matching original OEM registering providers. Rear sensor = slot1, ISP = slot4, shared platform = slot5; slots6/7 remain unknown. [E004oc provider routing](../experiments/E004-front-ir-vd55g0/e004oc-device-interface-identity-routing-static/README.md). Next decode each selected provider's **returned callback implementation and selector ABI**, not the shared numeric request alone.
- E004ob proves **both** original Qualcomm platform and ISP drivers match the same opaque interface request code, with distinct state/callback branches: [E004ob dual receiver static trace](../experiments/E004-front-ir-vd55g0/e004ob-dual-backend-ioctl-static/README.md). Next resolve the AVStream-selected device-interface identity and corresponding actual OEM recipient; the common numeric request alone is insufficient to decode any live camera-engine selector.
- E004oa now source-pins the actual external kernel-device interface acquisition: [E004oa binder and dispatch](../experiments/E004-front-ir-vd55g0/e004oa-avstream-kernel-interface-bind/README.md). The opaque internal device-control request `0x002326AB` returns an eight-byte callable interface; next find the original platform/ISP/sensor recipient and its request ABI. Do not interpret the recorded numeric engine selectors as hardware commands yet.
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
