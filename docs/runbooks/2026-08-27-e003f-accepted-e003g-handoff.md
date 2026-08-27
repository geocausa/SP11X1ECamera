# SP11 camera handoff — E003f accepted / E003g static transport start — 2026-08-27

Read with `CONTINUE.md`, `AGENTS.md`, `PROJECT_STATE.md`, `state/project.yaml`, and `experiments/E003-front-imx681-cphy/e003f-cphy-receiver-electrical/RESULT.md`.

## Exact machine state

SP11 Linux is back on byte-exact FullIO v19c Golden after the accepted E003f-R3 one-shot.

- kernel: `7.1.5-sp11-render-parity-v4+`
- marker: `sp11_entry=7.1.5-sp11-fullio-v19c`
- saved GRUB entry: `sp11-audio-fullio-v19c`
- `next_entry` empty
- Golden Image SHA-256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- Golden initrd SHA-256: `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`
- Golden DTB SHA-256: `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`
- Wi-Fi, MultiMedia1 playback, MultiMedia3 capture and Microsoft Surface G6 Touch healthy
- no serious kernel fault signature on return

Dynamic Wi-Fi and CCI identities remain boot-dependent; rediscover them every runtime.

## E003f-R3 accepted result

R2 had proved the CSIPHY2 aperture must be 8 KiB but direct local PHY power left 78 Windows non-zero values at zero. R3 added only the normal VFE0 host-power context around the receiver-only PHY sequence.

R3 exact identities:

- one-shot: `sp11-camera-e003f-r3-cphy-receiver`
- R3 initrd SHA-256: `082f9aebc0ba19ed2279856c6e7a55b8f9a29c6733586b7430a51c91578fa587`
- corrected DTB SHA-256: `e9fd13a29b6580955d2662c27377dbd1caba14f7f89613510b5e23bd6c266293`
- loaded patched CAMSS srcversion: `1D2912B8FF127D1F3D94704`
- verifier SHA-256: `20c60fa0d6fd5650a1cca51adb78b6697b8b0dbdb70edb692d7c1b2ba105a1f6`

Runtime:

- CSIPHY2 live mapping: `0x0ace8000-0x0ace9fff`;
- VFE0 host power-on passed;
- CSIPHY2 power-on passed with 400 MHz timer;
- Windows live comparison: **121 expected / 0 mismatches**;
- active common controls: CTRL5 `0x02`, CTRL6 `0x01`, CTRL7 `0x7a`;
- stream-off cleared CTRL5/6;
- VFE0 power_count returned to 0;
- verifier reported `E003F_RECEIVER_ONLY_PASS`;
- IMX681 remained suspended/usage 0, reset-low, MCLK4/front rails inactive;
- no IMX681/CCI/I2C/sensor kernel messages occurred in the R3 test window;
- rear OV13858 stayed bound/idle with its CSIPHY1 link; platform regressions passed.

This closes receiver electrical programming as the active unknown.

## Accepted front-camera milestones

- E003b: IMX681 same-machine electrical identity on CCI1/master1.
- E003c: native V4L2 bind with both platform and Sony IDs.
- E003d: immutable one-trio C-PHY IMX681 -> CSIPHY2 graph, streaming blocked.
- E003e: exact Windows 364-write init + 68-write 3840x2640@30 mode0 programmed in standby; MODE_SELECT stayed 0.
- E003f: receiver-only C-PHY electrical activation under correct host power, 121/121 Windows-live register parity.

Rear OV13858 production integration is already closed and is a regression check only.

## Exact next action: E003g static-only first

Do not immediately remove the IMX681 stream block or attempt a frame. Start with source/static derivation:

1. Re-open the accepted E003d/e/f source deltas and identify the exact front media path beyond CSIPHY2: CSID choice, VFE/RDI line and link state. Do not infer these from rear routing.
2. Trace the current CAMSS video-start order (`VFE`/`CSID`/`CSIPHY`/sensor) and teardown/error unwinds on this kernel source.
3. Trace the native IMX681 `s_stream(1/0)` implementation boundary. The accepted mode tables are already proven in standby; isolate the minimal change that permits streaming and verify MODE_SELECT ordering explicitly.
4. Compare that lifecycle with the same-machine Windows sensor/receiver oracle already archived in derived form. Use Windows/KD only if a remaining ordering or route fact cannot be mechanically resolved from current evidence.
5. Define E003g as one new unknown only, with a bounded timeout and fail-closed teardown. Preserve Golden and use a new one-shot.
6. Before any runtime, require reproducible kernel/module/initrd/DTB artifacts, ABI/CRC checks, source safety assertions, exact non-camera DT parity, and a preflight proving no automatic stream occurs at boot.

The first E003g runtime should be the smallest transport proof justified by the static audit; only then should a one-frame capture be attempted.

## Lab topology / quirks

- SP11 Linux: build/deploy/runtime target.
- SP11 Windows: same physical machine, Windows oracle/KD target.
- SP7 Windows: debugger/oracle companion and SSH fallback into SP11 Linux.
- SP11 Linux and Windows are mutually exclusive. PiMaster loss during reboot is not by itself a crash.
- SP7 project SSH key already exists; never expose/commit private key material.
- KDNET configuration already exists; never record its secret.
- Never hardcode SP11 IPv4/MAC or CCI adapter numbers.
- Never overwrite Golden or make an experimental camera entry the saved default.
- Never `git add .`; historical untracked artifacts are intentional.
