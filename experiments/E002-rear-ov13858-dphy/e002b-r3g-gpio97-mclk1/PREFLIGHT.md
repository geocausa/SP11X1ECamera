# E002b-r3g — physical MCLK1 pad correction

Status: PREPARED / NOT YET BOOTED

## Question

Does the rear OV13858 acknowledge the Windows-exact identity transaction when r3f is left byte-identical except for routing CAMCC MCLK1 onto its proven physical X1E pad, GPIO97?

## Evidence motivating the change

Windows KD plus Qualcomm X1E80100 camera pinctrl data prove MCLK1 -> GPIO97. See `WINDOWS-ORACLE.md`.

Golden/r3f Linux leaves GPIO97 at TLMM control `0x00000001` (GPIO/function 0, pull-down, output disabled). Windows uses `0x00000244` (cam_mclk, 4 mA, no pull, output enabled).

## Single intended functional delta

Exact r3f DTB base SHA-256:

`4eca2b3fb7f6793d780cc7d9e3642bf9f3a4703b7db011a6650f4857a2b12233`

r3g adds only:

```dts
rear-mclk1-r3g-default-state {
    pins = "gpio97";
    function = "cam_mclk";
    drive-strength = <4>;
    bias-disable;
    output-enable;
};
```

and on the existing `rear-probe@10`:

```dts
pinctrl-0 = <&rear_mclk1_r3g_default>;
pinctrl-names = "default";
```

Candidate DTB SHA-256:

`396259a06edffd4f9e0482480ef02201aa88acd98731db57fbb33358650a0b33`

`base-to-r3g.diff` confirms no other semantic DT change.

## Everything else fixed from r3f

- kernel: exact Golden/r3f bytes, SHA-256 `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`;
- initrd: exact r3f bytes, SHA-256 `0ed680055bdf5359478a29451e167679f2cba2b7c4f8b0ba30841046a453dbb2`;
- probe module and Windows-exact transaction unchanged;
- CCI0/master1, 400 kHz;
- Linux sensor address `0x10`;
- ID register `0x300b`, 16-bit expected value `0xd855`;
- MCLK1 19.2 MHz;
- GPIO110 reset sequence unchanged;
- LDO6_M 1.8 V -> LDO1_M 1.2 V -> LDO5_M 2.8 V -> LDO16_B 2.9 V unchanged;
- no CSI endpoint and no streaming.

## Runtime acceptance

The first boot remains permissive to preserve isolation (`clk_ignore_unused pd_ignore_unused`). Success requires:

1. separate r3g one-shot boot; Golden remains saved default;
2. provider and probe bind normally;
3. GPIO97 reads back as the intended `cam_mclk` state;
4. MCLK1 remains 19.2 MHz;
5. OV13858 returns chip ID `0xd855` at `0x10`;
6. all camera rails/MCLK tear down cleanly;
7. Wi-Fi/audio/touch remain healthy.

If this permissive boot passes, repeat an otherwise-identical strict boot without `clk_ignore_unused pd_ignore_unused` before accepting the rear identity gate.

## Rollback

Golden FullIO v19c remains `saved_entry=sp11-audio-fullio-v19c`. r3g has a separate `/boot` directory and one-shot GRUB entry.
