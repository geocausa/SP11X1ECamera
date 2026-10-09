# Native front normal-AEC metering

The active native IPA uses an independently written sum/count reduction over
all 1024 regions. Four channel sample means are retained by the pure decoder;
the current scalar callback is the equal Gr/Gb mean. The declared fixed mode
requires1980 samples/channel,34-bit sums,zero reserved sum bits and81920bytes.
Failures leave output unchanged. No Bayer array or pixels leave SP11.

This replaces the active path's historical OEM float scaling/checkerboard and
colour weighting. The older bounded-envelope helper remains historical and its
tests keep their previous meaning. No black level, full scale, optical target,
automatic controls or Windows quality parity is inferred.

Fresh front-meter01 will bracket exposure1000/3546/restored and analogue1x/
16x/restored via standard public libcamera requests, record private NV12 and
whole-frame scalar response, verify all sensor register readbacks, owner/SOF/
metadata and neutral shutdown. Kernel audit31 is unchanged. Private profile
dependency remains; this work is not an upstream-ready claim.
