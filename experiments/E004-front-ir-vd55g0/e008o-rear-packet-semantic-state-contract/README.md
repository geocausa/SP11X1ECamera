# E008o — rear packet-isolated semantic-state contract

Parent Git: `eb90c6148b7130be4710b3638085ad0a0f3b9210` (E008n).

Status: **BUILD-ONLY PASS — runtime denied**.

## Why this checkpoint exists

E008n closed command-DMA lifetime and one-shot retry policy, but a final audit
found that its inherited E008k preflight materializes all four E007y startup
packets through one shared `e007d_rear_register_state *` and one shared
`e007v_rear_dmi_state *`.

That shape is not sufficient for an actual rear startup:

- E006z startup bank selection is explicitly packet-phase dependent:
  `startup_phase & 1`, with phases 0..3.
- E007i LSC and E007q GTM handoffs are explicitly request-tagged.
- The accepted Windows startup corpus shows dynamic LSC/BF payload evolution
  across startup packets rather than one immutable payload image.

The old E008n/E008k shape was safe because it had no runtime call site, but it
must not be wired to hardware as-is.

## Contract

E008o introduces four independent packet semantic objects.  Each packet owns:

- one complete E007d register state;
- one complete E007v DMI state;
- its explicit request identity;
- an explicit readiness bit.

Validation requires the startup epoch, exact phase == packet index, coherent
request tag, valid PERIOD_CFG state and the complete recursive E007v DMI
contract.  Materialization consumes the four objects independently into an
unsubmitted E008l command arena.

This is intentionally a state **contract**, not a bootstrap policy.  It does
not invent AWB/AEC/AF/LSC/GTM values or copy captured Windows register/DMI
bytes.  The next gate is to provide a clean first-frame bootstrap producer for
these four semantic objects (or a narrowly justified semantic replay source),
then adapt the consumed one-shot runner to accept the packet-isolated set.

## Safety

No runtime entry point, MMIO, module load, camera activation or RT-CDM submit
is added.  `e008o_rear_runtime_authorization()` remains
`-EOPNOTSUPP`.


## Build result

A fresh isolated CAMSS build passed W=1 against the protected Golden headers.

- `qcom-camss.ko`: 14,691,296 bytes
- SHA-256: `038bcca30df2e6807d648d30ce1691dda460e6d56b3a13c7635d348216572ab0`
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- W=1 warnings/errors: 0
- retained symbols: `e008o_rear_materialize_commands`, `e008o_rear_semantic_recipe`
- PiMaster and independent Fabric verification: PASS
- install/load/camera/MMIO/RT-CDM submission/reboot: none
