# Machine and workspace map

## SP11 Linux

Primary camera-development target. Use it for source work, kernel/module/DT builds, boot packaging, dmesg, media-controller inspection and V4L2/libcamera tests.

The current protected Golden remains Audio FullIO v19c, kernel `7.1.5-sp11-render-parity-v4+`.

## SP11 Windows

The same physical SP11 booted into Windows. This is the primary **hardware oracle**. It is appropriate for ACPI/DriverStore inspection, ETW/WPP tracing, controlled camera lifecycle tests and KD when deeper observation is required.

Linux and Windows PiMaster endpoints are usually mutually exclusive because they represent the same machine.

## SP7 Windows

Companion/debug host. It can be used to drive KD into SP11 over the established lab path, including USB/EEM when configured, and to host analysis/tracing tools without disturbing the SP11 target.

## Canonical repository workspace

`/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`

Do not create competing camera source-of-truth workspaces. Temporary builds belong outside Git and must be referenced by experiment manifests.
