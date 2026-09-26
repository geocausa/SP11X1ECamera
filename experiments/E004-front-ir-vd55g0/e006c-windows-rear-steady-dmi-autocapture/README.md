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


## Runtime result — camera PASS / corpus PARTIAL / consumed

The single E006c Windows identity was consumed exactly once.

The bounded rear Color / VideoRecord / NV12 3840x2160 run passed its camera acceptance gate cleanly:

- StartAsync: Success
- elapsed: 15,309 ms
- valid 3840x2160 frame handles: 84
- StopAsync: Success
- acceptance threshold >=10: PASS

The SP7 external-KD probe remained auto-continue during the stream. The pseudo-register writemem syntax was tested before capture on harmless debugger memory. No MMIO/register write, data breakpoint or local SP11 kernel debugger was used.

The run captured two consecutive steady AC8 packets (requests 4 and 5). It also captured one 0x658 packet at request 3; that is startup and therefore does not satisfy the requested steady-658 sample. No A98 or 8F0 packet appeared within this bounded 15-second window. The identity is consumed and must not be replayed.

### Two-request AC8 payload stability

Both AC8 packets contained 16 patch records, one source mapping each, and every referenced DMI payload was fully contained in its private 0x8000 source snapshot. Raw source bytes and addresses remain private on SP7.

Exact payload hashing across the two consecutive AC8 requests divides the 16 DMI identities into 12 stable and 4 request-varying identities.

Stable: 0x3D08 selector1; 0x4308 selector3; 0x4908 selector1; 0x5F08 selectors1/2/3; 0xA008 selectors1/2; 0xA208 selectors1/2; 0xBC08 selectors1/2.

Request-varying: 0x4308 selectors1/2; 0x4708 selector1; 0x5A08 selector1.

This is the key E006c result: the rear steady materializer cannot freeze the full Windows DMI corpus as static templates. At least those four payload families require a per-request producer or independently derived equivalent. The 12 stable AC8 identities are candidates for normalized static payload templates, subject to cross-variant checks.

Cleanup completed: breakpoint removed, private log closed, target resumed, normal reboot returned protected Golden Linux, SP7 KD stopped, and overlap guard PASS.

Native rear Linux ISP remains **DENIED**.

### Next

Use a fresh identity for the still-missing A98 / 8F0 / steady-658 source windows. Require request generation >=4 for any 0x658 match so startup cannot satisfy it, and use a longer auto-continue capture window rather than manual debugger pauses. In parallel, source-trace the four proven request-varying DMI families toward their Windows IQ/3A producer so Linux does not replay stale captured bytes.
