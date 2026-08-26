# E002a result — accepted

Booted one-shot entry `sp11-camera-e002a-infra` using the exact FullIO v19c kernel and initrd with only the E002a DT delta.

## Acceptance result

- running kernel remained `7.1.5-sp11-render-parity-v4+`;
- `/proc/cmdline` proved the isolated E002a payload and `sp11_camera_e002a=1`;
- GRUB one-shot was consumed; `saved_entry=sp11-audio-fullio-v19c`, `next_entry=`;
- CAMCC bound at `ade0000.clock-controller` to `camcc-x1e80100`;
- CCI0 bound at `ac15000.cci` to `i2c-qcom-cci`;
- CAMSS bound at `acb7000.isp` to `qcom-camss`;
- `/dev/media0` appeared;
- sixteen VFE video nodes appeared (`/dev/video0` .. `/dev/video15`);
- no camera-driver warning/error was emitted for CAMCC, CCI0 or CAMSS.

## Electrical isolation

No rear/front/IR sensor node exists in E002a. Runtime state after enumeration:

- CCI0: `runtime_status=suspended`;
- CAMSS: `runtime_status=suspended`;
- CAMCC: `runtime_status=suspended`;
- `vreg_l2c_0p8` enable count: 0;
- `vreg_l1c_1p2` enable count: 0;
- CAMSS-created CSIPHY regulator consumers: enable count 0;
- camera MCLK0..7: prepare/enable count 0;
- CCI0, CSIPHY, CSID and VFE clocks: prepare/enable count 0;
- no `ov13858`, `imx681`, `vd55g0` or `d855` probe/log entry exists.

This proves the common X1E camera infrastructure can enumerate without touching a sensor or PHY power path.

## Golden regression check

Audio remained intact:

- card 0 device 0: `MultiMedia1 Playback`;
- card 0 device 2: `MultiMedia3 Capture`;
- three `SP11 stages pull-watermarks and soft-pause events accepted` messages;
- audio error signature remained the known baseline: one `0x1001021` timeout, seven `0x1001006` errors, one OOB frame-63 rejection.

A transient early-boot `grub2-common.service` failure occurred while GRUB was consuming the one-shot environment block. The same service was rerun after userspace settled and completed successfully; `systemctl --failed` returned to only the pre-existing `casper-md5check.service` failure. Saved Golden remained unchanged.

## Conclusion

**E002a PASS.** Proceed to E002b: add only the Windows-derived rear OV13858 power/reset/MCLK/control-bus node on CCI0 master1 and prove chip ID `0xd855`; do not stream.
