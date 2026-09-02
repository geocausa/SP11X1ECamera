# Raw Windows camera oracle preservation — 2026-09-02

This checkpoint makes the small, irreplaceable Windows camera captures used by the E003h/0073 offline proofs durable on Linux before the broken Windows installation is eventually replaced.

Preserved sources:

- `windows-adaptive-live-20260902/` — same-stream request4/5/6 adaptive IQ capture already copied from Windows before the boot incident. Contains exact ISPInput snapshots, LSC common/staging payloads, request4 calibration meshes, and GTM/TMC state/output.
- `oracle-request6/`, `oracle-request6-matched/`, `oracle-demux-dgain/` — earlier exact Windows request6/demux oracle payloads and logs.
- `oracle-vss-20260902-local/` — recovered read-only from VSS store 2 (creation `2026-09-02 13:41:45.931474900 UTC`) at `\Users\Geoca\Documents\SP11CameraOracle\E003H_20260902_LOCAL`; 17 original files plus `SHA256SUMS`.

The later raw `E003H_20260902_LSCTRIGSRC` and `E003H_20260902_TINTCTX` directories were created after the last surviving VSS snapshot and were removed from the live profile by System Restore. Their directory metadata is gone, but a later read-only raw-NTFS carve recovered authoritative subsets under `oracle-carved-20260902/`: LSCTRIGSRC req5/6 x22+x23, TINTCTX req5 x1/input/output meshes, and TINTCTX req6 post-state. The accepted derived oracle JSON/proof documents still cover additional hashes/state that were not raw-carved. See `LSC-TINTCTX-CAMERA-IDENTITY-CORRECTION.md`; do not claim the entire deleted sessions were recovered.

All preserved `.bin` files are intentionally force-added despite the repository-wide binary ignore rule because they are authoritative parity evidence, not generated build debris.
