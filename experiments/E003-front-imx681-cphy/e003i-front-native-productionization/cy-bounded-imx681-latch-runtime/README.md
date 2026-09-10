# E003i CY — bounded IMX681 group-hold optical-latch runtime

Status: **PASS LIVE LATCH BOUNDARY — one-shot executed once; mandatory Golden return PASS.**

CY is the first runtime after CX/CW and is deliberately narrower than continuous AEC. AP already proved the AM group-held transport live. CW then made the four request controls atomic without the old VBLANK/exposure cache bug. CX closes the Windows software side through `packet F` selection at `SOF F-1` and synchronous KMD I²C apply.

CY asks only the remaining hardware question: after a completed Linux frame, when does one released IMX681 group-held exposure step first appear in generation-tagged 3A/BHist?

The run starts from AP's proven baseline `FLL=3554, exposure=3500, analogue=64, digital=272`. Immediately after `DQBUF sequence 0`, the helper issues exactly one `VIDIOC_S_EXT_CTRLS` containing all four CW cluster members, preserving FLL/gains and changing exposure to `1000`. The helper then completes the unchanged six-frame/AO paired-stat path. No second exposure step is permitted.

Evidence retained for generations 1..6: QC10C frames, TL_BG, full STATS3A including raw BHist, the monotonic control-ioctl interval, dynamic-driver transaction lines, and cached controls after STREAMOFF. `verify-live.py` uses the exact CT BHist value-axis generator and requires a strong exposure-dependent BHist drop no later than generation 3; it reports the first affected generation rather than assuming it.

The candidate keeps AP's one-shot discipline: unique GRUB entry, camera modules blacklisted at boot, explicit load/prepare/invoke phases, no same-boot retry, and mandatory return to the saved Golden entry. A capture does not authorize continuous AEC by itself.


## Final one-shot result

The candidate was armed once, executed once, STREAMOFF completed, and the machine returned to saved Golden with camera modules absent. The exposure step completed in 1,802,121 ns and emitted exactly one CW hardware control transaction.

BHist weighted means by paired stats generation were `G1=1.319915499`, `G2=1.314026080`, `G3=0.818911603`, `G4=0.821169546`, `G5=0.519662546`, `G6=0.520933791`. G2 remained baseline-like; G3 is the first strong exposure-dependent drop. This closes the Linux sensor-side visibility boundary but does not by itself assign a Windows optical request/frame label. Raw QC10C/TLBG/STATS3A captures remain local under ignored `runtime-output/`; their SHA-256 values are pinned in `RESULT.json`.
