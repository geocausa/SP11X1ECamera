# Native front grouped frame-length timing

Fresh one-use control-timing01 uses audit30/libcamera build08 and standard cam.
The explicit frame-length-v1 development mode changes the normal four-member
sensor V4L2 cluster at receiver sequences16,32,48,64,80,96: FLL7108/3554 repeated
three times, with exposure1000/analogue0/digital256 fixed. It captures128 NV12
frames and paired actual isolated IPA statistics, recording CCI transaction
completion and actual receiver interval transitions. Baseline is restored at96.

Kernel tracing is opt-in/read-only; no new register addresses or DMA commands.
No automatic feedback or public applied-frame metadata is enabled. Derived timing
JSON may be committed; optical pixels/original tuning/private logs remain SP11.
Do not infer exposure/gain delays or quality from frame-length response. Standard
DelayedControls parameters still need measured per-field/frame associations.
The service returns Golden automatically; spent identity must be retired.
