# E006e — longer auto-continue capture for missing rear steady DMI families

Parent Git: `4ae9586b` (E006d static producer classification).

E006c passed the rear 4K camera gate with auto-continue KD but did not encounter steady `0xA98`, `0x8F0`, or a true steady `0x658` packet. E006e is a fresh single-use identity dedicated only to those missing variants.

## Capture target

At exact qccamisp8380 `DAL_ife_process_iq_packet` RVA `0x26838`:

- capture first steady MAIN `0xA98`;
- capture first steady MAIN `0x8F0`;
- capture first MAIN `0x658` only when request generation `dword(x1+8) >= 4`.

For each selected packet:

- record only a private marker and patchset in the SP7 KD log;
- derive source mapping from the live first patch record;
- privately snapshot `0x8000` bytes beginning at source mapping base + first source offset;
- ordinary/non-target hits immediately auto-continue.

No startup capture is needed.

## Runtime discipline

- SP7 is the only kernel debugger host.
- Windows is entered one-shot only; persistent Linux/GRUB Golden configuration is unchanged.
- One command breakpoint; no data breakpoints.
- No MMIO/register writes or driver mutation.
- 90-second rear Color / VideoRecord / NV12 3840x2160 camera window.
- Camera acceptance: clean Start/Stop and at least 10 valid 4K frame handles.
- Single-use marker is created atomically before camera access.
- Raw KD log, pointers, IOVAs and source bytes remain private/untracked.
- Cleanup is mandatory: clear breakpoint/log, remove one-shot task, resume, normal reboot to Golden Linux, stop KD, overlap guard PASS.

## Acceptance

Materializer corpus PASS requires all three missing steady families plus camera acceptance and full payload coverage after private reduction.

If any family is absent, the run is consumed and recorded as PARTIAL; do not replay the identity.

Native rear Linux ISP remains **DENIED**.
