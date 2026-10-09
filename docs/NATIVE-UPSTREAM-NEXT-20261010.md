# Native front/back completion gates

The deliverable is kernel V4L2/Media Controller support for the sensors and
Qualcomm capture/ISP pipeline, a standard libcamera pipeline and IPA, independently
measured tuning, and native application integration. The optional webcam bridge
cannot substitute for these gates. Current source and hardware results are
development qualifications, not a shipping or upstream-ready stack.

| Gate | Current evidence | Next acceptance |
| --- | --- | --- |
| Rear capture/control |66:400 real4K NV12 requests,400 native IPA joins,29.97fps callback, bounded acknowledged AE, clean stop/reclaim | Calibrate brightness target and clipping against fresh Windows references under controlled scene/light |
| Rear tone/color |63:measured chart curve/CST,4500-frame clean capture;66 retains exact published tuning | Neutral illuminants, off-chart colors, shadows/highlights, noise, detail and focus measurements |
| Front capture/manual controls |meter01:160 real2560x1440 NV12 requests at30fps, five known-register reads, public metadata and clean stop | Resolve raw mean714->628 when analogue gain rises, then bounded feedback using an optical response above the measured noise floor |
| Front image quality | Current Windows and Linux front images both dim; scene-registration comparison fails | Establish credible lit scene/physical orientation; compare raw sensor, ISP statistics and output before deriving black/scale/tone/color |
| Automatic features | Rear AE engineering target works; front AE/AWB and rear real-illuminant AWB unqualified | Stable convergence, clipping control, changing-light response and applicable focus behavior |
| Native applications/lifetime | Dedicated libcamera tests pass; earlier desktop-held subdevice module unload caused real UAF | Safe ordinary application ownership, client close/crash, front/back switches, repeated start/stop and recovery without unsafe module unload |
| Upstream source | Independent explicit statistics decoder and tested transport/lifetime work retained | Replace retained private profiles, review redistribution/provenance, production UAPI/bindings and maintainable source patches against pinned upstream trees |

Front firmware/profile and rear private startup profile are still dependencies.
No upstream patch submission or acceptance is claimed. Existing scalar chart
reports do not prove general Windows parity, sensor exposure equivalence, image
detail/SNR, day/night, or same-exposure statistics provenance.

Priorities for the next autonomous session:

1. Inspect the front meter tap/normalization and sensor/ISP black handling using
   retained private originals and source facts. A scene with little usable signal
   cannot qualify gain response or an AE target. Preserve manual controls until
   the feedback sign and settling response are physically supported.
2. Calibrate the rear exposure target and highlight/shadow behavior against fresh
   Windows references. The rear SP7 LCD subject is useful for controlled charts;
   a chart on a display alone cannot qualify real-illuminant white balance.
3. Implement and validate the missing automatic features on the same native
   kernel/libcamera path. Keep kernel owner/DMA/stop proofs and Golden return.
4. Remove private profile dependencies through independently written, reviewable
   driver configuration and measured redistributable tuning; assemble upstream
   changes by subsystem with exact build/test and hardware evidence.
5. Qualify native desktop/application use, camera switches and fault/soak cases
   once image correctness and automatic behavior are established.

Golden is5bc9215f-59f0-4157-aa61-5f945aab931f, defaultunchanged/nextentryempty.
Rear66, front-meter01 and Windows-front02 are consumed/retired; never rearm.
Source-only, build and private evidence stay on SP11; allowed global scalar facts
and independently written source are in Git. All spatial data/pixels remain
sameSP11. No OS sleep/suspend/hibernate/power-policy work. Counters after59 still
need ledger reconciliation; do not fabricate totals.

Front01 retention: all160 original NV12 payloads verified byte-for-byte in
root-only PRIVATE-ALL160-NV12.tar.zst. Five representative .bin files remain
directly available to the comparator. The archive preserves tar names/metadata;
restore only into a new root-only directory and compare exact extents before use.
No image hashes are published. The archive saved roughly608MB, leaving1.20GB.
