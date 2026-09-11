# E003i-FA — Windows R12 AWB GainAdj same-request oracle

Status: **STAGED OFFLINE / NO FA WINDOWS STREAM YET.**

EZ proved bounded Linux integration through R11. EB already proves GTM/TMC through R12 and ED proves sequential Tintless/LSC staging through R12. The remaining R12 component seam is AWB GainAdj/publication: EG/EL have same-request Windows differential only through R11.

FA uses one gated, read-only Windows front-camera stream. The holder initializes Surface Camera Front and stops before MediaFrameReader.StartAsync; CDB attaches to the live FrameServer and arms two SHA-pinned DeviceMFT hooks before START.GO is created.

Static hook authority comes from the pinned same-machine QcDeviceMFT8380.dll SHA c241b7... and the preserved Ghidra analysis. CTrigleAdjV1::Run is RVA 0x6bf1a0; at RVA 0x6bfa68, x19 still owns the completed GA object. CAWBMain::PopulateOutput publishes at RVA 0x68fa00; x23+0x128 is the request/frame label and x13+8..+0x14 contains published RGB/CCT.

The GA breakpoint only caches state. The publication breakpoint binds that latest state to the actual request label and emits paired R4..R12 records. R12 self-detaches CDB. Acceptance is same-run, not scene-equality to the historical EG capture. verify-fa.py advances EL's stateful calibrated selector over the new R4..R12 sequence and requires triangle, vertices, barycentric weights, nested CCT multiplier, final GA RGB, published RGB and integer CCT to be bit-exact for all nine requests. Only R12 is new authority.

Safety: direct Windows EFI BootNext=0006 once, persistent GRUB Golden unchanged, one holder stream, no camera register/IQ injection, normal holder stop, then reboot to Golden Linux. Raw debugger evidence stays outside Git.
