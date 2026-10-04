# E011ES: exact allocator, output conversion and CB76B0 return

Status: **PASS_EXACT_ALLOCATOR_OUTPUT_CONVERSION_RETURN**.

E011ES continues E011ER's exact 38-character query result through original `0xCB16C0`. The original allocator reads the already source-qualified process-heap handle, requests exactly 76 bytes with flags zero under the inherited owned HeapAlloc contract, and returns an owned guarded buffer. The second original conversion call then consumes the same 38-byte NUL-terminated ASCII source and produces the independently verified 76-byte UTF-16 result.

The exact output path was independently rerun through the accepted original Windows/NTDLL machinery: 468 original API instructions, 55 original write chunks, original NTDLL entry executed, no size/conversion-result stub, exact 38-character return and independently matching UTF-16 bytes.

Four retained camera placements execute the allocator, second conversion and complete original `0xCB76B0` return with status zero. They reject 736 altered contracts total. The selected object remains unchanged, the selected logical lock remains held, and the index-8 global lock remains released. Execution stops at the parent `0xCFD4E8` boundary. No camera Start, reboot, kernel build, production-C or PM change was required.

This does **not** qualify the native Windows heap implementation, live locale/default-codepage policy, general failure paths, `0xCFD570`, or the enclosing parent return.

NEXT **E011ET** resumes the original parent from `0xCFD4E8`, qualifies exact post-conversion cleanup/call setup, and stops at the first new dependency. Native rear runtime remains denied; front IRQ/exact-buffer/generation/DMA/IOMMU retirement remains open.
