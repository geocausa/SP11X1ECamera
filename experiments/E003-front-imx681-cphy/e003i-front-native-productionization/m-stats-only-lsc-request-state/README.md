# E003i-M — stats-only front LSC request state

This offline checkpoint removes the remaining captured Tintless request objects from the clean-room LSC calculation path.

The exact 0x130-byte front Tintless configuration is now constructed from:

- front rolloff geometry (`17x13`, `30x24` subgrid, 8 subgrids, offsets `0/72`);
- front Tintless-BG geometry (`3840x2160`, `120x90`, `32x24`, 18-bit);
- four `0x3ffff - 1` saturation limits;
- the installed `tintless23_sw_v2` active 264-byte tuning region;
- deterministic IFE temporal/mode settings.

The generated config SHA256 is exactly `8ce68010d1126105ae68490294bc6b3f2598dfe5dfc88ff5df40f8926efd9d86`, identical to Windows R4/R5/R6.

Input/output mesh descriptors are constructed locally from `count=221` and four plane pointers. Native descriptor metadata is not consumed by the clean core. Request4 starts from a zeroed fresh wrapper/core state; the only nonzero bytes in the Windows wrapper-pre image were an unused process pointer in the first qword. Normalizing that pointer, generated R5/R6 wrapper/core carry remains byte-exact.

Therefore the adaptive LSC runtime input is reduced to **raw 768-region Tintless statistics** plus ordinary request trigger state used by the already-clean tuning interpolation. No captured x1/x3/x4/wrapper/core state is a calculation input.

No camera runtime is performed or authorized here.
