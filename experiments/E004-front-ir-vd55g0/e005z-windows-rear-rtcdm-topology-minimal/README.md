# E005z — bounded Windows rear RT-CDM selector-2 topology oracle

Parent Git: `c98de86d`.

## Question

Does the same-machine Windows rear VideoRecord NV12 3840x2160 path use the already-proven qccamisp selector-2 RT-CDM queue contract, and what are the startup/early-steady BL record-count and byte-length vectors?

This is intentionally a topology-only oracle. It does not dump DMI payloads or bulk command bytes on the first run.

## Exact source-locked anchors

Exact same-SP11 `qccamisp8380.sys` SHA-256:

`64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`

The selector-2 consumer at RVA `0x28480` receives one queued batch. For selector 2:

- `0x287A4` loads the batch record count from stack `+0x50`;
- `0x287CC` fixes one queue record at 0x28 bytes;
- `0x287D0..0x287DC` addresses and copies one record;
- after `0x287EC` the stack copy exposes:
  - `sp+0x20`: hardware BL IOVA (u32)
  - `sp+0x28`: mapped CPU alias (u64)
  - `sp+0x30`: encoded length (u32, bytes minus one)
  - `sp+0x38`: extra qword
  - `sp+0x40`: final qword
- `w24` is the record index in the current batch.
- FIFO0 commit remains `0x28884 / 0x2888C / 0x28894`.

The earlier front oracle proved four startup batches followed by five-record steady batches. E005z does **not** assume rear shares those values.

## Runtime plan

- SP7 is the only kernel debugger host.
- One-shot direct Windows BootNext on SP11; persistent Linux/GRUB default remains unchanged.
- Recompute all absolute breakpoints from the current qccamisp module base.
- Use one auto-continue command breakpoint after the record stack copy.
- Maintain only debugger-local counters.
- For each record print: bounded batch counter, index, batch count and encoded byte length. Do not print raw pointers/IOVAs.
- Stop recording after a bounded number of batches sufficient to include startup and early steady state; breakpoint becomes disabled/cleared rather than emitting indefinitely.
- Run one bounded rear Surface Camera Color / VideoRecord / NV12 3840x2160 capture.
- Camera acceptance: clean Start/Stop and >=10 valid handles.
- No MMIO/register write, no data breakpoint, no driver mutation, no local SP11 kernel debugger.
- Raw KD log stays private on SP7.
- Cleanup: clear breakpoints, close log, remove one-shot camera task, continue target, normal reboot to protected Golden Linux, stop KD, run overlap guard.

## Interpretation

- If rear startup/steady record-count and length vectors differ from front, create a separate rear command/capsule materializer.
- If the topology matches front, use a second targeted oracle to capture only the rear-specific command/DMI state needed to populate the existing generic transport/capsule ABI.
- A topology match alone does not authorize reusing front IQ/tuning bytes.

No Linux rear ISP runtime is authorized by this experiment.
