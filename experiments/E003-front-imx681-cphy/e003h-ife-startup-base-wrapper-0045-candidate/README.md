# E003h — IFE startup base wrapper 0045 one-shot candidate

This package carries the static 0045 correction for the Windows-proven RT-CDM IFE startup base wrapper. Every startup packet 0..3 is preceded by a Linux-owned four-byte `CHANGE_BASE(VFE1)` BL (`0x0800f000`) while the captured startup main bytes, CSID companion ordering, selector-2 priming and steady Epoch0 batching remain unchanged.

The runtime assets are frozen locally on SP11 and hash-pinned by `asset-manifest.json`. Binary `.ko/.dtb/.bin` assets remain ignored by Git; the manifest, scripts and inspection records are durable Git evidence.

Candidate identity:

- GRUB ID: `sp11-camera-e003h-ife-base-0045-one-shot`
- boot directory: `/boot/sp11-7.1.5-camera-e003h-ife-base-0045`
- command-line marker: `sp11_camera_e003h_ife_base_0045=1`
- CAMSS SHA-256: `cfdd66c9d2c56533993f5f73831d77b3f5018c1d552183da634971378aa06923`
- front-only DTB SHA-256: `019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f`

`preflight.sh` is a package-only Golden gate and rejects any `AUTHORIZATION.json`. `install-candidate.sh` copies only the Golden kernel/initrd and the pinned front-only DTB into a new boot directory, installs a distinct GRUB entry, and never calls `grub-reboot` or writes `next_entry`.

`load-candidate.sh` calls `runtime-preflight.sh` before any camera module load. Runtime preflight requires a separately committed authorization whose package commit is an ancestor of the current synchronized branch, exactly one candidate boot, exactly one root helper invocation, persistent RT-CDM observation, and no same-boot retry. `run-once.sh` independently repeats the critical authorization/provenance/hash/observer gates and invokes the helper exactly once before archiving evidence and returning immediately to Golden.

**No runtime is authorized by this package.** The package is installed and inspected unarmed first. Any hardware run requires a separate authorization checkpoint after the package commit is public.
