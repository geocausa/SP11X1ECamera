# E003e result — ACCEPTED

E003e programmed the same-machine Windows Sony IMX681 init sequence plus 3840x2640@30 mode0 while the sensor remained in software standby, without activating CSIPHY2.

## Proven sensor state

- Exact local QTI sensor module SHA-256: `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`.
- Mechanical extraction produced 364 init writes + 68 mode0 writes = 432 ordered writes / 430 unique registers.
- The extracted tables contain zero MODE_SELECT/`0x0100` writes, zero group-hold writes and zero orientation writes.
- The runtime driver required MODE_SELECT=0 before programming and read it back as 0 after all 432 writes.
- Runtime readback also verified C-PHY signaling `0x0111=3`, RAW10, one trio, line length 6752, frame length 3554, crop start 104/256, output 3840x2640 and PLL2 3/375.
- Both identities still passed: Windows/platform `0x0004=0x0aff`, Sony silicon `0x0016=0x0681`.

Kernel proof line:

`SP11 E003e PASS: Windows init=364 + mode0=68 programmed in standby; MODE_SELECT=0; C-PHY symbol=2400MHz link=1200MHz`

## Transport metadata

The same-machine mode0 PLL is 19.2 MHz * 375 / 3 = 2.400 GHz C-PHY symbol rate. Linux CSI-2 documentation defines the corresponding fixed-transmitter V4L2 bus/link frequency as half that operating symbol rate, so the sensor reports via `.get_mbus_config()`:

- bus type: CSI-2 C-PHY;
- link frequency: 1,200,000,000 Hz;
- one trio;
- `data_lanes[0]=0`;
- line order ABC.

A test-only kernel harness called the bound sensor directly and mechanically observed:

`E003E_MBUS_TEST: ret=0 type=6 link_freq=1200000000 trios=1 data0=0 order0=0`

The same harness called only the sensor's `s_stream(1)` callback; it remained hard blocked:

`E003E_STREAM_BLOCK_TEST: s_stream(1) ret=-95 expected=-95`

Therefore CAMSS does not need the generic C-PHY pixel-rate fallback for this sensor path.

## Electrical / system state

After standby programming and again after the direct stream-block test:

- IMX681 runtime PM: suspended, usage 0;
- MCLK4: enable/prepare counts 0;
- CSIPHY2 and CSI2 PHY timer: enable/prepare counts 0;
- LDO3_M 1.8 V and LDO7_B 2.8 V: zero enabled consumers;
- GPIO237: output low/reset asserted;
- immutable IMX681 -> msm_csiphy2 graph remained present;
- rear OV13858 remained bound and linked;
- Wi-Fi, FullIO playback/capture and G6 touch remained healthy;
- no serious kernel fault was observed.

No C-PHY receiver electrical table was executed in E003e because no CAMSS receiver stream operation occurred.

## Dynamic identifiers

CCI Linux adapter numbering is not stable across these modular initrd boots. E003d happened to expose front IMX681 as `3-0010`; E003e exposed it as `5-0010` and rear OV13858 as `2-0010`. The initrd loader's historical `3-0010` wait therefore emitted a cosmetic timeout despite the successful native bind. Runtime tests correctly switched to driver-based discovery. Future loaders/tests must discover the bound client under `/sys/bus/i2c/drivers/imx681/` instead of hardcoding an adapter number.

Wi-Fi privacy/DHCP identity also changes across reboots. Golden returned at `192.168.0.79`, not the prior `.71`; mDNS/PiMaster or dynamic discovery must be preferred over a fixed IP.

## Golden recovery

Normal reboot returned to `sp11_entry=7.1.5-sp11-fullio-v19c`, with `saved_entry=sp11-audio-fullio-v19c` and empty `next_entry`.

Canonical hashes are exact:

- Image `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- initrd `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`
- DTB `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`

**E003e ACCEPTED.**

Next gate: **E003f — receiver-only C-PHY electrical activation**. Keep IMX681 MODE_SELECT=0 and the sensor stream callback blocked. Exercise CSIPHY2's X1E C-PHY electrical programming in a bounded start/stop path, verify the programmed receiver state against the Windows oracle, require complete clock/power teardown, and do not permit sensor transmission or frame capture yet. First real sensor transport remains a later gate.
