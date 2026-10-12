# Bounded X1E C-PHY receiver source checkpoint

This series adds a typed generic PHY C-PHY options proposal, ports independently
observed ooaklee register transactions into the newer standalone Qualcomm PHY,
and connects the matching CAMSS RAW path. It preserves the project's existing
allocator, completion, reset and dormant CDM ownership work.

The typed API is proposed source for review, not an accepted upstream ABI.
The observed header is unchanged GPL source pinned at both public revisions:
64999b9fc6e60ebccdc3755563cafcc63930cc90 and
2cbd1ec3e2da385e7bd91fd65c63ba5a8fb5b865 in
https://github.com/ooaklee/linux_ms_dev_kit-sp11.
Its author declares independent runtime MMIO transcription. Original comments
and attribution remain. See the prior reverse-engineering audit and source
reference JSON; a public license alone does not prove derivation.

| Runtime admission | Value |
| --- | --- |
| Physical PHY / extent | PHY2, 0x0ace8000 / 0x2000 |
| Trio / wire order | one physical trio 0, ABC |
| Symbol rate | 2,406,000,000 symbols/s |
| Explicit sensor link frequency | 1,203,000,000 Hz |
| Core / timer clock | 480,000,000 / 400,000,000 Hz |
| CAMSS route | PHY2 to X1E CSID0 |
| CSID RX CFG0 | 0x11300000 |
| VFE RDI writer config | 0x00010001, packed MIPI RAW |

Other rates, trios, permutations, polarity fields, physical instances and
clock rounding results are rejected before receiver MMIO. The binding describes
the generic three-trio hardware capability; runtime admission remains one trio.
The project's qualified 2.400 Gsymbol/s mode is not silently treated as 2.406.
Its measured timing, 24-bit frame-length ABI and calibration remain intact.

Startup performs the 138 observed initialization writes followed by 24 stale
IRQ-clear writes before enabling the exclusive Linux IRQ. Shutdown synchronously
disables/drains that IRQ while clocks remain on, masks 11 sources, clears 24
registers and performs the three observed shutdown writes before dropping power.
Modeled failures unwind only acquired provider references. These checks do not
prove physical IRQ concurrency, receiver retirement or streaming DMA teardown.

CAMSS passes explicit link frequency through typed symbol-rate options, preserves
D-PHY behavior, selects the observed C-PHY RX word and leaves unconfigured RDI
crop/drop engines disabled. The VFE RDI writer enables packed MIPI RAW.
The imported standalone IMX681 source includes the two previously qualified PM
and group-hold fixes; its mode data is unchanged. Sensor endpoint/xclk, measured
VT timing and frame-length reconciliation remain open.

Validation: five ARM64 objects with W=1/-Werror, zero warnings; same-source
receiver and sensor external modules with real modpost/link and pinned full-build
symbols, zero warnings; GCC and Clang ASAN/UBSAN each 448 provider and 488 CAMSS
cases; 12 actual binding controls; five patches replay across all 20 changed
files. Portable preparation also checks unchanged parent source pins. Final
export changes only Kconfig help text after the candidate19 build; a fresh
olddefconfig proves the config is byte-identical, and portable host tests run
against the final replayed source. No new full Image has been built.
Candidate16 remains the latest complete Image/modules build.

Checkpatch without certification checks and with the new-file advisory separately
reviewed is clean. Standard check retains missing certification/new-file review.
Existing generic PHY/Qualcomm entries must be reviewed, and the new sensor needs
a willing maintainer before submission. No authorship, signoffs, review tags or
submission acceptance are fabricated.

From the project repository, with the qualified candidate17 kernel source:

~~~sh
python3 tools/prepare-upstream-cphy-receiver.py --parent-source /path/to/candidate17/source --output /path/to/new-source
python3 tools/test-upstream-cphy-receiver.py --source /path/to/new-source --parent-source /path/to/candidate17/source --output /path/to/new-provider-tests
python3 tools/test-upstream-camss-receiver.py --source /path/to/new-source --parent-source /path/to/candidate17/source --output /path/to/new-camss-tests
make -C /path/to/new-source O=/path/to/new-build ARCH=arm64 DT_SCHEMA_FILES=phy/qcom,x1e80100-csi2-phy.yaml dt_binding_check
/path/to/schema-venv/bin/python tools/test-upstream-cphy-binding.py --source /path/to/new-source --build /path/to/new-build --output /path/to/new-binding-tests
~~~

Use the existing compatible ARM64 config and dtschema environment for the binding
command. Outputs must be fresh and outside the source/repository; mismatched,
missing and symlinked pinned inputs are rejected. Failed attempts remain on SP11.

This is source qualification. No board camera graph is enabled, and nothing is
installed, booted, loaded or captured. Both existing private startup consumers
and all 14 readiness gates remain. Next: qualify the sensor/power graph (including
the normal-regulator boot issue), build a compatible full candidate and obtain a
fresh open RAW stream with guarded stop/reopen. Hardware ISP/NV12 remains the
target; continue its ownership/physical retirement work separately and reuse
the existing independently measured/generated calibration. Directly extracted
Windows calibration, vendor tables and blobs remain excluded.
