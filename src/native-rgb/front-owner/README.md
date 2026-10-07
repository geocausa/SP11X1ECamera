# Native front completion ownership qualification

Fresh one-use identity: native-owner-20261007-02. Never rearm after consumption.
This is a prerequisite for continuous reuse, not continuous capture itself.

The isolated build requires both --nv12-trial and --front-owner-trial.
The native_front_owner_trial module parameter defaults false and requires the
NV12 diagnostic parameter too. Ordinary/rear/RAW paths retain their behavior.

The actual CSID ISR samples VFE680 ADDR_STATUS0 immediately after the existing
BUF_DONE clear, before publishing the front completion counters. No IRQ ACK or
camera-control write is added. Published Qualcomm source reads the same register
for last consumed address after IRQ handling; there is no invented pre-ACK rule.

Five completion groups cover nine WMs:
VIDEO bit0 -> WM0/1/2/3; AEC/BHist bit4 -> WM11/12; Tintless bit5 -> WM13;
AWB bit6 -> WM14; RS bit9 -> WM18.
Eight history records per group retain session epoch, exact sequence, mask and
consumed IOVAs. IRQ producer/worker reader share a spinlock. Session initialization
disarms the history, drains the IRQ, initializes history/lock, preserves the
existing counter base and publishes the session with release/acquire ordering.
The one-use NV12 latch prevents session reinitialization in this diagnostic.

Before FIFO pop, pending-bit mutation or video retirement, the actual VFE owner
checks the session, expected group sequence and each consumed WM address against
the owned slot. FULL is linear Ybase/UVbase+3686400; auxiliary addresses remain
kernel-owned coherent allocations. Wrong/stale/missing completion fails closed;
existing stop-before-free/pin-on-unsafe-stop behavior remains.

The qualification boot must produce four NV12 frames and twenty successful
address checks: four consecutive matching generations for each of five groups,
zero rejected owners, verified STREAMOFF, neutral graph, all sensor standby,
unchanged Golden assets and zero critical kernel faults. Pixel files and
original kernel logs stay root-only/private on SP11; only derived metadata is
published. Audit13 was uninstalled preparation; audit14 was the consumed owner01 failure; audit15 was uninstalled mapping preparation; audit16 uses the tested admitted BUS order for RS.

Tests use the same history/check code as the real driver: 3,242 ASan/UBSan checks,
including 96 generations per group, reused-buffer wrong IOVA, stale session,
duplicate/missing/out-of-order completion, incorrect masks, history overwrite and
sequence wrap rejection. Source composition checks also verify isolation.
Hardware qualification is still pending until a redacted result is committed.

Published authority: Qualcomm camera-driver82ac3a671a5b0a4e3b3ac4519208af1d37a93eb6,
camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe680.h and
vfe_bus/cam_vfe_bus_ver3.c. Group mapping and two-slot ownership reuse the
physically exercised SP11 front source. No raw OEM bytes/pixels are embedded.
