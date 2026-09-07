# E003i-AE — bounded live trigger → dynamic IQ producer

Status: **PASS offline, including the expanded two-dimensional LSC selector; AG reached live STREAMON but was consumed by the old narrow CCT guard before R5. A fresh corrected live one-shot is the next gate.**

AE connects the closed Linux statistics/trigger work to the existing template-free IQ transport without adding a kernel ABI. The producer consumes the paired generation-tagged TL_BG (`0x1241`) and 3A (`0x1242`) controls on the same front PIX fd, preserves W's `request = source_generation + 3` law, and generates only the dynamic LSC/GIC payloads for R5<-G2 and R6<-G3.

## Hot path

For each generation the producer performs:

`AEC_BE -> native measured-luma/Lux -> AWB_BG -> native AGW/CCT -> startup AWB temporal state -> front LSC trigger selection -> clean calibration/native resample -> TL_BG parse -> native sequential Tintless -> Titan680 LSC/GIC wire -> template-free capsule`.

G1 is processed only to establish the live Tintless/AWB temporal state. R4 is a template-free bootstrap submitted before STREAMON. G2 produces R5; G3 produces R6.

The bounded Linux stream does not issue per-frame IMX681 exposure/gain controls. Algorithm001 therefore uses the authoritative W request4 Lux `0x43b302c7` as a fixed history-baseline seed for this one-shot proof. This is not a complete continuous-AEC claim.

The LSC selector now follows the serialized two-dimensional tuning tree rather than assuming one lower-CCT leaf. The lower-AEC child selects/interpolates the CCT leaves `0x4b9`, `0x4bb`, `0x4bd`, `0x4bf` across the ranges/gaps `1..2500`, `2500..2700`, `2700..3200`, `3200..3400`, `3400..4500`, `4500..5000`, and `5000+`; that lower result is then selected/interpolated through the outer AEC tree, including the `390..490` gap toward upper leaf `0x4c3`. The selected mesh is calibrated with the physical front OTP/golden mesh and then enters the stateful Tintless chain.

## Offline acceptance

`prove-offline-producer.py` runs 200 sequential G1->G3 passes against the retained Z paired snapshots. R5/R6 are stable at:

- R5 SHA256 `350fed1aaa4c6c3e9fbed8d3e63f14fcaf7a6cf80be9e8f800536a0ddfa14795`
- R6 SHA256 `e85dbe7b8b46837e09207586b56e4e648d674ea4663d18ea6b46d1b1f885dd8c`

Against the template-free compatibility capsules, every changed byte belongs to steady DMI payloads LSC0, LSC1 or GIC0. No full 41,088-byte captured capsule is an input.

Accepted p95 on Golden SP11 is about 7.63 ms for each G2->R5/G3->R6 hot path, comfortably below 33.333 ms.

`prove-expanded-selector.py` adds the live-AG selector regression. It requires retained Z to keep the original R5/R6 identities and the actual AG G1-G3 captures to exercise `gap_4500_5000` inside the lower-AEC child followed by outer `gap_390_490`. `SELECTOR-EXPANSION.json` records the accepted actual-AG dynamic identities:

- R5 SHA256 `b05698889f607d5786a441a7c85ef07b6f61852d20a1894ff8f4919b07051d94`
- R6 SHA256 `f694734412fe7cf4669fd1bfadb0f7eecc4d8f4b34f94f60a4a9068537dc546e`

On the actual AG evidence the expanded selector remains comfortably inside budget at roughly 7.56/7.57 ms p95 for G2->R5/G3->R6. `RESULT.json` remains the retained-Z offline proof; `SELECTOR-EXPANSION.json` is the additional actual-live-trigger selector proof.

## Live deadline hardening

AH proved the expanded selector live but missed the deferred R5 Epoch0 handoff: the first two live generations took about 47.6 ms and 26.4 ms, so request5 reached the V4L2 IQ ingress only after the runner had already unwound. The producer now hardens only the live scheduling path: it pins itself to CPU11 at nice -20, performs a fixture-free synthetic LSC/Tintless/composer prewarm before signaling READY, resets all temporal/Tintless sequence state exactly, disables cyclic GC, and defers snapshot/capsule/manifest writes plus per-generation logging until both R5 and R6 submissions have completed. No RT scheduler policy is used.

`prove-live-deadline-hardening.py` exercises the expensive path without captured runtime fixtures and repeats it while all CPUs are under normal-priority synthetic load. The acceptance gate requires both G2->R5 and G3->R6 p95 and maximum latency to remain below one 30 fps frame (33.333 ms).

## Live architecture

`e003i-ae-six-frame-live-iq.c` forks `live-iq-producer.py` on the same inherited video fd and waits for a READY byte **before STREAMON**. The child then polls the read-only latest-generation controls, requires exact TL_BG/3A `(generation, source_seq, slot)` identity, processes G1/G2/G3, and submits the generated R5/R6 capsules through the existing `0x1240` V4L2 control. The parent independently DQBUFs/saves all six frames and stats for audit.

Any missed generation, unsupported bounded trigger branch, producer error or provider failure is fail-closed. Runtime packaging preserves the historical no-same-boot-retry / mandatory-Golden-return discipline.

## Reproduce offline

```sh
./prove-offline-producer.py --snapshot-dir /tmp/e003i-live3a-bench --iterations 200
```

`RESULT.json` is offline evidence only; it does not claim the live run has happened yet.
