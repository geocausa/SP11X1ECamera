# E004al — DeviceMFT internal KS owner / camera-controls pointer chain

## Result

**PASS as static authority. No new Windows runtime claim and no Linux SecureISP authorization.**

E004ak closed the SecureMode property object's internal SET/GET and observer chain.
E004al closes the direct-pointer wiring that feeds that broker.

## Camera-controls ownership chain

The exact internal route is:

1. `CInterfaceAccessor::SetCameraControls` at `0x180050d40` stores the
   `CCameraControls` pointer at accessor offset `+0x70`.
2. The accessor vtable begins at `0x1813345a8`.
3. Accessor vtable slot `+0xb8` is `0x180051830`.
4. That getter is mechanically just:
   `ldr x0, [x0,#0x70]; ret`.
   It therefore returns the exact pointer written by `SetCameraControls`.
5. `CPinConfigurer::KsProperty` at `0x18004d540` obtains its
   `CInterfaceAccessor`, calls accessor vtable `+0xb8`, and then invokes
   vtable `+0x20` on the returned object.
6. The primary `CCameraControls` vtable is `0x1813311b8`; its `+0x20`
   entry is `0x18002d0d0`, the already recovered
   `CCameraControls::KsProperty`.

That gives the direct static chain:

`CPinConfigurer::KsProperty`
→ `CInterfaceAccessor::CameraControls()`
→ `CCameraControls::KsProperty`
→ E004ak `CProperty::Handle`
→ SecureMode `SetProperty`
→ `NotifySetObservers`
→ `CaptureProperties::OnSetSecureMode`.

## Outer DeviceMFT route

The separate outer entry `CDeviceMFT::KsProperty` is `0x180018250`.

During `CDeviceMFT::InitializeTransform`, an internal KS-control face is obtained from
the source-transform/service chain and stored at `CDeviceMFT +0xb0`. The decoded
binary GUID constants involved are:

- `00000000-0000-0000-c000-000000000046`;
- `bf94c121-5b05-4e6f-8000-ba598961414d`;
- `28f54685-06fd-11d2-b27a-00a0c9223196`;
- service GUID `6a2c4fa6-d179-41cd-9523-822371ea40e5`.

`CDeviceMFT::KsProperty` asks that internal handler to consume the request first.
If it reports the property was not handled in DMFT, the call is forwarded to the driver
through the separate pointer at `+0x98`.

This `+0xb0` route is **not** the same pointer as the camera-controls pointer at
`CInterfaceAccessor +0x70`; E004al keeps the two paths separate.

## Relationship to E004aj

E004aj showed that the ordinary public Media Foundation / WinRT camera-source SET
attempt never reached the kernel SecureMode setter. E004al explains why repeating that
same client operation is not the next useful experiment: DeviceMFT has an internal
property-routing graph with its own PinConfigurer → InterfaceAccessor → CameraControls
path.

The next dynamic experiment, if needed, should be armed at the **DeviceMFT user-mode
functions** identified here (especially `CDeviceMFT::KsProperty`,
`CPinConfigurer::KsProperty`, and `CCameraControls::KsProperty`) and must use a
trusted Windows trigger capable of entering DeviceMFT's property path. A blind repeat
of the public source SET is not justified.

## Evidence

- `ghidra/DEVICEMFT-INTERFACE-ACCESSOR.txt`
- `ghidra/DEVICEMFT-CAMERA-CONTROLS-ACCESSOR.txt`
- `ghidra/DEVICEMFT-CAMERA-CONTROLS-GUID-CALLERS.txt`
- `ghidra/DEVICEMFT-PINCONFIGURER-KS-BRIDGE.txt`
- `ghidra/DEVICEMFT-KS-BRIDGE.txt`
- `ghidra/DEVICEMFT-KSPROPERTY-OWNER.txt`
- `ghidra/DEVICEMFT-CONSTRUCTION.txt`
- `VTABLE-GUID-AUTHORITY.txt`

Source binary remains the same DeviceMFT authority used by E004ak:
`QcDeviceMFT8380.dll`, SHA-256
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

## Safety

No Windows reboot was needed for E004al. Linux SecureISP runtime remains
**NOT AUTHORIZED**. Protected Golden remains unchanged.
