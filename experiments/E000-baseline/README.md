# E000 — baseline and project bootstrap

## Purpose

Establish the durable project workspace and record the known state before any camera modification.

## Proven starting state

- Deployed Golden remains Audio FullIO v19c.
- Running kernel: `7.1.5-sp11-render-parity-v4+`.
- No Linux `/dev/video*` or `/dev/media*` nodes.
- X1E CAMSS and CCI support/modules are present in the kernel.
- The Denali camera graph is not enabled in the deployed DT.
- Exact Windows hardware identities are IMX681 front, OV13858 rear and VD55G0 IR.

## No runtime mutation

E000 changes repository/documentation only. No kernel, DTB, initrd, module or GRUB payload was changed.

## Next

E001 — decode the Windows camera oracle into an implementation-grade resource/link/mode map.
