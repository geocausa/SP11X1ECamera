# E006t — rear disabled small-IQ startup providers

Parent Git: `0e9d362c` (E006s rear BC101 compile PASS).

Status: **STAGED / COMPILE-ONLY**.

## Goal

Close the four remaining non-stats startup-only IQ configuration words from
semantic rear module state, without freezing captured Windows register values:

- BayerGTM101: 0x4D60
- BayerLTM101: 0x5260
- LCAC111: 0x5460
- UVGamma101: 0x6360

## Titan680 source-lock

Pinned Surface `QcDeviceMFT8380.dll` identifies the exact Titan680 classes
and single-word CreateSubCmdList writes at the four offsets above.

The full packer audit corrects an earlier simplification: BayerLTM101's
0x5260 word is **not** merely an enable bit on the enabled calculation path.
It also carries fixed/mode/config fields. GTM101, LCAC111 and UVGamma101
likewise have larger module register images even though the startup-only word
here is their single configuration word.

For the selected rear startup this distinction is harmless only because the
four modules are disabled. Titan680 initialization zeroes each register image;
the disabled CreateSubCmdList path updates/clears the enable bit and emits the
existing configuration word. Therefore the source-derived disabled image is
zero. The implementation deliberately rejects enabled state with
`-EOPNOTSUPP` rather than pretending the enabled LTM configuration is just
a boolean.

## Rear tuning authority

Selected rear authority:

- `com.surface.tuned.rfc_ov13858.bin`
- SHA-256 `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`

Exact DeviceMFT CheckAndUpdateChromatixData paths select:

- `bgtm10_ife_v2`, symbol 22
- `bltm10_ife_v2`, symbol 25
- `lcac11_ife_v2`, symbol 40
- `uvg10_ife_v2`, symbol 44

Each selected record serializes module enable = 0. GTM/LCAC/UV propagate that
state directly. BLTM has documented runtime override inputs in addition to
its tuning enable; the retained private startup0 corpus was reduced only to
the final semantic active state and confirms BLTM is also disabled for this
startup.

## Private validation

Only safe semantic facts are retained: startup0 emits these four families and
their final active states are all disabled. Startup1/2/3 omit these four
registers. Raw register values and packet bytes are not committed.

The clean provider therefore takes four Linux-owned active-enable booleans,
returns the exact zero disabled word for the proven rear startup, and rejects
an unimplemented enabled configuration.

## Coverage

E006t adds four startup-only registers:

- startup-only implemented: 124/184
- concrete startup providers including E006o singletons: 592/714 (82.9%)
- remaining startup-only registers: 60, all statistics families

Native rear Linux processed ISP and RT-CDM submission remain **DENIED**.
