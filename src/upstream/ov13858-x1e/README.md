# OV13858 (rear) on the Snapdragon Surface Pro 11: device tree support

The in-tree `ov13858` driver was written for ACPI machines. Sergey Lebedev's
patch "media: i2c: ov13858: add regulator, clock and reset GPIO handling"
v3 (Message-ID `20260831130312.26296-1-lsa.uz@pm.me`) adds power sequencing.
We need that patch too, and it is the base here. On top of it, our series
adds:

- `0001` dt-bindings: new `ovti,ov13858.yaml`: three supplies, a
  19.2 MHz clock, the reset GPIO, and one four-lane D-PHY endpoint with
  link-frequencies. MAINTAINERS lists it.
- `0002` driver: an OF match table and an endpoint check, the way ov08x40
  does it. It defers until a bridge creates the endpoint, requires four
  lanes, and requires both link frequencies (540 and 270 MHz, which the
  modes switch between).

No new register values. The in-tree mode tables at 540 MHz work on the SP11
as they are. Our daily stack's 592.8 MHz Windows-derived PLL is not needed
upstream.

## Tested (2026-10-15, SP11 X1E80100, kernel 7.1.5 + camss module 50)

The test used the lab boot entry (`../imx681-x1e/lab/make-lab.py` plus
`lab/make-lab-rear.py`). The rear endpoint was
`link-frequencies = /bits/ 64 <540000000 270000000>` and MCLK was assigned
19.2 MHz. The source tested was mainline `ov13858.c` (62f482f), Sergey's v3
and ours, and it is identical to the patches. Raw RDI capture went
`ov13858 -> msm_csiphy1 -> msm_csid0 -> msm_vfe0_rdi0`:

- 4224x3136 SGRBG10 at 29.95 fps;
- colour bars intact;
- scene captures.

Other checks:

- W=1 -Werror and checkpatch --strict clean;
- `dt-doc-validate` clean;
- `dt-validate` passes the example and rejects two lanes.

## Sent

Sent 2026-10-15 by George Neacsu through the kernel.org b4 web endpoint, as
"[PATCH 0/2] media: ov13858: device tree support for the Surface Pro 11
(Snapdragon)", Message-ID `20261015-ov13858-x1e-v1-0-acdd918f4fb6@gmail.com`.
It went to Sakari Ailus, with Cc to the media/DT maintainers, Sergey
Lebedev, German Pablo Lindo, Bryan O'Donoghue, linux-media, devicetree,
linux-arm-msm and LKML. The content of `patches/*.eml` is as sent; only
the dates and signatures differ. The working tree is the b4 branch
`ov13858-x1e` in `06-camera/linux-sparse` on SP11, which b4 has moved to v2.
