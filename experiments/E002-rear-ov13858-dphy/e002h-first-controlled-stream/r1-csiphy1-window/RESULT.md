# E002h-r1 result — ACCEPTED: first native rear RAW10 frame

## Result

**PASS.** Correcting only the integrated CAMSS CSIPHY1 MMIO resource size from 0x1000 to 0x2000 removed the E002h reset Oops and allowed the unmodified native X1E CAMSS pipeline to capture one complete frame from the real Surface rear OV13858.

Native path:

`OV13858 -> CSIPHY1 -> CSID0 -> VFE0 RDI0 -> /dev/video0`

Format:

- sensor/media bus: SGRBG10 4076x2806;
- capture: packed GRBG10 (`pgAA`);
- bytes per line: 5104;
- size image: 14321824 bytes.

Capture evidence:

- `VIDIOC_STREAMON returned 0 (Success)`;
- dequeued sequence 0;
- `bytesused: 14321824`;
- timestamp source EOF;
- local frame SHA-256: `c025aaa52abe8701514cfe5bb1a938d7ca5886c3093fd3c0ebd9ce51dd987a7f`.

The raw frame itself remains local-only and is not committed.

## Payload validation

Excluding 9 bytes of per-line padding, MIPI RAW10 decoding produced exactly 11,437,256 pixels (4076x2806):

- min 52;
- max 99;
- mean 64.690;
- standard deviation 0.814;
- all 256 packed byte values present;
- packed-byte entropy 2.1914 bits/byte;
- non-constant spatial block/row statistics.

The ~64-count pedestal and low scene variance are consistent with a very dark first exposure; this does not affect the transport proof. The buffer is not zero-filled or a constant DMA artifact.

## Teardown

After normal one-frame completion/close:

- sensor runtime PM: `suspended`;
- runtime usage: `0`;
- MCLK1 enable count: `0`;
- CSIPHY1 enable count: `0`;
- CSI1 PHY timer enable count: `0`;
- all four rear sensor rails disabled in reverse order;
- Wi-Fi healthy;
- playback and capture ALSA devices healthy.

## Root-cause closure

The initial E002h Oops was caused solely by the stale integrated CSIPHY1 resource window. X1E's driver uses an internal +0x1000 register bank; a 0x1000 resource made the first reset write unmapped. With the one-cell size correction to 0x2000, the same kernel, initrd, OV13858 driver, mode, graph and stream request succeeded.

**E002 rear first-frame transport gate: ACCEPTED.**
