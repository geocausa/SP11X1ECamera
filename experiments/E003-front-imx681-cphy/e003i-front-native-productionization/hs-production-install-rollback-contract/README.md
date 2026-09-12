# E003i-HS — production install-image transaction and rollback contract

Status: **PASS / offline only**.

HR closed repeated-open behavior and produced the deterministic runtime package. HS adds a deployment transaction tool without changing that runtime package. `src/front-imx681/install-package.sh` requires an explicit staging root and target root; targeting `/` is refused unless `--allow-real-root` is explicitly supplied.

Install verifies the package manifest before creating target install state, pre-stages the new prefix/wrappers, preserves any previous install in a rollback directory, atomically switches the stable prefix/wrappers, and records the installed package-manifest SHA. One-step rollback restores an existing installation byte-exactly or removes a fresh installation entirely.

Offline tests cover existing-install roundtrip, fresh-install rollback, corrupt-package rejection before any target mutation, real-root refusal, package-manifest continuity from HR, and zero camera-device opens. The protected Golden system is not modified by HS.
