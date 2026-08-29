# E003h Linux VFE1 BUS recipe — compiled, retained, unreachable

Date: 2026-08-29

`0017-x1e-vfe1-pix-bus-unreachable-recipe.patch` compiles the newly closed Windows BUS lifecycle and dynamic-address semantics into `camss-vfe-680.c` without creating a runtime path.

## What the recipe represents

The private recipe is restricted to X1E80100 full IFE1 (`vfe->id == 1`, non-Lite). It retains the Windows client order:

`WM0, WM1, WM2, WM3, WM11, WM18, WM12, WM14, WM13`

which corresponds to:

`FULL Y, FULL C, DS4, DS16, AEC_BE, RS, BHIST, AWB_BG, TL_BG`.

The recipe has three private entry points:

- `prepare`: validate all caller-supplied DMA IOVAs, program the retained session-static client contract, enable all resources in Windows order, then program the initial dynamic addresses;
- `update`: recompute and program only dynamic image/meta addresses for a later queued buffer set;
- `stop`: clear the client enable bit in the same Windows resource order.

`prepare` intentionally matches the newly captured Windows MMIO lifecycle: **config -> enable -> initial addresses**. It does not submit RT-CDM or claim `ISP_START_DONE`; those remain a separate higher-level lifecycle layer.

## Dynamic addresses are Linux-owned

The input structure contains `dma_addr_t` values for the Linux allocations:

- one QC10C allocation;
- DS4;
- DS16;
- AEC_BE;
- RS;
- BHIST;
- AWB_BG;
- TL_BG.

Before any MMIO write, the helper rejects any derived address that cannot fit the 32-bit VFE BUS address register. FULL addresses are derived only from the accepted QC10C offsets:

- WM0 `META_ADDR = qc10c + 0`;
- WM0 `IMAGE_ADDR = qc10c + 0x6000`;
- WM1 `META_ADDR = qc10c + 0x4f2000`;
- WM1 `IMAGE_ADDR = qc10c + 0x4f5000`.

Auxiliary clients receive their own caller-supplied image IOVAs. No captured Windows IOVA is present in the source. The observed Windows `0x76c000` QC10C ring slot stride is also absent; Linux will use each queued DMA address rather than imitate the Windows allocator.

## Static client configuration

The retained `0016` Windows client contract supplies the stable client values. `0017` adds the missing BUS register names needed to compile the recipe, including `IMAGE_ADDR +0x04`, `META_ADDR +0x40`, metadata/mode/control/lossy fields and the existing frame/packer/drop configuration.

Client CFG is programmed with bit 0 clear. Windows' exact `0x1d830` routine is modeled by a later read/modify/write of bit 0, preserving the static mode bits. FULL is therefore toggled WM0 then WM1, followed by the auxiliary resource order.

The per-client stable field values are still the same-machine values retained by `0016`; no Qualcomm default is promoted to authority by this patch.

## Runtime isolation

`inspect_vfe1_bus_recipe.py` mechanically requires:

- patch scope is only `drivers/media/platform/qcom/camss/camss-vfe-680.c`;
- exact client order `0,1,2,3,11,18,12,14,13`;
- exact `prepare` MMIO phase order `config -> enable -> dynamic addresses`;
- `update` is address-only;
- `stop` disables through the same ordered helper;
- X1E IFE1/non-Lite target gate;
- no captured Windows IOVA or Windows slot stride in Linux source;
- existing X1E VFE1 PIX `-EOPNOTSUPP` gate remains before stream lock/IRQ/output setup;
- the normal `vfe_ops_680` table has no reference to the recipe;
- exactly three `R_AARCH64_ABS64` relocations retain `prepare/update/stop` from the private `__used` table;
- no compiled code/data relocates to the private recipe table itself.

The inspector passes. Its SHA-256 is `db54f0feec5948c68cf6450a1d424f1c447fcf8444c203671cf295aabefbd09d`; inspection JSON SHA-256 is `92715605c99523366dd619331c6abe9bb09c7e6476bf8921ccb5b18cbaae262e`.

## Build and reproducibility

- patch SHA-256: `55e88685bf71fff5ba74ceb53972b28f71c6c9120659cd756847d8308a7b2d5e`;
- `qcom-camss.ko` SHA-256: `44b9233d668cad0eb8da3c7805845d006ee3bd000ef17a5e2173fac9846783ef`;
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- compiler warnings/errors: none;
- patch forward/reverse dry-run and byte reconstruction: PASS;
- checkpatch code/style findings: zero; only non-mail patch metadata (description/Signed-off-by) is absent.

The module was not loaded. There are no `/dev/video*` or `/dev/media*` nodes on Golden. No VFE1 PIX register was touched by Linux, no RT-CDM command was submitted, no sensor stream write occurred, and no frame was attempted.

## Remaining gate

The BUS transport mechanics are now statically representable, but the generic CAMSS output model still owns only one WM/buffer queue and cannot yet manage one QC10C VIDEO surface plus independent DS4/DS16/statistics allocations/completions. The next static step is therefore **buffer/completion ownership architecture**, not a runtime frame: connect the already-proven one-surface FULL completion model and auxiliary allocation lifetimes to a private/unreachable PIX output state machine, then combine it with the unreachable RT-CDM/IQ recipe. Runtime remains blocked.
