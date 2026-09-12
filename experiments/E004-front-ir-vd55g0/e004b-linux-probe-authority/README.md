# E004b — Linux IR probe authority

Status: **PASS offline / no Linux VD55G0 power-on yet**.

E004b translates the Windows-only E004a oracle into the smallest Linux artifact capable of a first bounded identity/revision experiment. It deliberately does not attempt camera streaming or full VD55G0 support.

## Parent authority

The DT parent is the accepted deterministic IB unified rear+front artifact:

- `x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb`
- SHA256 `5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321`
- rear/front accepted topology remains byte-exact.

E004b adds 13 nodes and changes only one pre-existing non-symbol property: empty CCI0 master0's `clock-frequency` becomes 400 kHz, the Linux CCI driver's exact FAST mode.

## Windows-to-Linux translations

Same-machine Windows remains authority. Linux kernel source is used only to translate those resources into Linux encodings.

- Windows CCI0/master0 -> Linux CCI0 `i2c-bus@0`, GPIO101/102 `cci_i2c`.
- Windows FAST -> Linux CCI `clock-frequency = 400000`.
- Windows MCLK0 19.2 MHz -> `CAM_CC_MCLK0_CLK` ID 71 -> X1E `cam_mclk` GPIO96.
- Windows reset GPIO109 -> Linux active-low GPIO109.
- Windows CSIPHY0 `laneMask=0x81` -> sensor logical lane 1 / CAMSS physical lane 0, D-PHY, 420 MHz link metadata.
- Windows LDO4_M 1.8 V -> PM8010 LDO4 exactly 1.800 V.
- Windows LDO7_M 2.8 V -> PM8010 LDO7 exactly 2.800 V.
- Windows LDO2_M request 1.150 V -> PM8010 LDO2 hardware grid cannot represent 1.150 V. The nearest valid setpoint is **1.152 V**, only +2 mV. This is explicitly recorded as Linux hardware quantization, not silently called exact parity.

The Windows AeoB DELAY unit remains unresolved. E004b therefore preserves the power ordering but does not claim timing parity.

## Probe-only DT node

The IR node uses the private compatible:

`microsoft,sp11-vd55g0-idprobe`

rather than `st,vd55g0`. This prevents the pristine ST driver from binding: its normal probe path would upload an ST CUT patch, boot and configure the sensor, which is outside the first live gate.

There are no `st,leds`, illumination, sync, or invented lane-polarity properties.

## Write-free probe module

Source:

`src/front-ir-vd55g0/sp11-vd55g0-idprobe/`

The module is not a V4L2 camera driver. Its bounded probe:

1. keeps reset asserted;
2. requests/validates MCLK0 = 19.2 MHz;
3. enables VDDIO -> VCORE -> VANA;
4. verifies actual Linux regulator setpoints before reset release;
5. deasserts reset;
6. reads only model register `0x0000` and revision register `0x0004`;
7. logs raw bytes and both endian interpretations;
8. reasserts reset;
9. disables VANA -> VCORE/VDDIO -> MCLK before probe returns.

It contains no sensor register-data write helper, firmware/patch upload, boot/configure operation, V4L2/media registration, streaming operation, or illumination control.

The 5 ms inter-step sleep is a conservative safety delay only. It is not a claim about the unresolved Windows AeoB DELAY unit.

Two clean builds against Golden runtime headers are byte-identical:

`d749fb549ff7c03e0ebcd1690b78b795d985d6d37083ab938a2a2663c397daed`

with exact Golden vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

## Verification

```
python3 experiments/E004-front-ir-vd55g0/e004b-linux-probe-authority/verify-e004b-dtb.py
python3 experiments/E004-front-ir-vd55g0/e004b-linux-probe-authority/verify-probe.py
```

Both must pass before any candidate can be installed.

## Next gate

E004c is a one-shot runtime package only:

- install the E004b DTB beside Golden, never replace Golden;
- boot it once through GRUB `next_entry`;
- confirm the custom driver is not auto-loaded;
- manually load exactly the verified probe module once;
- capture only identity/revision and power-off markers;
- do not retry in the same boot;
- do not stream or upload any patch;
- reboot immediately to Golden and retire the candidate.
