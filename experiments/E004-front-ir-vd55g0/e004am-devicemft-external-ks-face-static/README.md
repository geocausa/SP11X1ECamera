# E004am — DeviceMFT external KS face and registration

## Result

**PASS as static authority. No Windows runtime claim and no Linux SecureISP authorization.**

E004al resolved the internal PinConfigurer → InterfaceAccessor → CameraControls route.
E004am resolves how the DeviceMFT itself is registered and exposes its own KS-control face.

## DeviceMFT COM registration

The same driver package INF registers:

- CLSID `{4C2331F0-66BE-4177-9841-2FCBA8CCF5CA}`;
- `InprocServer32 = %SystemRoot%\System32\QcDeviceMFT8380.dll`;
- threading model `Both`.

The package contains no separate Qualcomm executable or DLL with SecureMode strings.
Within this package, SecureMode references are confined to:

- `QcDeviceMFT8380.dll`;
- `surfacecamavs8380.sys`.

## DeviceMFT KS-control face

`CDeviceMFT::QueryInterface` is `0x180010a70`.

For the binary GUID constant at `0x181350d30`
(`28f54685-06fd-11d2-b27a-00a0c9223196`), QueryInterface returns the
subobject at object offset `+0x18` (`param_1 + 3`).

That subobject uses vtable `0x181330980`:

- `+0x18 -> 0x180018250` = `CDeviceMFT::KsProperty`;
- `+0x20 -> 0x1800186f0` = `CDeviceMFT::KsMethod`;
- `+0x28 -> 0x180018a50` = `CDeviceMFT::KsEvent`.

Therefore the DeviceMFT itself exposes an independent KS-control-style face.

## KsProperty routing

`CDeviceMFT::KsProperty` first asks its internal DMFT/source-transform handler at
object offset `+0xb0` to consume the request.

If that handler reports that the property was not handled, CDeviceMFT logs
`Forwarding KsProperty to driver` and forwards through the separate pointer at
`+0x98`.

If handled internally, it logs
`KsProperty handled in DMFT, not forwarding to driver`.

This outer route is separate from E004al's
`CPinConfigurer -> CInterfaceAccessor -> CCameraControls` chain.

## InitializeTransform interface chain

`CDeviceMFT::InitializeTransform` obtains the internal handler stored at `+0xb0`
through a source-transform/service interface chain using these exact GUID constants:

- service GUID `6a2c4fa6-d179-41cd-9523-822371ea40e5`;
- `00000000-0000-0000-c000-000000000046`;
- `bf94c121-5b05-4e6f-8000-ba598961414d`;
- `28f54685-06fd-11d2-b27a-00a0c9223196`.

The final interface pointer is stored at `CDeviceMFT +0xb0`.

## Relationship to E004aj

E004aj obtained KS control from the public camera source path and proved that ordinary
client SET attempts do not reach the SecureMode write path.

E004am shows a distinct object exists: the registered DeviceMFT itself has its own
KS-control face and its own internal handled-vs-driver-forwarding logic.

The next bounded Windows experiment should therefore answer:

1. which Windows process loads `QcDeviceMFT8380.dll` for the IR/FaceAuth path;
2. whether FaceAuth or another trusted Windows trigger calls
   `CDeviceMFT::KsProperty`;
3. whether that call then reaches E004al/E004ak's internal SecureMode broker.

Do not repeat the public source IKsControl SET as the primary trigger.

## Evidence

- `ghidra/DEVICEMFT-EXTERNAL-KS-FACE.txt`
- `ghidra/ExtractDeviceMFTExternalKsFace.java`
- `INF-REGISTRATION.txt`
- `RESULT.json`
- `verify_e004am.py`

Source authority:

- `QcDeviceMFT8380.dll`
  - bytes: 23998368
  - SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- `surfacecamavs8380.inf`
  - SHA-256: `4db3acab414e344dc460478b54d964c9c7b5d3d648ee0c19db13523431262fcb`

## Safety

No Windows boot was required for E004am. Linux SecureISP runtime remains
**NOT AUTHORIZED**. Protected Golden remains unchanged.
