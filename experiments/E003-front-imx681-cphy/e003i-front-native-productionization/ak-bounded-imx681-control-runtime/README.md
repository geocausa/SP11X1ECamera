# E003i-AK — bounded live AJ IMX681 control runtime

Status: **CONSUMED / FAIL PRE-STREAM — media/subdevice discovery permission bug; Golden return PASS.**

AK is a fresh one-shot validation of the committed AJ sensor-control implementation. It reuses the already-proven E003i-AI front-only DTB, Z/Y CAMSS module, six-frame helper, template-free R4 composer and live R5/R6 producer unchanged. The only camera hardware asset substitution is AJ `imx681.ko` SHA256 `15855b65512a15e66a732b1bf023fa8935a86b937426e2f590e161d25944bd54`.

Before STREAMON, AK enumerates the sensor subdevice controls and caches a deliberately small non-default request: exposure `3500` lines, raw analogue code `64` (`0x040`), global digital Q8.8 code `272` (`0x0110`), while vblank remains the mode2 default `1394` so FLL remains `3554`. The sensor is runtime-suspended at this point; the values are only cached.

AJ restores the Windows mode2 table during STREAMON and immediately reapplies the four-control cluster under the proven `0x0104` group hold before writing `MODE_SELECT=1`. The AJ module is loaded with dynamic debug enabled, so a successful hardware transaction must emit exactly:

`AJ request controls: FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0`

AK then runs the unchanged AI six-frame/R5/R6 path. Acceptance requires the exact AJ transaction line, six QC10C frames and generation-tagged TL_BG/3A 1..6, successful live R5/R6 submissions, clean kernel health, and mandatory return to Golden. Any failure consumes the one-shot; no same-boot retry is allowed.

## AK consumed result

AK executed its candidate boot exactly once. AJ bound successfully as `imx681 3-0010`, identity and mode2 programming passed, and the sensor runtime-suspended normally. Template-free R4 generation and the privileged media-graph setup also passed. The failure occurred immediately afterwards: `prepare.sh` invoked `media-ctl -d /dev/media0 -e "$SENSOR"` without `sudo`, while this candidate exposes `/dev/media0` to root only. The lookup returned `Failed to enumerate /dev/media0 (-13)`. Consequently no sensor control enumeration occurred, no control was set, the six-frame helper was never invoked, and **STREAMON was never reached**.

The candidate was not retried. It was archived and rebooted directly to the saved Golden entry. Golden return passed with kernel `7.1.5-sp11-render-parity-v4+`, empty `next_entry`, and no camera modules loaded. The dynamic sensor entity being `imx681 3-0010` (rather than AI's retained `4-0010`) also confirms that discovery must remain entity-based rather than hard-coding the adapter number.

AK is permanently consumed. The correction belongs in a fresh AL one-shot: use privileged `media-ctl`/`v4l2-ctl` for sensor-subdevice discovery and control access, while preserving all other AK/AI safety and hardware assets.
