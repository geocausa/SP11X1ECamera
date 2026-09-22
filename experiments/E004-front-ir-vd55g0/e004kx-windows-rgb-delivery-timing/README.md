# E004kx Windows RGB delivery timing
Hypothesis: Windows ordinary RGB VideoRecord modes advertise30fps and actual distinct-frame delivery approaches that cadence. Compare front1920x1080 and rear3840x2160 default NV12 against existing E004kr/E004kp Linux proofs.

Single consumed attempt, exact SP11 Windows host, signed-in camera session; exclusive marker before camera;240-second reboot watchdog to unchanged Golden default. Two30-second observations after2-second warmup, bounded WinRT waits. Enumerate supported modes and selected format; full NV12 SHA256 dedup in RAM, no pixels or hashes exported. Record monotonic unique arrivals, gaps, nullable timestamps and observer copy/hash/CPU overhead. No sensor control writes, no IR. Polling can miss frames, image processing can repeat content; this is observed distinct app delivery, not physical sensor maximum or driver CPU. No image-quality parity claim.

SP7 PowerShell parse and synthetic SoftwareBitmap fingerprint regression passed without camera access. Golden guard/source commit precede one-shot Windows boot. Return to Golden after collecting redacted numeric evidence; never rerun consumed identity.
