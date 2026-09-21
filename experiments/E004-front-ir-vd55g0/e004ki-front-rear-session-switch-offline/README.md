# E004ki — source-only front/rear managed session transition contract

2026-09-21. Parent `5da787a`. E004kh physically established bounded **front IMX681 → pRAA RAW10 → software 1080p NV12 → selectable temporary standard V4L2 /dev/video91 → 24/24 complete independently read app frames**, with all 24 output payloads distinct in memory. E004kd independently established the bounded rear OV13858 → 4K NV12 → ordinary temporary V4L2 /dev/video90 → 120/120 app frames path (source cadence under long load ~20fps). Both physical experiments used separate protected single-use boots; **front and rear in the same camera session, concurrent video, user-facing permanent service, Windows OEM ISP quality, and long-run frame rates remain unproven**.

`camera-session-contract.py` is a **camera-free** read-only classifier and fail-closed transition contract for a future real front/rear camera service. It requires precisely 44 current-boot media entities and all six known route links. Allowed transitions are **neutral → front-rdi-only → neutral → rear-only → neutral**, with separately verified publisher and reader exit at every transition. Direct front→rear switching, a partial front/rear route, a mixed route, front PIX QC10C and cross-instance CSID1→VFE0 RDI are forbidden. Its per-device V4L2 caps/identity contracts preserve the actually measured standard webcam nodes: front SP11-Front-Preview **NV12 1920×1080 /dev/video91**, rear SP11-Rear-Preview **NV12 3840×2160 /dev/video90**. A proposed manager must explicitly unload/neutralize the previous route, confirm all prior producers and subscribers are stopped, and only then enable the next isolated route. This contract does **not** install nodes, load any driver, activate the camera, modify GRUB or establish actual device switching.

Six Golden offline tests PASS: exact neutral/front/rear graph transitions, direct-switch and unconfirmed-exit rejection, front PIX/cross-instance/mixed links rejection, bad partial/missing 44-entity graph rejection, wrong sequence/fake neutral rejection, and the CLI's real read-only five-snapshot path. Tests mutate only **in-memory archived media graph fixture strings**; the physical SP11 Golden guard separately confirmed no camera or virtual modules/nodes/processes and original saved boot.

The next hardware milestone should use a **NEW uniquely identified auto-Golden, source/hash-locked, single-run** experiment (all E004kd, E004kg and E004kh identities are consumed forever), combining existing independently verified front/rear stages sequentially while keeping strict physical route neutrality and reader/publisher shutdown between modes. Both ordinary independent subscribers must collect bounded complete frames; the service must preserve source/app real timestamps, V4L2 sequence skips, private in-memory payload uniqueness and publisher/reader/format/byte-meter telemetry. Passing a finite sequential test does not establish permanent cold-boot service reliability, simultaneous use, exposure/white balance/detail parity or production-ready 4K30.

Run safely without hardware activation:

```bash
python3 -m unittest discover \
 -s experiments/E004-front-ir-vd55g0/e004ki-front-rear-session-switch-offline \
 -p 'test_*.py' -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

## Complete-graph guard correction (2026-09-21)

Review before session integration found that the original six-link classifier could label a graph neutral while other mutable links (including IR CSIPHY0 routes) were enabled. The strengthened classifier checks all 44 unique entities, device nodes, pad directions/counts and 119 unique edges, requires matching incoming/outgoing flags and the accepted immutable sensor/video links, and accepts only the exact neutral, front RDI or rear RDI enabled-edge sets. I2C adapter numbers remain dynamic. Nine offline tests pass, including IR/other-CSID activation, asymmetric flags, missing edges, duplicate entities/devices and immutable-link corruption rejection. No physical experiment was repeated or armed. The original six-test result above describes the earlier implementation.
