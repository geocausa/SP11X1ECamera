# E003i-EB — Windows R4..R12 GTM/TMC state oracle

Status: **PASS_WINDOWS_ORACLE / 9 OF 9 CLEAN-ROOM GTM REPLAY / GOLDEN RETURN PASS.**

EA proved the bounded Linux sensor + residual-ISP Demux loop through request6. Continuous extension is blocked by the remaining request7+ IQ state: the current Linux producer has exact raw base states only for R5/R6, while GTM is request-stateful through TMC/ADRC.

EB is one read-only same-machine Windows front-camera oracle stream. It uses the same gated holder pattern as DO/DM: initialize `Surface Camera Front`, stop before `MediaFrameReader.StartAsync`, attach CDB to the live FrameServer, arm the exact DeviceMFT breakpoints, then create the START.GO file. No exposure/IQ values are injected and no process memory is modified.

At `GTM131Setting::CalculateHWSetting` RVA `0x9aa6e0`, accepted only when LR is the proven IFE caller return `0x180a28f2c`, EB uses `qwo(x19+0x1ff8)` as the request frame and captures requests 4..12. It fails closed unless `poi(x0+0x50)` is non-null, internal TMC generation at +0x08 is 5 and valid at +0x10 is nonzero.

Per request it captures only the proven bounded inputs:

- GTM common input: 0x7c bytes;
- interpolated GTM region: 0x404 bytes;
- flags: 4 bytes;
- auxiliary halfword: 2 bytes;
- internal TMC ranges +0x0008/0x0c, +0x0074/0x04, +0x109c/0x08, +0x5104/0x1c, +0x5120/0x1c, +0x51b0/0x3c and +0x6228/0x1000.

At the proven post-final-staging-copy RVA `0xa290a8`, it captures the 0x800-byte cached GTM output at `x20+0x138`. It auto-clears breakpoints/detaches after request12 output.

Raw pointer-bearing files stay local/untracked. `analyze-eb.py` reconstructs the sparse TMC input, runs the existing clean-room GTM transform and requires byte-exact equality with every captured R4..R12 GTM output. It then classifies R6..R12 as stable, two-cycle, or evolving from the dynamic TMC/output hashes.

Safety: direct-Windows BootNext only, persistent Golden GRUB unchanged, one Windows stream, normal holder stop, then reboot to Golden Linux. No Linux camera candidate is armed by EB.

## Windows oracle result — 2026-09-11

One direct-Windows front stream was captured with the camera gated until both CDB breakpoints were armed. The first two debugger-script attempts failed closed before `START.GO` (oversized action string, then escaped-path validation); neither streamed camera frames. The final short-script form armed both breakpoints, started once, stopped normally after five seconds and auto-detached.

Requests R4..R12 all produced the complete bounded GTM/TMC input set and exact 0x800-byte post-calculation GTM output. The Linux clean-room generator reproduces **all 9/9 outputs byte-for-byte**.

For R6..R12:

- bounded dynamic TMC state has exactly one SHA-256: `e47edb77e0e072dc11003b6f47d2d4d06d14efe98d989641764f33111067c6bd`;
- GTM output has exactly one SHA-256: `074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa`;
- interpolated GTM region, flags and aux inputs are stable;
- the 0x7c common block differs in exactly one byte, `+0x14`, already statically identified as the bank/LUT selector; its R6..R12 values are `0,1,0,1,0,1,0`.

Therefore GTM/TMC is no longer a post-R6 adaptive-state blocker for this steady preview regime: carry forward the proven GTM content while advancing deterministic bank parity. This does **not** prove unrestricted continuous AEC, because request7+ LSC/Tintless and remaining scalar/AWB producer state are still to be closed.

Raw pointer-bearing evidence remains outside Git at:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-eb/windows-r4-r12-20260911`

Windows evidence zip SHA-256: `8aa7203d4d3789f687a2aaae89cc08f812f9421e99d673dedae5df4a754b69f1`. SP11 returned to protected Golden Linux with `saved_entry=sp11-audio-fullio-v19c`, empty `next_entry`, and no camera modules or video/media nodes.
