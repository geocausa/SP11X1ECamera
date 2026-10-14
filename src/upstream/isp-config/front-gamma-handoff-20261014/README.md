# Front Gamma151 handoff — source and compile checkpoint

Reuses the existing native RGB12 validator, startup tone conversion and CDM
serializers. It adds only typed bank/table command preparation and a separate
enable command. No new tone algorithm, curve, profile, queue or allocator.

Exact original Gamma151 packer b394a0/builder b38dd0 independently establish
bank bit0 in both words at5f58/5f5c and enable bit0 at5f60. The builder emits
count3 at5f58 then selectors1/2/3 at5f08, each1024bytes. Its metadata offset is
in words; the DMI helper receives bytes. Owned source contexts, actual caller
restoration and immutable original instructions are checked.

New preparation emits only banks plus three DMI commands (52bytes). Activation
is a separate12byte command. This intentionally differs from the original
combined activation-before-DMI sequence; hardware ordering is NOT qualified.
The existing native backend's semantic G/B/R binding is reused. Here the DMA
allocation remains semantic R/G/B, so selectors reference offsets1024/2048/0.
No private instruction topology or captured address is copied.

The caller must independently prove immutable CPU/DMA correspondence, live
mapping, exclusive startup, frame/bank eligibility, DMA completion lifetime
and activation ordering. This compiler proves none of those. It validates the
whole3072byte extent and encoding before atomic command publication.
Bank values beyond0/1 are rejected rather than source-bitfield truncation.

Source/DMI channel binding is not optical verification. LUT12 encoding does
not prove physical CCM/CST/video sample precision. Zero software register
images are own policy, not hardware reset evidence. Full startup and both
private runtime consumers remain open.

No installation, load, camera access, MMIO, table submission or reboot.
Synthetic tables and source instructions remain on SP11. No vendor tuning,
profile, pixel or optical array is read or committed.

Qualification:34 original-code cases;2048 commands/3151 atomic negatives and
five compiled unsafe mutations each GCC/Clang ASan/UBSan PASS. Native ARM64
W1/Werror and header style0/0/0 PASS. Final native02/compile02; excluded
initial fixture/style attempts retained privately. Evidence in
`docs/FRONT-GAMMA-HANDOFF-20261014.json`; catalog115->117 configuration addresses.
