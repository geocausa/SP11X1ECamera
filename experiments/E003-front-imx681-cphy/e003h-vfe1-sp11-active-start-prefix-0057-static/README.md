# E003h 0057 — SP11 active IFE1 DAL-start prefix, static only

0057 corrects the private Linux VFE1 start prefix using the superseding same-machine Windows oracle. SP11 IFE1 selector 0 executes qccamisp RVA `0x1be80` followed by RVA `0x1c0e0` (`ret`). The active callback programs TOP `+0x24=7`, TOP `+0x28=0x10`, BUS `+0xc18=0xdc000000`, and BUS `+0xc08=0x1ff`.

The existing TOP mask0/mask1 and BUS mask1 writes are retained explicitly as separately proven Linux IRQ-visibility prerequisites; they are not attributed to the active DAL callback. The steady-state Windows BUS mask0 constant `0xd0000000` remains unchanged elsewhere. No runtime is authorized by this directory.
