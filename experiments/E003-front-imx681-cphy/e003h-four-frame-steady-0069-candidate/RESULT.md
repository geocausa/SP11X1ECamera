# 0069 result

The authorized camera transaction was **not executed**. The sacrificial boot's standard Qualcomm CCI controller `ac16000.cci` timed out during probe (`-110`) before IMX681 registered in the media graph. The V4L2 helper was never invoked, STREAMON count stayed zero, RT-CDM remained idle/fault-free, and no forced CCI reset/rebind was attempted. The machine returned cleanly to Golden. Next action is a separately authorized 0069r1 boot with byte-identical camera assets; a second CCI failure will be treated as a boot-level blocker rather than bypassed.
