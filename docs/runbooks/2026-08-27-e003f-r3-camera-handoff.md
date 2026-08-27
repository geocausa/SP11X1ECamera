# SP11 camera handoff — E003f-R3 host-powered C-PHY receiver gate — 2026-08-27

This is the durable successor-chat handoff. Read it together with `CONTINUE.md`, `AGENTS.md`, `PROJECT_STATE.md`, `state/project.yaml`, and the E003f experiment directory.

## Exact stop boundary

SP11 Linux was mechanically verified on FullIO v19c Golden before this handoff update:

- kernel release: `7.1.5-sp11-render-parity-v4+`
- boot marker: `sp11_entry=7.1.5-sp11-fullio-v19c`
- saved GRUB default: `sp11-audio-fullio-v19c`
- `next_entry` empty
- Golden Image SHA-256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- Golden initrd SHA-256: `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`
- Golden DTB SHA-256: `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`

Git branch is `experiment/e003-front-imx681-cphy`. The mechanically proven R3 preparation parent commit is `5f2b727` (`E003f: add host-power receiver retry`), and it was already present on both local HEAD and `origin/experiment/e003-front-imx681-cphy` before this handoff update.

No E003f-R3 one-shot is armed. The R3 receiver electrical harness has **not** been run.

## Machine/tool topology

- **SP11 Linux**: primary build/deploy/runtime endpoint through PiMaster.
- **SP11 Windows**: the same physical SP11 booted into Windows; use as same-machine hardware oracle and KD target.
- **SP7 Windows**: companion/control/debug host. It can run KD against SP11 Windows and can SSH to SP11 Linux.
- Other PiMaster endpoints (geoserver/MacBooks/etc.) may be used as helpers, but SP11/SP7 are the authoritative hardware pair for this gate.

### SP7 -> SP11 Linux SSH

A dedicated project key already exists on SP7:

`%USERPROFILE%\.ssh\sp11_project_ed25519`

The corresponding public key is installed in SP11 Linux `~/.ssh/authorized_keys`. Do not commit or expose private-key material.

### KD

Use the installed Windows debugger on SP7 when Windows-oracle work is required. KDNET has already been configured for this lab; reuse the existing configured key rather than recording credentials in Git. Interactive KD needs a true PTY/Ctrl+C-capable session.

## Important access/runtime quirks

1. **SP11 Linux and SP11 Windows are mutually exclusive** because they are the same physical machine. PiMaster disappearance during reboot or while Windows/KD owns the target is normal.
2. **Do not hardcode SP11 IPv4 or Wi-Fi MAC.** Wi-Fi privacy/randomization changes MAC and DHCP address between boots. Rediscover through PiMaster, mDNS, ARP/IPv6 or SP7.
3. **Do not hardcode IMX681 as `3-0010`.** CCI adapter numbering has changed across boots (`3-0010`, `4-0010`, `5-0010` have all occurred). Discover the bound `sony,imx681` device dynamically.
4. Initrd-only `/usr/lib/modules/.../extra/...` files may not remain visible after switch-root. For a manual post-boot test module, mechanically hash-check and use the repo/build copy if the initrd copy is absent.
5. The canonical production-ish camera source is `/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src`. The true Golden source is `/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-repro/src`. Do **not** treat `.golden-v33-delta-replay/src` as the production source; it contains unrelated post-Golden audio drift.
6. The shared output build tree can have timestamp/dependency oddities. When a CAMSS source edit appears not to change the output-tree `.ko`, verify where Kbuild actually emitted the module and mechanically compare SHA/srcversion before packaging.
7. Never `git add .` in this repo. Historical build/runtime artifacts remain untracked intentionally. Stage exact files only.
8. Every risky boot must remain a separate GRUB one-shot. Never change the saved Golden default.

## Accepted front-camera milestones

- **E003b**: electrical identity accepted on CCI1/master1, Linux address `0x10`.
- **E003c**: native `sony,imx681` V4L2 bind accepted; Windows ID `0x0aff` and Sony ID `0x0681`; stream enable remains hard-blocked.
- **E003d**: one-trio zero-based C-PHY graph accepted, immutable IMX681 -> `msm_csiphy2`; receiver remained electrically idle.
- **E003e**: exact same-machine Windows mode0 programming accepted in standby: 364 init + 68 mode0 = 432 ordered sensor writes, `MODE_SELECT(0x0100)=0` throughout; C-PHY symbol rate 2.4 GHz, V4L2 link frequency 1.2 GHz; direct `s_stream(1)` still returns `-EOPNOTSUPP`.

Rear OV13858 is already accepted/closed and must remain a regression check only.

## E003f Windows C-PHY oracle

The exact installed Windows QTI MIPI-CSI driver yielded a 121-record ordered X1E C-PHY program. The final live receiver oracle used by the harness contains **121 distinct final offsets**: 118 unique table offsets plus common controls `0x1014`, `0x1018`, `0x101c`.

Key common values:

- `0x1014 = 0x02`
- `0x1018 = 0x01`
- `0x101c = 0x7a`

A static E003f simulation first caught generic CAMSS clobbering eleven Windows final values at `0x102c..0x1054`. The X1E+C-PHY-specific preservation fix reduces the modeled final-state mismatch count to zero without changing D-PHY behavior.

Patched CAMSS:

- SHA-256 `e1c8dcb099ee872ffd8bac263576b8f2db85cef104077df80d29a2916f47f308`
- srcversion `1D2912B8FF127D1F3D94704`
- 140/140 Golden imported-symbol CRCs

## E003f first runtime fault and 8 KiB MMIO fix

The first receiver-power harness attempt faulted inside `csiphy_reset()` on the first write at CSIPHY2 `+0x1000`. The Windows C-PHY lane table had **not** executed yet.

Root cause was mechanically proven: the parent X1E CAMSS resource mapped `csiphy2` as only `0x1000` bytes while the existing child PHY node and Windows both expose/use `0x2000` bytes.

One-cell DT correction:

`csiphy2 @ 0x0ace8000: size 0x1000 -> 0x2000`

Corrected DTB SHA-256:

`e9fd13a29b6580955d2662c27377dbd1caba14f7f89613510b5e23bd6c266293`

A DT-only smoke boot proved live Linux now maps:

`0ace8000-0ace9fff : acb7000.isp csiphy2`

with CSIPHY2 still idle and no faults. An independent R2-initrd-only smoke also booted cleanly and proved the harness does not auto-run.

## E003f-R2 full receiver result

The corrected R2 full candidate did run. Evidence is in `RUNTIME-R2-FULL-ATTEMPT.txt`.

It passed:

- 8 KiB MMIO resource preflight;
- C-PHY one-trio config preflight;
- CSIPHY2 local power-on (`timer_clk_rate=400000000`).

But after `CSIPHY2 .s_stream(1)` the Windows live comparison found **78 mismatches**. Expected non-zero lane/common values read back as zero, including CTRL5/6/7 all zero. This means the local CSIPHY power path alone did not establish sufficient host-side IFE/CAMNOC/CPAS context for receiver programming to take effect.

R2 unwind was clean: CSIPHY2/timer clocks returned to zero and the IMX681 remained non-streaming/reset/off.

## E003f-R3 prepared retry

R3 adds only the normal CAMSS **host power context** around the same receiver-only electrical test:

1. validate CSIPHY2 MMIO >= `0x2000` and C-PHY one-trio config;
2. `VFE0 .s_power(1)` to establish host IFE/CAMNOC/CPAS context;
3. `CSIPHY2 .s_power(1)`;
4. `CSIPHY2 .s_stream(1)`;
5. compare the 121 distinct final Windows-live offsets;
6. `CSIPHY2 .s_stream(0)` and require CTRL5/6 zero;
7. `CSIPHY2 .s_power(0)`;
8. `VFE0 .s_power(0)` last.

There is **no CSID stream call** and **no sensor callback/I2C/CCI/MODE_SELECT operation** in the harness. IMX681 must remain non-streaming.

R3 artifacts:

- harness SHA-256: `20c60fa0d6fd5650a1cca51adb78b6697b8b0dbdb70edb692d7c1b2ba105a1f6`
- harness srcversion: `ADBC641834EB18909E697EA`
- harness ABI: 13 imports / 0 Golden CRC mismatches
- reproducible R3 initrd SHA-256: `082f9aebc0ba19ed2279856c6e7a55b8f9a29c6733586b7430a51c91578fa587`
- corrected R2/R3 DTB SHA-256: `e9fd13a29b6580955d2662c27377dbd1caba14f7f89613510b5e23bd6c266293`
- patched CAMSS SHA-256: `e1c8dcb099ee872ffd8bac263576b8f2db85cef104077df80d29a2916f47f308`
- Golden Image SHA-256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`

Installed R3 boot directory:

`/boot/sp11-7.1.5-camera-e003f-r3-cphy-receiver`

GRUB entry ID:

`sp11-camera-e003f-r3-cphy-receiver`

During the handoff audit the R3 GRUB script was found to still contain R2 paths. It was corrected on 2026-08-27 and `update-grub` was regenerated. The corrected script is archived in this experiment directory as `99j_sp11_camera_e003f_r3_cphy_receiver`. All generated R3 paths now point to the R3 boot directory. **The entry is not armed.**

## Exact next action

1. Read this handoff plus the canonical state files.
2. Mechanically verify SP11 is still Golden, Golden hashes exact, saved default `sp11-audio-fullio-v19c`, and `next_entry` empty.
3. Verify R3 boot-directory hashes and the generated GRUB stanza again. Do not assume an old IP/CCI number.
4. Arm `sp11-camera-e003f-r3-cphy-receiver` as a one-shot only.
5. Allow ample reconnect time; Wi-Fi startup can be slow and its identity changes.
6. Verify the R3 marker, consumed `next_entry`, 8 KiB CSIPHY2 mapping, sensor suspended/reset/off and receiver clocks idle **before** loading the harness.
7. Hash-check the R3 harness against `20c60fa0...` and load it exactly once.
8. Required success: host/VFE power-on succeeds, CSIPHY2 power/stream-on succeeds, **121/121 final Windows-live receiver registers match**, stream-off clears CTRL5/6, CSIPHY2 and VFE power off cleanly, and IMX681 never transmits.
9. Verify all receiver/front clocks and rails return to zero; check rear/audio/Wi-Fi/G6 touch and serious kernel faults.
10. Return normally to Golden and re-verify the three canonical Golden hashes before accepting/pushing E003f.

Do not attempt a frame or remove the IMX681 stream block until E003f is accepted.
