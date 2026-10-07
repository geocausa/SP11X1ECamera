# Maintained SP11 OV13858 source

This is the board-powered source from the SP11-tested prepared kernel frontend,
copied byte-for-byte with GPL/copyright attribution preserved. PROVENANCE.json
records its origin and SHA-256. It includes the standard V4L2 sensor controls,
SP11 firmware-selected mode and regulator/clock/reset/runtime-PM lifecycle.

The prior src/sp11-camera-stack/authority/ov13858.c snapshot assumed ACPI-powered
probe and was not the SP11 board source used by its frozen runtime ELF.
It remains unchanged as historical evidence. The native builder uses this file.

See docs/NATIVE-RGB-SOURCE-CORRECTION-20261007.md. Compilation and actual module
runtime acceptance are separate gates; rear hardware ISP support remains open.

The import was byte-identical to the recorded kernel source. Maintenance then
removed one unused local and its side-effect-free lookup so W=1/-Werror passes.
No register/control/power behavior changed. Maintained SHA-256: 734e1455a7f94edc15bd2a0ade124378c0b06f5a55751dc4ead195ef9686cad9.
