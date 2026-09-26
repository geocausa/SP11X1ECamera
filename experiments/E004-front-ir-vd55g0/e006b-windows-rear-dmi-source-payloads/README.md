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

## Runtime result — consumed / PARTIAL, no replay

The single E006b Windows identity was consumed exactly once.

Camera control itself reached StartAsync=Success and StopAsync=Success, but the manual startup/KD inspection pauses stretched the streaming interval to 54,302 ms and no valid 3840x2160 frame handles were delivered. The predeclared >=10-frame acceptance criterion therefore failed. This run is PARTIAL and must not be replayed under the same identity.

Useful evidence was nevertheless captured before stopping:

- all four rear startup MAIN packets: 0xF1C, 0xEBC, 0xA00, 0x658;
- one real rear steady 0xAC8 packet;
- exact live KMD patch-record counts: 17, 16, 10, 3, 16 respectively;
- exact patch-record destination fields join one-for-one to E006a's decoded DMI address fields;
- private source payload windows were captured and reduced to DMI identity / selector / length / SHA-256 only;
- the steady 0xAC8 source references independently fit inside one 0x8000 source window.

The reduction found 18 DMI identities across the captured phases. Stable identities include 0x3D08/1, 0x4308/3, 0x4908/1, 0x5F08/1..3, 0xA008/1..2, 0xA208/1..2, and rear 0xBC08/2. Captured phase-dependent payload changes were observed for 0x4308 selectors1/2, 0x4708 selector1, 0x5A08 selector1, and rear-specific 0xBC08 selector1. These variations are evidence that one captured DMI payload must not be frozen globally.

Missing steady families remain 0xA98, 0x8F0 and steady 0x658. Rear materializer completion and native rear Linux ISP remain DENIED.

Cleanup completed: all breakpoints removed, private log closed, one-shot Windows task unregistered, target resumed, SP11 normally rebooted to protected Golden Linux, SP7 KD stopped, and overlap guard PASS.

### Next

Use a fresh Windows identity with an auto-continue-only steady DMI oracle. Do not manually stop the kernel during the camera stream. Automatically snapshot the private source window on first occurrences of 0x8F0, 0xA98 and steady 0x658 (and preferably a second sample for variation classification), then reduce after the run on Golden Linux.
