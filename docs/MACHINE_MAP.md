# Machine and workspace map

## Active camera workspace

Resume current camera work from `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean`.

Remote: `https://github.com/geocausa/SP11X1ECamera.git`.
Branch: `experiment/e004-front-ir-vd55g0`.

The project-level pointer is
`/home/geoca/Documents/SP11-PROJECT/CURRENT-CAMERA-WORKSPACE.txt`.
PiMaster workspace `sp11-camera-handoff` must use the active path above.
Read the current continuation/state and latest experiment before acting.

## Retained historical checkouts

| Path | Role | Retained checkpoint |
| --- | --- | --- |
| `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera` | Historical source/evidence, including untracked local artifacts. Preserve it. | `9908619d` |
| `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-active` | Historical E011AA/E008o composition checkout. Preserve it. | `9908619d` |

These checkouts are not current resume targets. They intentionally retain their
existing revisions and evidence. Do not reset, clean, delete or merge them merely
to match the active checkout. Temporary builds stay outside Git and are
referenced by experiment manifests.

## SP11 Linux

Primary camera-development target: source analysis, kernel/module/DT builds,
boot packaging, logs, media-controller inspection and V4L2/libcamera tests.
Protected Golden remains Audio FullIO v19c,
kernel `7.1.5-sp11-render-parity-v4+`.

## SP11 Windows

The same physical SP11 booted into Windows; primary hardware/behaviour oracle
for ACPI/DriverStore inspection, non-halting ETW/WPP and controlled camera
lifecycle tests. Original OEM binaries, tuning and optical evidence stay private
on SP11. Follow AGENTS.md's remote-debug safety rule: on-target kernel halts
are prohibited; ordinary user-mode camera debugging has its own bounded rules.
Linux and Windows PiMaster endpoints are normally mutually exclusive.

## SP7 Windows

Companion/debug and independent recovery host. Established external KD/CDB
and SSH tooling may be used within the current safety contract. Its historical
role does not imply a debugger is currently attached.

## PiMaster

Normal remote-control plane for discovery, commands, retained jobs/terminals
and recovery access. Rediscover endpoint identifiers and live reachability;
never infer active work from a disconnected chat UI.
