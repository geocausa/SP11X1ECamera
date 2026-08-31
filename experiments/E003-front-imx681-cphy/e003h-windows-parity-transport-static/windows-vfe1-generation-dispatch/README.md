# Windows VFE1 generation dispatch correction

Pinned ARM64 semantics prove selector zero chooses RVA `0x1be80`; nonzero chooses `0x1d2b0`. This supersedes only the old selector prose, not the separately decoded callback bodies. Active SP11 branch remains fail-closed until dynamically observed.
