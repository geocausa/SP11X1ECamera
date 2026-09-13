# E004v — CSIPHY0 8 KiB DT aperture authority

E004v is a DT-only correction derived from the single E004u receiver-power fault.

The parent is the proven E004o IR-only graph DTB:

- SHA256: `fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742`

The X1E CAMSS driver sets the CSIPHY common-register offset to `0x1000`. E004u proved that the parent DT's 4 KiB CSIPHY0 resource ends exactly where the driver's first reset access begins, causing the level-3 write fault at `base + 0x1000`.

Same-machine Windows independently exposes CSIPHY0 as:

`0x0ace4000..0x0ace5fff`

which is exactly 8 KiB.

E004v changes one DT cell only:

- old: CSIPHY0 `0x0ace4000 + 0x1000`
- new: CSIPHY0 `0x0ace4000 + 0x2000`
- next resource remains CSIPHY1 at `0x0ace6000 + 0x2000`

The builder patches the parent DTB bytes directly rather than recompiling DTS. Therefore the output remains byte-identical to E004o except for one byte in the CSIPHY0 size cell.

Output DTB SHA256:

`5547a43f06062053c7acdacbf8d6e103233f3d5e3ea7ebc8761bc32fbdcc0009`

No runtime action is performed in E004v.
