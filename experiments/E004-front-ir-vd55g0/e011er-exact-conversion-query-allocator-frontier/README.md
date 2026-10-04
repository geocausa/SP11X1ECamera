# E011ER: exact conversion query to allocator frontier

Status: **PASS_EXACT_CONVERSION_QUERY_TO_ALLOCATOR_FRONTIER**.

E011ER extends the accepted E011EQ query arguments with an exact bounded Windows/NTDLL conversion contract for this specific source: 37 ASCII bytes plus NUL, 38 bytes total. The original query path receives codepage selector 0, flags 9, input count -1, null output pointer and zero output capacity, and the original API machinery returns 38 UTF-16 characters. This implies an exact next allocation request of 76 bytes.

The contract is not borrowed from the older 37-byte-including-NUL case: this exact 38-byte input was run independently through the accepted original API machinery. The bounded query executes 373 original API instructions with no size/result stub, independently matches the UTF-8/UTF-16 outcome, restores callee-saved registers/SP, and preserves the complete owned-page/permission model.

Four retained camera placements then replay the joined original chain through the query return and stop immediately before original `0xCB16C0` executes. They reject 612 altered contracts total. Selected object/output state remains unchanged; the selected logical lock remains held and the index-8 global lock remains released. No camera Start, reboot, kernel build, production-C or PM change is required.

This does **not** qualify the native allocator implementation, converted output buffer, live Windows default-codepage/locale policy, or general error paths.

NEXT **E011ES** qualifies the exact 76-byte `0xCB16C0` allocation under the inherited owned process-heap contract and only then advances to the second conversion/output phase. Native rear runtime remains denied; front retirement/IRQ/DMA/IOMMU gates remain open.
