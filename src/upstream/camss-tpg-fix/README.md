# camss TPG: NULL dereference on the test pattern control

Found while testing the X1E80100 C-PHY series on a real next-20261015 kernel.

`testgen_payload_modes[]` (camss-tpg-gen1.c) is indexed by hardware payload
mode, so entries 3, 4, 7 and 8 are NULL, but the V4L2_CID_TEST_PATTERN menu is
created with max 9 and no skip mask. Setting one of the gaps (v4l2-compliance -m
does) oopses in `v4l2_ctrl_type_op_validate()`, and the oops leaves the control
handler lock held, so `rmmod qcom_camss` then hangs (and shutdown with it).

Introduced by 51fe835c485b ("media: qcom: camss: tpg: Add TPG support for
multiple targets"), in v7.2.

Fix: build the menu skip mask from the NULL entries. Verified on the Surface
Pro 11: menu lists 0,1,2,5,6,9; values 3,4,7,8 return -EINVAL;
v4l2-compliance -m completes; qcom-camss unloads and reloads.

- `0001-*.patch`: the patch (not yet sent)
- `evidence/before-*`: oops and hung rmmod without the fix
- `evidence/`: results with the fix
