# E011EG: source-qualified CRT startup ordering and lowIO-to-stream handoff

The original process-attach source path now establishes the missing ordering relationship between the CRT low-level I/O producer and the standard-stream initializer. This closes the ordering gap without copying the separate E011EF `0xCC08E8` emulator state into the stream context.

On process attach, the PE entry path reaches `0xCA29D8`. Before the later constructor iterator is called, `0xCA29D8` calls `0xCA31E0`; success from that helper requires `0xCB05A8` to succeed. `0xCB05A8` passes the exact `0xF8BA20..0xF8BB20` 16-byte-pair subsystem table to original walker `0xCBAE70`. That walker advances forward through first members and only advances past a non-null initializer when it succeeds.

Pair eight is `0xCB5DD0 / 0xCB5E20`. The initializer acquires the index-seven lock, calls original `0xCC06F0` with index zero, and can report success only when that producer returns zero. Therefore any successful process-attach execution which later reaches the constructor iterator has already completed the `0xCC06F0` lowIO producer.

Only after the pre-constructor path succeeds does `0xCA29D8` invoke original constructor iterator `0xCAEDA0` over `0xF7F440..0xF7F468`. The first non-null constructor entry is `0xCB3260`. This establishes the source ordering **`CC06F0` before `CB3260`**, conditional on process attach reaching the stream initializer. It does not claim that every native Windows CRT/OS prerequisite succeeds.

E011CM already qualified the complete producer/consumer state effects under explicit owned OS contracts, and its accepted eight-case matrix was rerun during E011EG with exit zero and no stderr. In the default cases, `0xCC06F0` creates the 64 × 72-byte lowIO table at `0x16A2A90`; `0xCB3260` then uses that table while constructing the 512-entry stream vector at `0x16A2A58`, links three original static stream objects, and returns zero. Thus the startup `CC06F0 → CB3260` state handoff is now source-qualified within the inherited owned OS-contract model.

The earlier E011EF `0xCC08E8` proof remains valid but separate. It is **not** the startup producer used for this handoff and its completed state is not copied into the stream initializer. Native allocation internals, native critical-section bytes/concurrency, complete CRT startup success, native loader internals and actual Windows handle lifetime remain unqualified.

Nine bounded original-source windows are SHA-pinned by E011EG. The original DLL remains SHA-pinned, and E011CM result/bootstrap/source hashes are checked. No original instructions, raw names, decompilation or optical material are exported.

NEXT **E011EH** establishes the lifetime/order relationship from the completed startup stream state to the retained camera caller at `0xCC6120`, then qualifies the camera read of `0x16A2A58` only if the source path supports that join. File/provenance, complete helper/descriptor/profile startup, populated RS/AFD lifetime and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. Native rear runtime remains denied.

Zero camera Starts, reboots, kernel builds, production-C or PM changes were made. Golden payloads, EFI/GRUB and historical repositories remain untouched.
