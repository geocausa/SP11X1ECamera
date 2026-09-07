# E003i-AK — bounded live AJ IMX681 control runtime

Status: **READY / UNEXECUTED**.

AK is a fresh one-shot validation of the committed AJ sensor-control implementation. It reuses the already-proven E003i-AI front-only DTB, Z/Y CAMSS module, six-frame helper, template-free R4 composer and live R5/R6 producer unchanged. The only camera hardware asset substitution is AJ `imx681.ko` SHA256 `15855b65512a15e66a732b1bf023fa8935a86b937426e2f590e161d25944bd54`.

Before STREAMON, AK enumerates the sensor subdevice controls and caches a deliberately small non-default request: exposure `3500` lines, raw analogue code `64` (`0x040`), global digital Q8.8 code `272` (`0x0110`), while vblank remains the mode2 default `1394` so FLL remains `3554`. The sensor is runtime-suspended at this point; the values are only cached.

AJ restores the Windows mode2 table during STREAMON and immediately reapplies the four-control cluster under the proven `0x0104` group hold before writing `MODE_SELECT=1`. The AJ module is loaded with dynamic debug enabled, so a successful hardware transaction must emit exactly:

`AJ request controls: FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0`

AK then runs the unchanged AI six-frame/R5/R6 path. Acceptance requires the exact AJ transaction line, six QC10C frames and generation-tagged TL_BG/3A 1..6, successful live R5/R6 submissions, clean kernel health, and mandatory return to Golden. Any failure consumes the one-shot; no same-boot retry is allowed.
