# E012J — rear mid-digital-gain optical one-shot

E012I proved digital gain spans the Windows rear brightness range: gain 4096 remained below the Windows histogram while 8192 overshot it. E012J therefore tests one interpolated profile only: exposure 3200, analogue gain 1024, digital gain 5632. The goal is a current private 4K optical render at approximately the Windows overall exposure, not another broad sensor sweep.

The stale global private PNG from earlier consumed experiments is admitted only if it is a root-owned mode-0600 regular file and is removed before the exclusive-create preview writer runs. The exact sensor baseline is restored afterward, rear is selected off, service is stopped, and protected Golden is restored. No VBLANK/FPS change, raw register write, IR/illumination, AI/effect, direct tone transform or soak is permitted.

If the image histogram shape or colour still differs from Windows at the matched overall exposure, the next step is Windows ordinary-rear ISP/tone/colour extraction rather than further gain tuning.
