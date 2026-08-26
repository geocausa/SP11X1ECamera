# E002b-r1 preflight — isolated camera RPMh providers, no sensor

## Why r1 exists

The first E002b boot exposed a hard isolation bug in the DT design, not a missing Golden kitchen.
The candidate was based on the literal deployed FullIO v19c DTB (SHA256 `2fcfa738...`) and retained all
Golden nodes, but E002b added PM8550-B `ldo16` as a child of the existing Golden `regulators-0` provider
with fixed 2.9 V constraints.

At boot the RPMh regulator core attempted to apply/read that new constraint immediately:

- `vreg_l16b_2p9_e002b: failed to get the current voltage: -ENOTRECOVERABLE`
- `regulators-0: ldo16: devm_regulator_register() failed, ret=-131`
- the entire existing PM8550-B provider then failed probe

That cascaded into Golden consumers:

- audio codecs waiting on existing B/LDO1 -> sound card deferred;
- WCN/Wi-Fi waiting on existing B/LDO15/LDO9 -> Wi-Fi absent;
- the new PM8010-M provider waiting on B/BOB1 -> rear probe deferred.

The failed E002b GRUB generator is quarantined (non-executable) and removed from generated grub.cfg.
The experimental probe module was removed from the shared Golden `/lib/modules` tree and `depmod` rerun.

## New isolation rule

Camera experiments must never add/modify children in an existing Golden regulator provider.
Experimental RPMh resources get separate provider devices so a camera-resource failure cannot remove
existing audio/WCN/USB supplies.

## r1 contents

r1 starts again from the literal deployed FullIO v19c DTB and adds:

- the already-accepted E002a CAMCC + CCI0 + CAMSS infrastructure;
- a separate PM8550-B provider containing only `ldo16`;
- a separate PM8010-M provider containing only `ldo1`, `ldo5`, `ldo6`.

There is **no sensor node, no CCI pinctrl, no reset GPIO, no MCLK consumer, no rail consumer**.
The four new regulator child nodes intentionally have **no min/max voltage constraints and no boot-on/always-on**.
Therefore registration must not issue a camera voltage/enable request.

The probe shim already calls `regulator_set_voltage()` before `regulator_enable()`. In this RPMh driver,
when initial state is unknown, set_voltage caches the selector and first enable sends voltage then enable.
That behavior is reserved for a later r2 sensor probe after r1 proves provider isolation.

## Mechanical DT proof

- Golden DTB SHA256: `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`
- r1 overlay DTBO SHA256: `a5cd70b66e381d0ddc4b378fc287f5622dd02330ac9c333135b50eb884aad4cd`
- r1 merged DTB SHA256: `f6219aaf282548a91fd03f9e284bd493beac200f4a9798512872e78a3085a6ad`
- normalized base->r1 diff: 105 insertions, 0 removals
- no diff touches `/soc@0/rsc@17500000/regulators-0`

## r1 acceptance

1. boot reaches userspace;
2. Wi-Fi interface exists and comes up;
3. playback and capture card/PCM enumerate exactly as Golden;
4. existing `17500000.rsc:regulators-0` binds successfully;
5. both isolated camera regulator providers bind successfully;
6. no `devm_regulator_register()` error for existing Golden providers;
7. no camera sensor node exists, so no GPIO/MCLK/I2C action can occur;
8. saved GRUB default remains `sp11-audio-fullio-v19c` and one-shot entry is consumed.
