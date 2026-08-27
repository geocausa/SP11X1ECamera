# Agent operating contract — SP11 camera

This file is the durable working agreement for assistants/agents operating this repository.

## Mission

Develop a native Linux camera stack for Surface Pro 11 (Denali/X1E80100) with the same evidence discipline used for the successful SP11 audio work. Windows on the same hardware is the behavioural oracle. The objective is native Linux implementation, not wrapping or redistributing Windows drivers.

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
