# IMX681 on the Snapdragon Surface Pro 11: C-PHY support for the upstream driver

Upstream step 1 of the SP11 camera work. Instead of a competing driver, these
patches extend the IMX681 driver that is already under review:

- **Base:** "[PATCH v8 0/3] Add support for the Sony IMX681 camera sensor",
  Sergey Lebedev and Andre Gilerson, 2 Oct 2026,
  Message-ID `20261002082537.74084-1-lsa.uz@pm.me`. It is written for the
  Intel Surface Pro 11 for Business (IPU7, two D-PHY lanes).
- **Ours, `patches/`:** an RFC series that replies to v8.
  - `0001` dt-bindings: allow `bus-type = <1>` (C-PHY) with one data lane;
    two D-PHY lanes stay the default.
  - `0002` driver: pick the bus from the endpoint. Per bus, only
    CSI_SIGNALING_MODE (2/3), CSI_LANE_MODE (lanes-1) and OP_PLL_MULTIPLIER
    (303/375) differ. C-PHY runs at 2.4 Gsym/s, which is a 1.2 GHz link
    frequency. The mode, the video timing PLL and the 720 MHz pixel rate are
    unchanged.

No OEM data is involved. The only register values the patches add are
standard CCS fields: the signalling mode, the lane count and one PLL
multiplier.

## Tested (2026-10-15, SP11 X1E80100, kernel 7.1.5 + camss module 50)

The test used a lab-only boot entry and DTB in which the front sensor
endpoint is `bus-type = <1>`, `data-lanes = <1>` and
`link-frequencies = /bits/ 64 <1200000000>`. MCLK4 was assigned 19.2 MHz,
and dvdd was put on the avdd rail. Raw capture went
`imx681 -> msm_csiphy2 -> msm_csid1 -> msm_vfe1_rdi0`:

- 3844x2640 SRGGB10 at 29.99 fps;
- colour-bar test pattern intact;
- a dark-room scene captures;
- VBLANK works: 8.19 fps at vblank 9000;
- the same RDI path at 3840x2160 with our production driver gives 30.05 fps.

Other checks:

- W=1 -Werror clean;
- checkpatch --strict clean, apart from the session-attribution trailers
  noted under "Sending";
- `dt-doc-validate` clean;
- `dt-validate`: accepts two D-PHY lanes, one C-PHY trio, and explicit
  bus-type 4; rejects one D-PHY lane and two C-PHY trios.

The test build against 7.1.5 strips the `v4l2_subdev_client_info` argument
from media-next, and nothing else. `lab/` holds the scripts:

- `make-lab.py`: lab DTB and a one-shot GRUB entry in `/boot/grub/custom.cfg`;
- `lab-ab.sh`: reload the modules with a chosen imx681.ko and capture RDI;
- `build.sh`: test build;
- `raw2png.py`: quick look at a raw frame.

Not tested: the D-PHY path on the Intel model. That path now also writes
CSI_LANE_MODE = 1. The cover letter asks German Pablo Lindo, the v8 tester,
to check it.

## Sending

The cover letter is the coordination mail to Sergey and Andre. It asks
whether they want to fold the two patches into their v9, or have them come
as follow-ups after v8 merges. Addresses, In-Reply-To and Cc are already
set. Before sending:

1. Replace `geoca` with your real name in `From:`, in `Signed-off-by:` and
   at the end of the cover letter. The kernel needs a known identity.
2. Remove the `Co-Authored-By:` and `Claude-Session:` lines from 0001 and
   0002. Kernel patches state AI help with the `Assisted-by:` tag, which
   is already there.
3. Send as plain text with `git send-email patches/*.patch`, which needs
   Gmail's SMTP and an app password. Web Gmail breaks patches.

## Next upstream pieces (not started)

- **SP11 camera device tree** (`x1-microsoft-denali`). It needs Bryan
  O'Donoghue's x1e80100 camera DT series (v7), the CSI2 PHY and CAMSS PHY API
  series, and X1E C-PHY support in the CSI2 PHY driver. The Dell XPS 13
  front-camera DT patch from Liviu Nicoara is the template: same MCLK4 and
  GPIO 237, and avdd/dvdd on PM8550 LDO7.
- **Hardware ISP**: Bryan's RFC "Switch on IFE YUV, Stats and Params support
  for sm8650" (74 patches, Oct 2026) adds the IFE pixel path to CAMSS. An
  X1E80100 (VFE 680) IFE configuration on top of it is where our own,
  non-OEM front and rear ISP values would go.
