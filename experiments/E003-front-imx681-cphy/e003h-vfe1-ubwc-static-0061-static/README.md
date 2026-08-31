# E003h 0061 — VFE1 UBWC static parity

Bounded X1E80100 VFE1-only candidate justified by consumed 0060 and exact qccamisp ownership proof. It adds one MMIO write before BUS client configuration/enable: VFE1 BUS common `+0xc58 = 0x00001046`. Existing 0060 read-only telemetry remains intact. No sensor, CSID, CSIPHY, RT-CDM, DT, clock, client contract, buffer address, IRQ mask, or event-pacing change.
