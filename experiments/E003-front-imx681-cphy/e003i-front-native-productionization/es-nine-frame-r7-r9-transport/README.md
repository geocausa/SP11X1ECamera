# E003i-ES — nine-frame R7–R9 transport extension

Status: **PASS offline transport build/proof; no camera runtime.**

ER proved the corrected IQ path live through G6/R9 composition but exposed a pure transport ceiling: the production CAMSS runner stopped after frame 6 and consumed only R5/R6. R7/R8 were queued but never consumed, and R9 arrived after `live_active` was cleared.

ES extends only that bounded transport window. `make-nine-frame-camss.py` transforms the exact ER CAMSS source into a 9-frame runner. Frames 7–9 repeat the proven steady sequence: wait for the recycled V4L2 buffer, consume exactly request R7/R8/R9 from the monotonic provider, wait for the next Epoch0, rebind the alternating VFE slot, submit the 0x958 steady batch, retire video/all-done, publish TL_BG then 3A, retire aux, and complete the buffer. Immediately after successful R7/R8/R9 provider dequeue it emits a bounded `E003I_ES_IQ_CONSUMED R=<id> FRAME=<n> SLOT=<s>` diagnostic so live acceptance can prove each new request was consumed at the intended gate. The expected buffer cycle is `0,1,2,3,0,1,2,3,0`.

The companion helper transform extends the native parent to DQBUF/audit G1..G9 and recycle completed buffers after frames 1..5. It preserves all nine QC10C frames before reuse. The scheduler accepts G1..G9 but retains exactly three physical sensor writes: G1@G2, G2@G3, G3@G4 with effects G4/G5/G6. CQ residual-gain publication remains deliberately capped at G1..G6 because the EN IQ producer needs only those generations to compose R5..R9.

Offline acceptance requires: exact pinned base hashes, deterministic generated-source hashes, CAMSS `W=1` build with Golden vermagic, helper `-Werror` build, and a pure scheduler test proving nine accepted generations with exactly three releases. No camera module is loaded and no stream is run here.

A fresh live successor must use a new one-shot identity (ER is consumed), the ES CAMSS module and nine-frame helper, and the already-proven EN/EP producer. A live PASS must show R5..R9 consumed, nine video/TL_BG/3A generations complete, R9 applied before frame9 completion, exactly three sensor writes, clean STREAMOFF/health, and Golden return. This remains bounded integration, not unrestricted continuous AEC.
