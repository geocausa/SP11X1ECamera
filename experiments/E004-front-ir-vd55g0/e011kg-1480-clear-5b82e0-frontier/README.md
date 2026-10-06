# E011KG — 0x1480 clear to descriptor merge frontier

PASS. E011KG follows the nonzero allocation path, executes `0x5B82DC -> 0xF5E600`, clears exactly `0x1480` bytes of the owned `x24` allocation, verifies adjacent redzones are untouched, and returns to `0x5B82E0`.

NEXT E011KH consumes the zero prior-count state, selects the new descriptor table, forms the first 32-byte copy call at `0x5B8344 -> 0x5B9888`, and stops before executing it. No new camera Start, reboot, rear runtime, or kernel build is used.
