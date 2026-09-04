# 0075a hardened 0072 control

PASS. The exact accepted 0072 kernel/module/helper/old-IQ path delivered five frames under `clk_ignore_unused pd_ignore_unused` with indices `[0,1,2,3,0]`, sequences `[0,1,2,3,4]`, 7,778,304 bytes each, `STREAMOFF_OK`, and clean RT-CDM stop at userdata 5.

Live sensor frame bytes are not required to repeat the archived September 1 pixel hashes; the current hashes are retained only as evidence of this run.

Important correction: the named `msm_vfe1` `/proc/interrupts` counter is zero even in this known-good run, so it must not be used as a frame-completion discriminator.
