# E004ea — canonical offline protected worker

Status: **PASS / MAINTAINED SOURCE / OFFLINE ONLY / TRUST BLOCK UNCHANGED**.

The Windows-exact protected transfer worker was mechanically complete by E004dj but its final source still lived across E004dc/E004dg/E004dh/E004dj experiment directories. E004ea promotes that final path into maintained `src/sp11-camera-protected-worker` source without changing its algorithm, wire contract or native ABI.

The canonical source flattens only historical relative include paths. Its offline build reproduces the exact E004dj Hexagon-v73 combined object SHA:

`4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48`

Host/full-frame verification still reports zero luma differences and zero neutral-tail differences against the stable 644x604 Windows oracle, and the shipped 96-byte loadalgo proxy call contract remains unchanged. The partial-linked native object has exactly the same ten Qualcomm/QURT unresolved imports as E004dj.

This promotion deliberately does **not** add a signer, FastRPC launcher, firmware mutation, trust-policy mutation or runtime activation path. E004de/E004df remain authoritative: the current SP11 production trust policy provides no legitimate source-controlled admission route for this new worker with the credentials/material available to the project. Verification bypasses and test/debug trust roots remain forbidden.

The practical consequence is useful: protected IR/Windows Hello is no longer blocked by missing implementation code or source organization. It is blocked only by legitimate production worker admission.
