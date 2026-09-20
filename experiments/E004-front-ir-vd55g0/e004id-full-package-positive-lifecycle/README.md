# E004id — current full-package positive lifecycle

PASS on SP11 ARM64, 2026-09-20. Closes the positive current-package
validation gap explicitly left by E004ib installer hardening.

The maintained hardware builder reproduced every current pinned hardware
artifact using the accepted kernel source and prepared build tree. Current
package staging and verification passed. The actual maintained installer
then passed fresh install and same-package reinstall, with installed checksums
and nonactivation verification after each. Actual uninstall removed both
managed library roots and preserved unrelated etc and var/local sentinels.
All destinations were beneath a fresh private user-owned /tmp directory.
No root privileges, live installation, camera activation or reboot occurred.
Golden/idle overlap guards passed before and after on the same boot.

This uses current HEAD inputs, not historical E004dw package bytes: later
accepted front-capture changes altered the current capture and manifest
hashes. Both historical evidence and current hash gates remain unchanged.
Exact input and output digests are recorded in RESULT.json.

No code change was required. This is package lifecycle evidence only, not
new optical capture, image-quality parity, IR illumination safety, biometric
authentication or legitimate SecurePD admission evidence. Those blockers
remain open. The preflight's documented concurrency limitation remains.
