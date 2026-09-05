# E003i-P live Tintless statistics correlation — 2026-09-05

Status: prepared; no new runtime result yet.

## Authorization and scope

The user explicitly authorized needed tool downloads/installation, Linux/Windows reboots, KD, ETW/ETL, Ghidra, static/dynamic analysis, and discretionary Git checkpoints on 2026-09-05. Scope remains SP11, SP7 and PiMaster. Golden protection and evidence discipline remain in force.

## Experiment

Base commit: 82fc092c9f17c20e9c9319405eb2520a0f88b322.
Hypothesis: the Windows front Tintless consumer uses a deterministically delayed completed TL_BG statistics generation. The inferred four-request delay is not yet authority.

Use existing SP11 Windows gated two-cycle helper and SP7 KD. Persist an on-disk debugger log before process-scoped observation of the Titan680 parser and Tintless wrapper. Re-resolve process/module addresses. Record ordered parser count, raw/output pointers and consumer stats pointer; inspect exact request identity where available. Pointer equality alone does not prove a numerical request delay.

Expected evidence: an ordered trace that establishes stats producer/consumer correspondence and distinguishes directly observed ordering from inferred request numbering. No Linux camera MMIO, module or DT changes in this experiment.

Preflight: SP11 Golden 7.1.5-sp11-render-parity-v4+, saved_entry=sp11-audio-fullio-v19c, next_entry empty; camera modules absent. Existing EFI 0006 resolves directly to Microsoft bootmgfw.efi. Use one-shot BootNext only; preserve BootOrder.

Rollback: stop the capture, remove debugger breakpoints, resume/detach KD, restart SP11 through unchanged default GRUB/Golden. Verify Golden command line, empty next_entry, unloaded camera modules and PiSlave reachability.

Raw logs/captures remain on lab disks outside tracked Git. Publish derived findings and hashes only.
