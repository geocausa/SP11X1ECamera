# E002b-r1 result — PASS

E002b-r1 proved that camera-only RPMh resources can coexist with the FullIO v19c Golden system when they are isolated in separate provider devices and are not given registration-time voltage constraints.

## Boot identity

- kernel remained `7.1.5-sp11-render-parity-v4+`;
- kernel and initrd were byte-for-byte copies of FullIO v19c;
- cmdline marker: `sp11_entry=7.1.5-sp11-camera-e002b-r1 sp11_camera_e002b_r1=1`;
- one-shot GRUB entry was consumed;
- saved default remained `sp11-audio-fullio-v19c`.

## Golden regression gate

PASS:
- Wi-Fi `wlP4p1s0` UP and associated to `GEOCA`;
- MultiMedia1 Playback present at card0/device0;
- MultiMedia3 Capture present at card0/device2;
- only known `casper-md5check.service` remains failed;
- existing PM8550-B `17500000.rsc:regulators-0` bound to `qcom-rpmh-regulator` with no errors.

## Camera infrastructure

PASS:
- `/dev/media0` present;
- `/dev/video0..15` present;
- CAMSS, CCI0 and CAMCC bound and runtime-suspended;
- MCLK1 prepare/enable counts remained zero.

## Isolated rail gate

Both isolated providers bound to `qcom-rpmh-regulator`:

- `17500000.rsc:regulators-camera-pm8550-b-e002b-r1`;
- `17500000.rsc:regulators-camera-pm8010-m-e002b-r1`.

All four experimental regulator handles were inert:

- `vreg_l16b_camera_e002b_r1`: 0 users, 0 mV, unknown mode;
- `vreg_l1m_camera_e002b_r1`: 0 users, 0 mV, unknown mode;
- `vreg_l5m_camera_e002b_r1`: 0 users, 0 mV, unknown mode;
- `vreg_l6m_camera_e002b_r1`: 0 users, 0 mV, unknown mode.

No rear sensor node existed, no probe module was loaded, and no reset/MCLK/I2C camera action occurred.

## Accepted rule

Never add an experimental camera regulator child to an existing Golden RPMh provider. Experimental resources remain in separate provider devices until their lifecycle has been proven safe.
