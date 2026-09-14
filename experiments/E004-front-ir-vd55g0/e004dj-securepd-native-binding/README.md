# E004dj — exact Qualcomm SecurePD native binding and shipped-proxy wire reuse

## Result

**PASS / OFFLINE NATIVE IMAGE BINDING CLOSED: the exact E004dg/E004dh Windows-parity camera worker now fits behind Qualcomm's already-shipped SP11 SecurePD proxy wire protocol without modifying that trusted proxy. The worker consumes the exact 96-byte `gaussian7x7_packet_t`, obtains camera-only control state from a protected HEAP prefix, binds directly to the same DSC/mapping/mailbox/thread APIs imported by shipped `example_image.so`, and remains byte-exact to the stable 644x604 Windows oracle.**

The result is still an unsigned/unadmitted ELF core. No CPZ process or protected runtime was launched and no trust-policy check was weakened.

## 1. Existing trusted proxy is reusable unchanged

`libloadalgo_skel.so` SHA-256:

`db1380cbe1e64fc21501eece86528a78efaded909262ca778769384f8a7d4a71`

Its DWARF gives the exact `loadalgo_Gaussian7x7u8` argument order:

`handle, srcFd, srcOffset, srcLen, srcWidth, srcHeight, srcStride, dstFd, dstOffset, dstLen, dstStride, heapFd, heapOffset, heapLen, mode_static`.

The implementation resolves source, destination and heap fds through `HAP_mmap_get`, constructs Qualcomm's 96-byte `gaussian7x7_packet_t`, sends exactly 96 bytes over the algorithm mailbox, then receives exactly an 8-byte completion value.

Static disassembly also proves the three offset arguments are not consumed by this shipping implementation:

- `srcOffset` arrives in input R3 but is overwritten before any read/use;
- DWARF places `dstOffset` at stack `+0x13c`, with no load/reference in the function;
- DWARF places `heapOffset` at stack `+0x14c`, with no load/reference in the function.

E004dj therefore forces all three to zero instead of pretending the proxy applies them.

`mode_static == 1` takes the built-in static-Gaussian route. The camera descriptor deliberately uses **`mode_static = 0`**, i.e. the dynamic ALGO-worker route whose admission remains trust-gated.

## 2. Camera metadata uses the protected HEAP, not ABI abuse

The proxy wire packet already carries three protected objects and geometry:

- source image handle;
- destination image handle;
- HEAP handle;
- width / height / source stride / destination stride.

The fields Windows needs beyond that are placed in a 32-byte header at offset zero of the protected HEAP:

- magic + version;
- 64-bit request ID;
- payload offset;
- captured extent;
- serialized extent;
- synthetic-fill flag.

The remainder of HEAP is the exact E004dg/E004dh SWAB scratch area.

This preserves the Windows concepts directly while keeping Qualcomm's packet layout untouched. Source/destination strides remain the real contiguous image stride and are not overloaded as control channels.

## 3. Existing proxy destination mapping remains the backing base

Because the shipping proxy ignores `dstOffset`, the SecurePD packet carries the mapped external backing base plus its declared captured length. The camera worker then applies Windows' serialized `payload_offset` itself before writing pixels, exactly as E004cf recovered from the Windows trustlet dispatcher.

Thus the Linux-native shape is:

`external protected backing base`
→ SecurePD trusted mapping
→ exact camera worker adds `payload_offset`
→ writes `Y + neutral tail`.

No HLOS mapping or copy is introduced.

## 4. Exact native Qualcomm imports

The shipping worker image `example_image.so` has SHA-256:

`e969f6bc537992689214ac1c7b47c353c7aa8bc292c924a3f2baa2fe2294ac46`.

Its DWARF/call sites recover the native signatures used by E004dj:

- `get_secure_channel_handle(dsc_feat_priv **)`;
- `dsc_verify_buffer(handle, type, paddr64, len)`;
- `secure_pd_mapping_create_64(&va32, paddr64, len, cache, permission)`;
- `secure_pd_mapping_delete_64(va32, len)`;
- `secure_pd_mb_get(mailbox, name, CREATE/RETRIEVE, id)`;
- `secure_pd_mb_receive(mailbox, buf, len, &received_len)`;
- `secure_pd_mb_send(mailbox, buf, len)`;
- `secure_pd_mb_delete(mailbox)`;
- `secure_pd_thread_create(...)`;
- `qurt_sleep(usec)`.

The image-side call sites prove:

- source/destination DSC type = `DATA (7)`;
- mapping cache mode = `QURT_MEM_CACHE_WRITEBACK (7)`;
- mapping permission byte = `3`;
- mapping deletion receives the returned 32-bit trusted VA plus length.

E004dj uses `HEAP (5)` when verifying its scratch/control object, matching the recovered `buffer_type_ext` ABI and the generic `loadalgo_physbuffer` registration path.

## 5. Mailbox and thread lifecycle matches the shipped image

The shipped Gaussian image establishes:

- `s2p_algo`: `CREATE_MB`, id `2`;
- `p2s_algo`: `RETRIEVE_MB`, id `3`;
- request size: `96` bytes;
- response size: `8` bytes;
- response semantics in the proxy: the complete 64-bit response is success iff it equals zero.

E004dj preserves that shape exactly.

Its exported `algo_main(void *)` also follows the shipping loader lifecycle: it creates a persistent worker thread and returns. The camera image uses the same shipping example stack size (**128 KiB**) and priority (`0x96`). The thread retrieves the proxy mailbox, receives one 96-byte packet at a time, runs the exact parity worker, and returns an 8-byte zero/nonzero result.

## 6. Full-frame wire differential

The exact shipped-proxy wire shape was tested with host-mocked protected mappings against the synchronized authoritative fixtures:

- geometry: 644x604 NV12;
- `GAUSSIAN_WIRE_FULL_LUMA_DIFF=0`;
- `GAUSSIAN_WIRE_NEUTRAL_TAIL_DIFF=0`.

Therefore changing from E004di's explicit camera packet to the unmodified Qualcomm 96-byte packet + protected HEAP control prefix changes **zero image bytes**.

## 7. Native Hexagon-v73 artifact

The native binding + wire adapter + exact parity worker partial-links freestanding/non-PIC for Hexagon v73:

- `.text = 9604` bytes;
- `.bss = 131072` bytes (the shipping-pattern persistent thread stack);
- SHA-256 `4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48`;
- exports `algo_main`, the worker thread, native process binding, wire processor and exact parity worker.

Its unresolved symbol set is **exactly ten symbols**, all present as imports in the shipped Qualcomm worker:

`dsc_verify_buffer`
`get_secure_channel_handle`
`qurt_sleep`
`secure_pd_mapping_create_64`
`secure_pd_mapping_delete_64`
`secure_pd_mb_delete`
`secure_pd_mb_get`
`secure_pd_mb_receive`
`secure_pd_mb_send`
`secure_pd_thread_create`

There is no libc, generic OS, FastRPC, camera-MMIO, HLOS-copy or signature-bypass dependency in the image core.

## 8. Host/proxy call descriptor

`sp11_loadalgo_camera_build_call()` mechanically constructs the already-shipped proxy call:

- real source/destination/heap fds;
- real geometry and contiguous strides;
- destination length = Windows/E004db captured extent;
- HEAP length sufficient for the 32-byte control plus exact SWAB scratch;
- all ignored offsets = `0`;
- `mode_static = 0`.

It does not invoke FastRPC or SecurePD. It exists to prevent future glue from silently relying on an offset behavior the shipping proxy does not implement.

## What remains blocked

The **mechanical image and invocation ABI is now closed**. A source-built parity worker can be represented as the same kind of `algo_main` SecurePD image used by Qualcomm and can communicate through the existing trusted proxy without a new proxy protocol.

The remaining blocker is still E004de/E004df's independent trust requirement: the production dynamic loader must legitimately accept the camera worker image. E004dj does not provide or fabricate an OEM signature/static-hash credential and does not patch the verifier.

Once legitimate admission exists, the next protected-runtime steps are already bounded by E004db/E004da: map/register the protected objects, invoke through the existing proxy, wait for the zero completion response, unmap/detach, then reclaim ownership.

## Safety boundary

Golden FullIO v19c stayed active. No one-shot Windows boot was needed because the open questions were entirely covered by exact shipping Hexagon binaries with DWARF and existing authoritative Windows pixel fixtures. No FastRPC ioctl, CB9 enable, ownership transition, CPZ migration, mailbox creation, protected mapping, camera runtime, firmware modification, signature patch, or Linux SecureISP runtime action occurred.

## Next gate

Return to whole-stack parity and attack the next non-admission gap that is independently actionable. The SecurePD camera worker route should remain frozen at this closed offline checkpoint until a legitimate production trust path exists; do not weaken it merely to obtain runtime output.
