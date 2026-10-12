# VFE680 input and output source audit

The interrupted October 11 audit was resumed on October 12. Checkout
26fac4b1b1e398e3526596d11a5122136ed46daf was clean and synced; the boot ID remained
936d7197-d2ee-415d-a907-450a2e7b9cb2. No unfinished audit/build process remained.
The cached public references survived and all 21 selected source files passed
their recorded SHA-256 checks. No private file, tuning value or camera pixel was
read. No camera, module, DT, service, boot or system-power setting changed.

## References and hardware dispatch

The older GPL mirror is KleeUI/android_vendor_qcom_opensource_camera-kernel at
c5ebe7e7f68b97b7669711c6c0b060e9ec0f5cf5. Ten selected files are retained in
/home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-vfe680-input-public-20261011-02,
with reference-v2.json. A first inventory that requested a nonexistent generic
cam_vfe_camif.h was stopped; its tree and failure remain in stage01. The actual
versioned files were selected afterward. No source was invented for that name.

The stronger reference is Qualcomm's published camera-driver at
3f5ef25e12b501a518d2d4f4a870288e9bb127a0, tree
27e77a604ec38e82dcc0cd30d7685679b0f91ebb. Eleven GPL-labelled selected files,
819024 bytes, are pinned by path, size, Git blob and SHA-256 in
src/upstream/isp-config/nv12-bus-reference-20261012.json. The actual sources stay
in /home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-vfe680-official-public-20261011-01.
This is a source identity check and functional reference, not license clearance
of all earlier project code, an accepted upstream patch or hardware proof.

Both cam_vfe680_hw_info descriptions select TOP version 4. The old CAMIF version
3 routine validates Bayer/YUV patterns and programs core fields, but it is not
the routine selected for VFE680. Its bit-field packing cannot establish this
chip's core startup.

The selected version 4 code records the pixel pattern while acquiring a
resource. Its core-config control function retains configuration flags. In the
pixel resource start path it expects top registers to have been programmed by
CDM; the reviewed functions do not implement the missing Bayer/core packing.
The core-register addresses alone do not establish their bit meanings.

The public pattern constants also differ from the order of our local enum:

| Bayer tile | Public row-pattern ordinal | Local sp11_front_bayer ordinal |
|---|---:|---:|
| RGGB | 0 | 0 |
| GRBG | 1 | 1 |
| BGGR | 2 | 3 |
| GBRG | 3 | 2 |

This is a metadata mapping observation, not a register encoder. Do not cast
these enums when implementing routing. The current processing builder accepts
RGGB only, so this finding does not invalidate its supported-input checks.

## Output definitions that can be implemented independently

The exact VFE680 descriptor identifies FULL Y/C clients 0/1 at 0xe00/0xf00,
in completion group 0. The public bus code writes FULL image dimensions using
the image width and plane height. Chroma has half the height. FULL must not use
the RDI stride-divided-by-16 width rule.

The public packer function distinguishes ordinary two-plane NV12, NV21 chroma
and three-plane output. The new test compiles that actual function and checks
the emitted setup against all 34 used register addresses. The new independent
232-byte bus builder derives address, increment, dimensions and stride from
bounded declared extents. Both write clients remain disabled, and it does not
load or reconstruct a private carrier. Tests and a compile-only kernel object
pass; see docs/UPSTREAM-VFE680-NV12-VALIDATION-20261012.json.

## Other public pixel-path series

The October 6 Qualcomm 45-patch series also provides explicit pixel-path source:
[SA8775P TOP v4.1x patch](https://patchew.org/linux/20261006223953.3382273-1-gjorgji.rosikopulos@oss.qualcomm.com/20261006223953.3382273-30-gjorgji.rosikopulos@oss.qualcomm.com/).
It is useful reference material, with public GPL declarations and author
attribution. Its displayed TOP IRQ and scaler addresses differ from the exact
VFE680 references above. A shared major version or core address is insufficient
to transplant its bit masks or setup. This patch was inspected, not replayed,
compiled or qualified on SP11. Keep the existing-CAMSS integration direction
already documented in docs/UPSTREAM-OVERLAP-20261011.md.

## Remaining work

1. Establish the exact VFE680 core/Bayer and DEMUX/CHANNEL_GAIN definitions from
   reviewed public register documentation or independently recorded functional
   hardware measurements. Do not fill gaps from a private profile, schema,
   legacy carrier or opaque other-chip word.
2. Establish processing precision/channel order and whether optional blocks can
   be bypassed. The GPL NV12 packer definition does not establish these domains.
3. Bind reviewed core and CSID setup, the processing builder and disabled NV12
   bus setup to owned resources, shared/cache initialization, completion groups,
   IRQ synchronization, CDM lifetime and physical stop/retirement.
4. Compile a new recorded candidate with private startup and retained
   steady-update consumers/fallbacks absent. Only then run cold-start,
   stop/reopen and switching qualification without system sleep. Preserve the
   daily cameras and Golden rollback. Ask before a prepared front optical test;
   the last reported orientation had only the rear facing the SP7 screen.

Both installed private dependencies remain. The source work does not establish
a bootable new provider, upstream readiness or optical parity.
