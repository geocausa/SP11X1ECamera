# E011JD — local/buffer fields to +0x4890 frontier

PASS. The accepted 1040-byte zero clear covers `x26+0x6C`. The accepted 18,832-byte enumeration buffer supplies `+0x442C=0`, `+0x1C=0`, `+0x0C=0`, and current `+0x20=0x08000000`. Original `0x5BE424..0x5BE46C` therefore leaves locals `+0x68/+0x6C/+0x470` zero. Execution stops before `0x5BE470` reads `buffer+0x4890`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JE qualifies `buffer+0x4890`.
