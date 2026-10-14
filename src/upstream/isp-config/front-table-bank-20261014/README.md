# Front LSC/ABF bank configuration

Reuses retained bank-pair ownership and CDM serialization, without calibration,
table generation, allocation, queue or request-scheduling changes.
New typed32byte configuration emits4358/435c LSC and4958/495c ABF pairs only.
Each field admits0/1 and owns zero reserved bits. No module enable or DMI transfer.

Complete original LSC packer b3d8a0 and ABF packer b41090 execute unmodified
with owned synthetic inputs and output tables. Existing builders b3cda0/b404f0
then observe their fixed register command arguments. No arithmetic/branch shims,
constructor or original serializer execution. ABF descriptor fields4/8 select
owned0/0 contexts; source requires them below2/3. Initial fixture treated field8
as a pointer and later used excluded2/3 values; these were fixture errors,
not camera failures or accepted original contexts. Object80 stores the ABF
table pointer; owned metadata is checked rather than permitting a whole object.

This qualifies the bank fields, not the rest of the synthetic zero configuration.
Source LSC gains are14+14 bits; measured fit-lsc deliberately admits a narrower
13-bit subset. Existing table validator's13-bit rule is generator policy, not a
claim that hardware fields are13-bit. The vendor tuning-dependent old E003i-K
backend is functional packing evidence, not new policy/default data.

Retained E006z differentiates startup and steady: startup all bank families
use phase parity; steady LSC/Gamma use request parity and ABF uses the opposite.
The new compiler accepts explicit parent-owned bank values and never reimplements
that schedule. These source rules still require binding to the native startup
and frame provider, live bank eligibility and DMA/completion lifetime.

Whole zero-reserved images are independently chosen software policy, not reset
or inherited-private-profile equivalence. Full mesh geometry, LSC/ABF module
controls/configuration, core/input/precision and runtime integration remain open.
No install/load/camera/reboot/tuning/profile/pixel access or optical data export.

Qualification:50 full original source calls,12 source comparisons and2081
atomic negatives/five compiled mutations each GCC/Clang ASan/UBSan PASS.
Native ARM64 W1/Werror and style0/0/0 PASS; native01/compile01. Evidence
`docs/FRONT-TABLE-BANK-20261014.json`. Catalog117->121, not a complete startup.
