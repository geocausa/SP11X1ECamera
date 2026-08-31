# E003h 0057 candidate — SP11 active IFE1 DAL-start prefix

Fresh Golden-safe one-shot package derived from accepted static commit `139aeb16e4296041234ae97da91cfef105ee7d46`. Relative to consumed 0056, the only camera-programming delta is the corrected private VFE1 start prefix: active SP11 callback writes TOP `+0x24=7`, TOP `+0x28=0x10`, BUS `+0xc18=0xdc000000`, BUS `+0xc08=0x1ff`; separately proven TOP IRQ masks and BUS mask1 remain retained prerequisites.

The Windows-selected IMX681 mode2 module, helper, exact media graph, RT-CDM observer, front-only DTB and firmware capsule are frozen. The accepted 300 MHz CAMNOC correction remains in the CAMSS baseline.

Installed boot ID: `sp11-camera-e003h-vfeactive-0057-one-shot`. Golden remains the saved default and `next_entry` stays empty. Package installation does not authorize runtime.
