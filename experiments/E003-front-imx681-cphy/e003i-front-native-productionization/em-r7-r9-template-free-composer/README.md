# E003i-EM — request7–request9 template-free component composer

Status: **offline component composition; no new Linux camera runtime.**

EM extends the accepted template-free transport beyond R6 without opening or reading any R7/R8/R9 full Windows capsule or DMI slot. It composes R7–R9 from independently closed request-state components:

- **banks:** F request-parity backend;
- **Demux/BLS:** DV from EA's generation-tagged CQ residual ISP gain (`R7/R8/R9 = 0x3f801646`);
- **PDPC/WB:** EL's Linux-OTP-calibrated, stateful Windows GainAdj publication path;
- **LSC0/LSC1/LSC2/GIC:** DS clean sequential Tintless/LSC replay over exact EA G1..G6 TL_BG fixtures. State is advanced through G1..G3 before the first EM request so R7 really uses the G4 temporal state;
- **GTM0:** J clean GTM packer fed only the compact EB R6 TMC state. EB proves that TMC state and GTM output are byte-stable R6..R12; the generated wire is SHA256 `074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa`. Only the GTM bank bit alternates;
- **PDPC DMI / BPC-ABF / Gamma / DSX:** individual R4/R5/R6 payload regions proven invariant and reused from the existing E authority;
- **transport:** E's normalized 36-section, 41088-byte template-free capsule format.

The six EA TL_BG fixtures are preserved here because the original runtime-output copies are root-owned/untracked. Their SHA256 values are already present in the EA/EL evidence chain. Only the ~4.2 KiB TMC ranges actually consumed/proven by EB are retained for the stable GTM carry-forward.

EM deliberately does **not** claim whole-capsule byte identity against Windows R7–R9: no such full capsule is used as an oracle. Instead it requires every request-dependent component to have its own existing authority and records the resulting section/module/capsule hashes. This is the correct gate before wiring the composer into a fresh bounded Linux producer.

Next gate: integrate EM state construction into the live producer, benchmark G4–G6 deadline margin offline, and only then stage a fresh one-shot runtime candidate that submits R5–R9 without reusing any consumed DP/DT/EA boot identity.
