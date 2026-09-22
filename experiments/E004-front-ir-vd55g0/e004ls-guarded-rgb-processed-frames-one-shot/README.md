# E004ls — bounded real libcamera processed RGB888 viewfinder one-shot

Fresh unused E004ls identity, separate from CONSUMED E004lr RAW-stream hardware proof. Parent project commit 1fd7409280a0013d76398eeb19de274b1dc2e53b, dated 2026-09-23 Europe/London. E004ls must never reuse any prior experiment identity or boot asset. Golden v19c remains protected saved default and cannot be replaced, modified or made an experimental default.

Goal: independently test the pinned libcamera 0.7.0 Simple software ISP processed-output path by requesting exactly 6 metadata-confirmed 640x480 RGB888 viewfinder buffers from real OV13858 rear and IMX681 front in separate sequential libcamera cam processes, with no --file or saved payload. The full native read-only Media Controller v2 graph must be neutral before, between and after sessions; root node seal and no competing/leaked FDs are checked. Reject any silently adjusted output format/size: libcamera's own configure log must contain 640x480-RGB888 and the metadata validator requires 6 distinct strictly increasing request sequences/timestamps and positive bytesused per camera. The 6 frames can validate buffer delivery and bounded lifecycle but NOT sustained 30fps, meaningful colour fidelity or independently different optical payloads; night lights remain OFF so low-light images are not an image-quality parity test.

Hardware authority: exactly the E004le physically tested separate qcom-camss.ko 8aa3e7cb3ce790a0b37b6494f540e4075d78f8b3fed69ed415e81f4da5cfb75d and IMX681.ko 448bd926193c003cdf3c1407382cde0af7ba0ebfdca7cb36d8c797797c0bc6c modules reproduced byte-for-byte from E004ld timing patch at its fixed debug prefix; no accepted production authority mutated. Canonical independent four-module package manifest SHA ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c. Exact private root-owned pinned libcamera 0.7.0 base b7854fd + E004lh RGB route filter + E004lm guarded Simple native transaction + E004lo failed STREAMOFF fail-closed patch + validated IMX681 gain helper, compiled full 368-target build and 77-test suite (45 pass, one expected fail, 31 skip, zero unexpected failures). The Simple pipeline explicitly enables SoftwareIsp for qcom-camss and DebayerCpu lists the physical cameras' packed 10-bit Bayer formats as capable of RGB888 output; this is a source capability, not proof of processed output from actual SP11 hardware.

Admission: unique dedicated single-use nondefault boot sp11_camera_e004ls_rgb_frames=1 and exact sp11_entry marker; first-write consumed marker BEFORE camera module bind. 45 actual media/video/subdevice nodes root:root 0600, lease current quiescence+cooperative lock and root node ownership checks, bounded independent cam processes, immutable session assets verified from root-sealed /var/lib private bundle, separate full graph audits, automatic Golden return via systemd ExecStopPost on success or failure. No IR camera stream or emitter, no Windows Hello, no PAM/login. The service must not retry a consumed identity; on any writer/STREAMOFF/format/metadata failure it leaves uncertain graph untouched and reboots to Golden. Only archive numeric camera metadata, source hashes and safety evidence after independently verifying return to Golden; retire temporary GRUB entry, service and private bundle before committing result.

Limits: root-only DAC protects an isolated experiment against ordinary unprivileged desktop clients, not arbitrary root-equivalent actors or production multi-client exclusivity. Calibrated ISP/Windows QC10C parity, service robustness and ordinary consumer app output remain unproven until separate tests. This is NOT a production driver deployment.

Status at preparation: SOURCE ONLY. Final attempt status must be determined from its own fresh RESULT.json and CONSUMED.json; never infer success from earlier E004lr RAW frames.

## Final physical result — strict-contract FAIL, partial rear processed output

One unique candidate boot ec89a029-8fb3-4801-b99a-b01a682a9a2a
ran a real root-guarded libcamera X1E rear viewfinder stream. The
requested 640x480 RGB888 format was ADJUSTED by libcamera to actual
640x480 XRGB8888/sRGB, so the pinned strict configure-log check
correctly FAILED and the one-shot terminated without attempting the
front camera or executing the rear post-session full-graph check.
This is NOT a pass for the requested RGB888 contract, nor for front
processed output. The rear cam process independently reported six
completed sequence numbers 0..5 and 1,228,800 bytesused in each output
buffer (640*480*4), with no saved pixel payload; intermittent timing
is not a sustained frame-rate proof. The initial full media graph
was independently NEUTRAL. The post-rear graph was NOT independently
checked, because the strict format gate stopped the runner first;
do not infer its state from the automatic reboot. The candidate
systemd service failed as expected (rc1), requested and achieved
automatic protected Golden return boot
2fdd13fe-daa1-44a4-bd36-8802cc0943f7. Golden default v19c,
empty next_entry and absence of camera nodes/modules were verified.
Kernel VD55G0 remained stream=0 illumination=0. Root-private E004ls
bundle/build, unique boot and service were RETIRED; E004ls identity
is CONSUMED and must NEVER be rearmed. See RESULT/CONSUMED and
redacted numeric evidence. The next fresh candidate should explicitly
request the observed XRGB8888 output from BOTH sensors, require a
separate full neutral graph read after each session, and still
record no image payload in the dark nighttime scene.
