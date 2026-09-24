# Agent operating contract — SP11 camera

This file is the durable working agreement for assistants/agents operating this repository.

## Canonical Windows → native Linux camera architecture and slice map (2026-09-24)

Before selecting a porting task, driver function, Windows app, breakpoint,
or camera mode, read [docs/CAMERA-STACK-PORT-MAP.md](docs/CAMERA-STACK-PORT-MAP.md).
It is the PINNED Windows request/AVStream/platform/sensor/ISP/DMFT/physical
graph and separate L0–L6 Linux responsibility map, with two schematics,
evidence classes P=physical, S=static, H=hypothesis, D=design, and
mode-specific test ledger. Its acceptance verifier is
`PYTHONDONTWRITEBYTECODE=1 python3 tools/verify-camera-stack-port-map.py`.

USER SCOPE: clean, controllable, native Linux stack with essential Windows-
observed sensor, ISP, DMA, power, controls and safe front/rear switching;
**no required Windows Camera app, Frame Server, .sys/.dll translation,
Windows Studio Effects, AI image enhancements or proprietary orchestrator**.
Put deterministic physical safety/ownership in kernel CAMSS/V4L2; put
optional AE/AWB/AF algorithm/policy behind standard controls or a small
open libcamera IPA where appropriate. Existing E004nr–E004nv rear native
ISP source is compiled but UNCALLED and DENIED; static BF group8 does
not prove a live event; front 27-frame, rear RAW/software fallback and
Golden remain protected. Every new experiment MUST name a Linux L0–L6
slice, an explicit mode/client, evidence tier and falsifiable next gate;
update the map if the Windows→Linux component boundary changes.

## E004os IFE original resource arrays originate in MmMapIoSpaceEx, not DMA stop proof

[E004os original same-SP11 ISP mapping producer](experiments/E004-front-ir-vd55g0/e004os-ife-original-mmio-map-resource-array-producer-static/README.md): 97 exact original ARM64 instructions, original `MmMapIoSpaceEx` vs `MmUnmapIoSpace` IAT check and 16 negative tests PASS. Resource-table global0x4AEE0 fields+0x50/+0x20 are allocated arrays conditionally populated with four descriptor-match `MmMapIoSpaceEx` return pointers from descriptor start+0x18, length+0x20; IFE original lookup0x2B568 chooses their first/second entries for context+0x140, then mode+0xC00/+0x1200 yields selected window+0x150. This proves *static original MMIO pointer provenance*, not which physical VFE1 instance the live rear4K selects, successful live mapping, BF0x0F or WM16 IRQ/DMA retirement. NEXT map selected resource name/physical device and independent WM16 bus/IRQ/per-buffer retirement; no rear runtime arm or blocked KD attempt. Golden/front PIX/rear RAW fallback/IR protected.

## E004or IFE register-base software pointer provenance source-verified, not physical VFE1

[E004or same-SP11 original ISP base lookup](experiments/E004-front-ir-vd55g0/e004or-ife-register-window-provenance-static/README.md) verifies 93 exact original ARM64 instructions, three source-decoded PE jump-table entries and 16 negatives: IFE init calls resource lookup0x2B568, selecting global resource-table RVA0x4AEE0 field+0x50 first pointer for selector0 or field+0x20 first/second pointer for selectors2/3, stores base at context+0x140 and selects window at +0x150 by base+0xC00 (mode zero) or +0x1200 (nonzero). Source-derived original finalizer offsets are +0xC18/+0xC1C/conditional +0xC08 versus +0x1218/+0x1208. Actual live rear4K selected physical VFE1 base, global resource-table population, BF0x0F WM16 DMA retirement remain UNKNOWN. NEXT map global resource-table pointer producers to mapped physical IFE instance and independent IRQ/bus per-buffer DMA completion. No rear ISP runtime activation; protect Golden/front PIX/rear RAW+SW4K/IR.

## E004oq actual original IFE finalizer callbacks are mode-specific register writes, not DMA fences

[E004oq same-SP11 original ISP finalizer source](experiments/E004-front-ir-vd55g0/e004oq-ife-mode-selected-finalizer-register-writes-static/README.md): 94 exact original ARM64 instructions/two PE function entries/14 negative tests PASS. IFE context+0x6B678 zero-state selects finalizer RVA0x1D2B0, nonzero-state RVA0x1BE80, stored context+0x6B690 and invoked from E004op stop helper0x27358. Both bounded callback bodies write different original base/selected register-window offsets and call software-bookkeeping helper0x1C958; neither directly validates WM16 DMA quiescence or IRQ retirement. Live rear Windows mode/base/BF event remain unproven. NEXT independent original register-window/WM16 bus/IRQ/DMA stop acknowledgement and active Windows rear selected mode before any native Linux rear hardware ISP activation. Do not free DMA on callback return/event. Preserve Golden/front native PIX/rear RAW fallback/IR; rear compiled Linux ISP runtime DENIED.

## E004op distinct original IFE stop-progress flags and two software events

[E004op original same-SP11 ISP flag producer](experiments/E004-front-ir-vd55g0/e004op-ife-stop-pending-flag-two-event-modes-static/README.md): 50 exact original ARM64 instructions + four PE entries + 14 negative tests PASS. Bounded IFE stop helper sets software active context+0x173, after selected finalization callback +0x6B690 sets pending context+0x171=1, and signals KeSetEvent on context+0x38. Separate mode-one0x1C9D0 and mode-zero0x1EF90 handler branches clear that flag and use later helper signalling **different context+0xC8 event**. Neither signal independently proves live rear4K path, BF0x0F, WM16 bus/IRQ or DMA retirement. NEXT trace +0x6B690 callback's actual physical ack and independent selected Windows mode; do not free/handoff on flags/events. Keep Golden/front native PIX/rear RAW/software4K/IR protected; experimental rear Linux ISP runtime-denied.

## E004oo IFE later-progress event is KeSetEvent, no DMA-stop inference

[E004oo original same-SP11 ISP later IFE event](experiments/E004-front-ir-vd55g0/e004oo-ife-later-progress-event-not-dma-ack-static/README.md) checks 60 exact original ARM64 instructions, all 33 instructions of helper RVA0x241D8 and three source-resolved original imported API slots, with 11 fail-closed negatives. Conditional context flag+0x171 is cleared before calling helper; wrapper RVA0x2A1D8 invokes original imported **KeSetEvent**. This is SOFTWARE EVENT signalling, not an independent WM16 DMA/IRQ bus drain or buffer fence. Other hardware-driven callers may exist; do not claim entire stop sequence lacks a hardware ack. NEXT trace flag producer and independent BF/WM16 per-buffer bus/IRQ retirement, live rear selected IFE mode. Preserve Golden, front PIX, rear RAW+software4K and IR safeguards; source-compiled experimental Linux rear ISP runtime remains denied.

## E004on three concrete 0x809 first callbacks do not acknowledge physical stop

[E004on original same-SP11 ISP first callback source](experiments/E004-front-ir-vd55g0/e004on-isp-selector-809-three-concrete-core-receivers-static/README.md): E004og-installed CSID/IFE/CDM first callback valid-input 0x809 paths source-checked at 57 original ARM64 instructions + 13 negatives. CSID default diagnostic status 0, IFE default status 0 **without** 0x805 IFE stop helpers, CDM unsupported-selector status 0x0E. Conditional [S], no claim that live rear Windows 4K selects any of them. Neither zero return nor 0x809 is physical WM16 DMA/IRQ quiescence; never release buffer or switch native Linux shared-core owner from these selectors/statuses. NEXT independent IFE later progress/bus/IRQ/WM16 DMA retirement and live rear selection evidence; maintain source-compiled rear ISP runtime DENIED and protect Golden/front/rear RAW fallback/IR.

## E004om conditional manager per-core list writer identified, no live rear inference

[E004om same-SP11 ISP manager list](experiments/E004-front-ir-vd55g0/e004om-isp-manager-core-list-producer-static/README.md) 80 original ARM64 instruction anchors and 17 fail-closed tests PASS: conditional 0x802 hardware-descriptor configuration can append two paired descriptor indices or one selected index to manager indexed words starting at six and increments manager +0x24 count. E004ol 0x809 generic dispatch reads the SAME record/count. Count-nonzero branch skips the checked builder; not all producer/teardown cases are closed. Actual live rear4K configured core IDs, callback semantics, IRQ/BF/WM16 DMA retirement remain unproven. NEXT trace actual 0x809 branch/return of concrete E004og CSID/IFE/CDM first callbacks and independent physical stop. Preserve Golden, front PIX, rear RAW/software fallback, IR privacy; experimental rear Linux ISP remains runtime DENIED.

## E004ol selector0x809: generic default forwarding, not a decoded stop command

[E004ol original same-SP11 ISP source](experiments/E004-front-ir-vd55g0/e004ol-isp-selector-809-independent-dispatch-static/README.md) independently traces 0x809 through dedicated-case fallthrough into manager generic/default branch RVA0x1932C; eligible configured core callbacks receive original w1=0x809. 58 exact original ARM64 instruction anchors + 12 fail-closed checks PASS. Generic list starts at manager index six, but actual live rear VideoRecord selected cores, receiving callback bodies and 0x809 argument/return/hardware semantics remain UNKNOWN. Do not equate with 0x805, a physical stop, or DMA buffer retirement. Signed >=4 ID guard is not proof of nonnegative IDs. Next find exact generic-list producers/receivers; independently trace IFE/WM16 IRQ/bus/DMA stop and live selected rear profile. Linux rear native ISP remains runtime-denied; Golden/front PIX/rear RAW fallback/IR safe.

## E004ok immediate BF stop callback is NOT physical WM16/DMA retirement

[E004ok source-only original ISP trace](experiments/E004-front-ir-vd55g0/e004ok-bf-stop-cfg0-postwrite-software-state-static/README.md) establishes that the conditional BF0x300D WM16 CFG0 zero-write at original RVA0x1DA74 branches to a common tail and entire 16-instruction helper RVA0x1C990–0x1C9CC, which only updates original context mapping/software status. Valid resource flag update/return and the outer IFE loop also do **not** provide a hardware IRQ/DMA completion acknowledgement. Exactly 47 original ARM64 instructions + 12 fail-closed checks PASS, **static-only**. Next independently source-trace later IFE progress/event and BF/WM16 bus/IRQ/queue buffer-retirement; confirm live rear Windows selected instance/mode separately. Never free WM16 DMA or switch Linux shared PIX owner based solely on CFG0 zero or callback return. 0x809 independently unknown. Protected Golden, front native PIX, rear RAW/software4K, IR safeguards unchanged; experimental Linux rear ISP still runtime-denied.

## E004nz OEM AVStream camera-engine handoff — next reverse-engineering slice

The same-SP11 `surfacecamavs8380.sys` has now been independently
verified **statically** at 66 exact ARM64 instruction anchors, see
`experiments/E004-front-ir-vd55g0/e004nz-avstream-profile-control-static/README.md`
and `RESULT.json` and rerunnable `verify.py` (17 negative cases).
Not merely a list of Windows drivers: we pinned AVStream preview/still/
video/stats pin handlers, single-active-filter policy, privacy state,
CameraEngine OnStart/OnStop, actual separate user-mode sensor timing
and profile/processing CONFIG packet path, separate PER-REQUEST packet,
and separate ISP notification worker. Windows INF **registers**
QcDeviceMFT8380.dll but its actual involvement in the rear recording
is UNPROVEN; OEMCameraProfiles syntax in that INF is COMMENTED EXAMPLE.
CCameraEngine engine start RVA0x1efd0 / stop RVA0x1f130 both call
indirect helper RVA0x20da8 with potential ordered selector sites
0x804,0x804,0x5,0x17 (start) and 0x805,0x809,0x805,0x18 (stop).
These NUMERIC VALUES ARE **NOT DECODED COMMAND MEANINGS OR LINUX
IOCTLS**. Do not port them until the helper's backing interface and
actual platform/ISP/sensor recipient have source-backed mapping;
branches may skip certain command calls. Source code proves Windows
separately handles IFE and sensor stop and timing-aware user-mode
control without requiring a Windows AI/effects pipeline. Linux kernel
must preserve hardware safety/ISP/DMA ownership; optional 3A/IQ policy
may be small open libcamera IPA / explicit standard user controls.
The E004nv mode0 BF branch, live rear BF and Linux native4K ISP frame
remain unproven; no new runtime code loaded, Golden untouched.

## E004oa backend interface — next Windows→Linux source slice

The original same-SP11 AVStream CameraEngine's common dispatcher now has
a SOURCE-VERIFIED **external Windows kernel-device interface acquisition**
path, see
`experiments/E004-front-ir-vd55g0/e004oa-avstream-kernel-interface-bind/README.md`.
Exact OEM SHA pinned, 42 ARM64 instructions + five Windows IAT mappings
+ two engine virtual-table entries + 12 negative mutations pass.
Engine→binder RVA0x20b60 actually calls IoGetDeviceInterfaces,
IoGetDeviceObjectPointer, then internal device-control
**opaque request code 0x002326AB** with 8-byte output via
IoBuildDeviceIoControlRequest/IofCallDriver; chosen backend interface
record later feeds engine common indirect dispatcher RVA0x20da8,
which calls the returned vtable or alternate callback. This proves
there is an external driver interface; it does **NOT** identify the
active rear-session device-interface identity, receiving
qccamplatform/qccamisp/sensor driver, selector meanings, nor live BF.
E004nz engine start/stop selector numbers must NEVER be treated as
Linux commands until original OEM receiving handler/request ABI
is matched. NEXT static trace: original OEM device-instance interface
identity + receiver for 0x2326AB, then hardware-only necessary
sensor/ISP command lifecycle. No Windows services/AI needed for native
Linux hardware safety. Golden/front/native27/rearRAW/software4K intact.

## E004ob actual matching OEM interface-code receiver branches

E004oa's source-verified opaque internal request0x2326AB is NOT
a unique marker for one camera backend! The next static audit
`experiments/E004-front-ir-vd55g0/e004ob-dual-backend-ioctl-static/README.md`
and `verify.py` source-locks originals qccamplatform8380.sys and
qccamisp8380.sys (20 exact ARM64 receiver instructions, both OEM
SHA256, 12 fail-closed mutations). Platform matches same code at
RVA0x6334→0x6364 and clears a state flag/two fields; ISP matches
at RVA0x5638→0x566c and populates its pointer/flag/callback.
Do NOT equate those structures/semantics or presume both received
one request. **LIVE rear VideoRecord selected interface and receiving
driver unverified.** Next map AVStream binder's device-instance
interface identity to original platform/ISP/sensor registration;
only then decode the opaque OnStart/OnStop selectors into real
hardware effects. Current source-only audit changes no Golden,
front native27, rearRAW/software4K, IR or Linux rear native4K status.
Do not port Windows orchestrator, hidden .sys/.dll code or AI effects.

## E004oc closes static backend-GUID routing, NOT callback semantics

[E004oc device-interface routing](experiments/E004-front-ir-vd55g0/e004oc-device-interface-identity-routing-static/README.md) SHA-pins original same-SP11 OEM Windows binaries and **nine** AVStream table identities; **seven** have independently checked original provider registration-code call sites. The correct static provider mapping is **rear sensor slot 1, front sensor slot 2, ISP slot 4, shared platform slot 5**, flash slot 0, auxiliary slot 3, secure ISP slot 8. Slots 6–7 remain UNKNOWN in the scoped archive. The ISP, rear and front sensors also **query** the platform-common GUID, which is **registered** by the platform driver: do not mislabel consumers as duplicate providers. One opaque 0x2326AB request appearing in both platform and ISP does not mean it broadcasts a single command.

**Live rear VideoRecord selected identity remains UNKNOWN**, as do the original returned callback implementations/selector argument ABI, true BF/WM16 DMA retirement and native Linux rear ISP4K optical frames. Next only source-trace **ISP slot-4, rear sensor slot-1 and platform slot-5 returned interfaces**, then map physical effects into independent Linux CAMSS L0–L3. No Windows Frame Server/AI/effects dependence; no numeric Windows engine selector promoted to a Linux command without source-backed receiver evidence.

## E004oc ISP nested callback source proof — do not name Windows selectors yet

The original same-SP11 ISP matching interface-acquisition branch sets callback RVA0x4E30. Only if the AVStream alternative-dispatch path is selected, its engine selector is passed to that ISP callback. Source-locked original ARM64 code at ISP RVA0x50C4–0x5210 sends selector values 0x804/0x805/0x809 to a **SECOND, currently unidentified callback interface at ISP state/context +0x10**. Proof: experiments/E004-front-ir-vd55g0/e004oc-device-interface-identity-routing-static/verify_isp_callback_delegation.py (24 exact instruction anchors) and README addendum. Do not map these numbers to native ISP/sensor start/stop or assume this was the actual rear video runtime path. The next static dependency is the nested callback producer and its actual receiving hardware request ABI. Protect original Golden/front/rear RAW fallback, no Windows AI/effects port.

## E004od resolves the ISP hardware-manager callback, but NOT core-side MMIO semantics

The prior ISP context +0x10 callback UNKNOWN is now resolved in original same-SP11 OEM source: ISP context initialization at RVA 0x6A0A0 passes +0x10 to a 16-record pool helper RVA 0x15A40, which installs a real callback **RVA 0x15D70**. The hardware-manager callback distinguishes 0x804 and 0x805, forwards them to different per-core interface arrays with conditional error paths, and does not directly prove the physical IFE/CSID/CDM per-core implementation, Linux-equivalent register order or actual runtime selection in Windows rear VideoRecord. 0x809 is separately UNKNOWN. See experiments/E004-front-ir-vd55g0/e004od-isp-hw-manager-nested-start-stop-static/README.md and 50 original ARM64 source anchors/16 negative tests in verify.py. Next trace ISP HW-manager per-core receiving IFE/CSID/CDM callback implementations and parameter ABI; port only independently verified hardware effects. Keep Golden native front/rear RAW fallback protected, no Windows AI or opaque command transplantation.

## E004oe: verified ISP-manager core dispatch order, NOT physical stop acknowledgement

[Same-SP11 original ISP E004oe analysis](experiments/E004-front-ir-vd55g0/e004oe-isp-manager-per-core-order-static/README.md) checks 55 exact original ARM64 instructions, six distinct diagnostic-hash/code-xref stage identities and 13 fail-closed mutations. Conditional selector 0x804 branch source software dispatch **CDM→IFE→CSID**; 0x805 branch **CSID→IFE→CDM**. These stage labels are now source-backed in the manager; their receiving per-core callback implementations/ABI and physical hardware register/IRQ/DMA completion are NOT identified. 0x809 and live rear Windows 4K session path also remain UNKNOWN. Next static only: identify CDM, IFE, CSID interface array producers and lower callback bodies; don't encode opaque Windows selectors into protected Linux Golden. No Windows AI/effects dependence or native rear4K claim.

## E004of exact per-core interface provenance — next function-body boundary

[E004of](experiments/E004-front-ir-vd55g0/e004of-isp-per-core-interface-provenance-static/README.md) source-locks original ISP core-array allocators 0x3918/0x15768, dynamic descriptor lookup 0x156E8, and 0x30-byte per-core records populated with independently obtained callable pointers at 0x698A8, then read/checked/indirectly called from E004oe's CDM/IFE/CSID manager. 56 exact original ARM64 anchors + 15 negative tests PASS; all static only. NEXT: locate actual first callback function bodies in the core descriptors; verify argument and physical MMIO/interrupt/DMA lifetimes before implementing native Linux L0–L3. No live rear profile, 0x809, BF/WM16 retirement or Linux-native rear ISP4K proven. No opaque Windows interface/effects transplant or Golden runtime changes.

## E004og original CSID / IFE / CDM *actual* callable functions now identified

[Exact same-SP11 original ISP first core callback functions](experiments/E004-front-ir-vd55g0/e004og-original-isp-three-core-callback-implementations-static/README.md): original init code stores CSID RVA0x211B0 at 0x176A4, IFE RVA0x22CD0 at 0x2234C, and CDM RVA0x28480 at 0x1835C into their respective original core interface slots. All three are independently original PE function-entry metadata and each has explicit 0x804/0x805 dispatch, source-locked with 45 ARM64 instruction checks and 14 negative tests. Original IFE 0x805 branch calls separate stop helpers RVA0x221A0 and 0x27278; CSID and CDM have distinct worker/event/state progress paths. **Those are static installed original function bodies, NOT live rear session execution nor proof of VFE DMA/WM16 safe physical retirement**; do not infer source-only group8 BF event live. Next source trace IFE stop helpers, CSID stop worker and CDM event/hardware completion and per-mode DMA/IRQ before runtime-changing Golden. No Windows command/code/AI port.

## E004oh original multistage stop: never free DMA on the outer callback alone

[E004oh original same-SP11 ISP source proof](experiments/E004-front-ir-vd55g0/e004oh-isp-multistage-stop-progress-static/README.md) traces the concrete IFE 0x805 receiver through two distinct stop helpers 0x221A0 and **bounded per-resource stop helper 0x27278**, plus separate later IFE progress path 0x1F230/event helper 0x241D8. Original CSID also has separate atomic pending-work decrement RVA0x1BCCC and worker/event stop RVA0x21B00; CDM its own command state/event. 45 actual original ARM64 anchors and 14 fail-closed tests PASS, static only. **Do not interpret CSID pending zero, IFE stop callback return, or CDM event progress as hardware VFE WM16/DMA/IRQ quiescence**. NEXT trace IFE per-resource indirect callback in 0x27278 to original VFE/WM stop/ack and actual frame/stats buffer ownership. No Windows AI/Frame Server, original OEM binary transplant, Golden camera activation or 4K-native rear proof.

## E004oi actual IFE resource callback is mode-selected and BF-port aware

[E004oi source-locked original ISP resource callbacks](experiments/E004-front-ir-vd55g0/e004oi-ife-resource-callback-bf-port-static/README.md): original IFE init tests +0x6B678 state and chooses **0x1C0F0 for nonzero, 0x1D830 for zero**; stores chosen original PE function into IFE +0x6B688 at 0x19FE8. E004oh bounded stop loop at 0x27278 reads SAME field at 0x272E4 and invokes with resource ID and stop flag zero. **The zero-state alternate callback 0x1D830 explicitly branches for BF-associated resource 0x300D**. Static-only 35 original instruction anchors and 16 negative tests; do not assume live rear 4K selects zero state or that BF FIFO8/WM16 DMA completed. Next trace 0x1D830 BF resource+stop flag 0 to specific VFE bus register/IRQ/WM16 safe retirement, validate active rear session, preserve Golden/native front and RAW fallback. Do NOT transplant Windows selector/AI/effects stack.

## E004oj conditional BF0x300D IFE stop-zero write matches original WM16 CFG0 offset

[E004oj source-verified original IFE register math](experiments/E004-front-ir-vd55g0/e004oj-bf-resource-zero-register-offset-static/README.md) proves the IFE zero-state callback uses original register base+0xC00; the E004oi bounded 0x805 stop helper calls this handler for resource 0x300D with zero flag; original switch-table entry 13 selects RVA0x1DA6C which writes zero at chosen window+0x1200. Thus **original register base+0xC00+0x1200 = base+0x1E00**, matching independently E004nv BF/WM16 CFG0 relative offset. 35 exact original ARM64 instructions and original jump-table source plus 14 negative mutants. Static conditional register write != proof actual live Windows rear4K selected this mode/base, BF0x0F FIFO8 event, IFE bus stop/WM16 safe DMA retirement or Linux rear ISP4K optical pixels. NEXT source-check original post-write WM16 bus/IRQ/queue stop and live selected rear4K mode before Linux runtime arm; no direct Windows command/AI transplant, Golden preserved.

## Mission

Develop a native Linux camera stack for Surface Pro 11 (Denali/X1E80100) with the same evidence discipline used for the successful SP11 audio work. Windows on the same hardware is the behavioural oracle. The objective is native Linux implementation, not wrapping or redistributing Windows drivers.

## RGB product priority (latest user decision, 2026-09-23 ~19:36 BST)

User EXPLICITLY selected the previously optional SECOND route:
resume native Qualcomm Spectra hardware ISP / SAME SP11 Windows
OEM camera stack as the engineering oracle to seek improved real
front1080/rear4K image detail, color and brightness. This decision
SUPERSEDES the earlier software-FIRST / ask-before-ISP wording
below. The proven opt-in Linux RAW10-to-NV12 software camera
(E004ne last complete original acceptance) is RETAINED as a
fallback and for safe baseline comparison, not silently promoted
to final Windows-parity production. CORRECTION: E003i-HY
physically captured 27 REAL hardware-generated front VFE1 PIX
QC10C frames under protected Golden; E003i-Z previously passed
six actual native front AEC/BHist/AWB generation-matched stats.
Windows-equivalent FRONT colour/detail/true linear NV12 and
any REAR hardware-ISP processed 4K image are NOT proven.
The earlier E003h initial PIX first-frame attempts failed but
do not invalidate LATER successful E003i front evidence.
Front IQ materializer is a source reference, NOT independently
a working rear OV13858 service. Read both source-only
audits FIRST:
experiments/E004-front-ir-vd55g0/e004nj-icp-firmware-host-compatibility-readonly/README.md
experiments/E004-front-ir-vd55g0/e004ni-native-isp-windows-rear-oracle-source-audit/README.md.
Do not blindly load Xtensa Windows CAMERA_ICP firmware
with Linux Q6 AUDIO remoteproc. Linux currently has
ADSP/CDSP only and the checked CAMSS source firmware
requests are HOST IQ capsules, not an ICP loader.
Re-use ACTUAL validated E003i native front PIX QC10C/
3A hardware evidence for a source-locked OV13858
REAR-specific native PIX first-frame design, NOT
as if front tuning or the rear processed frame
were already proven.
The installed MSHW0491 rear OV13858 selects its OWN Windows
sensor module and tuning; do not confuse with MSHW0561 or front
IMX681 package, nor try to run Windows PE .sys/.dll as Linux
drivers. Windows binaries/firmware, optical photos/pixels/RAW/
thumbs/image hashes never enter Git/chat/other hosts.
All existing Golden one-shot source-pin, >=29fps each actual
gain window, complete native neutral, IR OFF and NO Linux
OS-level sleep rules remain mandatory. Do not enable a default
native ISP or flash unverified Windows firmware.


## E004nq rear-native Windows route supersedes rear RAW parity assumption

2026-09-23 E004nq physically captured TWO same-SP11 Windows Rear OV13858
VideoRecord 3840x2160 sessions using the **original working front E003g
SP7 KDNET `dd /p` PHYSICAL register command** at IDLE/LIVE1/POST/LIVE2/POST2.
The later E004nm `!dd` was NOT the same physical acquisition and its
all-0x80000000 camera values must NOT block hardware work.
E004nq's five-phase/repeated OEM proof shows Windows REAR uses:

- CSIPHY1, **4 D-PHY lanes**, CSID1 RAW10 IPP crop **x0..4063/y0..2285**
  (4064x2286, GRBG Bayer phase unchanged);
- shared VFE1 FULL WM0 luma 3840x2160 and WM1 chroma 3840x1080,
  **physical WM stride 5120**, packer reg0x0b, plus DS4/DS16 and stats;
- CSID0 IPP disabled and VFE0 inactive in BOTH actual Windows rear PIX
  capture passes. Both stopped states return exactly to all-sentinel idle.

Front E003g ALSO uses CSID1/VFE1, but has IMX681 C-PHY CSIPHY2,
input crop3840x2160 and output2560x1440: the two OEM camera modes
**time-multiplex the same processing cores** with distinct CSI and IQ
profiles. Preserve the existing Linux rear CSIPHY1→CSID0→VFE0 RAW
E004lr diagnostic capture and E004ne SW4K fallback: they are REAL,
but NOT Windows rear native ISP parity. Historical E004nk/E004nl rear
VFE0 source preflight/route must not be used as a *Windows native rear
4K processed route gate*. Do NOT copy front-only predicates, tuning,
2560x1440 QC10C output or MF app stride3840 into new rear hardware.
New Linux rear PIX must have separately source-locked CSI1/VFE1
graph ownership, 4K hardware output surface, OV13858 Bayer crop, IQ/
RT-CDM/3A scheduling, checked DMA/SMMU and Golden-safe cleanup;
**Linux rear native 4K ISP frame remains unproven**. The reusable E003g
method is physical `dd /p`, not a dependency on private OEM WPP/TMF
decoders. See E004nq README.md/RESULT.json/WINDOWS-RESULT.json/verify.py.

## E004nr compiled rear native-ISP source-only profile (NOT an arm gate)

The next Linux rear native-ISP graph/profile is now real **compiled ARM64
CAMSS kernel source**, independently staged against the existing integrated
CAMSS base instead of changing the deployed Golden or accepted front path:
`experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile/`.
It rejects any sensor other than physical rear OV13858 GRBG4076x2806
CSIPHY1 four-lane D-PHY linked to **CSID1 PIX → VFE1 PIX**; it is
not the still-useful diagnostic rear CSID0/VFE0 RAW media graph.
E004nq-proven Windows rear IPP 4064x2286 x0/y0, FULL Y3840x2160,
C3840x1080, physical WM stride5120 packer0xb are separate from the front
IMX681 QC10C profile. New SP7-private-KD whitelisted WM two-live-pass
registers show WM0 frame-incr0x00a9d000, WM1 frame-incr0x00559000,
FULL metadata cfg0x800, WM modes0x23/0x33; this still does NOT prove
a safe Linux DMA/UBWC allocation/IOVA/V4L2 buffer format or IQ.
`camss_e004nr_rear_pix_runtime_authorization` unconditionally returns
`-EOPNOTSUPP`; no runtime caller/module parameter was added.
The isolated new qcom-camss module was actually compiled and validated,
but it was NEVER installed/loaded/booted. The original integrated
CAMSS camss.c is byte-identical and the accepted Golden/front sources
are not changed. See E004nr verify.py and README.md for source-lock
checks and 15 fail-closed negative tests; do not rerun an already-used
staged build directory without an independently new source identity.
NEVER promote the source-only rear profile to live hardware without
separately establishing 4K buffer metadata/IOMMU ownership, sensor IQ/
3A/RT-CDM packet lifecycle, and safe exclusive shared CSID1/VFE1
front/rear switching. A Linux-native rear 4K optical ISP frame is
**still unproven**.

## E004ns source-only compiled rear CSID1 IPP register configuration

A NEW isolated ARM64 kernel build now includes real rear-only CSID1 IPP
mode/receiver-word/prepare/enable routines from
`experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline/`.
The code is compiled with the prior E004nr rear graph check but **has NO
caller in any runtime path**; authorization always returns
`-EOPNOTSUPP` and no module is installed/loaded on protected Golden.
Both original E004nq Windows rear KD LIVE1/LIVE2 samples match ALL 26
whitelisted CSID1 configuration dwords. Rear `RX_CFG0=0x10232103`
contains `TPG_NUM_SEL=1` despite FOUR-lane D-PHY; the existing
`__csid_configure_rx()` only sets that bit for the front C-PHY, so it
MUST NOT be reused unchanged for rear. Rear IPP register +0x330 is
`0x02000000` (front companion writes zero); rear HCROP x0..4063,
VCROP y0..2285; +0x388 is **IPP_FORMAT_MEASURE_CFG1** configured
expected dimensions 4064x2286, NOT an independently observed
completed-frame width/height register. See E004ns README.md/verify.py
for 17 negative tests, isolated module SHA and source preservation.
Only final LIVE register targets, not OEM startup order, were observed.
Do NOT connect rear prepare/enable to front code, probe, V4L2 or sysfs
until independently implemented 4K FULL Y/C+metadata/IOMMU-safe buffer
surface, RT-CDM/IQ/3A lifecycle, rear-specific startup order,
CSID1/VFE1 front/rear mutual-exclusion and Golden-safe rollback are
validated. Existing front E003i, Linux rear E004lr RAW and E004ne
software fallback remain unchanged.

## E004nt compiled rear 4K VFE1 coherent-DMA surface — still offline

A NEW source-only isolated ARM64 CAMSS build, E004nt at
`experiments/E004-front-ir-vd55g0/e004nt-rear-vfe1-4k-buffer-contract/`,
retains original E004nr graph and E004ns rear IPP and adds actual
compiled Linux rear VFE1 FULL Y/C surface alloc/address/free routines.
SP7 PRIVATE E004nq Windows rear LIVE1/LIVE2 register snapshots gave
the identical RELATIVE layout: Ymeta=0, Ydata=0x11000,
Cmeta=0xA9D000, Cdata=0xAA6000, frame increments Y0xA9D000,
C0x559000, combined output window0xFF6000=16,736,256 bytes,
both WM physical stride5120. NO Windows DMA address or optical bytes
were exported; only relative geometric offsets were committed.
Linux source uses the ACTUAL CAMSS device for a single coherent
DMA allocation, verifies whole 4K-aligned IOMMU DMA aperture fits in
the 32-bit VFE registers, compile-time bounds metadata+row coverage,
and refuses address-rebind/free in-flight. **This is NOT already
allocated, NOT a V4L2 NV12 format, NOT UBWC metadata correctness**.
`vfe680_e004nt_rear_4k_runtime_authorization` still ALWAYS
returns `-EOPNOTSUPP`; no source caller, module installation,
Golden boot mutation, real device DMA allocation or rear native 4K
optical frame has occurred. Existing front 27-frame E003i, rear RAW
E004lr and software4K E004ne implementations remain intact.
The new qcom-camss module compiled cleanly in a unique isolated
directory, NOT installed/loaded; see E004nt README/verify.py for
actual module SHA, byte-for-byte original-source preservation and 18
negative tests. Next integrate rear-only VFE1 WM programming,
exclusive CSID1/VFE1 ownership, ISP IQ/RT-CDM/3A and safe hardware
retire before ANY Golden-safe live rear 4K native optical-frame test.

## E004nu rear VFE1 BUS ten-client source-only implementation

The new independently compiled ARM64 CAMSS experiment
`experiments/E004-front-ir-vd55g0/e004nu-rear-vfe1-ten-wm-ownership/`
incorporates all prior E004nr graph/E004ns rear CSID1 IPP/E004nt coherent
4K buffer source-only gates and adds a distinct ten-WM rear VFE1 BUS
static configuration and conservative candidate per-client frame lifecycle.
Windows rear had WMs 0,1,2,3,11,12,13,14,**16**,18 in BOTH live
recordings; the working front BUS recipe only has nine, OMITTING the
active rear WM16 BAF autofocus stats. DO NOT reuse front's nine-master
configuration for rear. New rear code checks all ten existing enable
bits BEFORE writing anything and writes only STATIC config fields with
WM enables cleared, and NO Windows/Linux DMA image/meta addresses.
The ten-client frame model refuses buffer release until all ten verified
master completions (including WM16) and independent HW BUS STOP.
**Actual rear WM16 completion event/group mapping remains UNKNOWN,**
so DO NOT connect this model to any real ISR, deem a front VIDEO event
sufficient, or free a timed-out in-flight buffer. The rear-only runtime
authorization still unconditionally returns -EOPNOTSUPP and the new
source has NO callers in the active Golden kernel. The isolated kernel
module was actually compiled with zero warnings/errors and verified
against exact two-phase rear WM nonpointer physical evidence, 20 negative
tests and byte-identical original front CAMSS/CSID/VFE source.
No module installed/loaded, no camera activated, no DMA allocated,
and Linux native rear 4K ISP optical frame is still UNPROVEN.
See E004nu README, verify.py and BUILD-RESULT.json.

## E004nv OEM static BF completion group8, six-group rear candidate

The NEW isolated same-SP11 E004nv
`experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/`
recovered a previously-unexercised OEM Windows BF stats IRQ branch in
the exact private same-SP11 qccamisp8380.sys (SHA64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c):
event 0x0F at RVA0x1fc60, diagnostic "IFE%d IFE BF stats buf done
Irq occured." RVA0x37b88, passes group index8 at RVA0x1fc8c
to the SAME independent FIFO helper RVA0x26460, and stores resource
port0x300D at RVA0x1fce8. Both Windows rear 4K physical live
snapshots showed active extra WM16 BAF, absent from the working front.
This supports a new **static-candidate** sixth rear completion group:
VIDEO0x03/idx0 WM0-3, AEC_BE_BHIST0x0D/idx5 WM11-12,
TL_BG0x0E/idx6 WM13, AWB_BG0x10/idx7 WM14,
BF0x0F/idx8 WM16, RS0x12/idx9 WM18.
IMPORTANT: BF event 0x0F was **NOT ACTUALLY OBSERVED** during either
Windows rear live session, nor was a WM16 DMA completion proven.
Do not present a static OEM BF branch as a proven LIVE rear DMA/IRQ
lifecycle. E004nv source-only six-group mapping compiled on ARM64
with 720 offline cross-order simulations and 20 negative tests but
the runtime stays DENIED -EOPNOTSUPP, NO new caller, and Golden/front
sources remain unchanged. Private OEM binary remains only SAME SP11.
Next is a dedicated private Windows REAR LIVE BF completion trace,
then real per-group stats DMA/retire, RT-CDM/IQ/3A and safe exclusive
CSID1/VFE1 hardware lifecycle before any Linux-native rear4K run.

## E004nx/E004ny Windows rear 4K delivery control — KD contrast

Real SAME-SP11 Windows rear NV12 3840x2160 frame-reader delivery is
REPRODUCIBLE with NO KD attached. E004nx delivered 365 and 366 valid
rear4K handles across 2×35sec successful Start/Stop passes; E004ny
delivered 1152 and 1154 handles across 2×110sec successful passes,
after recording ≥12 valid handle pre-KD checkpoints EACH PASS.
The earlier E004nw SP7 KDNET one-shot BF0x0F branch was armed but
its Windows WinRT StartAsync=Success delivered ZERO handles, so no
actual BF event/WM16 completion was observed. E004ny debugger launch
was blocked by a tool safety check; **NO debugger was attached** in
that healthy test and the block MUST NOT be circumvented. Comparing
KD-armed zero frames and these two no-KD healthy runs does NOT
establish KD causation; camera timing/state may differ. See
`experiments/E004-front-ir-vd55g0/e004ny-rear4k-live-control/README.md`
and E004nx RESULT, E004nw previous failure scalar, E004ny RESULT +
verify.py with 14 fail-closed mutations. Windows ScheduledTask removed,
original private logs and binary remain private, Windows NTFS mounted
read-only and unmounted, user-authored frame-count-only source/evidence
in Git; new Linux boot verified protected Golden v19c BootCurrent0005
Linux-first order, no loaded camera/process, no Golden modifications.
Maintain E004nv BF0x0F/group8 as STATIC driver-dispatch candidate
until an authorized live debugger event is observed DURING confirmed
rear4K frame delivery, with independently established WM16/stats DMA
and IQ/RT-CDM lifecycle. Linux-native rear 4K ISP optical frame is
still UNPROVEN.

## E004nv BF static callgraph — direct WM16 proof and mode caveat

`experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/STATIC-BF-CALLCHAIN.md`
and `verify_static_bf_callchain.py` (47 SHA-locked OEM ARM64
instruction anchors) now trace **who invokes and where BF goes**.
Registration at RVA0x1a100 installs mode0 event handler RVA0x1ef90
or mode1 alternate RVA0x1c9d0 at object+0x6bd8; real event
worker at RVA0x239a0 loads/calls that handler. In mode0, incoming
second 32-bit status word bit7 generates BF event0x0F; event branch
pops FIFO group8, invokes mode0 per-event callback RVA0x1d620,
event15 target RVA0x1d710. Its mapped MMIO window begins at
VFE_base+0xc00; direct BF hardware reads VFE+0x1e00 = **WM16 CFG0**
and VFE+0x1e70 = **WM16 ADDR_STATUS0**. It stores WM16 CFG0 bit0
in device+0x1c0, which is EXACTLY the subsequent extended BF
completion gate. A nonempty/enabled path matches queued item/tag,
stamps BF resource port0x300d and notifies via RVA0x26340.
**IMPORTANT:** same binary has TWO event dispatch modes selected by
per-device instance/threshold, and actual Windows rear 4K runtime
mode is UNPROVEN; no BF input bit7, event0x0F LIVE or WM16 DMA
retirement was observed. This static route is real evidence of
BF↔WM16 connection but does NOT authorize Linux runtime, ISR or
Golden installation. Full report + offline verifier in above path.

## Resume behaviour

When asked to continue camera work:

- Do **not** ask the user to re-explain the project.
- Read `CONTINUE.md`, `PROJECT_STATE.md`, `state/project.yaml`, and the latest experiment.
- Query live machine state before acting.
- Treat repository state as authoritative for what was mechanically proven; treat hypotheses as hypotheses.

## Lab topology

- **SP11 Linux** — primary build/deploy/log/DT/V4L2 target.
- **SP11 Windows** — same physical SP11, used as hardware oracle for DriverStore, ACPI, ETW/WPP, live behaviour and KD target. It will normally be offline from PiMaster while Linux is booted and vice versa.
- **SP7 Windows** — companion/debug host. May be used for KD into SP11, USB/EEM debugging, tracing and comparative tooling.
- PiMaster is the normal remote-control plane. Rediscover exact endpoint identifiers from the tool rather than hard-coding secrets.

Reboots, static inspection, dynamic tracing and debugger work are normal parts of this lab workflow. Still preserve the known-good boot path and checkpoint before mutations.

## Access and lab quirks

- SP7 has a dedicated SSH key for SP11 Linux at `%USERPROFILE%\.ssh\sp11_project_ed25519`; the public key is already authorized on SP11. Never commit private-key material.
- SP7 also carries the established KD tooling/configuration for SP11 Windows. Reuse the configured KDNET secret locally; do not record credentials in Git. Interactive KD requires a true PTY.
- Never hardcode SP11 IPv4/MAC. Wi-Fi privacy/randomization and DHCP change them across boots; rediscover via PiMaster, mDNS, ARP/IPv6 or SP7.
- Never hardcode CCI adapter numbers such as `3-0010`; discover the bound sensor dynamically because numbering changes across boots.
- PiMaster loss during reboot, Windows/KD ownership or Wi-Fi startup is not itself evidence of a crash. Use independent SP7 reachability when needed and allow adequate boot/network time before concluding failure.
- Initrd extra-module paths may disappear after switch-root; for a manual post-boot harness, use a SHA-checked repo/build copy if the initrd copy is no longer visible.
- Do not use `.golden-v33-delta-replay/src` as the production camera source. Use `.golden-v33-repro/src` for true Golden reference and `sp11-camera-e002k-d-src` for the accepted integrated camera source.

## SP11 Linux system sleep: prohibited camera test path

The user reports that **OS-level standby/suspend/resume is not yet
implemented reliably on SP11 Linux and may crash the whole OS**.
Do NOT initiate system suspend, resume, hibernate, hybrid-sleep,
systemctl suspend, loginctl suspend, rtcwake suspend, or
write a sleep state into /sys/power/state for camera testing.
Do not schedule automated suspend/resume loops or label their absence
as a camera failure. Normal independent camera experiments and
guarded reboots with verified Golden fallback remain authorized.
Test sustained capture, sequential camera switching, stop/reopen,
service lifecycle and recovery WITHOUT putting Linux into system sleep.
Read-only observation that individual camera sensors enter ordinary
runtime-PM suspended/idle state while Linux remains awake is distinct
from OS-level standby and remains permitted. Do not change system
power-management policies. Revisit system standby/resume only after
independent platform support is established and explicit user
authorization is obtained.

## Golden protection

Current deployed Golden is the FullIO v19c audio kernel/DT/initrd stack. Camera work must not overwrite it.

- Never replace the v19c `/boot` payload in-place.
- Never make an unproven camera candidate the permanent saved GRUB default.
- Prefer a separate camera kernel release/build directory and a one-shot GRUB candidate.
- Preserve the working `7.1.5-sp11-render-parity-v4+` module tree and prepared build anchor.
- Camera changes must not silently change audio, touch, display, power or USB behaviour.

## Experiment discipline

Every meaningful hardware experiment uses `E###-slug`.

Before runtime mutation record:

- hypothesis;
- exact source/base commit or snapshot;
- files changed;
- kernel release/DTB/initrd hashes;
- expected observation;
- rollback path.

After the run record:

- boot result;
- relevant dmesg/media graph/V4L2 output;
- Windows comparison when applicable;
- conclusion: proven / disproven / inconclusive;
- next smallest experiment.

One major unknown per experiment whenever possible.

## Evidence hierarchy

Prefer, in order:

1. behaviour observed on this SP11 under Windows or Linux;
2. static data from this SP11's ACPI/DriverStore/configuration packages;
3. upstream kernel code/documentation for X1E80100 and the exact sensors;
4. working Linux implementations on closely related X1E hardware;
5. community SP11 notes/issues;
6. inference.

Never silently promote (5) or (6) into fact.

## Clean-room / repository hygiene

Do not commit proprietary Microsoft/Qualcomm binaries, firmware extracted from Windows, raw DriverStore packages, ETL dumps containing private data, or credentials. Derived facts, hashes, structure names, register observations and independently written Linux code are appropriate.

`.gitignore` intentionally blocks common proprietary/raw extensions. `tools/check-repo-hygiene.sh` is a pre-push sanity gate.

## Kernel strategy

Do not rewrite generic Qualcomm infrastructure merely because Surface support is absent from DT. Reuse and, when necessary, minimally extend upstream:

- X1E80100 CAMSS;
- CCI;
- CSI PHY;
- CSID/VFE;
- media-controller/V4L2 infrastructure.

Independently derive the Denali board graph, power rails, GPIOs, clocks, sensor modes and link configuration from Windows evidence.

## Definition of success

Transport parity and image-quality parity are separate milestones.

First achieve stable native RAW capture with correct power, reset, link, mode, exposure/gain and lifecycle. Only then work on ISP/libcamera processing, tuning and Windows-like image quality.

## User authorization — 2026-09-05

The user explicitly authorizes installation of useful missing tools on the project machines/OSes, discretionary Linux/Windows reboots, KD, ETW/ETL, Ghidra and static/dynamic analysis, and saving/committing/pushing meaningful progress. Proceed without repeatedly asking for these routine project actions. The user reaffirmed on 2026-09-23 that ANY lab machine and useful static/dynamic tool may be used; this supersedes the prior SP11/SP7/PiMaster-only HOST restriction. Same-SP11 proprietary Windows tuning/drivers/firmware and camera optical pixels/photos/RAW/thumbs/image hashes must still remain private on SP11; do not put originals in Git/chat or export them to another host. Preserve Golden and checkpoint exact hardware experiments. SP11 can remain on one-shot Windows for an extended oracle session; a normal reboot returns via persistent Linux-first EFI BootOrder and saved Golden GRUB entry. SP7's LCD NEVER sleeps, but has a permanently non-rendering thick dark LOWER band: use only registered healthy upper display ROI for private SP11 rear-camera comparison, and never classify its dark lower band as a camera/lens/exposure defect.


## Windows oracle scheduled-task single-use guard — E004nn correction

On 2026-09-23 E004nn a signed-in Windows user task was manually started
and THEN automatically re-ran at its `New-ScheduledTaskTrigger -Once -At
(Get-Date).AddMinutes(1)` time. Separate private original JSON files
and the original first-run ETW time boundary proved two invocations.
The ETW covers the FIRST ONLY; never merge their counts or claim
single-use. This does not invalidate the recorded first-run Windows
FrameServer 297/295 unique timestamped client samples, but is an
execution-control failure. The Windows Scheduled Task was unregistered. Source-only guarded future-task helper and duplicate-rejection selftest live in experiments/E004-front-ir-vd55g0/e004nn-rear-oem-ife-windows-observer/windows-atomic-consumed-guard.ps1 and test-windows-atomic-consumed-guard.ps1, verified on SP11 pwsh7.6.5 and SP7 native Windows PowerShell5.1. The helper was NOT used in historical E004nn and does NOT negate its second invocation.

Future Windows camera oracle tasks MUST use a persisted atomic
`[System.IO.File]::Open($marker,[System.IO.FileMode]::CreateNew,
[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)` at script
ENTRY, before any camera access, so a later unintended trigger fails
closed; also unregister the task after the intended invocation ends.
Do not assume a file-exists check only at task REGISTRATION protects
against a later automatic trigger. Do not re-use an already-consumed
Windows or Linux experiment identity. Keep original source ETL and
optical files private; commit only verified scalar evidence and
source, with explicit unproven hardware contracts.

## Concurrent-turn / UI-disconnect safety

The user-facing UI can disconnect while a backend command or another turn remains active. Never assume a missing response means the operation stopped.

Before every meaningful mutation run `tools/camera-overlap-guard.sh`, compare local HEAD/origin, inspect tracked status and active camera/build processes, verify Golden/`next_entry` for boot work, and inspect the proposed stage/evidence path.

If unexpected stage or attempt evidence exists, audit it first. For a one-shot runtime, evidence that a stream may have started makes that identity consumed until proven otherwise. Never same-boot retry and never reuse a consumed candidate.

Do not mass-clean historical untracked evidence and do not use `git add -A`; stage explicit intended paths only.
