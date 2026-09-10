# DV static proof

## Active tuning selection

Pinned tuning file:

`com.surface.tuned.ffc_imx681.bin`
SHA256 `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

The existing decoder proves front `Sensor2` and checks the effective required IFE module signatures for Sensor2 Preview, Snapshot and Video. They are identical. Its effective Demux/BLS record is Default symbol 31, data offset `2898936`, 64 bytes. The pointer graph terminates at one region whose four float words are exactly `602,593,592,596`.

Therefore the distinct top-level direct Usecase Demux records are not the active Sensor2 effective records and must not be substituted into this scoped path.

## Surface common setting

Pinned DLL:
SHA256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

Critical code `VA 0x180998ef0..0x18099918c` SHA256:
`57255c88e4f526cd2c888f5dfd3af7a5444736eec080c5571e1df337697f8627`

At `0x180998f34..` the ARM64 code uses scalar `FSUB/FDIV/FMUL` on `s` registers to form the four normalized channels. `param_1+0x1c` is the already-closed post-sensor dGain input.

Constants at `0x180999478`:
- `0x41fffdf4` = 31.999000549316406f
- `0x44800000` = 1024.0f

The scalar rounding helper at `0x1800014d0` is exactly:

`FRINTA s0,s0; RET`

helper bytes SHA256:
`5a7c0d8e787755f52c8149240c202b219109509583c7e89c2d800afd856425d4`

The Titan680 packer at RVA `0xb42840` places calculated u16 6/7 in register `0x3b70` and 9/8 in `0x3b74`, masking each to 15 bits.

## Exact accepted sample

The accepted matched request6 dGain is float bits `0x3f8024b7` = 1.0011204481124878. DV must produce Q10 `1064,1064,1064,1064` and registers `0x04280428/0x04280428`, exactly matching the accepted same-stream Windows oracle.
