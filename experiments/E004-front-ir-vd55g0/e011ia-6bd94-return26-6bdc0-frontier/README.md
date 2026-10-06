# E011IA — 0x6BD94 return-26 propagation to 0x6BDC0 epilogue frontier

Four exact placements execute the immediate caller path after the `CAD868` return. The accepted result `26` is stored at caller-frame `+0x10`, reloaded, takes the source branch at `0x6BDA4 -> 0x6BDB4`, is copied to frame `+0x14`, and reloaded as output `w0=26`.

Execution stops before the caller epilogue at `0x6BDC0`. E011IB source-qualifies the unique `0x6BE08 -> 0x6BD48` callsite and returns this frame to `0x6BE0C`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
