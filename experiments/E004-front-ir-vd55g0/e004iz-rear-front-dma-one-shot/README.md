# E004iz — bounded SAME-BOOT rear RGB + front RGB QC10C DMA regression

Date: 2026-09-20. Parent `665e93b`. This is a **new, unique**
one-shot candidate; previous E004iq, E004iv and E004iw identities
were each consumed and retired and must never be reused.

## Why BOTH cameras

The user's next objective is working front AND rear RGB in ordinary
Linux applications. The accepted E004dz hardware boot previously
delivered one byte-exact OV13858 rear test-pattern frame, eight
real rear `pgAA` GRBG10 Bayer frames near 30fps, neutralized the
rear route, then delivered 27 front IMX681 QC10C compressed YUV
frames with both sensors safely suspended and final route neutral.
Rear desktop NV12 conversion is now fast enough in a bounded
offline test (E004iu), but only a previous colour-bar frame was
retained and converted; **no real normal optical rear frame**
remained for validating the new conversion. Front output remains
compressed QC10C: do not call it NV12 or a ready desktop webcam.

The new mapped-DMA span guard in E004ip compiles and passes
simulated tests, but its first physical front regression E004iq
aborted on GRUB environment preflight before loading any camera
module. E004ix reproduced concurrent GRUB writer/read errors
on disposable files. The scoped E004iy reversible GRUB service
ordering has passed a manual start and **one** ordinary Golden
cold boot, with both stock writer units success, saved Golden
and empty one-shot entry. Repeated candidate-boot correctness
and the E004ip real DMA mapping are still unproven.

## Exact source-locked staged candidate

The original package was rebuilt entirely from its accepted,
provenance-pinned SP11 source, Golden v4 ABI and unified DTB
into a private, disposable `/tmp/sp11-e004iz-two-rgb-candidate-20260920`
tree. The 7 accepted hardware sources and full 50-file stack
package passed their exact original manifest hashes:

- Hardware manifest SHA-256:
  `ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c`
- Full package manifest SHA-256:
  `11a649fafbfbfc3467f86f2f17d8ff4d4a86e2f5f4fc36c7f1d1c7839160c646`

The only candidate driver change is the isolated E004ip
QC10C-only mapped-SG DMA prefix guard, built against the
same original Golden-v4 ABI. It is kept separate from the
unchanged accepted CAMSS module and is SHA-pinned as
`4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d`.
The separate NV12 kernel planner remains fail-closed,
non-runnable and uninstalled.

The prospective one-shot boots the protected Golden kernel,
Golden initrd and separately accepted **unified camera DTB**
only for this one attempt. It blacklists auto-loading the four
camera modules; their exact source-locked root-private copies
are loaded only by the conditional E004iz service after all
preflight checks succeed. No camera module or DTB is installed
as the system default. GRUB's persistent saved default
remains `sp11-audio-fullio-v19c`, with a separately consumed
unique `next_entry`. Its root service waits for BOTH stock
GRUB environment writers and requires actual successful
execution timestamps and correct ordering, a valid read-only
GRUB environment, exact boot marker and package/driver
checksums BEFORE any camera module is loaded. The service
reboots to Golden on success, failure or timeout, with
a one-attempt marker and no same-boot retry.

## Bounded physical capture plan, not yet a live result

Using the exact previously accepted rear route and `pgAA`
format, capture one byte-exact OV13858 hardware colourbar
frame (expected original SHA
`6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`),
switch the sensor back to **normal optical mode**,
capture precisely eight full Bayer10 rear frames and
check exact frame sizes, ordered sequences and approximately
30fps timestamps, then suspend/neutralize the rear route.
The resulting eight full optical frames remain in a
root-only 0700/0600 local directory, are never committed or
shared, and may be used only for an **offline private**
rear-to-NV12 conversion after the machine returns to Golden.
The rear script resets the test-pattern control if and
only if it was left active.

Then run the accepted **front RGB QC10C, shadow policy**
27-frame bounded stream using the E004ip candidate CAMSS
module, verify sequential buffers and size 7,778,304 bytes,
suspension and neutral final route, and check kernel health.
No IR sensor stream, IR illumination/physical emitter, PMIC
write, SecurePD signing, protected Hello, NV12 mode, or
unproven compressed-QC10C-as-NV12 interpretation is
authorized. The already accepted IR sensor module is loaded
only in its neutral passive state to preserve the tested
three-sensor topology. The hardware output **must not** be
treated as a normal Linux app-facing front camera yet.

After a verified Golden return, inspect only redacted
sequences, counts, hashes and statuses; run the private
rear NV12 preview and GStreamer consumer on a bounded
normal optical frame if it actually exists, and retire
this unique staging/service/GRUB entry. If any preflight
or capture fails, record the first failure, **do not
retry this candidate**, and preserve Golden.

Static offline safety tests:
```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004iz-rear-front-dma-one-shot \
  -p test_two_rgb_one_shot.py -v
```

Ten static positive/negative checks pass, including exact
separate rear/front source identities, accepted original
package hashes, candidate kernel ABI and SHA, root-safe Git
preflight, GRUB writer completion/ordering gates, rear
normal-to-neutral-to-front capture sequence, pattern reset
and explicit absence of IR illumination calls. These
checks do **not** constitute a live camera result.
