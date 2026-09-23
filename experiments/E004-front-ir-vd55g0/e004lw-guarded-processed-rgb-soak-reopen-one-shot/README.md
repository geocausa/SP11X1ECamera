# E004lw — guarded sustained processed RGB and independent reopen, no system sleep

Date: 2026-09-23. Fresh single-use E004lw identity. Parent E004lv proved 30 error-free real libcamera 640x480 XRGB8888 frames per camera with a neutral graph between streams; E004lu front Soft IPA caps active exposure to 3550 even-step lines. E004lw is a new experiment, NEVER reuse consumed E004lv or any earlier one-shot boot.

This experiment validates *ordinary powered-on camera lifecycle*, not unsupported Linux system suspend/resume. In a distinct root-only nondefault one-shot GRUB entry, start **four independent libcamera cam processes** in order **front → rear → front → rear**. Each process requests 900 processed viewfinder frames at exactly 640x480-XRGB8888/sRGB, a nominal 30 seconds per session (3600 total frames across about two minutes). A strict offline-tested validator requires precisely 900 consecutive seq0..899 entries, 1228800 bytesused per entry, strictly increasing timestamps, 26–40s first/last span, and no adjacent timestamp gap over 250ms. The native read-only full Media Controller v2 probe verifies neutral before first capture and after EVERY one of four session closes. Before and after each independent process, no other camera node users may be present. Front IPA must log exposure range 4–3550 for each front reopening; ANY sensor set-control error, incorrect format, nonneutral graph, missing capture, resource leak or timeout is a failed test. No frame payload is saved; output metadata and logs are the only retained evidence, so it cannot prove optical image quality.

Exact four-camera hardware package and DTB are recompiled/hashed to the previously accepted authority SHA, alongside the E004le physically accepted byte-identical IMX681/CAMSS timing module pair. Pinned clean libcamera v0.7.0 includes E004lh RGB filter, E004lm guarded native routes, E004lo fail-closed STREAMOFF handling, IMX681 gain helper, E004lu fixed-frame Soft IPA, and an E004lw-specific strict experimental kernel-cmdline lease. Everything is installed into a separate root:root 0700 private source/build and one-shot stage; all 45 camera nodes are temporarily root:root 0600, with process/FD checks. This is *not* production exclusivity against root-equivalent or uncooperative clients.

The unit has a bounded startup timeout and requests automatic reboot to the saved Golden Linux boot on success or failure. Original Golden kernel, DTB, initrd, saved GRUB entry, system services and /lib/modules are not replaced. The one-shot experiment is irrevocably consumed on arming; its candidate boot/service/build assets are retired only after independently verified Golden return. **Never send SP11 Linux into OS standby, suspend, hibernate or resume**: the user reports system sleep is not implemented reliably and may crash the OS. Read-only per-sensor runtime-PM idle observation is distinct from system sleep.

Acceptance is a *sustained, repeated-open processed-video diagnostic*. It does not provide a normal-user desktop device/service, calibrated Windows QC10C ISP parity, full-resolution processed RGB, or system suspend/resume. Production service and ordinary-camera-app publication require separate engineering and validation.

Preparation status: source only; no physical E004lw attempt yet. RESULT.json / CONSUMED.json supersede preparation after the one-shot.

## Final physical result — strict cadence FAIL; safely retired

Fresh E004lw physical boot 38faf9e3-6f47-4e5b-bc28-f7101df53491
returned **FAIL, rc6** from its 900-frame per-session strict validator.
First front process 900 consecutive 1228800-byte XRGB8888 frame records
over 30000971us, first rear 900 over 30018414us. Independent full kernel
graph snapshots confirmed neutral before first and after each first-two
processes, and zero later >250ms timestamp gaps were observed.

The *second front reopen* did deliver all 900 consecutive nonempty frames,
with 30962668us total span and NO later (post initial 10 frames) >250ms
gaps. However a real **1001018us** timestamp gap between sequence 3
and 4 violates the advertised all-interval <=250ms contract.
Its summary file was created empty by shell redirection before the
validator returned rc6. Consequently the runner did NOT execute a
post-third-session independent neutral snapshot, and did NOT start
the fourth/rear reopening. These missing checks are NOT inferred from
the first two successful runs. No V4L2 control-range/STREAMOFF failure
was observed in the completed first three processes. The abrupt gap
may reflect sensor, kernel or application pipeline scheduling; no
per-layer trace independently attributes the root cause. A previous
E004ls short rear processed session also exhibited an early 1s gap.

The service deliberately failed and automatically rebooted into
protected Golden boot 3fe1e5eb-d574-4ac0-8e7e-efaa03bfe3ad, saved
v19c and empty pending next entry, no active camera nodes or modules.
VD55G0 remained in IR stream=0 illumination=0 standby. No OS-level
system sleep was initiated. The unique root stage, private libcamera
build, GRUB candidate and service were retired ONLY after Golden
recovery checks. Identity E004lw is CONSUMED, NEVER reuse.
Numeric evidence and RESULT/CONSUMED record the failed acceptance.
The next distinct experiment should report startup vs steady cadence
separately and still require neutral+FD checks after every actual process,
even if its strict startup-gap criterion fails. Ordinary service and
multi-application desktop access remain unfinished.
