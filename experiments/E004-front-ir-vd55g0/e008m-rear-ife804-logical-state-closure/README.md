# E008m — rear IFE 0x804 logical-state closure

Status: **STATIC CLOSURE PASS / NO BUILD / NO RUNTIME**.

E008f observes the Windows rear start manager sequence CDM804 -> IFE804 -> packet0. E008k already represents CDM804 with the accepted RT-CDM open/start bridge, but intentionally did not invent an IFE start MMIO stage.

The exact same qccamisp8380.sys static oracle previously proved that the IFE command-0x804 branch performs no direct MMIO and calls no hardware-start primitive. It only stores two logical fields: camera_use_case and frames_to_skip. Exhaustive object-field xrefs found only two downstream consumers, IFELite and full-IFE IO/BUS configuration. Both override per-resource frame-drop settings only when camera_use_case == 4.

For the rear path, the final hardware consequence is independently closed without needing to guess the rear 0x804 payload: the two accepted OEM rear VFE1 snapshots used by E004nu show all ten active rear write masters with FRAME_DROP_PERIOD=0 and FRAME_DROP_PATTERN=1. E008d's safe disabled-only writer programs those exact source-locked fields before enable.

Therefore the Windows IFE804 event does not imply a missing Linux hardware-start action. Its entire hardware-visible downstream state for the accepted rear session is already represented by the exact rear BUS contract. No synthetic IFE804 MMIO or extra runtime stage should be added.

This conclusion is deliberately narrow. It does not assert the rear camera_use_case numeric value; that value is unnecessary because the final downstream frame-drop state is independently measured and represented.
