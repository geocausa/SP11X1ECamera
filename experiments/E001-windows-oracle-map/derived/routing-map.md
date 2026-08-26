# E001 Windows oracle — host routing map

This map is derived from the exact installed SP11 Windows `CAMP_PCFG_MSHW0495.bin` and the exact installed `qccamplatform8380.sys`; it is not inferred from a community DTS.

## PCFG packed sensor descriptors

The AeoB PCFG payload begins with feature flags `0x00000107`, then sensor connection descriptors. The active descriptors are:

| Sensor slot | Packed descriptor | Direction | I2C master index | CSI PHY index | Other evidence |
|---|---:|---:|---:|---:|---|
| rear RGB | `0x00110000` | 0 = rear | 1 | 1 | OV13858 |
| front RGB | `0x00230010` | 1 = front | 3 | 2 | IMX681 |
| front IR | `0x01000110` | 1 = front | 0 | 0 | Face Authentication bit set; VD55G0 |
| fourth slot | `0x00000000` | unused | 0 | 0 | descriptor disabled by PCFG presence mask |

Qualcomm camera direction semantics independently define 0 as rear/back and 1 as front.

## Bitfield recovered from `GetPlatformConfiguration`

The exact `qccamplatform8380.sys` PCFG parser is at RVA `0x2ef0`. Its logging strings and ARM64 bitfield extracts establish:

- bits 0..3: sensor orientation
- bits 4..7: sensor direction
- bit 8: flash presence
- bits 9..11: flash index
- bits 12..13: flash / CCI timer index
- bits 14..15: flash / trigger type
- bits 16..19: I2C master index
- bits 20..23: CSI PHY index
- bit 24: Face Authentication
- bit 25: flash / shutter type

The same function logs these exact field names, including `I2C master` and `CSI PHY index`.

## Flattened CCI master index

The exact platform helper at RVA `0xa988` mechanically splits the packed I2C master index as:

```
cci_controller = index / 2
master_within_controller = index % 2
```

Therefore the physical control-bus routing is:

| Sensor | Windows packed master | CCI controller | master within CCI | CSI PHY |
|---|---:|---:|---:|---:|
| OV13858 rear | 1 | **CCI0** | **master1** | **PHY1** |
| IMX681 front | 3 | **CCI1** | **master1** | **PHY2** |
| VD55G0 IR | 0 | **CCI0** | **master0** | **PHY0** |

Windows exposes both `cam_cc_cci_0_clk` and `cam_cc_cci_1_clk` at 37.5 MHz in the selected platform performance package.

## Host MIPI resource correlation

The Windows `QCOM0C98` MIPI-CSI device owns MMIO windows matching the X1E Linux CAMSS map:

- `0x0ACE4000` -> CSIPHY0
- `0x0ACE6000` -> CSIPHY1
- `0x0ACE8000` -> CSIPHY2
- `0x0ACEC000` -> CSIPHY4
- `0x0ACF6000/7000/8000` -> CSI test-pattern blocks

Thus Windows and Linux are addressing the same X1E camera receive fabric. No alternate hidden Surface camera transport is indicated.

## Rear transport rate for first Linux target

For the Windows OV13858 modes:

- RAW10
- four D-PHY lanes (`laneAssign = 0x3210`)
- output pixel rate = 474.24 MHz
- all three Windows modes use the same PLL program

For RAW10 over four lanes:

```
per_lane_bit_rate = 474.24 MHz * 10 / 4 = 1.1856 Gbit/s
DDR link frequency = 592.8 MHz
```

Microsoft programs, among other PLL registers, `0x0300=0x05`, `0x0301=0x00`, `0x0302=0xf7`, `0x0303=0x00`.

Mainline OV13858 currently exposes 540 MHz and 270 MHz link-frequency profiles, so the first SP11 rear candidate must not claim Windows parity while using an unmodified generic 540 MHz mode. E002 should add/audit the 592.8 MHz Windows-derived mode separately.

## Remaining non-blocking dynamic unknown

Windows sensor-driver debug strings show the host payload also carries `settleTimeNS` and `dataRate`. The exact runtime settle value was not observed because this Windows boot had no interactive camera session. For rear E002, the data rate is mechanically derivable above and Linux PHY timing can be calculated from the endpoint/link frequency. We keep an explicit task to capture Windows settle timing later rather than guessing it.
