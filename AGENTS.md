# Agent operating contract — SP11 camera

This file is the durable working agreement for assistants/agents operating this repository.

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
