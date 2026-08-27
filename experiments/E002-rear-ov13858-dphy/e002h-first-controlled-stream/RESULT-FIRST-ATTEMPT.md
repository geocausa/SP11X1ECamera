# E002h first stream attempt — BLOCKED at CSIPHY1 MMIO reset

## Runtime result

The first bounded one-frame request did not reach sensor streaming or frame transport. `v4l2-ctl` queued four buffers, then `VIDIOC_STREAMON` caused an ARM64 kernel data abort during CAMSS pipeline power-up.

Key evidence:

- output file remained zero bytes;
- `v4l2-ctl` entered uninterruptible `D` state;
- sensor runtime PM remained `suspended`, usage `0`;
- sensor MCLK1 enable count remained `0`;
- CSIPHY1 clock and CSI1 PHY timer were enabled by pipeline PM;
- kernel Oops: `Unable to handle kernel paging request` at `ffff8000810de000`;
- PC: `csiphy_reset+0x3c/0x170 [qcom_camss]`;
- stack: `csiphy_set_power -> pipeline_pm_power_one -> v4l2_pipeline_pm_get -> video_prepare_streaming`.

This mechanically places the failure before CAMSS subdev streaming and before OV13858 `s_stream(1)`.

## Root cause

The active integrated CAMSS DT maps `csiphy1` as:

`0x0ace6000 + 0x1000`

The exact X1E `csiphy-3ph-1-0` driver sets `regs->offset = 0x1000`; `csiphy_reset()` immediately writes `csiphy->base + 0x1000`. The fault therefore occurs on the first byte outside the mapped 4 KiB resource.

Independent local source evidence agrees that the window must be larger:

- Denali's standalone `phy@ace6000` node uses `<0xace6000 0x2000>`;
- SM8550/SM8650 monolithic CAMSS definitions use 8 KiB CSIPHY windows at the same address family.

## Recovery

Because the faulted userspace task was stuck in `D` state, the candidate was force-rebooted. GRUB one-shot had already been consumed, so SP11 returned to Golden v19c. Golden hashes, Wi-Fi, playback and capture were reverified.

## Next smallest experiment

E002h-r1 changes only the integrated CAMSS `csiphy1` resource size from `0x1000` to `0x2000`. Kernel, initrd, native OV13858 module, sensor mode, power sequence, link frequency, media graph, active RAW10 route and stream permission remain byte-identical.
