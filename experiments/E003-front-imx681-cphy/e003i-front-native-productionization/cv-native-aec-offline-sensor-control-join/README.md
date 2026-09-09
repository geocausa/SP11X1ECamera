# E003i CV — offline raw AEC → IMX681 control join

Status: **PASS (full parent-backed static/offline + native differential).**

CV appends the already-accepted CQ sensor-control arithmetic to CU without opening a camera device or issuing any Linux control operation. The complete pure function is:

`generation-tagged STATS3A -> CU native AEC -> CP Short T681 -> CQ -> {FLL,VBLANK,exposure,analogue,digital,ISP gain}`.

## Identity and delay coordinates

Three identifiers are deliberately kept separate. CU's `frame_id` is its zero-based cold-sequence coordinate and requires `generation == source_seq == frame_id + 1`. W's same-process Windows oracle separately proved 104/104 selected statistics pointers obey `request_frame = source_generation + 3`: request4 selects G1, request5 G2, request6 G3. AP independently live-proved the G2->R5 and G3->R6 portion. Source generation therefore remains a source identity, not a request ID.

AV closes a different delay: exact IMX681 linecount, gain and FLL delays are all 2, equal to `maxPipeline=2`, with `frameSkip=0`. Windows therefore performs zero extra `HandleDelayInfo` request-history realignment. CV exports the two-frame sensor pipeline depth, but intentionally does **not** label `request+2` as an optical frame; AV left final group-hold/frame-boundary latch semantics open.

## Failure atomicity

CV runs CU on a copy of the recurrence state, runs CQ on the resulting Short T681 value, and writes the copied state back only after CQ succeeds. A malformed stats envelope therefore cannot advance AEC state, and a future CQ-domain failure would also leave the caller state unchanged.

## Offline differential

`verify-cv.py` builds the full native chain with strict FP options and drives the same four deterministic generated STATS3A frames used by CU. For each frame it compares the CV wrapper with independent calls to CU followed by CQ and requires byte-exact raw-request output, byte-exact CQ controls, and byte-exact final recurrence state.

The current deterministic outputs are preserved in `RESULT.json`; generated G1..G4 map to request ownership R4..R7. The fixture reaches CQ's expected maximum coarse integration region (`FLL=3562`, exposure lines `3554`) while exercising changing analogue/digital gain.

## Safety boundary

CV contains no `open`, `ioctl`, `VIDIOC`, CCI, I2C, STREAMON, module load, MMIO or sensor-write path. It is an arithmetic/request-association checkpoint only. A new live camera run remains unnecessary here.

The next checkpoint should join this tuple to the already-live-proven AM group-held Linux control transaction **offline first**, close request/frame-boundary ownership, and only then consider a bounded live run.
