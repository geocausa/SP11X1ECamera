# E003i-AM — IMX681 exposure cluster fix

Status: **PASS — static/offline closure; live runtime remains a separate fresh one-shot.**

AM is the additive correction after AL proved a V4L2 cache bug before STREAMON. AJ clustered VBLANK, exposure, analogue gain and global digital gain together and unconditionally called `__v4l2_ctrl_modify_range(exposure, ...)` from the cluster callback. Linux 7.1.5's control core begins that helper with `cur_to_new(exposure)`, so AL's in-flight exposure request `3500` was replaced with the old current/default `3546` before the cluster committed. Analogue gain `64` and digital gain `272` survived, exactly matching that mechanism.

AM keeps VBLANK standalone and clusters only exposure + analogue gain + global digital gain, with exposure as cluster master. VBLANK alone owns exposure-range updates. Both the standalone VBLANK path and the exposure/gain cluster call the same group-held Windows-parity sensor transaction.

The sensor transaction itself is unchanged from AJ: group hold `0x0104`, 24-bit FLL `0x033d`, even 24-bit coarse integration `0x0229`, 16-bit analogue code `0x0204`, 16-bit global digital Q8.8 code `0x020e`, then group-hold release. The transferred Windows oracle remains SHA256 `2dffc0370dbc19345bbfc09d80bd7ea6919259a371fc7f35e6b4cf65fe5fad9f`.

`prove-am.py` checks the exact V4L2 core ordering/root cause, the corrected topology, the AL `3546 -> requested 3500` cache regression, the Windows oracle self-test, and 20,000 randomized dynamic byte transactions. The module builds with `W=1` and Golden kernel vermagic.

This stage does not claim a live sensor write. A fresh AN one-shot must cache `3500 / 0x040 / 0x0110`, observe the exact AM CCI-success log at stream-on, complete the unchanged six-frame/R5/R6 path, and return Golden.
