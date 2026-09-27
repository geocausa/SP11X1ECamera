# E008g — rear startup-batch and Linux physical stream-order static correlation

Parent Git: bc5a1096e6982d8ef61b5e812d47e56d205a77a8 (E008f).

Status: STATIC CORRELATION PASS / NO BUILD / NO CAMERA / NO REBOOT.

## Why this checkpoint exists

E008f source-locked two selector-2 call sites and the relative BUS/CSID event
order, but deliberately stopped short of assigning every observed RT-CDM
batch to E007y's four startup packets. It also did not instrument Windows
CSIPHY/sensor stream-on.

This checkpoint closes both questions from already accepted evidence. It does
not perform another Windows boot and does not make rear native runtime
reachable.

## Pre-CSID selector-2 owner

The exact installed qccamisp8380.sys, SHA-256
64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c,
has a runtime function beginning at RVA 0x246f0. Its first diagnostic string
is exactly:

CSID%d DAL_csid_process_iq_packet cslPacket %#p, requestId %d

Inside that function RVA 0x24918 loads selector 2 and RVA 0x2491c calls
the shared RT-CDM dispatcher RVA 0x28480. This is E008f
CALL_A_SELECTOR2.

The separate E008f CALL_B_SELECTOR2 is RVA 0x25ec8. Prior exact-driver
source locking places that call in IFE Epoch0, after the BUS address-update
wrapper. It is the steady request consumer.

## Exact rear batch mapping

E005z already established that the first four rear selector-2 batches are
the startup corpus:

| logical startup batch | BL vector |
| --- | --- |
| 1 | 0x4 / 0xF1C / 0x4 / 0x3C |
| 2 | 0x4 / 0xEBC / 0xC / 0x4 / 0x10 / 0x14 |
| 3 | 0x4 / 0xA00 / 0xC / 0x4 / 0x10 / 0x14 |
| 4 | 0x4 / 0x658 / 0xC / 0x4 / 0x10 / 0x14 |

E006a uses the same selector-2 post-copy site RVA 0x287f0 and explicitly
defines capture_n as the zero-based batch index. Its startup entries
capture_n=0..3 have MAIN sizes 0xF1C,0xEBC,0xA00,0x658 and DMI counts
17,16,10,3.

E007y materializes exactly four packets with those same MAIN sizes and DMI
counts. Therefore E008f's zero-based BATCH 0..3 map directly to E007y
packets 0..3:

- E008f BATCH0 / logical batch1 / E007y packet0 is consumed by
  DAL_csid_process_iq_packet before BUS configuration.
- E008f BATCH1 / logical batch2 / E007y packet1 is consumed by the same CSID
  DAL call after BUS config+enable+initial addresses and before CSID start.
- E008f BATCH2 / logical batch3 / E007y packet2 is consumed by the first
  post-ISP_START_DONE Epoch0 selector-2 call.
- E008f BATCH3 / logical batch4 / E007y packet3 is consumed by the next
  Epoch0 selector-2 call.
- E008f BATCH4 is already beyond the four-packet startup corpus and is the
  steady-state boundary.

This also means the accepted front native runner's all-four-startup-packets
before-CSID-enable order must not be copied to rear.

## Linux CSIPHY1 / OV13858 ordering

The ordinary CAMSS video_start_streaming() path walks from the video sink
upstream and invokes each subdevice s_stream(1) in that order. On the
accepted rear RAW graph this establishes the physical source-side relative
order CSIPHY1 -> OV13858.

E004lr physically exercised that ordinary Linux rear path: OV13858 delivered
six complete 4076x2806 SGRBG10_CSI2P frames, STREAMON/STREAMOFF completed,
the graph returned neutral, IR readback remained stream=0 illumination=0,
and Golden was restored.

For a future rear PIX runner, the safe Linux-owned source activation order is
therefore:

CSID1 IPP enable -> CSIPHY1 s_stream(1) -> OV13858 s_stream(1)

The first edge uses the same downstream-to-upstream CAMSS ownership model as
the accepted custom front PIX runner; the final CSIPHY1 -> OV13858 edge is
already physically proven on this SP11. This is a Linux safety/control-order
conclusion, not a claim that Windows uses the same PHY/sensor call order.

## Remaining gate

E008e shows address activity after ISP_START_DONE and before later
selector-2 batches. E008d owns only one complete ten-WM allocation set.
Before assembling a live-capable rear runner, the next checkpoint must close
the initial DMA prime depth / second-slot ownership question and ensure an
in-flight first frame can never have its ten output addresses reused.

No new Windows boot is justified for startup-batch identity or
CSIPHY1/OV13858 relative ordering.
