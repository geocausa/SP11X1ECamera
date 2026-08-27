# SP11 camera boot-parameter audit

Audited on 2026-08-27 after the Windows rear-camera oracle session, after returning to the protected FullIO v19c Golden.

## Golden policy

Do not edit the Golden v19c boot entry to make camera work easier. Camera candidates inherit the known-good baseline initially, then must pass an otherwise-identical strict-validation boot before a stage is called accepted.

### Permissive bring-up boot

The existing Golden/camera command line contains:

- `clk_ignore_unused`
- `pd_ignore_unused`
- `cma=128M`
- `efi=noruntime`
- `crashkernel=...`

`clk_ignore_unused` and `pd_ignore_unused` only suppress the late-init sweeps that turn off unclaimed clocks and unused generic power domains. They do not disable normal driver/runtime-PM clock or power-domain transitions. They are therefore useful during first hardware bring-up, but can mask a missing DT clock/power-domain consumer.

### Strict validation boot

Once a camera gate passes under the permissive command line, repeat the same candidate with **only** `clk_ignore_unused` and `pd_ignore_unused` removed. Do not promote the gate to accepted if it depends on those two flags.

## Other audited parameters

- `cma=128M`: not a direct CAMSS capture-buffer limit in this kernel. X1E CAMSS uses `vb2_dma_sg_memops` and the ARM SMMU runs translated DMA domains. Keep 128 MiB unless measured pressure proves a reason to change it.
- `efi=noruntime`: disables EFI runtime services; it does not block Linux firmware loading, CCI, CAMSS, CSIPHY or V4L2.
- `crashkernel=...`: reserves RAM but is useful for risky hardware bring-up and should remain enabled.
- `quiet splash`: affects observability only, not camera function.
- `mshw0485_touch.*` and `soundwire_qcom.*`: real module-qualified parameters for the known-good touch/audio stack; no camera dependency was found.
- bare `sp11_*` markers: the kernel reports these as unknown command-line parameters and passes them to userspace. They are not camera kernel controls.

## Conclusion

No current GRUB parameter blocks CCI/CAMSS binding. The only camera-specific validation concern is that `clk_ignore_unused pd_ignore_unused` can hide incomplete DT ownership. Use them for first bring-up, then require a strict boot without them.
