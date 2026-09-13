# E004ak — DeviceMFT SecureMode broker static authority

## Result

**PASS as static broker authority. No new Windows runtime claim and no Linux SecureISP authorization.**

E004aj proved that the ordinary Media Foundation / WinRT camera-source client can read
SecureMode but its SET request is rejected before the kernel SecureMode setter. E004ak
maps the separate DeviceMFT property broker that actually owns the SecureMode state
transition.

## End-to-end static chain

The recovered DeviceMFT chain is:

1. `CItemFactoryBase::CreateCameraControls` constructs the internal
   `CCameraControls` object.
2. `CaptureProperties::Initialize` (`0x180292f20`) calls
   `CaptureProperties::RegisterPropertyObservers` (`0x1802f7458`).
3. If `m_isSecureCameraSupported` at CaptureProperties `+0x1357c` is 1,
   registration resolves the named `SecureMode` property and registers:
   - SET observer: `CaptureProperties::OnSetSecureMode` at `0x180302d20`,
     observer mode 1;
   - GET observer: `CaptureProperties::OnGetSecureMode` at `0x180302f40`,
     observer mode 0.
4. `CCameraControls::KsProperty` (`0x18002d0d0`) walks the internal property
   objects and dispatches the matching request to `CProperty::Handle`
   (`0x180047690`).
5. The SecureMode property object has its class vtable at `0x1813336e8`.
   Important slots are:
   - `+0x50`: `CProperty::Handle` = `0x180047690`;
   - `+0x60`: `CProperty::NotifySetObservers` = `0x180047c60`;
   - `+0x68`: `CProperty::NotifyGetObservers` = `0x180047cd0`;
   - `+0xb8`: `CProperty_SecureMode::SetProperty` = `0x180043f60`;
   - `+0xc0`: `CProperty_SecureMode::GetProperty` = `0x180043ce0`.
6. `CProperty::Handle` decodes the standard KSPROPERTY flag bits:
   - GET bit: NotifyGetObservers first, then SecureMode GetProperty;
   - SET bit: SecureMode SetProperty first, then NotifySetObservers.
7. `CProperty::RegisterPropertyObserver` (`0x180309760`) stores the observer
   context, callback, auxiliary argument and mode in the property's observer list.
   `CProperty::NotifyObservers` (`0x180047d40`) selects entries by mode and
   calls the matching callback.
8. `CaptureProperties::OnSetSecureMode` reads the SecureMode property flags:
   - flag 2 => internal state `+0x13578 = 1`;
   - flag 1 => internal state `+0x13578 = 0`.
9. The capture-pipe setup path consumes that state. In the
   `CaptureDevice::CreateCapturePipe` path, helper `0x180293ad8` checks
   `+0x13578`; the secure mono path logs and selects
   `IFE_LITE_SECURE_MODE`, bypassing IPE for the SecureBio use case.

This closes the DeviceMFT side of the SecureMode control path.

## Why E004aj generic SET did not prove the protected path

The internal `CCameraControls` object is not the same interface object as the public
camera-source IKsControl obtained in E004aj.

Its internal vtable includes QueryInterface/refcounting plus Initialize, KsProperty,
KsEvent and NotifyAllObservers. Its `QueryInterface` implementation compares only
against `IID_IUnknown = {00000000-0000-0000-C000-000000000046}`; it does not expose a
public camera-controls IID that an ordinary source client can request.

Therefore the next missing owner is not another lower camera-source SET attempt. It is
the internal DeviceMFT/factory/interface-accessor code that receives the direct
`CCameraControls` pointer and calls its KsProperty entry.

## Source authority

Binary:
`QcDeviceMFT8380.dll`

- bytes: 23998368
- SHA-256:
  `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

The analyzed binary is the same Windows DeviceMFT authority used by E004ai/E004aj.

## Evidence

- `ghidra/DEVICEMFT-SECURE-BROKER-FOCUSED.txt`
  - SecureMode callback references, registration/unregistration, capture-use-case callers.
- `ghidra/DEVICEMFT-PROPERTY-BROKER.txt`
  - CCameraControls::KsProperty and observer/property framework.
- `ghidra/DEVICEMFT-SECURE-VTABLE.txt`
  - SecureMode CProperty::Handle routing and class vtable method bodies.
- `ghidra/DEVICEMFT-PROPERTY-OBSERVER-LOOP.txt`
  - observer list storage and SET/GET callback invocation.
- `ghidra/DEVICEMFT-CCAMERACONTROLS.txt`
  - CCameraControls construction, QueryInterface and private interface layout.
- `ghidra/DEVICEMFT-CAMERA-CONTROLS-WIRING.txt`
  - camera-controls factory/wiring strings and method references.
- accompanying Java scripts reproduce the focused extraction against the cached Ghidra
  project.

## Safety boundary

- No Linux SecureISP runtime was attempted.
- No Windows boot was needed for E004ak.
- E004z static SecureISP ABI remains valid.
- E004aj dynamic negative boundary remains valid.
- Protected Golden remains unchanged.

## Next gate

Trace the direct pointer wiring from
`CItemFactoryBase::CreateCameraControls` / `psCInterfaceAccessor::SetCameraControls`
to the component that invokes the internal `CCameraControls::KsProperty` method.
Only once that caller is identified should another same-machine Windows dynamic pass be
considered.
