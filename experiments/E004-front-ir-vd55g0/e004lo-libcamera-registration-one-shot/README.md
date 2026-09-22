# E004lo — first guarded SP11 native libcamera camera registration (one shot)

Date 2026-09-22. Fresh E004lo identity, not previously used E004lk/E004ll/E004ln; no physical E004lm run ever occurred. Parent state after E004ln: pinned 28/28 live subdevice CAP_STREAMS=0, E004ll real native neutral/front/neutral/rear/neutral route PASS, E004lm libcamera Simple offline build/test PASS. Experiment stops at CameraManager enumeration/camera listing and never executes capture, STREAMON or light/IR commands. Nighttime scene darkness is irrelevant.

The actual binary is built in a clean, separate pinned libcamera v0.7.0 b7854fd source tree with E004lh exact RGB BFS/path patch, E004lm native link/neutral lifecycle patch and the independently verified IMX681 gain-helper patch. This unique e004lo 0003 patch explicitly denies libcamera Simple's unguarded active subdevice-routing reset, selects an exact new one-shot boot token and fails closed on a failed streamOff. The experimental lease header is root-only, requires the exact E004lo boot token, independently suspends all three sensors before admission, retains a cooperative media-fd lock, and rechecks root:root 0600 ownership on the *exact* 1 media + 16 video + 28 subdevice node set for each graph transaction. The candidate runner checks no previously open camera FDs, seals the nodes AFTER the accepted modules bind, verifies its SHA-pinned root-private libcamera bundle and runs only cam --list under a 30s hard bound. The resulting stdout must contain one real IMX681 and one real OV13858 camera ID, not only virtual cameras; IR sensor must not be registered. It rejects any libcamera errors or leaked camera descriptors. Automatic one-shot service reboot returns to protected Golden regardless of pass/fail.

Limits: root:root 0600 is kernel-enforced exclusion of *ordinary non-root clients during this disposable candidate boot*, NOT enforced exclusion of root-equivalent, malicious, or race-winning external clients. The cooperative lock does not provide a kernel V4L2 exclusive ownership API. This experiment is not a production service, persistent app integration, or acceptance of full upstream parity. It does not prove front/rear libcamera image formats, real camera manager registration until its physical result is recorded, simultaneous operation, FPS, dark-scene quality, front Qualcomm QC10C Windows ISP parity or safe native IR. On any partial route/link failure no unsafe rollback is attempted: abort and return to Golden. Never reuse E004lo after it has been armed even if the result is inconclusive. No Golden kernel/initrd/default or /lib/modules files are modified.

Procedure: commit and push the exact new source/scripts, verify clean Golden overlap guard and saved_entry=sp11-audio-fullio-v19c with empty next_entry, then install-unarmed.sh (isolated source/binaries/entry/service), separately verify root-private hash manifest and conditioned service, run arm-once.sh once. Inspect actual candidate service result/boot ID/logs, next Golden boot, source and root-private marker before archiving numeric/string evidence and executing retire-after-golden.sh. Do not call the user-facing camera manager or install the library on Golden.

## Final physical result — FAIL front mandatory controls; rear registered; consumed

One-shot candidate boot 137fc04d-a632-4e3d-9b1c-199b69bcbcb2
successfully reached root-only camera-device seal, checked the staged
libcamera bundle and ran the pinned cam --list program. libcamera
registered the REAL OV13858 rear camera, while the REAL IMX681 front
failed CameraSensor construction: mandatory V4L2 HBLANK (0x009e0902)
and PIXEL_RATE (0x009f0902) are absent from the canonical accepted
production IMX681 driver. libcamera also emitted crop-selection ENOTTY
diagnostics for both sensors, which were NONFATAL for the rear
registration. The four Virtual cameras do not count as physical RGB.
The attempt correctly reported status FAIL rc=1 and automatically
rebooted to Golden boot 3925efc3-b544-4b75-92bb-abd156744c43,
saving v19c and no pending boot/camera modules/nodes. VD55G0 kernel
standby readback stream=0 illumination=0. No frames/STREAMON or IR
emitter were requested. Root-private candidate bundle, single-use
service and GRUB entry RETIRED. E004lo is CONSUMED and must NEVER be
rearmed; source and experiment are retained as evidence of the
specific driver metadata blocker.

Additional source-integrity finding: IPA config load logs resolved
an absolute scratch path under geoca-writable /home despite the
root-owned copied bundle. This one-shot was never production-approved
and had no protected camera frames. For any NEW candidate, build
directly under an eventually sealed root-owned persistent directory
so all compiled IPA/config paths are root-private before launch.
Do NOT label E004lo a dual-RGB libcamera PASS.

See RESULT.json, CONSUMED.json and evidence/. Next stage needs the
separately accepted E004ld/E004le fixed timing controls+CAMSS clock
module pair (not blind PIX clock override) in a NEW unique one-shot.
