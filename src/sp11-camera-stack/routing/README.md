# SP11 RGB route policy

Pure policy and transaction engine. There is deliberately no live device backend, CLI, shell execution, module loading or boot action.

The accepted complete119-edge contract is copied byte-for-byte from E004ki/E004le. The policy normalizes sensor bus numbers only, admits exact four-edge front/rear paths, excludes IR/PIX/alternate routes, and plans camera switches through neutral. Intermediate states are accepted only when they exactly match an internal transaction step; external entry must be neutral or one of the two complete approved RGB routes.

Controller callers must own an exclusive camera session and provide fresh kernel graph reads plus actual all-camera-stopped checks. Reads before/after each write detect graph drift; a failed or uncertain write poisons the controller with no retry or speculative rollback. This does not itself implement a cross-process lock or eliminate races from uncooperative external clients.

Not integrated with libcamera, not installed and not runtime-admitted. libcamera's cached MediaLink flags are insufficient for the required fresh-read backend. A guarded native integration and a new one-shot remain required.
