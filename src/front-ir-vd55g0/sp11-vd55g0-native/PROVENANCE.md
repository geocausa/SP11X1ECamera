# SP11 VD55G0 native bind-only provenance

Sensor programming authority is the exact same-machine Surface Windows package:

- com.surface.sensormodule.aux_vd55g0_MSHW0492.bin
- SHA256 e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794

The generated header is produced by the copied clean-room generator from E004h and contains:

- exact 552-byte Surface patch, SHA256 5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321
- exact final Windows 43-write sequence identity
- safe 42-write sequence excluding only 0x0468=0x02

E004i proved the physical CUT1 sensor is already at 0x0468=0x02 immediately after the Surface patch/setup/boot prefix, before the safe 42 writes. This driver therefore refuses to write 0x0468 and requires that post-boot baseline to equal the Windows value.

Linux V4L2 registration/control structure is implementation scaffolding only. It does not contribute sensor constants or parity claims.

E004l is bind-only: .s_stream(1) returns -EOPNOTSUPP.
