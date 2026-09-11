# E003i-EB — Windows R4..R12 GTM/TMC state oracle

Status: **STAGED / WINDOWS ORACLE NOT YET EXECUTED.**

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
