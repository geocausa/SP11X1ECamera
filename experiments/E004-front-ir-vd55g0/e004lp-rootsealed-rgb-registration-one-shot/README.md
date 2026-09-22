# E004lp — root-sealed real RGB libcamera registration (fresh one-shot)

Prepared 2026-09-22 after the consumed E004lo registration attempt, which registered physical OV13858 but rejected IMX681 because the canonical baseline module did not expose mandatory HBLANK and PIXEL_RATE controls. E004lp has a completely NEW one-shot identity and deliberately tests registration only. E004lo (and E004ld/E004le physical test identities) are never rearmed.

New candidate camera modules: the EXACT SHA-256 binary pair independently accepted in E004le optical 1080p/4K sequential physical test:
- qcom-camss.ko: 8aa3e7cb3ce790a0b37b6494f540e4075d78f8b3fed69ed415e81f4da5cfb75d
- imx681.ko: 448bd926193c003cdf3c1407382c3de0af7ba0ebfdca7cb36d8c797797c0bc6c

These modules were reproducibly rebuilt from the accepted sources with the archived E004ld timing/clock patch (SHA-256 f553a8de8cd1389a69978af7bace0f8a9ca6c6f9491d412314aed50a4137a92a) and the EXACT original compiler work path /tmp/sp11-e004ld-kernel-_ai7a8ph/source with standard Kbuild W=1, not different path-mapping options. SHA-256 exactly matched the E004le accepted evidence. IMX681 exposes read-only HBLANK=2912 and pixel-array PIXEL_RATE=719898240, while CAMSS calculates C-PHY transport rate separately; E004le sustained 1080p front optical RGB at ~30fps using VFE1 RDI345.6 MHz, but did NOT physically test PIX594 MHz. E004lp does not start capture and does not establish image quality or fps through libcamera.

libcamera v0.7.0 source from pinned commit b7854fd07d42168f099b5ce30d1702e0e0875bf5 is extracted clean into /var/lib/sp11-e004lp-build/source. E004lh RGB route path filter + E004lm guarded native libcamera Simple + E004lo fail-closed streamOff patch + independent IMX681 gain helper are applied, plus the distinct E004lp boot token and lease header. The root-only build and SOURCE path were intentionally /var/lib/sp11-e004lp-build from the outset, unlike the prior E004lo scratch build whose absolute IPA config paths resolved into an unsealed /home source. Once native build 368/368 and full 77-test suite completed (45 OK, one expected failure, 31 skips, zero unexpected failures, IMX681 helper test OK), the entire persistent build source tree was changed to root:root mode 0700 recursively and is NOT installed on Golden.

The installer uses the unchanged canonical 4-module package with its independent accepted manifest and copies only the two exact timing/clock candidate modules under a separate root-private candidate directory. It installs a separate nondefault, one-shot boot, strict root-only conditional systemd service and a distinct E004lp boot command-line authorization; Golden kernel, initrd, saved_entry and /lib/modules remain untouched. The runner consumes the attempt BEFORE binding modules, checks all sensors suspended, no existing camera FDs, seals the exact 1 media / 16 video / 28 subdevice root:root 0600 node set, SHA verifies the root-owned pinned bundle, invokes ONLY cam --list under a 30-second bound, and requires exactly one real IMX681 and one real OV13858 camera ID, with no IR camera registration. Known nonfatal G_SELECTION ENOTTY crop diagnostics do not alone invalidate registration; missing mandatory controls, failed sensor construction, routing, or lost ownership do. No capture/STREAMON/IR emitter or pixel files are permitted. The unit reboots to saved Golden on completion or error.

Root ownership and the cooperative media lock provide bounded experimental exclusion of ordinary nonroot applications only. They do NOT prove general multi-client OS-enforced exclusivity against root-equivalent/uncooperative clients and do not make the camera stack production-ready. Failure or inconclusive result permanently consumes E004lp. After independent Golden return, archive actual evidence and remove candidate boot files, service, root-private staging and root-only build tree. Never rerun this attempt under E004lp.

Status at preparation: SOURCE AND SCRIPTS ONLY, NO E004lp BOOT yet. Subsequent RESULT.json / CONSUMED.json supersede this status once the unique physical attempt runs.

## Final physical result — PASS; one-shot consumed and fully retired

The unique physical candidate boot c5f7d2f0-7164-4fba-9550-7fbb64e3ffff
successfully registered BOTH real libcamera cameras: ov13858 and imx681,
each exactly once. Four Virtual cameras were deliberately excluded from the
acceptance count. The earlier E004lo mandatory HBLANK/PIXEL_RATE registration
blocker was cleared using the byte-identical E004le accepted IMX681/CAMSS
timing pair. No capture or STREAMON was requested by cam --list, no IR camera
was registered, and VD55G0 kernel standby confirmed stream=0 illumination=0.
The root-private IPA configuration resolved only under the root-owned
/var/lib/sp11-e004lp-build/source path, not the prior geoca-writable /home
scratch. Runtime logs still report optional crop/selection ENOTTY, defaulted
sensor rectangles and missing per-sensor calibrated IPA YAML; registration
is not image-quality or streaming proof. Candidate one-shot service passed
and automatically returned to Golden boot 78eea3f0-1852-42ea-8ab5-c250319b38c5.
The saved default remained v19c, next_entry empty, no camera nodes/modules.
All candidate boot, private build, service and root-staged assets were
retired after Golden verification. See RESULT.json, CONSUMED.json and
redacted evidence/. NEVER rearm E004lp. The next independent guard is
libcamera configure/start/stream/stop/neutral with a fresh identity and
current exclusive/quiescent ownership, not an unguarded production install.
