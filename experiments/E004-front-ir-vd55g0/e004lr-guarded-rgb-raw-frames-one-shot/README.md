# E004lr — bounded native libcamera RAW frame sessions, front and rear

Fresh, unique one-shot identity prepared 2026-09-22 after consumed E004lp/E004lq. Parent SP11 camera repo commit dd42fcdbfc05cb44d40deca2f9242098788c355d. Protected Golden v19c remains the saved GRUB default. E004lr is a new physical experiment, not a replay of any consumed identity.

Goal: have two independent libcamera `cam` processes capture exactly six **metadata-confirmed** RAW video frames each, rear first then front, and prove the complete kernel Media Controller v2 graph is neutral before, between and after sessions. No frame payloads, images or screenshots are saved: `cam` runs with `--stream=role=raw --capture=6` and without `--file`. E004lr accepts six strictly increasing distinct source frame sequences/timestamps and positive buffer bytesused per camera; the brief 6-frame span is NOT a long-run FPS guarantee or quality verdict. Nighttime darkness is an expected scene condition, not a camera defect. The IR emitter remains disabled.

Hardware: exact E004le physically accepted CAMSS+IMX681 front timing pair reproduced byte-for-byte at the original Kbuild path: qcom-camss.ko SHA-256 8aa3e7cb3ce790a0b37b6494f540e4075d78f8b3fed69ed415e81f4da5cfb75d; imx681.ko 448bd926193c003cdf3c1407382c3de0af7ba0ebfdca7cb36d8c797797c0bc6c. Canonical independently accepted four-module package manifest SHA-256 ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c; two exact timing modules are staged separately and never replace production authority. The unchanged Golden kernel/initrd are COPIED to a new private, nondefault one-shot GRUB entry alongside the accepted unified RGB/standby IR DTB.

Source: pinned clean libcamera v0.7.0 b7854fd07d42168f099b5ce30d1702e0e0875bf5 with E004lh RGB path filter, E004lm native fresh-kernel-graph transaction/lifecycle, E004lo failed STREAMOFF fail-closed patch, and independently verified IMX681 analogue-gain helper. The E004lr lease has its own exact root-only boot token and repeatedly checks sealed root:root 0600 ownership of all 1 media / 16 video / 28 subdevice camera nodes and sensor quiescence before route mutations. Every libcamera library, worker, IPA config and source directory is rooted under a dedicated /var/lib/sp11-e004lr-build owned root:root 0700 after the offline build and tests; the candidate bundle is separately SHA-pinned and root-private. No unguarded root access is granted to ordinary desktop apps on Golden.

Runner: writes an irreversible consumed marker before any sensor bind, verifies Golden and stage checksums, locks all nodes to root:root 0600 and refuses existing open FDs. Calls `cam --list` and matches exact real rear and front device-tree identities (virtual cameras are not success; no IR camera may register); checks full fresh media graph neutral. It runs a separate `cam` process bounded to 25s for each selected real camera. After each process exits, an exact SHA-pinned metadata validator confirms six distinct nonzero frames, rejects libcamera start/stop errors, a separate read-only native full-graph checker requires neutral and fuser rejects leaked camera-device FDs. Any unexpected state is a permanent fail-closed candidate failure; the one-shot systemd service requests automatic reboot to saved Golden even when it fails. Do not rerun E004lr under the same identity if it arms or fails.

E004lp already physically proved both real sensors register; E004lq physically proved rear RAW 4076x2806 SGRBG10_CSI2P and front RAW 3840x2160 SRGGB10_CSI2P configuration and neutral release. E004lr is the FIRST guarded native libcamera streaming test. The separate prior V4L2 software-publisher path demonstrated 30 FPS front 1080p/rear 4K, but no such FPS, Bayer-to-RGB ISP quality or production libcamera capture claim carries over automatically.

Safety limit: DAC and cooperative media FD lock exclude ordinary unprivileged competing clients in a controlled root-only one-shot, not arbitrary root-equivalent processes or production multi-client exclusivity. No general libcamera installation, IR illumination, PAM/login setup, quality-parity score, or change to protected Golden is authorized. The candidate is bounded and must return to Golden before archived numeric evidence is committed, and its private boot/service/bundle/compiled source are retired only after independent Golden verification.

Status at preparation: SOURCE AND GUARDED TEST ONLY, no E004lr physical attempt until explicit consumed/boot evidence. A later RESULT.json and CONSUMED.json override this preparation status.

## Final physical result — PASS, consumed, retired

One unique root-sealed camera-capable boot e6164854-1633-438e-87a2-93d8fe135a40
ran the pinned libcamera v0.7.0 cam client in two completely independent
sequential RAW streaming processes with --capture=6, no --file payload sink.
OV13858 rear RAW 4076x2806 SGRBG10_CSI2P delivered 6 strictly increasing
0..5 request frame sequences, positive 14,321,824 bytesused each, with
165,862 us between first and last kernel timestamps. IMX681 front RAW
3840x2160 SRGGB10_CSI2P delivered 6 strictly increasing 0..5 frame
sequences, positive 10,368,000 bytesused each, spanning 166,416 us.
Each source timestamp span is compatible with about 30 fps during the
brief six-frame sample, not a sustained-rate benchmark or distinct-pixel
hash proof. An independent native full-graph Media Controller v2 read
confirmed neutral before the first capture, after rear stream shutdown,
and after front stream shutdown; the runner denied existing/leaked
video/subdev/media FDs and any libcamera failed STREAMOFF/route-shutdown
diagnostic. IR kernel readback remained stream=0 illumination=0, and no
IR camera or emitter was activated. The dedicated systemd oneshot passed
and automatically returned to protected Golden boot
117c3de9-efdb-4cab-9add-1a56339e8acd, with saved_entry v19c, empty
next_entry and absent camera nodes/modules. Exact staged binaries were
SHA-verified and root-owned. Separate boot entry/service/private candidate
and private IPA-source build were retired after independently confirming
Golden. E004lr CONSUMED, NEVER rearm. Numeric/non-image request metadata
and kernel standby evidence are archived in RESULT/CONSUMED/evidence/.
Ordinary desktop processed RGB (as opposed to RAW), sustained FPS,
multi-client service lifecycle, ISP calibration and Windows quality parity
are STILL OPEN. The scene was dark at night, not a quality assessment.
