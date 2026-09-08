# E003i CN — Windows cold-start history bootstrap

Status: **PASS (Windows static + read-only live oracle)**.

CN closes CM's remaining exposure-history warm-up ambiguity for ordinary SP11 front IMX681 preview.

Windows owns a distinct synthetic `0x1b0` start-history record. Two fresh read-only FrameServer probes independently observed the same start-record SHA-256 (`7d703a37...d2a1d5f`), while the ordinary real-frame list was separately populated and capped at ten entries. The synthetic record is frame 0, marker 1, and all seven retained exposure lanes are exactly **33,333,332**. Sampled real records are marker 0 and are not byte-equal to the synthetic record.

`CAECXHistory::GetInternalFrameHistory` uses the start record as the initial fallback. Once real history exists, it scans newest to oldest for a record satisfying `saved_frame + requested_offset <= current_frame`; if none is old enough yet, the last inspected (oldest available) real record remains selected. Thus F-1/F-2/F-3 naturally warm up without callers fabricating three history frames.

Convergence separately proves the true NULL-history fallback is `PredGain=1.0f`, `previous_delta=+0.0f`. With a returned history record it loads `+0x178/+0x17c`; the ordinary control carrier initializes the `+0x178` source to zero, and `+0x17c` is zero in the captured synthetic record. In the scoped convergence path, a history DRC gain affects Short only when it is greater than 1, so the startup zero state is the identity case.

CN does not modify Linux camera runtime. The Windows oracle used user-mode read-only FrameServer memory reads only; no process patching/suspension or camera-register writes were performed.
