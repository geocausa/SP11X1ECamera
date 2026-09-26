# E006g — unreachable rear RT-CDM materializer skeleton

Parent Git: 29e5e99c (E006f duplicate cleanup; authoritative E006f is 94cd3c50).

Status: STAGED / COMPILE-ONLY. No runtime authorization.

## Objective

Convert the E006a rear RT-CDM structure and E006d/E006f producer ownership into a compiler-visible Linux contract without loading or calling it.

The skeleton encodes:

- startup BL byte-length vectors:
  - 4/f1c/4/3c
  - 4/ebc/c/4/10/14
  - 4/a00/c/4/10/14
  - 4/658/c/4/10/14
- steady six-BL shape 4/MAIN/c/4/10/14;
- exact steady DMI identity/length sets for MAIN AC8, A98, 8F0, 658;
- explicit producer boundaries:
  - LSC411/Tintless for 0x4308 selectors 1/2;
  - exact Surface LSC wire alias for 0x4708/1;
  - GTM131/TMC for 0x5A08/1;
  - BFStats25 AF-request producer for 0xBC08/1,2;
  - separate stable-payload provider for cross-variant-stable identities.

No raw Windows command/payload bytes, pointers or IOVAs are embedded.

## Safety

camss-e006g-rear-materializer.inc is injected only into an isolated copy of accepted CAMSS source for compilation. A retained static recipe keeps the functions compiler-visible, but no probe, stream, ioctl, VFE, RT-CDM, module-init or MMIO path references the recipe.

The build script never installs or loads the resulting module.

Native rear Linux processed ISP remains DENIED.
