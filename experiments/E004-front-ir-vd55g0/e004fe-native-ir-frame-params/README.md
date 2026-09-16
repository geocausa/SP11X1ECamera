# E004fe: frame-associated software ISP parameters

E004fd proved 16 processed DMA buffers and clean sensor/PM lifecycle, but its first
frame was white because processing ran before asynchronous IPA parameters arrived.
The failed gate is preserved. This candidate changes only the application/IPA.
Kernel modules, DT, firmware and all hardware controls are byte-identical to E004fd.

Patch 0003 retains asynchronous IPA operation and adds the frame ID to its reply.
The software ISP queues each input/output pair until that frame's parameters are
ready. Only one parameter computation owns shared memory at a time; parameters
are copied into the processing job before the next computation is requested.
Stop suppresses late replies and cancels pending buffers using the existing
lifecycle. This fixes the ordering rather than defaulting bad settings or dropping
frame zero. It also avoids running synchronous IPA code on the wrong thread.

All three patches reapply byte-exactly to upstream v0.7.0, with 17 modified source
files hashed. Four focused processing/helper/format tests pass. The E004fc sanitizer
result applies to pixel processing; it is not proof of this new asynchronous
lifecycle. The bounded live run validates delivery, first-frame image and shutdown.

APP-MANIFEST.json records the coherent rebuilt application/library/IPA/proxy set.
The private IPA event ABI changed, so mixing these build components is forbidden.
No system installation. RPATH/build-tree lookup selects this isolated build.

Use the same strict 16-frame RGB888 generated-ramp gate as E004fd, including frame
zero, automatic backend/tuning selection, neutral pixels, equal rows, cleared
padding and sensor/kernel/PM health. Initial exposure=1000, analogue=16, digital=256;
IPA may adjust exposure/gain. No illumination or protected runtime.

Fresh one-shot entry, 120-second return watchdog, automatic Golden return and
hash-checked retirement. No same-boot retry. Successful output would prove the
generated-pattern path only; optical image quality and endurance remain open.
