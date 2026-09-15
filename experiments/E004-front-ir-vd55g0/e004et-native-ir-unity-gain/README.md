# E004et: native IR unity digital gain

Hypothesis: E004es black-level-only frames result from the preserved Windows initial
manual digital gain of zero. ST source defines V4L2 digital gain as 256–2048 with
unity at 256. The later Windows per-frame control path was not replayed by E004es.
This is a hypothesis until measured on this sensor cut and firmware.

Change: standard V4L2_CID_DIGITAL_GAIN, cached while idle, applied with a two-byte
little-endian register write and readback. Replay cached controls after runtime
resume and before stream start. Initial firmware/table verification is unchanged.
Exposure remains 100, analogue gain zero, GPIO outputs disabled, corrected E004v
DT and ordinary CSID0/VFE0 RDI0 route unchanged. Four frames, one stream attempt.

Acceptance: digital-gain readback 256, four full Y10P frames, clean start/stop,
autosuspend, Golden return and retirement. Offline pixel metrics determine whether
scene signal appears. No protected runtime or illumination is activated.

ST reference: src/front-ir-vd55g0/st-vd55g0/vd55g0.c, manual digital gain register
0x0450, vd55g0_init_controls(), gain bounds 256–2048. Frozen reference commit is
recorded in the existing ST provenance. This candidate is not libcamera complete.

Result: PASS for gain register readback, four buffers, sequences 0–3, start/stop, autosuspend and clean kernel. Golden restored and candidate retired. Pixels remain in 59–69, with means 63.70–64.39. Unity gain alone did not recover scene signal, so zero gain is not established as the sole cause. Next: a sensor-generated pattern to check payload correctness independently of scene illumination.
