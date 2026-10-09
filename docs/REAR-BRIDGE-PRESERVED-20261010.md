# Preserved webcam compatibility experiment

The unfinished Claude bridge source, loopback-loading setup edit and
WirePlumber configuration are preserved together. They are not a production
installation: only a transient sp11-webcam-test service existed, and installed
setup-camera.py did not include loopback loading. Five transient sessions
completed at about27-29fps. The current boot kernel log retained three clean
all-four-stop/owner/DMA/cache release receipts; sensors idle.

The temporary service was stopped without unloading camera modules.
Golden assets/default remain protected. Earlier module unloading while desktop
clients held subdevices caused a kernel use-after-free; never repeat that
operation. Preserve the bridge as optional compatibility work. Mainline work
prioritizes native V4L2/Media Controller + libcamera/IPA, both RGB cameras,
honest statistics ABI, normal lifecycle and independently measured tuning.
No upstream-readiness or full Windows-parity claim.
