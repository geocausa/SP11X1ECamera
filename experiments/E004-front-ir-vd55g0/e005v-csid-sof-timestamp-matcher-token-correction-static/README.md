# E005v — correct matcher return to CSID current-SOF timestamp token

Parent Git `92c3b61b9ea5d1fb2310ed9e72f9a6690e6a0369` (E005u). This stage is a static correction on protected Golden Linux. No camera stream, reboot, debugger, module load, MMIO write or Golden mutation occurs.

## Correction to E005u

E005u correctly source-locked the BF CSID status/ACK sequence, the synchronous WM16 ADDR_STATUS0/CFG0 sample, and the six-slot key/tag matcher. It incorrectly described the first qword stored in each matcher slot as a request-associated opaque object/pointer.

The deeper type-1 source trace shows that value is not a pointer.

The type-1 normalizer at RVA `0x1B7D0` constructs normalized record `+0x30` directly from two CSID hardware registers:

- RVA `0x1B7F8` loads the mapped CSID register base;
- RVA `0x1B7FC` reads CSID `+0x398`;
- RVA `0x1B804` reads CSID `+0x39C`;
- RVA `0x1B808` inserts 24 high bits above the low 32 bits;
- RVA `0x1B80C` stores the resulting 56-bit scalar at normalized record `+0x30`.

The pinned Qualcomm camera-driver v1.0.6 CSID680 register table independently names these exact offsets:

- `timestamp_curr0_sof_addr = 0x398`
- `timestamp_curr1_sof_addr = 0x39C`

Therefore normalized record `+0x30` is the current CSID SOF timestamp token.

## Matcher meaning

The type-1 event path loads normalized record `+0x30` and passes it as installer argument x1 to RVA `0x24F60`. That installer stores the 64-bit scalar into the first free matcher slot at device `+0x2E60 + slot*0x20`.

Matcher RVA `0x25078` later requires exact FIFO key and 16-bit tag equality, then returns the corresponding first-qword slot value.

So the matcher return is:

**the CSID current-SOF timestamp token associated with the matched key/tag generation.**

It is not a request-object pointer, kernel pointer, DMA address or WM16 buffer address.

## Consequence

This correction improves the provenance model. For every accepted BF event the Windows path now gives us:

1. a real CSID BUF_DONE bit7 event with explicit same-word ACK;
2. FIFO8 key/tag;
3. synchronous WM16 ADDR_STATUS0 and CFG0 sampled after FIFO8 pop and before matching;
4. an exact key/tag-matched CSID current-SOF timestamp token.

That provides a strong generation/time identity. It still does not establish exact WM16 DMA-buffer identity or an independent WM16 BUS completion fence.

A useful next direction is to determine whether the OEM physical WM16/BUS completion path carries the same SOF/request-generation token, or otherwise has a source-defined join to this CSID timestamp. If such a join exists, it can close same-generation identity without guessing from asynchronous addresses.

Native rear processed ISP remains **DENIED** until independent WM16 completion, DMA/IOMMU quiescence and safe reuse are proven.

## Supersession

Where E005u calls the matcher return a request-associated opaque object/pointer, E005v supersedes that interpretation. E005u's BF CSID status/ACK and synchronous WM16-sample ordering remain valid.
