# E005 front-provider HPM-only qualification, identity03

Hypothesis: the same isolated standard front providers that registered in
identity02 accept documented initial HPM requests without voltage or enable
requests. Golden remains the saved default and protected payload; a fresh
one-use service collects evidence then requests normal Golden return.

The independently published Denali OLED board graph sets initial HPM on
LDO7_B and LDO3_M. Its pinned source/parents are retained in identity01/02
preparation. Our E003b front identity source also set HPM for standard LDO7_B.
This experiment does not enable either rail or claim physical voltage/current
capability. No sensor, CCI, CAMSS, MCLK, reset or privacy node is added.

The new DTB differs from identity02 only by regulator-initial-mode=3 on the two
new child nodes. Every Golden node/property, reservation map and boot CPU is
preserved. Parent constraints and consumer ownership remain unchanged.
Candidate SHA256: 6da79578a9ef5644473ee0ce0c45d95e76f1e36a9126c9b8b25484df4c83491b.
Kernel/initrd are byte-identical deployed Golden7.1.5, not candidate23/24 7.2.

Pinned OF mapping: DT HPM3 -> REGULATOR_MODE_NORMAL2.
Pinned PMIC5 mapping: NORMAL2 -> hardware HPM7.
PM8010-M's pmic5_pldo502ln supports HPM only; its idle/retention requests reject.
Actual mode setter requests resource+8, value7, synchronous active-only state.
It changes its mode cache only after successful transport; duplicate mode
requests do not resend. Voltage stays cached while enable state is unknown.
Full generic OF/core/transport execution is not a hosted fixture claim.

audit-modes.py executes five actual callback bodies, actual mode tables and
header constants from old retained and candidate23 sources. Selected excerpts
are byte-identical. GCC/Clang ASAN/UBSAN each41 cases for each source:
first HPM, duplicate suppression, invalid modes, HPM-only rejection, timeout/
I/O failures and cache integrity. Mode transport functions are hosted models,
not hardware. Full source pins include the actual core/OF/RPMh/RSC/trace sources.

Trace acknowledgement interpretation is based on CMD_MSGID_RESP_REQ=BIT(8)
in the pinned RSC driver and the synchronous rpmh_write completion path.
The trace's 'complete' field is cmd->wait, not the overall synchronous request;
complete:0 can coexist with the response-request bit. Parser tests explicitly
cover that valid case and reject wrong HPM/state/response bit, voltage/enable,
duplicate/missing mode, malformed events and resource-address aliases.

The collector verifies both standard bindings, expected cache voltages,
zero users, exact parent links and logical mode 'normal'. It freezes only
kernel tracing after these checks, before reading the CPU rings; no regulator/
clock/GPIO operation is issued by the collector. All retained RPMh event lines
must parse, frozen CPU entries must equal parsed count, no drops/overruns may
exist, and exactly one active HPM7 response-request event per new resource is
required, with zero child voltage/enable events. Raw traces/debug logs stay on
SP11. Logical mode/cache and a successful synchronous request path do not
establish a physical mode readback or rated-current capability under load.

Cached Golden parents are BOB2=3.0V and SMPS4_C=1.856V, nominal cached differences
of200mV and56mV to the child target voltages. These are not electrical readings
or qualified dropout margins; neither parent is changed or enabled by this test.
Sensor sequencing, actual voltage/headroom, privacy and capture remain pending.

Eight DTB rejection controls, nine trace-parser rejection controls, scoped
RPMh schema and root-Golden/unprivileged runner refusals pass. First preparation
file-write failure was confirmed absent and retried before build/install;
its stage record remains. No failed preparation is hardware qualification.

Install requires clean pushed source, Golden guard and fresh unique assets.
Never reuse a consumed/armed identity. The service uses atomic consumption,
sealed asset verification and existing GRUB writer completion/order, then
token-guarded recovery on success/failure/timeout. Saved default stays Golden.
A kernel failure before the service requires an independent normal reboot to
the saved Golden path; no suspend/hibernate is allowed. Retirement archives
the one-use menu script and disables its conditional service after verified
Golden return. Both earlier identities remain consumed and retired.

Source base f75fd0bddb4a91ab57a29a4794f155eaebba9df6.
Stage /home/geoca/Documents/SP11-PROJECT/02-kernel/standard-front-providers-20261013-03.
Source audit /home/geoca/Documents/SP11-PROJECT/02-kernel/standard-front-mode-audit-20261013-01.
Hardware result pending. Both private startup consumers/all14 release categories
remain open. Functional independently reconstructed behavior is eligible;
copied proprietary camera firmware, blobs and vendor tuning/calibration stay out.
