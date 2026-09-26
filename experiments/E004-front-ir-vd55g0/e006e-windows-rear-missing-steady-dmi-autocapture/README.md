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

## Runtime result — camera PASS / corpus PARTIAL / A98 cross-variant PASS

The E006e identity was consumed exactly once.

The first debugger command used an unsupported WinDbg `&&` expression and stopped at the first qccamisp hit. This was repaired in place with nested `.if` statements while the same single-use camera invocation remained active; the camera was not restarted and the experiment identity was not replayed.

After repair the rear 4K run completed cleanly:

- StartAsync: Success
- elapsed: 90,077 ms
- valid 3840x2160 frame handles: **592**
- StopAsync: Success
- acceptance threshold >=10: **PASS**

The corrected auto-continue probe captured steady MAIN `0xA98` at request generation 12. Its 15 patch records all use one source mapping and all 15 exact DMI payload ranges are fully covered by the private 0x8000 source snapshot.

Neither MAIN `0x8F0` nor a request>=4 MAIN `0x658` appeared during the bounded healthy capture. E006e is therefore **PARTIAL** for the three-family capture goal and must not be replayed.

### A98 cross-variant result

The 12 identities that were byte-stable across E006c's two consecutive AC8 requests are all present in A98 and **all 12 are byte-identical**:

- `0x3D08 selector1`
- `0x4308 selector3`
- `0x4908 selector1`
- `0x5F08 selectors1/2/3`
- `0xA008 selectors1/2`
- `0xA208 selectors1/2`
- `0xBC08 selectors1/2`

The A98 dynamic payloads behave consistently with E006d's producer classification:

- `0x4308 selector1/2` differ from AC8 and remain LSC/Tintless-produced;
- `0x5A08 selector1` differs and remains GTM/TMC-produced;
- A98 does not contain the `0x4708` GIC alias command.

This upgrades the 12 identities from same-variant AC8 stability candidates to **AC8↔A98 cross-variant static candidates**. It does not yet prove 8F0 or steady-658 behavior.

Cleanup completed: KD breakpoints removed, private log closed, one-shot task unregistered, target resumed, normal reboot returned protected Golden Linux, SP7 KD stopped, and overlap guard PASS.

Native rear Linux ISP remains **DENIED**.

### Next

Prefer static closure before another rare-variant Windows hunt. Source-lock the rear-visible `0xBC08` selector1/2 module and producer. If its payload contract plus existing producer proofs close the remaining 8F0/658 uncertainty, avoid another physical capture. Otherwise use a fresh identity targeted only at the residual missing payload family.
