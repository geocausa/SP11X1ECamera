# E002d preflight — rear OV13858 <-> CSIPHY1 graph only

Status: PREPARED / NOT YET BOOTED

## Question

Can the accepted native OV13858 sensor be attached to the existing X1E CAMSS media graph on the Windows-proven **CSIPHY1** input, with the Windows-proven four-lane D-PHY ordering, while remaining electrically idle and never starting a stream?

## Fixed accepted base

E002c-r1 is accepted and remains byte-identical except for this DT graph addition:

- kernel SHA-256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`;
- E002c-r1 initrd SHA-256: `d1e56f66b742e33f980748a66e4184e92ba1b7e0cb4f7a1844471b5fb7ffe344`;
- patched native OV13858 module SHA-256: `35c99b50106265449e18e633851b6653268382e59d7e7a3ce938cf7d0135b148`;
- native module srcversion: `02C96088AA5798CD5A70BFE`;
- CCI0/master1, 400 kHz, address `0x10`;
- GPIO97 `cam_mclk`, Windows-equivalent TLMM `0x00000244`;
- MCLK1 = 19.2 MHz;
- GPIO110 active-low reset;
- accepted four-rail D0/D3 sequence;
- native identity PASS and runtime-suspended teardown.

No driver, initrd, kernel, power, CCI or clock byte changes are part of E002d.

## Windows routing evidence

Static SP11 Windows oracle established for the rear OV13858:

- receiver = **CSIPHY1**;
- bus = D-PHY;
- four data lanes;
- `laneAssign = 0x3210`;
- RAW10 / VC0.

No Windows link-frequency or sensor-mode value is added in E002d. Those remain a later stream/mode gate.

## Exact local Linux mapping

The exact X1E source used by Golden mechanically maps CAMSS ports:

- `port@0` -> CSIPHY0;
- `port@1` -> **CSIPHY1**;
- `port@2` -> CSIPHY2;
- `port@3` -> CSIPHY4.

`camss_parse_endpoint_node()` sets `csiphy_id = endpoint.base.port`, requires CSI-2 D-PHY, and records lane positions only.

Qualcomm's local four-lane camera overlays use the same convention:

- CAMSS/host endpoint: `data-lanes = <0 1 2 3>`;
- sensor endpoint: `data-lanes = <1 2 3 4>`.

E002d sets `bus-type = <4>` explicitly on both endpoints (`MEDIA_BUS_TYPE_CSI2_DPHY`) rather than relying on parser inference.

## Graph delta

Accepted E002c DTB SHA-256:

`721ba8473e9b1c6ea6328fe43a3397d795d81f696402ab32c1067d5502c23d83`

E002d candidate DTB SHA-256:

`ea55cafdc4b35197e4d839a8435c7514c351ef4cfd2933d81458db0bea10472d`

`e002c-to-e002d.diff` shows only reciprocal graph endpoints plus generated symbols/phandles:

```dts
/* CAMSS / CSIPHY1 side */
port@1 {
    reg = <1>;
    endpoint {
        bus-type = <4>;
        data-lanes = <0 1 2 3>;
        remote-endpoint = <&ov13858_e002d_ep>;
    };
};

/* OV13858 side */
port {
    endpoint {
        bus-type = <4>;
        data-lanes = <1 2 3 4>;
        remote-endpoint = <&csiphy1_e002d_ep>;
    };
};
```

There is deliberately:

- no `link-frequencies` property;
- no mode/register change;
- no CSID/VFE route selection;
- no stream invocation.

The candidate introduces no new DTC warning category; its 30 decompile warnings are byte-base pre-existing duplicate-unit-address warnings.

## Why graph creation is electrically idle

Exact local CAMSS/media source proves:

1. endpoint parsing only records D-PHY lane configuration and async remote fwnode;
2. notifier `.bound` assigns the matching CSIPHY object to the sensor;
3. notifier `.complete` creates an immutable+enabled sensor-source -> CSIPHY-sink media link and registers subdev nodes;
4. `media_create_pad_link()` only creates graph objects; it does **not** call `link_notify`;
5. CSIPHY regulator/clock enable and `lanes_enable()` occur only through its `.s_power` / `.s_stream` paths;
6. E002d will call neither.

Thus E002d can prove topology independently of physical CSI activation.

## Runtime acceptance

One-shot strict boot only. Accept if:

1. exact E002d payload hashes boot and Golden remains saved default;
2. E002c native provider/OV13858 automatic identity cycle still passes;
3. patched native OV13858 remains bound at `1-0010`, runtime PM `suspended`, usage 0;
4. CAMSS async notifier completes with no endpoint/bus errors;
5. media graph contains the OV13858 sensor entity;
6. sensor source pad has an immutable+enabled link specifically to **CSIPHY1** sink;
7. sensor gets a V4L2 subdev node through the CAMSS media device;
8. no stream is invoked and no CSIPHY lane-enable/stream errors appear;
9. all camera sensor rails remain off after identity;
10. MCLK1 enable count remains 0 at 19.2 MHz;
11. GPIO110 remains reset/asserted after identity;
12. Wi-Fi, playback and capture remain healthy.

## Rollback

Golden FullIO v19c remains permanent saved default. E002d gets a separate one-shot boot payload and never overwrites E002c or Golden files.
