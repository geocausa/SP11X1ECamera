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


## Runtime result — consumed / PASS

The single E005z Windows attempt was consumed exactly once.

Rear Surface Camera Color / VideoRecord / NV12 3840x2160 completed cleanly:

- StartAsync: Success
- elapsed: 8,055 ms
- valid 3840x2160 frame handles: 55
- StopAsync: Success
- acceptance threshold >=10: PASS

The external-SP7 KD selector-2 probe positively hit the same source-locked queue consumer used by the front oracle. Raw debugger state remained private; the committed reduction contains only batch record counts and byte lengths.

The intended debugger self-clear at batch 21 did not take effect while executing its own command breakpoint. The probe was manually interrupted and cleared after 33 batch headers; 32 complete batches were retained. This does not invalidate the topology result, but the run identity is consumed and must not be replayed.

### Rear topology observed

Startup / first four batches:

- batch 1: 4 BLs = 0x4, 0xF1C, 0x4, 0x3C
- batch 2: 6 BLs = 0x4, 0xEBC, 0xC, 0x4, 0x10, 0x14
- batch 3: 6 BLs = 0x4, 0xA00, 0xC, 0x4, 0x10, 0x14
- batch 4: 6 BLs = 0x4, 0x658, 0xC, 0x4, 0x10, 0x14

Early steady-state batches remain 6-BL vectors of the form:

0x4, MAIN, 0xC, 0x4, 0x10, 0x14

with MAIN variants observed in the bounded sample:

- 0xAC8
- 0xA98
- 0x8F0
- 0x658

### Direct comparison with canonical front corpus

Canonical front startup:

- 4 BLs = 0x4, 0xE94, 0x4, 0x3C
- 5 BLs = 0x4, 0xE34, 0x4, 0x10, 0x14
- 5 BLs = 0x4, 0x904, 0x4, 0x10, 0x14
- 5 BLs = 0x4, 0x4E8, 0x4, 0x10, 0x14

Canonical front steady state is always 5 BLs:

0x4, MAIN, 0x4, 0x10, 0x14

with front MAIN variants 0x958, 0x868, 0x83C, 0x6B8 and 0x5A4.

Therefore rear and front are structurally different command corpora. From rear batch 2 onward, rear adds a persistent 0xC BL that the front corpus does not have, and the observed rear main-list sizes are different.

This decisively rejects reusing the front 36-section corpus as a rear template with only sensor-specific tuning substitutions.

Cleanup completed: all breakpoints were removed, private KD logging closed, the one-shot Windows task unregistered, SP11 rebooted normally to protected Golden Linux, and the SP7 KD job was stopped.

## Next

Build a dedicated rear command-corpus oracle/materializer. A second targeted Windows capture should dump exact bytes only for:

1. the four rear startup batches;
2. the persistent 0xC BL;
3. one representative instance of each observed rear steady MAIN variant;
4. the fixed 0x4/0x10/0x14 wrapper lists as needed for identity comparison.

Then decode commands/DMI references using the already-proven front CDM parser, normalize relocatable addresses, and construct a separate rear capsule schema. Do not reuse front IQ bytes by assumption.
