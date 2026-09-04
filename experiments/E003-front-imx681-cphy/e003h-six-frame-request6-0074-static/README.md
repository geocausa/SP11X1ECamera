# E003h 0074 bounded six-frame request6 static candidate

Static extension of the accepted 0072 five-frame IQ-provider path.

## Intended runtime delta

- Preserve request4 startup/bootstrap and all accepted sensor/CSIPHY/CSID/VFE/RT-CDM programming.
- Preserve the two-slot V4L2 ownership model.
- Keep accepted request5 delivery through the owned monotonic IQ FIFO.
- Add exactly one subsequent request6 FIFO packet and one sixth QC10C frame.
- Expected V4L2 index order is exactly `[0,1,2,3,0,1]`.
- Requeue buffer0 after sequence0 and buffer1 after sequence1; request5 reuses slot0/buffer0 and request6 reuses slot1/buffer1.
- Request IDs are parsed/materialized fail-closed as exactly `4 -> 5 -> 6`.
- Request6 uses the fresh atomic Windows-derived R6 capsule checkpointed by 0073; no IQ bytes are invented.

No DT, sensor, CSID, VFE register recipe, IRQ recipe, startup/priming sequence, or unrelated MMIO change is part of 0074. This directory is static evidence only and does not itself authorize hardware execution.
