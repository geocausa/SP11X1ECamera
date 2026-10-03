# SP11 camera stack evidence audit — 2026-10-03

Hardware transport and substantial ISP composition work already exist. The missing product milestone is a clean, controllable front/back image path with deterministic selected-mode startup and physically verified buffer ownership. E011DI is the latest accepted emulation checkpoint; its totals include earlier work. This audit creates no new capture or runtime acceptance.

Audited Git base: 08613fb105f6d92ce745b48e748ccf457744ca28. SP11 was idle on protected Golden, local/upstream/live matched and Git was clean before this documentation change. No running PiMaster jobs, camera Starts, reboots, module loads or production C/kernel changes occurred.

## Current scope and evidence

Native Qualcomm ISP remains the chosen engineering priority. E011BS narrows the first milestone to one clean normal-colour mode per front/rear camera. Optional AI/effects/HDR/multiframe/catalogue and protected IR/Hello are deferred. Existing RAW/software paths remain fallback/reference evidence. Name the processing route for every image claim. There is no measured overall completion percentage.

| Requirement | Evidence level | What we have | Still missing |
| --- | --- | --- | --- |
| physical topology | LIVE_BOUNDED | Three-sensor bind and separate front/rear routes established. [hardware authority](../src/sp11-camera-stack/PROVENANCE.json); [port map](../docs/CAMERA-STACK-PORT-MAP.md) | Production shared-PIX owner/switch lifecycle remains to be proved. |
| front native ISP transport | LIVE_BOUNDED | 27 front VFE1 PIX QC10C frames with statistics and clean stop. [front native](../experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hy-production-one-stream-r27/README.md) | Chosen output decode, usable colour and matched Windows image quality. |
| front rear libcamera RAW | LIVE_BOUNDED | Six metadata-confirmed RAW frames per sensor and neutral handoff. [raw](../experiments/E004-front-ir-vd55g0/e004lr-guarded-rgb-raw-frames-one-shot/README.md) | Separate from a processed native-ISP colour pipeline. |
| front rear software app fallback | LIVE_BOUNDED | E004ne front1080p/rear4K supported controls, near30fps source, app negotiation and neutral switch passed. [fallback](../experiments/E004-front-ir-vd55g0/e004ne-screen-rear-stable-window-guarded-one-shot/README.md) | Matched Windows ISP optical detail/colour and persistent daily service. |
| ordinary app lifecycle | LIVE_BOUNDED | Finite maintained RGBSession opens, client-kill recovery and neutral graph passed. [app lifecycle](../experiments/E004-front-ir-vd55g0/e004lz-guarded-real-rgb-session-backend-one-shot/README.md) | Long-run native-ISP service, arbitrary clients and production kernel ownership. |
| rear startup packet parity | OFFLINE_CONDITIONAL | Four-phase replay has zero remaining semantic register differences. [offline startup](../experiments/E004-front-ir-vd55g0/e011am-rear-rs-full-startup-integration/INTEGRATION-SAFE.json); [cold aec](../experiments/E004-front-ir-vd55g0/e011bw-rear-source-cold-aec-weights/INTEGRATION-SAFE.json) | Some normal semantic inputs are observed records; complete deterministic bootstrap remains open. |
| packet isolated runner | BUILD_ONLY | Four owned command arenas, real composer preflight and host fault injection; ARM64 build passed. [runner](../experiments/E004-front-ir-vd55g0/e011ar-rear-packet-isolated-runner/README.md) | No reachable live rear path or physical IRQ/DMA/stop proof. |
| inactive cold gamma | OFFLINE_AND_BUILD | Cold gamma inactivity implemented; dummy active table removed. [inactive gamma](../experiments/E004-front-ir-vd55g0/e011as-rear-explicit-inactive-cold-gamma/README.md) | Full selected-mode startup still has other open dependencies. |
| cold AWB quad | OFFLINE_SOURCE_PRODUCER | Portable decoder produces bounded invariant Default cold quad. [cold awb](../experiments/E004-front-ir-vd55g0/e011av-rear-source-cold-awb-quad/README.md) | Whole profile/source selection and general dynamic AWB are wider scopes. |
| cold AEC weights | OFFLINE_SOURCE_PRODUCER | Portable decoder produces invariant Default weights; later live first-frame join exists. [cold aec](../experiments/E004-front-ir-vd55g0/e011bw-rear-source-cold-aec-weights/INTEGRATION-SAFE.json); [live aec join](../experiments/E004-front-ir-vd55g0/e011bx-rear-first-aec-source-query/README.md) | Complete startup and normal input authority remain open; no wholesale factory requirement inferred. |
| factory runtime chain | EMULATED_BOUNDED | E011DE-DI extend original caller/guard/constructor checks in owned memory. [latest emulation](../experiments/E004-front-ir-vd55g0/e011di-original-enumeration-bootstrap/RESULT.json) | Full original factory incomplete; these checks have not installed a Linux driver. |
| Windows live BF | LIVE_BOUNDED | E005o observed 22 BF/nonempty-FIFO/matcher events during 13 valid rear4K handles. [live bf](../experiments/E004-front-ir-vd55g0/e005o-windows-live-bf-fifo8-matcher-vs-vfe-bus7/RESULT.json); [bf correction](../experiments/E004-front-ir-vd55g0/e005r-type1-csid-provenance-and-output-group-field-correction/RESULT.json) | No exact same-generation WM16 hardware-retirement proof. |
| native WM16 completion | STATIC_AND_BUILD | Independent comp-group7/consumed-address contract and isolated observer build exist. [bf contract](../experiments/E004-front-ir-vd55g0/e005m-vfe680-wm16-baf-compgrp7-busdone-static/README.md); [bf observer](../experiments/E004-front-ir-vd55g0/e005n-vfe680-wm16-compgrp7-observer-isolated/README.md); [bf correction](../experiments/E004-front-ir-vd55g0/e005r-type1-csid-provenance-and-output-group-field-correction/RESULT.json) | Independent hardware completion, exact consumed IOVA, IRQ/ACK and DMA/IOMMU retirement. |
| native rear processed frame | OPEN | Rear-specific source recipes and startup composer exist. [runner](../experiments/E004-front-ir-vd55g0/e011ar-rear-packet-isolated-runner/README.md); [offline startup](../experiments/E004-front-ir-vd55g0/e011am-rear-rs-full-startup-integration/INTEGRATION-SAFE.json); [port map](../docs/CAMERA-STACK-PORT-MAP.md) | First Linux rear native-ISP processed optical frame and controlled stop unproven. |
| clean colour and Windows parity | OPEN | Existing fallback has bounded structured-scene evidence. [fallback](../experiments/E004-front-ir-vd55g0/e004ne-screen-rear-stable-window-guarded-one-shot/README.md); [native priority](../src/sp11-camera-stack/RGB-PHASED-ROADMAP.md) | Chosen-route decode/exposure/colour, controlled matched scene and calibration. |
| optional effects IR Hello | DEFERRED | Baseline defers AI/effects/additional modes; IR remains off. [scope](../experiments/E004-front-ir-vd55g0/e011bs-clean-front-rear-scope/BASELINE-SCOPE.json); [hardware authority](../src/sp11-camera-stack/PROVENANCE.json) | Protected IR admission and illumination are separate gates. |

## What the latest checks added

E011DE tested the standalone startup guard. E011DF joined its actual factory caller. E011DH added factory initialization and the 1,040-byte clear. E011DI reused that VM and added stack setup, the second guard and a distinct 56-byte initialization: 80 new original instructions per case, 32 cases. Its combined 15,936 instructions are not 15,936 newly covered instructions. These are emulator results with explicit owned OS/loader/allocator models; they do not install or activate a Linux camera driver.

E011DJ private exploration reaches the startup registry's EnterCriticalSection boundary. Its CRT lock initialization and callback result remain unqualified. Preserve that trace. Resume deeper factory/CRT work only when the selected input ledger names the field, consumer or lifetime dependency it must resolve. Linux needs no replica of Windows runtime scaffolding; required source-backed numerical and hardware behaviour still needs authority.

## Corrections made by this audit

- Primary status named E011DE/E011DF despite current/next E011DI/E011DJ; align it and the next action.
- Readiness software-first instruction was superseded by native-ISP priority and later clean-front/back scope; mark it historical.
- Active architecture and verifier required live BF=false. E005o already proves 22 BF events with nonempty FIFO8/matcher during 13 rear4K handles; current aggregate becomes true, old E004nv/nx/ny records remain unchanged.
- Live BF does not prove independent hardware retirement. E005r preserves type-1 CSID provenance, unknown live composite-group binding and unproven exact consumed-buffer/generation correlation. Enforce those limits in the active verifier.
- Older black-frame diagnoses are valid for those sessions. E004ne later passed a structured rear scene, supported-control restoration, near30fps source and ordinary apps. Matched Windows colour/detail and rear native ISP remain unproven.
- Direct source inspection confirms accepted VFE680 ISR only returns IRQ_HANDLED. E005n observer is isolated/build-only, not deployed completion support.

## Next useful work, in order

1. **selected baseline inputs (L2/L4).** Inventory selected enabled startup semantic inputs; attach existing producer, authority and actual consumer; classify source, observed and owned-fixture inputs. Isolate remaining normal RS count/whole-frame offset and other required normal-input gaps. Acceptance: Every required field has an evidence-backed producer or explicit open dependency. Further factory/CRT/catalogue tracing names a required baseline consumer.

2. **integrated preflight (L1/L2/L3).** After input gaps close, compose existing cold AEC/AWB decoders, inactive gamma, packet-isolated runner and required normal producers in one new source-only preflight. Acceptance: Four packets derive from declared authority; owned command/output lifetimes, failure/stop paths and existing parity remain checked. Build evidence alone does not authorize runtime.

3. **physical completion (L1/L3).** Prepare a separate fresh bounded observer after exact source-defined completion/identity/stop criteria and Golden rollback are reviewable. Acceptance: Independent completion correlated to exact output/generation; verified stop, IRQ/ACK and DMA/IOMMU retirement. Manual focus does not disable BF outputs.

4. **clean front rear image (L5/L6).** After required gates, use the existing E011BS eight-fresh-frame-per-camera normal-scene front/rear/off target in an ordinary app, naming each route and processing path. Acceptance: Fresh complete normal-colour frames, supported controls, neutral stop/switch and private image QA. Full 30fps/4K/catalogue parity is later.

The disposable E011AR runner intentionally pins exposed output mappings until reboot. Safe persistent free/reuse remains a later production gate; this audit does not replace the current finite-run authorization conditions with a demand for an everyday service.

Immediate E011DJ task: selected-baseline input/dependency ledger, especially normal RS count/whole-frame offset and normal inputs still provided by observed records. This source-only scope correction grants no runtime, removes no enabled BF/statistics channels, copies no captured packets as producer inputs and invents no minimal whitelist.

## Lab and reporting contract

SP11 Linux is the source/build/test target; SP11 Windows is the same physical oracle; SP7 supplies independent debug/recovery; PiMaster is the control plane. Use only these authorized hosts. Keep original OEM binaries/tuning/name/instruction data and optical pixels/image hashes private on SP11. Preserve Golden FullIO v19c, historical checkouts and consumed identities. Linux system suspend/hibernate remains prohibited. No default promotion or persistent service is claimed.

Each update names the product gate, new evidence, inherited regression evidence and next falsifiable check. Describe physical capture as live, a compiled candidate as build-only and owned-memory checks as emulated. Closed numerical producers need no rediscovery unless inputs/contracts change.

See [machine-readable audit](CAMERA-STACK-AUDIT-2026-10-03.json) for references and open gates.
