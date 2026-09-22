# Bounded native RGB publishers

Self-contained source package for the accepted front RAW10 to1080p NV12 and rear RAW10 to4K NV12 publishers. Conversion files are byte-identical copies with committed provenance; native capture/lifecycle remains the E004la implementation. No build-time include depends on experiments or local Windows-derived assets.

Run bash build.sh NEW_OUTPUT_DIRECTORY or bash tests/test.sh. Default binaries deny all live capture, including consumed boot identities. Tests admit only a fake token with linker-wrapped device operations; they do not load modules or access cameras. A future fresh, source-pinned one-shot candidate must explicitly bind its admission token and retain the existing host/boot/manifest/consumption guards. This consolidation grants no production/default activation.

Fixed accepted input/output geometries,2400-frame and210-second limits, strict V4L2 validation, bounded polls, signals and STREAMOFF checks are retained. It remains uncalibrated software processing, not a libcamera pipeline or Windows ISP equivalent. This userspace package is self-contained; the separate hardware/bootstrap package still has its documented local R4 requirement.
