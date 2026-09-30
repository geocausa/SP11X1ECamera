# E011AT — actual AWB SetParam retained BG boundary

Status: LIVE SETPARAM CALLBACK EXCLUDED; EARLIER INITIALIZATION STILL OPEN.
Fresh attempt E011AT-20260930-2029A is consumed. Preparation 204b961fc20c69967630b1a309d17c3c50b8ce21; parent 96e7a441a820e3a086aae942ce481c3b448fefee.

One original Windows rear Color VideoRecord NV12 3840x2160 run completed 714 valid 4K frame handles, one successful Start and a clean Stop. The user-mode CDB session explicitly detached and exited 0; its manual-only scheduled task was removed. No kernel debugging, BCD change, optical-pixel storage, Linux camera activation, production C change or kernel build occurred.

The live callback is the pinned original CamX::CAWBMain::AWBSetParameter at RVA 0x68C090. Its correct dispatch chain is wrapper+0x28 -> actor+0 -> vtable+0x08. The same thread entered and returned from the callback with result 0. The 40-byte parameter record at the outer call and actual callback entry is identical.

The actor's 92-byte retained BG record already contains quad=1 at the actual callback entry. All 92 bytes are identical at callback return, outer return, before GetParam2 and the later first observed tuning-helper hit. Publication property 0x5000001D/size 0x80 and the first request-1 consumer both contain quad=1. Therefore AWBSetParameter RVA 0x68C090 does not initialize or modify the retained BG record in this sampled cold startup. The numeric initialization/value-selection rule remains OPEN and lies earlier than callback entry: in pre-dispatch wrapper/configuration/registration or actor construction.

The generated outer handler had one excess pointer dereference. Its derived actor/code/IO dumps are invalid or incomplete and are explicitly excluded. While the same SetParam call was held, the actor/vtable/callback chain was corrected and the actual entry/return evidence was captured. The requested ARM64 data watch could not be inserted because the thread had no free data-breakpoint slot; the failed breakpoint was removed before continuing. This produced one invalid-insert and two too-many-data-breakpoint diagnostics, but no access violation and no second camera Start. Because no first-write trap fired, this experiment narrows the boundary but does not identify the first writer.

The tuning helper at RVA 0x689228 first fired after the first publication/consumer in this run. Its sampled actor matches and retained bytes remain identical, but this timing does not prove it ran inside the first observed SetParam call. It is not claimed as the cold initializer.

Private originals, process bytes, raw CDB output and captures remain on the same SP11. Only derived facts and hashes enter Git. Run validate-private.py on SP11 to verify the private evidence. The frozen make-observer.py remains an auditable consumed generator and must not be reused.

Normal reboot returned protected Golden Linux 7.1.5-sp11-render-parity-v4+, boot 25a899ad-ae69-418f-86fb-d110b5bd84d0, saved sp11-audio-fullio-v19c, empty next_entry, camera idle and NTFS unmounted.

NEXT: bracket the SetParam wrapper from its entry at RVA 0x681C40 through the pre-dispatch instructions before 0x83180C, then trace actor construction/configuration registration if quad is already one at wrapper entry. Do not repeat RVA 0x68C090, infer a constant policy from one sample, or hardcode quad=1. Cold AEC weights, exact AWB retained initialization, RS count/whole-frame offset authority, final deterministic bootstrap and independent same-generation WM16 IRQ/consumed-IOVA/DMA/IOMMU retirement remain open. Native rear ISP runtime remains DENIED.
