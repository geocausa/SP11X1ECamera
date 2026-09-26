# E007f — rear DMI provider integration

Parent Git: `cccb9517` (E007e BFStats25 DMI encoding PASS).

Status: **STAGED / COMPILE-ONLY**.

## Goal

Bind the proven E007e BFStats25 selector-1/2 encoder into the existing E006g rear DMI materializer without collapsing the remaining upstream producer boundaries.

E006g deliberately uses one opaque `ctx` for all DMI producers. E007f supplies the missing adapter layer so each producer family can retain its own semantic state.

## Integration model

`e007f_rear_dmi_state` contains:

- separate LSC/Tintless context;
- separate GTM/TMC context;
- separate stable-payload context;
- concrete E007e BFStats25 semantic DMI state.

The E006g callback table is bound as follows:

- LSC selectors -> explicit upstream LSC callback;
- GTM selector -> explicit upstream GTM callback;
- BFStats25 selectors 1/2 -> **E007e clean encoder**;
- stable DMI identities -> explicit upstream stable callback.

E007f then calls the existing E006g `prepare_dynamic` and `fill_slot` functions unchanged.

## Fail-closed behavior

The integration validator rejects:

- missing upstream LSC/GTM/stable callbacks;
- BF ROI state that does not contain the required 25 records;
- invalid/missing BF gamma state.

Therefore the presence of a completed BF encoder cannot accidentally make the still-open LSC/GTM/stable families look complete.

## Boundary

This closes the **BFStats25-to-E006g DMI binding**. It does not yet close:

- LSC/Tintless live DMI production;
- GTM/TMC live DMI production;
- stable-family clean payload production;
- BPC/ABF, Gamma, DSX and mode-dependent PDPC DMI production;
- BF AF ROI/gamma policy and request-state scheduling;
- upstream PERIOD_CFG transport-state derivation.

No DMI or RT-CDM command submission is added.
