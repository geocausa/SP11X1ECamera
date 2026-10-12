# X1E public PHY/platform dependency checkpoint, 2026-10-12

Candidate16 combines the pinned 74-patch IFE RFC and project CAMSS patches
0001..0009 with twelve public dependency patches: CSI2 PHY v17 (2),
CAMSS PHY API v17 (5), and platform DTSI v6 (first 5 of 13). Eight unrelated
board patches were retained in the lab archive and were not selected.

The original decoded patch bodies are byte-pinned in
`x1e-dependencies-20261012/manifest.json`. Message IDs, authors and public
mbox URLs identify the original publications. Transport mbox envelope
timestamps are not stable content pins. Preserve the original authors,
licenses and trailers. They do not certify review of our integration or
context adaptation. No project signoff or upstream acceptance is claimed.

Only two contexts in CAMSS PHY API patch4 were rebased: the Kconfig select
retains the RFC's V4L2_ISP/VMALLOC dependencies, and the camss.h insertion
retains camss_buf_done_info. Additions/deletions are identical to the original;
the three other file diffs are unchanged. The original and adaptation are
separate pinned files. Fuzz is disabled during replay.

Reproduce from an immutable source tree containing the pinned RFC and own
patches0001..0009:

```sh
python3 -B tools/prepare-upstream-x1e-dependencies.py \
  --parent-source /path/to/candidate14-source \
  --output-source /path/to/fresh-candidate16-source
python3 -B tools/test-upstream-x1e-dependency-pins.py \
  --parent-source /path/to/candidate14-source
```

Replay changes16files and verifies47 unchanged CAMSS/ISP files, including the
CDM power/reset backend. The importer breaks hard links for every patch target.
It retains failed output directories and refuses existing paths. Untouched
files share hard links with the immutable parent: use a separate `O=` build
directory, and unlink a source file before any later edit. Eighteen modified,
missing and symlink reference controls reject before output creation.

Four AArch64 targets compiled with W=1 and KCFLAGS=-Werror, zero warnings:
CAMSS, generic ISP, PHY core and standalone Qualcomm CSI2 PHY. Targeted binding
schemas and examples passed; the Denali OLED DTB built and passed validation
limited to the X1E CAMSS and CSI2 PHY schemas. Camera nodes remain disabled.
These checks do not qualify a board sensor graph or camera hardware.

The full ARM64 Image/modules and modpost build passed (kernel7.2.0). CAMSS
and standalone PHY modules are AArch64 with matching vermagic. The full build
has1153 warnings, all in baseline-identical source files; camera/PHY/ISP
warning count is zero. This is source/link qualification, not a boot result.
The full Image/modules qualification is recorded separately in
`docs/UPSTREAM-X1E-DEPENDENCIES-VALIDATION-20261012.json`. Initial global
-Werror attempts failed on unmodified ARM64 syscall initializers and VLAN/Xen
format-truncation diagnostics, then Samsung serial format-overflow warnings.
Each failure was reproduced on the pinned baseline. The follow-up is a normal
full-kernel W=1 build without global -Werror; the scoped camera/PHY object
checks used strict -Werror with no exceptions.
Failed attempts, baseline controls and logs remain on SP11.

The published standalone driver supports D-PHY. It does not yet implement
SP11's C-PHY mode. The next work is a typed C-PHY configure contract, validated
logical trios and symbol-rate units, a public GPL CSIPHY2.1.2 sequence, reviewed
CSID routing, and the board's sensor/power graph. CDM provider wiring and
physical command/image retirement remain separate open requirements.

See `../phy/CPHY-RATE-AUDIT-20261012.md` before porting the C-PHY v9 fallback.
Both installed private startup consumers and all14 readiness blockers remain.
No kernel/module/DT installation, boot, capture, service or OS sleep changes.
