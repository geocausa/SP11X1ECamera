# E004lv — fresh guarded IMX681 exposure-control hardware validation

Date: 2026-09-23 (Europe/London). This is a NEW single-use candidate separate from retired and consumed E004lt. Parent repository commit f5a77dfbb08c758f6b90b5869ee8355376fbd210. Golden v19c is the only saved boot default.

**Purpose:** Test the E004lu source-supported hypothesis for E004lt's six repeated IMX681 V4L2 control ERANGE errors. E004lt proved real front and rear processed 640x480 XRGB8888 frame delivery and independently neutral graph before, between, after, but failed six front sensor-control writes during six frames. E004lv uses accepted fixed IMX681 FLL3554, exposure cap3550 and two-line quantization in Soft IPA. It demands the exact front logged active AGC exposure range 4–3550 and ZERO failed V4L2 controls on both front and rear, not merely delivered frames.

**Bounded test:** A uniquely guarded root-only one-shot boots a separate exact E004le physically accepted camera-capable kernel/DTB and root-sealed pinned libcamera v0.7.0 bundle with E004lh RGB path filter, E004lm native route guard, E004lo failed-STREAMOFF guard, verified IMX681 gain helper, E004lu front fixed-frame Soft IPA patch, and this experiment's distinct boot-token lease header. All 45 camera nodes are root:root 0600 and the runner rejects active users; this excludes ordinary nonroot clients within the isolated experiment, but DOES NOT prove production exclusivity against root-equivalent/uncooperative clients.

A read-only full kernel Media Controller v2 probe requires neutral BEFORE, BETWEEN and AFTER separate 30-frame front-then-rear libcamera cam sessions. Exact 640x480-XRGB8888/sRGB, precisely 30 distinct sequence/timestamp metadata entries per camera and exactly 1228800 bytesused each are mandatory. No --file option, pixel payload, optical hashes, image-quality or sustained-performance claims. Reject any sensor-control ioctl failure, incorrect front active exposure range, camera start/stop errors, nonneutral graph, leaked FDs, IR registration or enabled illumination. The root-only service has a bounded timeout and requests automatic Golden return on completion or failure. Any attempt irreversibly consumes E004lv; no retry under this ID. Actual source, modules, IPA/binary hashes are checked at install and again on candidate boot. Golden kernel, initrd, default, /lib/modules and normal camera apps are untouched.

**Source prerequisites:** The exact accepted candidate CAMSS+IMX681 module pair from prior E004le physical test is rebuilt and matched byte-for-byte (qcom-camss 8aa3e7cb3ce790a0b37b6494f540e4075d78f8b3fed69ed415e81f4da5cfb75d, imx681 448bd926193c003cdf3c1407382c3de0af7ba0ebfdca7cb36d8c797797c0bc6c), alongside the canonical four-module package/DTB. Pinned libcamera is compiled from the outset under a separate /var/lib/sp11-e004lv-build root-private path to protect its baked IPA configuration location; it is sealed root:root mode0700 BEFORE candidate installation.

**Limitation:** Even a zero-error 30-frame run is only a short control-path test. The exact failed control from E004lt was not recorded; a fixed outcome supports but does not by itself isolate the root cause. Ordinary desktop service, multi-user ownership, repeated suspend/reopen, calibrated colour/Windows QC10C ISP parity and longer low-light testing remain open.

Preparation status: source and scripts only, not yet a physical attempt. Once attempted, RESULT.json/CONSUMED.json and numeric evidence supersede this status; NEVER rearm a consumed E004lv.

## Final physical result — PASS; consumed and retired

Unique guarded E004lv candidate boot c3662af2-cbd3-4240-b0d6-f52d65535d12
verified E004lu's bounded IMX681 fixed-mode software IPA: front IPA
logged active exposure range 4–3550 lines. Real front IMX681 then
rear OV13858 each produced THIRTY distinct-sequence 640x480-XRGB8888/sRGB
processed camera buffer records, exactly 1228800 bytes per frame,
first-to-last timestamp spans 967530us and 968393us (about 30fps across
29 short frame intervals), and ZERO V4L2 set-controls errors on BOTH
cameras. This is a 30-frame-per-camera short test, NOT a multi-minute
performance, image-content, low-light quality or Windows ISP parity test.
The previously observed six front ERANGE events did NOT recur in this
bounded test, though E004lt's exact failed V4L2 control ID was never
independently captured, so this is evidence supporting the fixed-frame
exposure hypothesis rather than per-control causal isolation.

Each independent media-v2 read showed complete NEUTRAL graph before,
between and after separate real-camera sessions. No --file image payloads
were saved, no IR camera or emitter used, and VD55G0 kernel standby
confirmed stream=0 illumination=0. Root-private libcamera source, IPA
config and entire staged binary bundle passed SHA and ownership checks.
The one-shot service passed and automatically returned SP11 to Golden
boot 50b23212-8e86-4f5b-bc8b-f1705db5546d, with original v19c saved
entry, empty pending next entry and no camera nodes/modules.

After independent Golden recovery, the separate E004lv boot files, GRUB
entry, root-private libcamera build, stage and service were fully
RETIRED. E004lv identity is CONSUMED; NEVER rearm. Redacted numeric
frame metadata, format, AGC exposure-cap, neutral graphs, root asset
verification and IR standby are in RESULT/CONSUMED/evidence.
Next step is new uniquely guarded sustained processed camera
reopen/suspend/30fps and functional selectable service ownership
tests; eventual Windows ISP comparison must use controlled lighting.
