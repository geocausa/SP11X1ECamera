# E003i DO — Windows internal-cap branch producer oracle

Status: **PASS_WINDOWS_BRANCH_ORACLE**.

Purpose: bind the two remaining ordinary-preview inputs used by the DN native internal exposure cap without guessing: the bank9:data10 lookup that produces the internal `w12` rescale-disable branch and the compact output field at `+0x98`.

The capture is evidence-only on normal SP11 Windows front preview. It records the same-call CapExposure entry and exit tuples, the lookup return/valid/value at RVA `0x3d35e4`, final `w12`, convergence config `+0x2c`, compact `+0x98`, and selected history1 Short if the conditional rescale path executes. The debugger auto-detaches after exactly decimal 18 completed cap calls. The holder starts/stops the camera normally. No exposure targets are injected.

Safety: one-shot direct Windows `BootNext=0006`; persistent GRUB Golden remains `sp11-audio-fullio-v19c`; no Linux camera module or candidate is armed. Raw debugger evidence stays outside Git. Return to Golden after capture.

## Result

The bounded normal-preview run completed 18 cap calls and detached automatically. The bank9:data10 lookup returned 0 on all 18 calls, so the Windows function set `w12=0` on every call without reading a bank value. `compact+0x98` was `0x00000000` and convergence `+0x2c` was `0x3f000000` (0.5f) on every call. The rescale branch was not entered during these 18 calls, so no runtime history-helper hit occurred.

Static code at the same pinned DLL shows `mov w1,#1` immediately before the history helper call at RVA `0x3d3638`; its returned record supplies Short from `+0x28`. This matches the already-native request-loop H1 selector and lets DN bind history without inventing delay or state.

The post-capture reboot returned through GRUB to Golden with camera modules and `/dev/video*`/`/dev/media*` absent. Raw Windows debugger material remains outside Git under the recorded Windows prefix and is SHA-pinned in `WINDOWS-EVIDENCE-HASHES.txt`.
