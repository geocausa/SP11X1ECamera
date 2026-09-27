# E008i — rear CSID1 IRQ / consumed-IOVA observer

Parent Git: `50ea4bd61a0732da13bfe1d2d588590764191fd1` (E008h).

Status: **BUILD-ONLY PENDING / ISOLATED ISR OBSERVER / NO MODULE LOAD / NO CAMERA**.

## Why this checkpoint exists

The accepted front PIX software latch in `camss-csid-680.c` only records
Epoch0 and BUF_DONE generations when `__csid_sp11_front_ipp_mode0()` is true.
A rear native session uses the distinct E004ns CSID1 D-PHY mode, so those
front counters are intentionally not populated for rear.

E008h can own and retire two complete ten-WM output sets, but a future rear
runner still needs a race-safe way to associate each already-latched CSID
BUF_DONE event with the VFE1 write-master `ADDR_STATUS0` values that existed
for that event.

## Rear completion mask

E007z source-locks the ten WMs to completion groups:

- group0: WM0/1/2/3;
- group4: WM11/12;
- group5: WM13;
- group6: WM14;
- group7: WM16 / BAF;
- group9: WM18.

That is exactly BUF_DONE mask `0x2F1`. Existing private Windows rear4K
E004nq scalar reduction observed CSID1 BUF_DONE status `0x2F1` and mask
`0x1FFFF` in both retained live captures, including group7/BAF.

## Observer design

The isolated E008i build extends `struct csid_device` with a 16-record
rear-only software history. Each record contains:

- the owner epoch seeded before rear IRQs are armed;
- the raw already-read CSID BUF_DONE status;
- the exact implicated WM mask;
- read-only VFE1 `ADDR_STATUS0` values for every WM in the signaled group(s).

The hook is inserted immediately after the existing
`writel(buf_done_val, CSID_BUF_DONE_IRQ_CLEAR)`. It does **not** read CSID
status a second time and adds no IRQ clear/ACK. It only samples VFE1
`ADDR_STATUS0` for groups present in that already-latched status. The normal
ISR later issues its existing global clear command unchanged.

The rear IPP Epoch0 counter is likewise incremented from the already-read
`ipp_val` before the existing clear. Front counters and front mode checks are
left untouched.

Before a future runner arms rear IRQs it must call
`csid680_e008i_rear_reset(csid, owner_epoch)` after exclusive REAR owner
acquire. Reset synchronizes the existing IRQ then clears only E008i software
history. A zero owner epoch cannot produce an accepted record.

The ring never overwrites. Overflow or any VFE snapshot error permanently
causes the accessor to fail closed with `-EOVERFLOW`. A future runner must
abort rather than infer a lost completion.

## Safety boundary

E008i is not a stream implementation. The build contains no rear activation
caller. It does not submit RT-CDM, start CSID/CSIPHY/sensor, enable WMs, free
DMA, requeue VB2, or expose a new user interface. Its standalone runtime
authorization remains `-EOPNOTSUPP`.

The next gate, after a clean build and independent verification, is to compose
a complete **still-unreachable** rear runner that drains these event records
into E008h's exact-IOVA ledgers.


## Build result — PASS

The isolated CAMSS build completed with `W=1 -j4`, zero warnings/errors and exact protected-Golden vermagic. The resulting private `qcom-camss.ko` is 13,818,112 bytes, SHA-256 `3f7a06b153aef68497f4539a00a63997df7cebbf83622d1d5e7b54b0d3e23859`. PiMaster verification and an independent Fabric verifier/hash/vermagic check pass.

The first post-build verifier invocation failed only because its source-range parser looked for the wrong function marker after `csid_isr`; the module had already built successfully and BUILD-RESULT.json had already been written. The verifier was corrected without rebuilding or changing the staged module, then passed on PiMaster and Fabric.

No module was installed or loaded, no camera node was opened, no reboot occurred and no hardware runtime action was performed.
