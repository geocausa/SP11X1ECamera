# Windows VFE1 SP11 active DAL-start prefix

This gate supersedes the earlier generation-family assumption for SP11 IFE1. Exact qccamisp ARM64 dispatch plus a same-machine live KD threshold read proves IFE1 index 1 uses selector 0: callback slot `+0x6b690` -> RVA `0x1be80`, then slot `+0x6b698` -> RVA `0x1c0e0` (`ret`).

The active first callback writes TOP `+0x24=7`, TOP `+0x28=context+0x160`, BUS `+0xc18=0xdc000000`, and BUS `+0xc08=0x1ff`. Two successful stock-Windows front-camera passes read TOP `+0x28=0x10`, and none of the four initial IFE CDM packets owns `+0x28`; the exact KMD callback is the direct software owner.

This is static/dynamic oracle work only. It does not authorize Linux runtime.
