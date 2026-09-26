# E006b — bounded Windows rear DMI source-payload oracle

Parent Git: 6eb47df0 (E006a structural decode).

## Purpose

E006a closed the rear selector-2 RT-CDM command topology but deliberately left DMI payload ownership unresolved. E006b captures the CPU-visible source payloads that the exact same-SP11 OEM KMD uses to patch DMI addresses into the rear command lists.

Raw payload bytes, kernel pointers, CPU VAs and IOVAs remain private/untracked. Git receives only payload identity, selector, byte length, hashes, variation classification and source-locked offset relationships.

## Source-locked capture contract

Exact qccamisp8380.sys SHA-256:
64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c

The already-accepted front oracle mechanically proved the packet patch-record ABI and is reused without assuming front payload contents:

- IQ packet entry: qccamisp RVA 0x26838 (DAL_ife_process_iq_packet).
- Main BL shape: dword at x1 + 0x84 + dword(x1 + 0x18).
- Patch-record count: dword(x1 + 0x2c).
- Patchset start: x1 + 0x74 + dword(x1 + 0x28).
- One patch record is 0x18 bytes.
- Source handle is the qword at patch-record + 0x0c.
- Source offset is dword at patch-record + 0x14.
- Source mapping record contains CPU VA at source_handle + 0x08.
- Therefore one patch source byte is CPU_VA(source_handle) + source_offset.

The observed front 0x8000 slot/ring geometry is NOT assumed as Linux ABI. During this Windows oracle it is only used if this rear run independently shows the same allocator relationship.

Startup DEVICE_START packet source mapping remains independently observable at RVA 0x16094 using the same patch-record ABI.

## Runtime

- SP7 is the only kernel debugger host.
- Direct EFI BootNext 0006 only. Persistent BootOrder and GRUB saved entry are unchanged.
- One fresh single-use rear Surface Camera VideoRecord NV12 3840x2160 trigger.
- Target capture length is extended enough to tolerate debugger pauses; acceptance still requires clean Start/Stop and at least 10 valid handles.
- Capture startup source windows and representative steady source slots for rear MAIN families 0xAC8, 0xA98, 0x8F0 and 0x658.
- For each representative, inspect patch records first; derive source CPU mapping from the live source handle. Do not guess CPU VA from a previous run.
- Prefer private .writemem binary capture to text dumps.
- No MMIO write, data breakpoint, driver mutation, or local SP11 kernel debugger.
- Every run identity is single-use.
- Cleanup is mandatory: clear breakpoints, close log, remove one-shot task, resume, normal reboot to Golden Linux, stop SP7 KD, overlap guard PASS.

## Fail closed

Do not construct a rear materializer if:
- a referenced DMI identity has no source payload;
- a source offset is guessed rather than observed;
- source bytes do not cover the exact DMI payload length;
- repeated samples show unexplained variation;
- startup or steady payload identity cannot be joined to an E006a DMI command.

Native rear Linux ISP remains DENIED.
