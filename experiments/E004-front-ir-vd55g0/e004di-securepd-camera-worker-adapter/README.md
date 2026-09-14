# E004di — SecurePD camera parity worker image adapter

## Result

**PASS / OFFLINE IMAGE-INTEGRATION CLOSED: the exact E004dg/E004dh Windows-parity worker is now wrapped in the same protected-buffer execution shape proven by Qualcomm's shipped SP11 SecurePD example. The adapter uses the recovered typed `{paddr,len,type}` buffer identity, verifies every protected range before mapping, maps source/destination/scratch only inside the trusted worker, runs the exact camera parity transform, unmaps in reverse order, and reports a bounded completion result. The full 644x604 SecurePD-shaped path remains byte-exact to the stable Windows oracle.**

This is still an unsigned, unadmitted offline artifact. Nothing was loaded into CDSP/CPZ and Linux SecureISP runtime remains unauthorized.

## Same-machine authority carried forward

E004dc recovered Qualcomm's SP11 SecurePD ABI directly from the shipped debug-bearing modules:

- `loadalgo_packet_t = { uint32_t paddr, uint32_t len, int32_t type }`, exactly 12 bytes;
- buffer types `ALGO=4`, `HEAP=5`, `POOL=6`, `DATA=7`, `STATIC_EXEC=8`;
- trusted worker flow verifies protected ranges with DSC before `secure_pd_mapping_create_64`;
- source/destination mappings are deleted before mailbox completion.

E004di does not invent a second protected-buffer identity. Its camera packet embeds three exact 12-byte SecurePD buffer descriptors: source DATA, destination DATA, and later-request HEAP scratch.

## Camera work packet

`sp11_securepd_camera_packet` is exactly **80 bytes**:

- version + flags;
- source `{paddr,len,DATA}`;
- destination `{paddr,len,DATA}`;
- scratch `{paddr,len,HEAP}`;
- width / height;
- source / destination stride;
- payload offset;
- captured extent;
- serialized extent;
- 64-bit request ID.

The adapter intentionally requires `src_stride == dst_stride == width`, matching the contiguous Windows transfer worker recovered in E004cf rather than silently inventing stride semantics.

## Trusted mapping lifecycle

The image-side adapter is parameterized by three platform callbacks whose semantics match the shipped SecurePD worker:

1. `verify(paddr,len,type,access)`;
2. `map(paddr,len,access) -> trusted_vaddr`;
3. `unmap(trusted_vaddr,len)`.

Execution order is fail-closed:

`validate packet`
→ `verify src/dst[/scratch]`
→ `map src`
→ `map dst`
→ `map scratch if request >= 10`
→ `sp11_parity_worker_run()`
→ `unmap scratch`
→ `unmap dst`
→ `unmap src`
→ report completion.

A verification failure maps nothing. A partial mapping failure cleans up every prior mapping. An unmap failure is surfaced even after successful pixel processing.

The 16-byte result separates adapter status, parity-worker status, and cleanup status so a future mailbox thread can distinguish transform failure from trusted-mapping cleanup failure.

## Exact Windows transform remains intact

The adapter does not contain a substitute algorithm. It calls the committed E004dg parity worker, which composes the byte-exact E004dh SWABF/SWASF implementation for request IDs >= 10.

Host mock tests cover synthetic, early copy and later SWAB paths plus validation, verification failure, partial-map cleanup and unmap failure.

The full 644x604 adapter differential uses the synchronized raw Windows fixture and reports:

- `SECUREPD_ADAPTER_FULL_LUMA_DIFF=0`;
- `SECUREPD_ADAPTER_NEUTRAL_TAIL_DIFF=0`.

So adding the protected-worker packet/mapping boundary changes **zero output bytes**.

## Hexagon-v73 image artifact

The adapter + exact parity worker + SWABF + full SWASF + tuning is compiled freestanding/non-PIC for Hexagon v73 and partial-linked into one relocatable:

- `.text = 9220` bytes;
- zero unresolved symbols;
- SHA-256 `a6540c007df1c35173399a1589505555e69358b912c519818388290be43d26c6`;
- key exported symbols include `sp11_securepd_camera_process_packet`, `sp11_parity_worker_run`, `sp11_swabf_reference`, and `sp11_swasf_reference`.

This is the algorithm/image core a legitimate admission/signing route could package. It deliberately does not fake production signatures or patch SecurePD verification.

## What is still missing

The remaining image-side mechanical step is a thin binding from these callback semantics to the exact shipped Qualcomm SecurePD imports (`get_secure_channel_handle`, `dsc_verify_buffer`, `secure_pd_mapping_create_64`, `secure_pd_mapping_delete_64`) and mailbox receive/send ABI. The shipped module retains DWARF for those declarations, so that can be recovered statically without executing CPZ.

Even after that binding is complete, **production trust admission remains independently blocked** by E004de/E004df unless a legitimate accepted signing/static-hash route becomes available.

## Safety boundary

SP11 remained on Golden FullIO v19c. No Windows boot was required for this gate because the relevant output behavior and SecurePD architecture were already closed by preserved authoritative artifacts. No CB9, FastRPC ioctl, ownership transition, CPZ migration, protected mapping, camera runtime, firmware change, verification patch or Linux SecureISP runtime occurred.

## Next gate

**E004dj — exact Qualcomm SecurePD import/mailbox binding, offline/static only.**

Recover the precise parameter semantics and constants for the four trusted mapping imports and mailbox receive/send calls from the shipped `example_image.so` DWARF + call sites, then compile a thin binding layer around E004di. Do not load it and do not weaken admission policy.
