# E005 front26 probe02: corrected GPIO observer

Fresh one-use boot identity after probe01 returned Golden and was retired.
Kernel, DT, modules and initrd are the qualified package from probe01; no
camera implementation or firmware changes. The observer admits the actual
7.2 TLMM GPIO debug format and checks local pin237 output-low/function0.
Retained model0x0681, registered graph, suspended sensor, child rails0 and
MCLK0 at19.2MHz already passed in01;02 completes the unload check.

Same temporary headless scope and recovery as01: no stream/capture/DMA, no
OS suspend, no proprietary camera inputs. Golden saved default/180-second
independent return plus observer ExecStopPost. Kernel panic timeout30.
Userspace recovery cannot cover a pre-userspace hard lock.
Three TPG entity-function warnings observed in01 remain recorded as a source
metadata correction; this test does not qualify upstream release readiness.
See ../E005-upstream-front-boot-20261013-01/README.md and build/preparation docs.
