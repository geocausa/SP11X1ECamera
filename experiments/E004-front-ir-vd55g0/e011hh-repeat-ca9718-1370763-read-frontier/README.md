# E011HH — repeat CA9718 case to RVA 0x1370763 read frontier

Four exact placements execute the already-qualified `0xCA9718` case under the new receiver state. The owned mutations remain identical, while receiver `+0x20 = 1`, parser state `1`, and source pointer RVA `0x1370763` are preserved. `0xCA9848` reloads that pointer.

Execution stops before `0xCA984C` reads the next byte. E011HI separately source-qualifies RVA `0x1370763`, executes the byte update and loop arithmetic, derives first lookup RVA `0xF8B2B7`, and stops before reading it.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
