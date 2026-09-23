# Opt-in RGB software camera service — owner/session policy (OFFLINE ONLY)

The first RGB product priority is **real front 1920x1080 NV12 and rear 3840x2160 NV12 through ordinary unprivileged Linux applications**. The parent software publisher package now has an explicit candidate-only compile-time opt-in long-lived mode with a four-hour failure deadline, normal builds continuing to reject it; this does not itself create an installed camera. The supported source plan is the already physically exercised RAW10→NV12 direct publisher pair at `../front-direct-publisher.c` and `../rear-direct-publisher.c`. The separately exercised libcamera 640x480 XRGB8888 software-ISP path is NOT high-resolution parity, and the native QC10C hardware ISP is a later optional decision.

`session.py` is the maintained **single-owner safety state machine** for the future opt-in camera service. It is intentionally a standalone, camera-free policy component, **not** a deployed live backend and **not** evidence of working persistent service. A future root-private, fresh one-shot candidate must implement `SessionBackend` with independently checked kernel state. The physical backend must bridge the already maintained `../../routing/route_policy.py` complete 119-link transaction policy and the known-good source publisher format/STREAMOFF guards; do not create a second ad-hoc unverified graph switching algorithm. A staged opt-in candidate must maintain both discoverable /dev/video91 front1080p and /dev/video90 rear4K endpoints with one active physical CAMSS route at a time.

New maintained Linux integration sources:
- media_backend.py supplies the exact bounded media-ctl argv backend
  for the 119-edge full-graph route_policy.Controller, admitting only
  documented front/rear RGB links and fail-closing on uncertain writes.
- rgb_device_backend.py joins that policy to RGBSession, source/virtual
  format negotiation and the root-owned source publisher service
  start/stop/invocation verification contract.
- candidate_owner.py implements the root-private, unique-candidate
  boot/GRUB/consumption checks, process-backed exclusive controller
  flock, fresh independent device FD and IR-idle checks, an operation
  command allowlist and source publisher 143/STREAMOFF proof.
- candidate_driver.py is the candidate-ONLY front→neutral→rear→neutral
  acceptance harness for independently launched ordinary uid1000
  first/reopen/crash/recovery app clients and one publisher invocation
  per camera. It does not load modules, install anything, arm a boot
  or schedule sleep: the separate freshly source-pinned one-shot
  candidate must first validate and stage all assets and automatically
  return to Golden on error or success.

35 offline mock-controller, exact graph-write, device-format, root
operation allowlist and stop-proof tests pass. **E004lz** subsequently
physically exercised these joined components on both real RGB cameras
(front 1080p and rear 4K) with three ordinary-user normal app opens,
intentional app kill and recovery, planned 143/STREAMOFF and complete
neutral media graph. See its RESULT/CONSUMED/evidence. This confirms
bounded hardware integration, NOT a deployed permanent selectable
camera service, long-run reliability or acceptable calibrated image
quality. Both test scenes sampled near-black. The previous E004ly
trial proved longer ~115s per camera but used older scripted route
transitions.

Service invariants implemented by the policy:

- Before admission, require **exact authorized candidate boot/asset identity, live exclusive camera lease, IR-off readback, zero camera-owner/client FDs and independently verified complete neutral media graph**. The prospective backend MUST implement these checks against fresh physical state; a boolean mock is not a security boundary.
- Only allow `front` or `rear`. Route-neutral→selected, verify the complete selected native graph, verify RAW source + named NV12 endpoint configuration, and check that the expected publisher invocation actually started. Duplicate or concurrent selections are denied.
- On stop, request publisher termination and require **verified STREAMOFF AND process/child reap**, then independent camera/device FD release before ANY graph write; verify the current selected graph, guarded neutralization, fresh neutral graph, IR off and lease continuity. Never assume publisher exit=0, a stale cached graph or a V4L2 loopback advertisement proves source was stopped.
- `switch` always performs a full verified stop and neutral checkpoint before starting the other camera. A missing/uncertain stop, lease loss, unexpected graph, failed link write, invalid IR state or outstanding app reader **poisons** the session. No guessed retry or rollback. Outer isolated candidate systemd unit must terminate its entire cgroup and return to preserved Golden on any uncertain state or process failure, rather than attempting another camera.
- Nothing here touches system sleep. SP11 Linux OS standby/suspend/resume/hibernate tests remain prohibited. Keep IR sensor/illuminator unstreamed and Golden camera-free.

Run the camera-free suite:

```sh
python3 -m unittest discover -s src/sp11-camera-stack/rgb/service/tests -p 'test_*.py' -v
bash src/sp11-camera-stack/rgb/tests/test.sh
python3 src/sp11-camera-stack/routing/tests/test_route_policy.py
```

**Next engineering work, not yet proved:** implement the actual root-private candidate backend and service lifecycle against the accepted physical authority, source-pinned publishers and `route_policy.Controller`; independently validate unprivileged front1080p/rear4K optical application frames, peer-reader release, repeated normal-powered-on selection, process signal/stop, neutral after every switch, service timeout/crash recovery and controlled-lit image quality. Then separately design a safe opt-in release install and longer-lived publisher (normal builds remain bounded at **2400 frames/210 seconds**;
the new explicit compile-time opt-in \`continuous\` mode is only
camera-free mock-tested with a hard **4-hour** safety deadline,
and has NOT been validated on real SP11 hardware or as a persistent
service). The source-only policy must never be described as these live gates passing. Windows ISP parity, QC10C import and protected IR/Hello remain outside Stage 1.
