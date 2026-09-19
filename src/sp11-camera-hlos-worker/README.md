# SP11 native Linux IR pixel worker — HLOS proof of concept

This is an **unprotected, offline-only Linux userspace adapter** around the maintained, Windows-derived pixel-processing core in `../sp11-camera-protected-worker/`. It runs as an ordinary ARM64 Linux program; it does **not** need Qualcomm SecurePD signing or load an unsigned DSP image. It does not change firmware, signature verification, the protected camera path, the Golden boot, or any installed camera service.

`sp11-hlos-ir.c` reads **exactly one contiguous 644×604 NV12 frame** on standard input and writes one processed NV12 frame on standard output. It uses the maintained parity core's request ID 10 SWABF→SWASF path with caller-owned scratch; it clears scratch/input/output buffers before release. Its Y plane must exactly match the pinned Windows reference oracle; UV is neutral 0x80 by the current worker contract. This is a pixel-processing proof, **not** a face detector, liveness check, biometric template system or working login/unlock mechanism.

Run `./src/sp11-camera-hlos-worker/test-offline.sh` from the repository (or any cwd). The test builds from maintained sources on the current host, checks the pinned oracle hashes and full-frame output, and rejects short, overlong and empty inputs. All executables and image buffers used by the test stay in a temporary directory, which is removed when the test finishes. No runtime camera access is performed.

## Integration boundary

Native IR camera transport and monochrome processing have separate hardware evidence. A future guarded, opt-in prototype can accept **ordinary non-protected** VD55G0 captures via the existing V4L2/libcamera path, apply this processing, then evaluate a separate face-authentication application and PAM integration. That is a new, unprotected security model: ordinary host processes with permission to access the device or frame memory can potentially inspect or tamper with the images. It must not be represented as Windows Hello or hardware-backed protected face authentication.

Do **not** feed protected CPZ/SecurePD images to this adapter, enable a forbidden protected-buffer mapping, patch verification, or claim that this proof establishes biometric identification. Do not activate IR illumination until its independent timing/current/timeout safety evidence is closed. Camera hardware and login configuration are not touched by this stage.

## E004fe archived-capture integration

`sp11-ir-rgb888-to-nv12.c` is a strict format bridge for the **actual, archived E004fe sensor-pattern libcamera output**, which was captured as 644×604 RGB888 with a 1936-byte stride. It requires three identical colour components per pixel, zero row padding, and exactly one complete frame. It copies each grayscale value to 8-bit NV12 luma and sets chroma to neutral 128 before passing the frame to the existing HLOS worker. It is intentionally not a generic colour conversion or live camera launcher.

`bash src/sp11-camera-hlos-worker/test-capture-integration.sh` checks the unchanged 16-frame archive SHA-256 and per-frame SHA-256, independently constructs expected NV12 from the first frame, verifies the bridge byte-for-byte, runs the maintained parity pixel core, confirms the direct and piped paths agree, and rejects short/long/non-neutral/padded-corrupt frames. The bounded end-to-end pattern-output SHA-256 is `beb89bd8799fb43549d1ab1ade9135145e31651efcba4b8b72a8856dd4cdb7f9`. A separate ASan/UBSan full-frame pipeline passed on the same fixture.

This demonstrates compatibility between the already-proven **libcamera output format** and the HLOS image-processing algorithm without another camera boot. The archived image is a sensor-generated greyscale pattern with illumination disabled, not an illuminated face, ordinary optical-quality test, identity match, anti-spoofing proof, or login/unlock demonstration. E004fq Windows sensor/exposure and strobe timing authority remains the independent live illumination prerequisite.
