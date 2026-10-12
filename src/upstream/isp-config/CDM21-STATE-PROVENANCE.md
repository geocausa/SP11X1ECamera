# CDM 2.1 FIFO and reset observations, 2026-10-12

`sp11-cdm21-state.h` is an independently written driver-internal source helper,
not a CAMSS hardware provider or submission ABI. It performs no MMIO, reset,
allocation, firmware read, submission, unmapping or free.

## Exact public source

The eight GPL files in
`../camss/cdm-lifetime-reference-20261012.json` are archived on SP11 from
Qualcomm's camera-driver revision
`3f5ef25e12b501a518d2d4f4a870288e9bb127a0`. Tree SHA, file sizes,
Git blob SHA1 and SHA256 were checked. The hosted test requires the three
specific unchanged input files used by its oracle.

The public `cam_cdm_hw_reg_2_1.h` declares four FIFO/IRQ contexts and two
pending registers, at 0x6c/0x70. Each register contains two nine-bit counts,
at shifts 0 and 16. The unchanged public function
`cam_hw_cdm_bl_fifo_pending_bl_rb_in_fifo` is the decoder oracle, compiled
with its two actual descriptor initializers and test-only types/MMIO.

The generic public FIFO limit is ten; CDM 2.1 implements four. The new helper
decodes exactly four and accepts only the public version 0x20010000.
That version is the expected value in the existing daily source admission
check; this checkpoint made no fresh hardware version read.

Public completion masks are reset=1, inline=2 and BL_DONE=4. The public IRQ
handler counts reset bits across the four IRQ contexts in one invocation and
completes when all four are present. The own observation helper accumulates
four unique bank bits in a serialized software epoch, so split observations
and duplicates cannot accidentally satisfy a count-based predicate. Its reset
state policy is stricter: any bit outside reset/inline/BL_DONE, including error
or flush bits, latches a fault. This policy is independently tested, not a claim
that the full public IRQ handler was compiled or that split delivery occurs
on this SP11.

The public 2.1 descriptor has no `cdm_status` register. The common public
pause helper consequently has no pause-complete polling on this revision.
CDM 3.1 status fields are not accepted as substitutes.

## Observation and ownership contract

The caller must own the device and serialize these operations. Before beginning
a reset observation it must separately mask all four IRQ banks, read back,
drain the handler, clear old status, verify clear, and issue/observe a fresh
hardware transaction with correct ordering. An epoch is software bookkeeping;
it cannot establish the age of a hardware IRQ. Unique epochs must increase;
active observations cannot be rearmed, and closing retains the epoch to prevent
reuse. Late faults invalidate a previously complete observation until close.

Two pending-register reads are not necessarily an atomic snapshot. Zero FIFO
counts do not prove absence of a command being fetched, outstanding bus writes,
producer activity or IRQ work. Four reset acknowledgments do not, by themselves,
certify DMA lifetime. There is deliberately no `retireable` or release API.

The provider still needs hardware-specific reset/stop ordering, ownership of
submitted command buffers and image buffers, active-fetch/bus retirement,
drained IRQ work and timeout quarantine. This helper is not wired into either
daily driver. The existing daily stop source masks CDM IRQ and closes software
ownership; its separate completed-transaction/ledger checks must be considered
in any audit. No conclusion that earlier hardware tests are invalid follows
from this source checkpoint.

## Validation and reproduction

Evidence: `../../../docs/UPSTREAM-CDM21-STATE-VALIDATION-20261012.json`.

From the repository root, supply the three exact GPL reference files:

```sh
python3 src/upstream/isp-config/test_cdm21_state.py \
  --reference "$SP11_CDM21_REFERENCE" --output "$SP11_CDM21_NEW_RESULT"
```

The output path must not exist. GCC and Clang each run ASAN/UBSAN:
12,048 pending snapshots (all 512 values in each FIFO with reserved bits set,
plus 10,000 deterministic mixed snapshots), 24 bank-order sequences,
partial/complete fault cases, duplicates, stale epochs, wrong version,
overlap, null arguments and epoch exhaustion. Each run passes 111,298
assertions; assertion count is not a count of independent physical tests.
Nine changed/missing/symlink reference fixtures are rejected. Attempt01 and
attempt02 results are retained; attempt02 adds explicit public IRQ-mask checks.

The compile-only probe is copied with both headers to a new SP11 staging
directory and built against prepared candidate08:
```sh
make -C "$SP11_KERNEL_SOURCE" O="$SP11_KERNEL_BUILD" \
  M="$SP11_CDM21_PROBE_STAGE" ARCH=arm64 W=1 KCFLAGS=-Werror sp11-open-cdm21.o
```
The stage requires `Makefile`, `sp11-open-cdm21.c`, `sp11-cdm.h` and
`sp11-cdm21-state.h`. The AArch64 relocatable object passes with zero warnings,
and header/probe checkpatch passes with zero errors/warnings. Its only undefined
symbol is stack protection. This is an object check, not modpost, a full kernel,
an installed module or hardware qualification. Never load this probe.

Both installed private startup consumers remain. All fourteen upstream
readiness components remain blocked. Golden, services, boot, camera orientation
and original evidence are unchanged; no capture, reboot or runtime change.
