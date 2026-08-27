# E002b-r3g result — permissive PASS, strict confirmation pending

## Result

**PASS on the permissive isolation boot.**

The r3g DT-only correction selected the Windows-proven rear MCLK1 pad:

- GPIO97 raw TLMM control after boot: `0x00000244`;
- Linux debug decode: `out ... func1 4mA no pull`;
- X1E function 1 on GPIO97 is `cam_mclk`.

With the kernel, initrd, probe module, rails, reset, CCI route/rate/address, MCLK rate and Windows-exact ID transaction all unchanged from r3f, the rear sensor changed from `-ENXIO` to a valid identity response:

`SP11 E002b-r3f PASS: OV13858 chip ID 0xd855 at 0x10`

(The message retains the `r3f` label intentionally because r3g reuses the exact r3f probe module byte-for-byte.)

## Mechanical controls

- kernel SHA-256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a` — unchanged;
- initrd SHA-256: `0ed680055bdf5359478a29451e167679f2cba2b7c4f8b0ba30841046a453dbb2` — unchanged from r3f;
- r3f DTB SHA-256: `4eca2b3fb7f6793d780cc7d9e3642bf9f3a4703b7db011a6650f4857a2b12233`;
- r3g DTB SHA-256: `396259a06edffd4f9e0482480ef02201aa88acd98731db57fbb33358650a0b33`;
- DT semantic delta: GPIO97 `cam_mclk` state plus `pinctrl-0`/`pinctrl-names` on the existing rear probe only.

## Teardown / health

After the successful ID read:

- all four camera rails disabled in reverse order;
- MCLK1 branch/source returned to enable count 0 at 19.2 MHz;
- GPIO110 reset returned low/asserted;
- CAMSS media/video nodes remained present;
- Wi-Fi remained up;
- `MultiMedia1 Playback` and `MultiMedia3 Capture` remained present;
- Golden remained `saved_entry=sp11-audio-fullio-v19c`; one-shot `next_entry` was consumed.

## Conclusion

The r3f NACK root cause is **proven**: Linux enabled the internal MCLK1 clock but did not route it to physical GPIO97. Adding the Windows-equivalent GPIO97 MCLK pin state is sufficient for the real OV13858 to ACK and return its expected silicon ID.

Before accepting the rear identity gate, run one otherwise-identical strict r3g boot with only `clk_ignore_unused pd_ignore_unused` removed. No other change is justified.
