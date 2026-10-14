# Front video Crop12 binding reuses retained coordinate compilers

E006p and sp11-geometry-stats.h already generate the four crop coordinates.
They remain unchanged. The new wrapper selects only the calibrated front
output2560x1440, with1280x720 chroma, by the existing geometry policy and
copies the existing two Crop12 commands. It emits32 bytes at0x9c68/0x9e68
count2, with no module or extra CFG command.

Original Crop12 Titan680 packer0xb57980 and builder0xb57740 execute on SP11
in the retained native mapper/caller fixture. Object48=1 selects Video Full;
object48=0 selects display0x7c68/0x7e68 and is a checked counterexample.
Original constructors/live routing are not claimed. The selector is owned
metadata; command addresses are source-fixed, never substituted.
Metadata16/24 point to owned luma/chroma rectangles in first_pixel,first_line,
last_pixel,last_line order. The selected video image is its first16 bytes;
the display slot at16 is preserved. Only object40's exact source metadata
store and selected-image writes are allowed.

31 source cases cover24 comparisons across eight dimensions and three
placements, the display counterexample, unchanged request output-depth
declarations8/10/12/14 and a nonzero-image residual counterexample.
Both retained coordinate compilers agree under GCC/Clang ASan/UBSan:
3 calibrated cases admitted,21 other dimensions rejected,36 atomic
negatives and three compiled unsafe mutations each pass. SP/X19..29/D8..15
restoration, canaries, immutable original PE/inputs and unused slot checks
pass. Only0x85ee78 command observation/success is intercepted; original
arithmetic/branches run unchanged and actual serialization is not executed.
Native ARM64 W1/Werror and header style0/0/0 pass; native01/compile01 accepted.

These are source geometry contracts, not physical input-depth evidence,
hardware reset, inherited-profile equality or runtime format negotiation.
No colour/module/Gamma/DMI/startup lifetime integration, install/load,
camera, reboot, private profile/tuning/pixel read or calibration change occurs.
Existing unified48/libcamera21/run93/v15 and Golden are preserved.

This adds4 addresses to the catalog111->115, following the complete CCM
checkpoint. The independent startup remains incomplete and both private
runtime consumers remain. See docs/FRONT-CROP-CONFIG-20261014.json.
Next finish core/Gamma/module/precision and startup around proven native
lifetime, replace private loading only in a fresh isolated candidate, then
qualify actual physical/image parity.
