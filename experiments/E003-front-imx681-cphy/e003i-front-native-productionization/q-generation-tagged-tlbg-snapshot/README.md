# E003i-Q — generation-tagged live TL_BG snapshot

Status: **static PASS; runtime not yet performed**.

E003i-P dynamically proved that every observed Windows Tintless call consumes the immediately preceding Titan680 TL_BG parser output, while parser generations 82, 84 and 104 were superseded before any Tintless call. That means an unlabeled "latest stats" buffer or parser-count/request FIFO would be an incorrect production contract. This checkpoint therefore adds an explicit latest-completed **generation-tagged** snapshot to the existing Linux front-PIX V4L2 surface.

## Contract

The existing VFE680 front PIX path already owns coherent TL_BG DMA for BUS client 13 and its independent completion group. No new statistics engine, MMIO access, IRQ programming, DMA allocation strategy or camera register value is introduced here.

For each of the bounded six frame generations, after `csid680_x1e_front_poll_all_done()` proves the target completion generation and **before** `vfe680_x1e_pix_runtime_retire_aux()` can release/reuse that slot, the runner copies exactly the first `0x25800` bytes from the still-owned TL_BG coherent buffer into a private per-video-node snapshot.

The front PIX node gains one read-only volatile compound V4L2 control, `V4L2_CID_USER_BASE + 0x1241`. Its payload is 153,632 bytes:

- 32-byte little-endian header
- 153,600 (`0x25800`) raw Titan680 TL_BG bytes

Header v1 fields are: magic `TLBG`, header size, monotonic snapshot generation, **source completion generation**, slot, raw byte count and flags. The 32-byte header size is compile-time asserted. Before the first completed snapshot, reads fail with `-EAGAIN`.

`source_seq` is a TL_BG/BUF_DONE completion generation for the current stream. **It is not a camera request ID and must not be converted into one using the historical four-request inference.** The numerical request-delay mapping remains open.

The control is latest-only by design. A userspace consumer compares `generation`; skipped values mean an intermediate completed snapshot was superseded before it was read, matching the observed Windows producer/consumer behavior.

## Static proof

- exact patch: `0011-media-qcom-camss-expose-generation-tagged-tlbg.patch`
- strict source checkpatch: 0 errors / 0 warnings / 0 checks (only raw-diff commit-message/sign-off diagnostics explicitly excluded)
- patch forward and reverse round-trip: byte-exact PASS against the five source files
- new direct MMIO reads: **0**
- new direct MMIO writes: **0**
- six publication sites: exact source generations `+1..+6`, slots `0,1,0,1,0,1`
- every publication is ordered after its completion gate and before aux retirement
- final module SHA256: `ed027c0c1632a7cb16f7449134be40fa00ff53d469f23431a203940920673a24`
- module srcversion: `27658434020B2FE51CBB0DA`
- Golden vermagic exact: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

`inspect-generation-tagged-tlbg.py` fails closed on patch/source/module hashes and mechanically checks the lifetime ordering, V4L2 read-only contract, exact byte counts and absence of new MMIO access.

## Safety boundary / next gate

This checkpoint does **not** install the module, arm GRUB or authorize/claim a camera runtime. The next step is a distinct Golden-safe one-shot package using this exact module, followed by package inspection and a separate bounded runtime checkpoint. Runtime should read the new control through the existing exclusive front-PIX fd and verify generation/source sequence plus Linux Titan680 parsing before any live R5/R6 IQ use.
