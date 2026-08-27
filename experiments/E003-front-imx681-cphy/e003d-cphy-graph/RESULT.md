# E003d result — ACCEPTED

E003d connected the accepted native IMX681 sensor to X1E80100 CAMSS CSIPHY2 as an idle one-trio CSI-2 C-PHY graph while preserving the sensor's hard streaming block.

## Accepted runtime result

- one-shot boot used the exact Golden kernel Image and consumed `next_entry`; saved default remained `sp11-audio-fullio-v19c`;
- candidate CAMSS srcversion `446A14F6FC085EC7F4C542F` loaded from the isolated initrd;
- IMX681 again passed both identities: Windows/platform `0x0004 = 0x0aff` and Sony silicon `0x0016 = 0x0681`;
- `/dev/media0` contains `imx681 3-0010` as a sensor subdevice at 3840x2640 SRGGB10;
- the front media link is `imx681 3-0010:0 -> msm_csiphy2:0` with `ENABLED,IMMUTABLE` flags;
- a direct test-only kernel harness called only the sensor's `s_stream(1)` callback and received `-EOPNOTSUPP` (`-95`) exactly as required;
- after the callback, IMX681 runtime PM remained `suspended`, usage `0`;
- MCLK4, CSIPHY2 and CSIPHY2 timer enable/prepare counts remained zero;
- LDO3_M 1.8 V and LDO7_B 2.8 V remained at zero enabled consumers;
- GPIO237 remained output-low/reset asserted;
- therefore the Windows-derived 121-record X1E C-PHY electrical table was present in the candidate CAMSS module but was not electrically executed in E003d;
- the accepted rear OV13858 immutable link remained intact;
- Wi-Fi, MultiMedia1 playback, MultiMedia3 capture and Microsoft Surface G6 Touch remained healthy;
- no serious kernel fault was observed.

## Build/provenance result

- Windows X1E C-PHY table: 121 ordered records, 118 unique final offsets, exact two-run KD validation;
- candidate `qcom-camss.ko` SHA-256: `04e92a3ea8b9075f6d5ffa43856276595b0bb2b47877ce43b3987c08c4a41e91`;
- 140/140 candidate CAMSS imported symbol CRCs match Golden;
- candidate DTB SHA-256: `9e5eab025ed4dc0d23983f0e0ab0b84ca6095826f5a9b4f57fb1c6b9b3e50d79`;
- DT semantic gate: four intended graph nodes, zero unexpected node/property changes;
- reproducible candidate initrd SHA-256: `f44bda2c835985cae5ca77a50bc986567c606b08a4e225bff96c6bcfa07b2bdd`.

## Golden return

Normal reboot returned to FullIO v19c. Canonical hashes were byte-exact:

- Image: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`;
- initrd: `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`;
- DTB: `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`.

Saved default remains Golden and `next_entry` is empty.

Next gate: **E003e — IMX681 mode0 standby**. Introduce the exact same-machine Windows mode0 register lifecycle and transport metadata, but keep MODE_SELECT/`0x0100` prohibited and keep CSIPHY2 electrically idle. First actual sensor/PHY streaming remains a later gate.
