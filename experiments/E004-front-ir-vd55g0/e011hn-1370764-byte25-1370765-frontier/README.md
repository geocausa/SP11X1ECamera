# E011HN — RVA 0x1370764 byte 0x25 through repeated case to RVA 0x1370765 read frontier

The pinned image source qualifies RVA `0x1370764 = 0x25`. Four exact placements execute the signed read and advance the retained pointer to `0x1370765`. Reusing accepted parser-table and dispatch authority, the path reads `0xF8B21B = 1`, `0xF8B230 = 1`, dispatches through signed entry `-52`, and executes the accepted `0xCA9718` case body while preserving receiver `+0x20 = 2`.

Execution returns to the common resume and stops before `0xCA984C` reads RVA `0x1370765`. E011HO source-qualifies that byte and reuses the accepted byte-`0x73` parser chain to the `0xCA9838` helper frontier.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
