# E003i-AE — bounded live trigger → dynamic IQ producer

Status: **PASS offline; live one-shot is the next gate.**

AE connects the closed Linux statistics/trigger work to the existing template-free IQ transport without adding a kernel ABI. The producer consumes the paired generation-tagged TL_BG (`0x1241`) and 3A (`0x1242`) controls on the same front PIX fd, preserves W's `request = source_generation + 3` law, and generates only the dynamic LSC/GIC payloads for R5<-G2 and R6<-G3.

## Hot path

For each generation the producer performs:

`AEC_BE -> native measured-luma/Lux -> AWB_BG -> native AGW/CCT -> startup AWB temporal state -> front LSC trigger selection -> clean calibration/native resample -> TL_BG parse -> native sequential Tintless -> Titan680 LSC/GIC wire -> template-free capsule`.

G1 is processed only to establish the live Tintless/AWB temporal state. R4 is a template-free bootstrap submitted before STREAMON. G2 produces R5; G3 produces R6.

The bounded Linux stream does not issue per-frame IMX681 exposure/gain controls. Algorithm001 therefore uses the authoritative W request4 Lux `0x43b302c7` as a fixed history-baseline seed for this one-shot proof. This is not a complete continuous-AEC claim.

The retained Linux G1/G2/G3 triggers fall in the front AEC interpolation gap `390..490`; their temporally published CCT stays in the direct `5000..10000` lower-CCT band. The producer therefore interpolates the validated lower front leaf `0x4bf` with upper front leaf `0x4c3`, calibrates with the physical front OTP/golden mesh, and runs the stateful Tintless chain.

## Offline acceptance

`prove-offline-producer.py` runs 200 sequential G1->G3 passes against the retained Z paired snapshots. R5/R6 are stable at:

- R5 SHA256 `350fed1aaa4c6c3e9fbed8d3e63f14fcaf7a6cf80be9e8f800536a0ddfa14795`
- R6 SHA256 `e85dbe7b8b46837e09207586b56e4e648d674ea4663d18ea6b46d1b1f885dd8c`

Against the template-free compatibility capsules, every changed byte belongs to steady DMI payloads LSC0, LSC1 or GIC0. No full 41,088-byte captured capsule is an input.

Accepted p95 on Golden SP11 is about 7.63 ms for each G2->R5/G3->R6 hot path, comfortably below 33.333 ms.

## Live architecture

`e003i-ae-six-frame-live-iq.c` forks `live-iq-producer.py` on the same inherited video fd and waits for a READY byte **before STREAMON**. The child then polls the read-only latest-generation controls, requires exact TL_BG/3A `(generation, source_seq, slot)` identity, processes G1/G2/G3, and submits the generated R5/R6 capsules through the existing `0x1240` V4L2 control. The parent independently DQBUFs/saves all six frames and stats for audit.

Any missed generation, unsupported bounded trigger branch, producer error or provider failure is fail-closed. Runtime packaging preserves the historical no-same-boot-retry / mandatory-Golden-return discipline.

## Reproduce offline

```sh
./prove-offline-producer.py --snapshot-dir /tmp/e003i-live3a-bench --iterations 200
```

`RESULT.json` is offline evidence only; it does not claim the live run has happened yet.
