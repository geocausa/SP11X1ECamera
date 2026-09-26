# E006c — auto-continue rear steady DMI source-window oracle

Parent Git: 15bad8ea (E006b partial).

E006b captured every startup DMI source payload plus one steady 0xAC8 source window, but manual KD pauses destroyed camera acceptance. E006c removes human-paced debugger stops from the stream entirely.

## Goal

Capture private source windows and patch records for:

- two independent steady 0xAC8 samples, to classify same-variant payload stability;
- first steady 0x8F0;
- first steady 0xA98;
- first steady 0x658.

No startup breakpoint is required; E006b already captured all four startup packets.

## Source-locked breakpoint

Use exact same-SP11 qccamisp8380.sys RVA 0x26838, DAL_ife_process_iq_packet.

At the entry:

- MAIN bytes = dword(x1 + 0x84 + dword(x1 + 0x18))
- patch count = dword(x1 + 0x2c)
- patchset = x1 + 0x74 + dword(x1 + 0x28)
- first source handle = qword(patchset + 0x0c)
- source CPU mapping base = qword(first_source_handle + 0x08)
- first source offset = dword(patchset + 0x14)

For each selected packet the debugger will privately dump exactly 0x8000 bytes beginning at CPU mapping base + first source offset. Post-run reduction must prove every referenced payload lies inside that window; otherwise that sample fails closed.

## Runtime discipline

- SP7 external KD only.
- Direct EFI Windows BootNext only.
- Before camera trigger, syntax-test pseudo-register based .writemem on harmless debugger memory.
- One command breakpoint only; all ordinary hits end in gc.
- Private KD log contains patchset/address data and never enters Git.
- Private source windows never enter Git.
- Camera role: rear Color / VideoRecord / NV12 3840x2160.
- Clean Start/Stop and >=10 valid handles required.
- No MMIO writes, data breakpoints, driver mutation or local SP11 debugger.
- Single-use camera trigger.
- Cleanup: clear breakpoint/log, remove task, resume, normal reboot to Golden, stop KD, overlap PASS.

## Acceptance

The run is useful for materializer closure only if:
- camera acceptance passes;
- requested steady families are captured;
- each captured patchset joins exactly to E006a DMI fields;
- every patch source range is contained in its private 0x8000 snapshot;
- raw addresses and bytes remain private.

Native rear Linux ISP remains DENIED.
