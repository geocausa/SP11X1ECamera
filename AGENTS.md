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
