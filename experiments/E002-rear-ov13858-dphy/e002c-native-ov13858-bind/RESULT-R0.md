# E002c r0 result — automatic packaging fail, manual native bind PASS

## Automatic boot result

r0 booted safely but the init-top loader failed before any camera resource was touched. The custom RPMh provider was not inserted, so the loader skipped the native sensor driver. GPIO97 remained Golden-like, MCLK stayed disabled and no camera rail vote occurred.

Root cause is a deterministic initrd packaging error: Golden has no `usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/` directory. The r3f builder explicitly created that parent. E002c r0 emitted only `extra/e002c/`, so its early nested module files were not reliably materialized for `insmod` even though archive listing tools could enumerate them.

The r0 loader also had an error-reporting bug: the shell `if insmod; then ...; fi` construct lost the original failure code before logging it. r1 must capture `$?` immediately.

## Controlled late-load result

Without rebooting or changing DT/kernel:

1. the exact accepted RPMh provider module was inserted after full kernel initialization and bound normally;
2. the E002c patched native `ov13858.ko` was then inserted;
3. the client bound to `/sys/bus/i2c/drivers/ov13858`;
4. the native upstream 24-bit identity transaction succeeded;
5. dmesg logged `SP11 E002c PASS: native OV13858 identity verified`;
6. all four rails were disabled immediately afterward;
7. runtime PM reported `suspended`, usage `0`;
8. MCLK1 enable count returned to `0` at 19.2 MHz;
9. GPIO110 returned physically low/asserted;
10. GPIO97 remained the accepted Windows-equivalent `0x00000244` pinctrl state while the bound native device existed;
11. no CSI endpoint exists in the sensor DT node and no stream was invoked;
12. Wi-Fi, ALSA playback and ALSA capture remained healthy.

This proves the E002c **driver/DT/electrical design itself passes**. r1 is packaging-only: add the missing `extra/` parent and fix loader rc logging. No driver source, DTB, rail, reset, MCLK, CCI or V4L2 behavior may change.
