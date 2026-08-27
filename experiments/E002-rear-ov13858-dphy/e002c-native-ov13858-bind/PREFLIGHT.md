# E002c preflight — native OV13858 bind, no CSI endpoint

Status: PREPARED / NOT YET BOOTED

## Question

Can the native Linux `ov13858` V4L2 sensor driver bind to the real SP11 rear sensor, own the already-proven Windows-derived power/reset/MCLK lifecycle, verify silicon identity, register as a sensor subdevice, and return to electrical idle **without introducing CSI transport or streaming**?

## Accepted base

E002b-r3g is accepted:

- CCI0/master1 at 400 kHz;
- Linux sensor address `0x10`;
- GPIO97 = rear `cam_mclk1`, Windows-equivalent TLMM state `0x00000244`;
- MCLK1 = 19.2 MHz;
- GPIO110 active-low reset;
- LDO6_M 1.8 V -> LDO1_M 1.2 V -> LDO5_M 2.8 V -> delay -> LDO16_B 2.9 V -> MCLK1 -> reset release;
- reverse D3 teardown;
- real OV13858 ID `0xd855` proven on permissive and strict boots.

E002c does not alter any of those electrical facts.

## DT delta

Exact accepted r3g DTB SHA-256:

`396259a06edffd4f9e0482480ef02201aa88acd98731db57fbb33358650a0b33`

E002c DTB SHA-256:

`721ba8473e9b1c6ea6328fe43a3397d795d81f696402ab32c1067d5502c23d83`

`r3g-to-e002c.diff` proves the sole semantic change is:

```diff
-compatible = "microsoft,sp11-ov13858-probe";
+compatible = "ovti,ov13858";
```

There is deliberately **no sensor endpoint**, no CSIPHY1 graph link and no stream configuration in E002c.

The X1E I2C core derives the client name by stripping the vendor prefix from the compatible, so `ovti,ov13858` creates client type `ov13858`; the existing driver's I2C ID table then matches it even though the legacy upstream driver has no OF match table.

## Native driver delta

Baseline source:

`drivers/media/i2c/ov13858.c` from the exact deployed Golden source tree.

E002c keeps the upstream sensor implementation intact and adds Denali ownership of resources which the legacy ACPI-oriented driver previously assumed firmware had already powered:

- four named regulators: `ldo6m`, `ldo1m`, `ldo5m`, `ldo16b`;
- reset GPIO;
- the proven D0/D3 ordering;
- 19.2 MHz MCLK validation and enable/disable;
- runtime-PM suspend/resume callbacks;
- explicit power-up for native identity and immediate power-down after identity;
- E002c PASS log after native identity succeeds.

The native upstream 24-bit identity read remains unchanged (`0x300a`, expected `0x00d855`). Mode tables, controls, start/stop-stream implementation and register programming are otherwise untouched.

Patched source SHA-256:

`b69606cd43080b376c0ccb2fcbcad3dfb56f3942aa71dd897374a2f6748c5908`

Built module SHA-256:

`35c99b50106265449e18e633851b6653268382e59d7e7a3ce938cf7d0135b148`

Built against the exact v4 ABI with vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

## Initrd isolation

E002c is rebuilt from **Golden v19c initrd**, not from r3g/r3f, so no old probe-only loader is inherited.

Golden initrd SHA-256:

`ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`

E002c candidate initrd SHA-256:

`48e092c4e038a95ef51d683fb10ee78d515341338082e46337a9d8f92047a035`

Two independent builds are byte-identical.

The deterministic initrd layer adds only:

- accepted `sp11_camera_rpmh_regulator.ko`;
- exact-ABI `mc.ko`;
- exact-ABI `videodev.ko`;
- exact-ABI `v4l2-async.ko`;
- exact-ABI `v4l2-fwnode.ko`;
- patched native `ov13858.ko`;
- one E002c init-top loader;
- the corresponding `ORDER` addition and containing directory.

The loader explicitly loads the modules in dependency order and never invokes any V4L2 stream operation.

See `INITRD-DELTA.txt`.

## Kernel

Kernel remains exact Golden/r3g bytes:

`bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`

No kernel image rebuild is part of E002c.

## Runtime acceptance

First boot is one-shot and keeps Golden as saved default. Accept only if all of the following hold:

1. E002c boot identity and hashes are exact;
2. provider binds;
3. native `ov13858` module loads and `/sys/bus/i2c/devices/1-0010/driver` points to `ov13858`;
4. native upstream identity succeeds and E002c logs PASS;
5. sensor runtime-PM status is suspended after probe;
6. all four camera rails are disabled after probe;
7. MCLK1 enable count returns to 0 at 19.2 MHz;
8. GPIO110 is back in reset/asserted state;
9. no CSI endpoint exists and no streaming occurs;
10. Wi-Fi, playback and capture remain healthy;
11. Golden remains `saved_entry=sp11-audio-fullio-v19c` and `next_entry` is consumed.

## Rollback

Golden FullIO v19c remains the permanent saved default. E002c receives a separate `/boot` payload and GRUB one-shot entry. No Golden file is overwritten.
