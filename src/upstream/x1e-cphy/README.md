# X1E80100 C-PHY on the upstream CSI2 PHY (RFC)

The front camera (IMX681) on the Snapdragon SP11 uses one MIPI C-PHY trio
on CSIPHY2. Upstream, CSIPHYs are moving to Bryan O'Donoghue's
`qcom-mipi-csi2` PHY driver, and CAMSS talks to it through the PHY API. Both
are in linux-next, but only for D-PHY. This RFC adds C-PHY:

1. `phy: Add MIPI C-PHY mode and configuration options`:
   `PHY_MODE_MIPI_CPHY`, plus `struct phy_configure_opts_mipi_cphy`
   (symbol rate, trios).
2. `phy: qcom-mipi-csi2: Add C-PHY support for X1E80100`:
   - accepts bus-type C-PHY, with up to 3 trios and no polarities;
   - `set_mode()` must match the endpoint;
   - the trios are the odd CTRL5 bits;
   - the X1E C-PHY sequence comes from Qualcomm's GPL-2.0
     `cam_csiphy_2_1_2_hwreg.h`. The two Windows-only `0x?94=0x09` writes
     our daily stack adds are dropped: they are not needed.
3. `media: qcom: camss: csid-680: Select C-PHY in the receiver`: writes
   `phy_sel` to `CSI2_RX_CFG0_PHY_TYPE_SEL`. Windows's extra `TPG_NUM_SEL=1`
   is not needed either.
4. `media: qcom: camss: Configure C-PHY through the PHY API`.

It is based on next-20261015 plus David Heidelberg's camss C-PHY v9
(Message-ID `20260617-qcom-cphy-v9-0-83da8a8e4e44@ixit.cz`). Its 8/9 was
ported by hand.

## Tested (2026-10-15)

This is the first run of the **complete upstream stack** on the SP11:

- linux-next CAMSS and CSI2 PHY, built as modules for 7.1.5 (`lab/build-next.sh`;
  the shims cover API differences only);
- a lab DTB with CSI2 PHY nodes as in Bryan's x1e80100 camera DT v7
  (`lab/make-lab-next.py both`, one-shot GRUB entry `sp11-next-lab`);
- upstream-candidate sensor drivers: imx681 v8 + our C-PHY patch, and
  ov13858 mainline + Sergey's power patch + our DT patch.

Results (`lab/lab-next.sh`):

- **Front, C-PHY, CSIPHY2 -> CSID1 -> RDI:** 3844x2640 at 30.01 fps. The
  colour bars are byte-identical to those captured through our own camss.
- **Rear, D-PHY 4 lanes, CSIPHY1 -> CSID0 -> RDI:** 4224x3136 at 29.89 fps.
  It was the same before the C-PHY patches.
- Both sensors were bound together in one CAMSS graph.

checkpatch --strict (mainline script) is clean, except the generic
"new file, MAINTAINERS?" note. `include/linux/phy/` is covered by GENERIC
PHY FRAMEWORK.

## Sent

Sent 2026-10-15 by George Neacsu through the kernel.org b4 web endpoint, as
"[PATCH RFC 0/4] phy: qcom-mipi-csi2: C-PHY for X1E80100", Message-ID
`20261015-x1e-cphy-rfc-v1-0-1f3fa9af940a@gmail.com`. It went to Bryan
O'Donoghue, Vinod Koul and David Heidelberg, with Cc to Neil Armstrong,
Vladimir Zapolskiy, Loic Poulain, Mauro, Mani, linux-phy, linux-media,
linux-arm-msm and LKML. The working tree is the b4 branch `x1e-cphy-rfc`
in `06-camera/linux-next-sparse` on SP11.

## v2 (16 Oct 2026, draft, not sent)

Bryan asked for a base that applies to linux-next (phy-next after -rc7). Plain
linux-next has no C-PHY in CAMSS at all (that is David Heidelberg's v9), so v2
is the PHY side only: `patches/v2/`, RFC v2 0/4 on next-20261015, which
applies there on its own. The two CAMSS patches are kept in `patches/v2-camss/`
to send on top of David's series. Review from Bryan, Loic, Nihal and Konrad is
addressed (changelog in the cover letter): C-PHY helpers in the PHY layer, a
D-PHY init-sequence rename, the settle count computed instead of fixed,
lanes_enable() split into helpers, no separate bus_type, the C-PHY table
renamed lane_regs_v2_1_2_cphy.

Tested on the sp11-next-lab boot with David's v9 and the CAMSS patches on top
(`lab/build-next2.sh`, `lab/next2-tests.sh`):

- front IMX681, C-PHY: 3844x2640 at 30 fps, colour bars byte-identical to the
  v1 capture (md5 8c1d6d97...); timer 400 MHz, computed settle count 28;
- settle sweep (`lab/settle-sweep.sh`): 6, 14, 20, 34, 48 give identical frames,
  64 gives none;
- rear OV13858, D-PHY: 29.9 fps, settle count 18 as before.

Every commit builds on its own.
