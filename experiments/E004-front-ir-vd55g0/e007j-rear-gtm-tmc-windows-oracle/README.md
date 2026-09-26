# E007j — rear GTM/TMC Windows oracle

Parent Git: ed72bb8e (E007i rear LSC DMI handoff PASS).

Status: **PREPARED / ONE-SHOT NOT YET CONSUMED**.

## Goal

Capture one bounded OV13858 rear 4K GTM/TMC sequence and determine the actual rear request-time law behind 0x5A08 selector1.

The GTM131 transform and Titan680 packing are already clean-room closed. The remaining unknown is the rear live TMC/ADRC request state. E006c proves rear GTM changes between consecutive steady requests, so front's post-R6 constant-GTM shortcut must not be reused without a rear oracle.

## Capture

The holder reuses the gated E007g rear stream: Surface Camera Rear / Color / VideoRecord / NV12 3840x2160.

It waits at WAIT_START; camera streaming starts only after SP7 external CDB has both GTM hooks armed and START.GO is created.

For R4..R18, the debugger captures only GTM common input (0x7c), interpolated region (0x404), flags (4), aux (2), the seven source-proven sparse TMC ranges, and the final 0x800 GTM output. No optical frame bytes are copied.

The entry hook fails closed unless the selected TMC pointer is non-null, generation is 5 and valid is non-zero. The post hook clears breakpoints, closes the log and detaches automatically at R18.

## Analysis

analyze-capture.py reconstructs only the sparse TMC state consumed by the accepted clean GTM backend, requires byte-exact 0x800 output replay for all 15 requests, then independently classifies R6..R18 TMC, GTM output, normalized common, region, flags and aux as stable, two-cycle or evolving.

No front steady-state law is assumed.

## One-shot discipline

The copied E007g holder keeps the consumed-entry marker and START.GO gate. The prepared identity is single-use. Persistent GRUB/UEFI boot order remains unchanged; only the temporary direct-Windows BootNext entry is used. After capture, SP11 returns to protected Golden Linux before offline analysis.

No Linux camera runtime, module load, DMI submission or RT-CDM submission is authorized by this oracle.
