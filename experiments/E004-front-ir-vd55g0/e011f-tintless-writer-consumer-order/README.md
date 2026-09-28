# E011F — Tintless retained writer and first consumer order

Parent Git: 6d98ce399e230e58e6da0a53fb41dbbeee578977 (E011E).

Status: LIVE ORDER BOUNDARY PASS, INTERVENING 18-TO-14 WRITER OPEN. Native rear ISP runtime remains denied.

Fresh same-SP11 original Windows rear Color VideoRecord NV12 3840x2160 used an isolated E011F holder. CDB attached to FrameServer before StartAsync and armed the pinned IFENode Tintless writer RVA 0x736DB0 and Tintless dependency RVA 0xA10E58. The first writer hit preceded the first dependency. Its pointer table entry 1 addressed IFENode's retained configuration at node `+0x60E90+0x360`, so its `+0x1A0` record was the retained `+0x500` slot, not the request object. The writer saw node field `+0x9764=18`, pointer table `+0xEC=0`, and override flag `+0x7CAC=0`. It changed an all-zero record to grid 32x24, zero origin, full 4064x2286 rectangle, four 0x3ffff threshold lanes and word `+0x28=18`. A second writer hit used that same retained pointer and source controls.

At the first Tintless dependency, request ID 1's context selected its own request configuration. Its `+0x500` slot read the same 32x24/full-crop/0x3ffff geometry and thresholds, but word `+0x28=14`. The retained record's word was also 14 by then. A hardware write watch on the retained word later caught a direct store inside Tintless Execute at RVA 0xA1174C: the store wrote 18 over 14. This establishes an intervening change from 18 to 14 between the IFENode helper and first dependency, and an explicit later module write back to 18. The earlier 18-to-14 writer was not watched in this run. Do not attribute the first consumed word to the IFENode helper alone or encode a fixed 14/18 transition without that writer's source and timing.

The observed branch controls close the full-width, no-override branch for this physical rear4K session, while the source rule still needs its conditional branches for other modes. The holder completed StartAsync, acquired 1,242 valid 4K handles, passed StopAsync and ended. Breakpoints were cleared, CDB detached, ordinary reboot returned to Golden Linux, and overlap guard passed. No native rear ISP runtime was loaded or submitted.

Next precise trace: after the first retained writer returns, arm a single data watch on retained record `+0x28`, then capture the first 18-to-14 store and its call stack before the Tintless dependency. Resolve how the request object receives that value. Other E008p seeds and VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement remain open.

Only source-safe relationships and scalar outcomes are committed; debugger output, OEM bytes and pixels stay private on SP11.
