# E003i-G — clean-room front pre-Tintless producer

This checkpoint removes the native Surface geometry-resampler dependency from the repaired/current IMX681 LSC upstream path.

`cleanroom-front-lsc.py` contains an independent float32 implementation of the observed geometry transform. The 17x13 calibrated mesh is padded by one linearly extrapolated cell. The 15x11 interior output points use separable Catmull–Rom bicubic interpolation; the 56-point outer ring uses the Windows-observed bilinear branch. For 4048x3152 -> 3840x2160 with crop 104,496, source half-resolution pitch is 126.4375 x 131.25. The output uses 120 x 96 half-resolution pitch; the 96-high vertical grid is centered over the 1080 active half-height, producing a 36-pixel half-resolution vertical centering adjustment.

The proof reconstructs request4/5/6 directly from the installed IMX681 tuning leaves (`0x4bd -> 0x4bf`), the nominal front `lscgolden41`, and the directly captured physical front OTP slot. Request4 uses float32 ratio 0.342; request5/6 use leaf 0x4bd. It then compares generated 0xdd0-byte pre-Tintless payloads against the raw 2026-09-04 Windows atomic inputs.

Exact payload SHA256:

- R4 `25b80b20b5410ac0742a5fd26dbb32ac716cfa41a41965a5aaa98cbba39635e7`
- R5 `beea73b4857fc1c39464f6d360a43c5ba4232e22a16fbb190206d5f2d704f7c7`
- R6 `beea73b4857fc1c39464f6d360a43c5ba4232e22a16fbb190206d5f2d704f7c7`

No DeviceMFT code, Unicorn execution, or captured pre-Tintless mesh is an input to the generator. The Windows raw meshes are validators only.

Remaining production LSC work is downstream: replace the native Tintless callback replay with a clean-room implementation and acquire the physical OTP/live trigger state through the Linux runtime path rather than a captured proof fixture.

No Linux camera runtime is authorized or executed by this checkpoint.
