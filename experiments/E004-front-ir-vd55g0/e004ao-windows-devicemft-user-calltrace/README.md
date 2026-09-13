# E004ao — Windows DeviceMFT user-mode call trace

## Result

PASS as a strong dynamic negative boundary: the trusted FaceAuth media profile loads QcDeviceMFT8380.dll in Windows Camera Frame Server, but does not execute the mapped DeviceMFT SecureMode / KS broker chain during initialization or 12-frame IR streaming.

Linux SecureISP runtime remains NOT AUTHORIZED.

## Why this experiment was needed

E004am established that QcDeviceMFT8380.dll exposes its own KS-control face, while E004an proved that the DLL is hosted by Windows Camera Frame Server. The missing question was whether the trusted FaceAuth-oriented media profile actually invokes that DeviceMFT KS / SecureMode path.

## Dynamic method

The first post-init trace armed the exact live DeviceMFT RVAs after MediaCapture.InitializeAsync() completed. Twelve real IR frames then streamed successfully and none of the mapped functions fired.

Because that could have missed calls occurring during initialization, the experiment was tightened:

1. FrameServer was started with QcDeviceMFT8380.dll absent.
2. A user-mode debug monitor attached to FrameServer with SeDebugPrivilege.
3. The monitor caught the exact LOAD_DLL_DEBUG_EVENT for QcDeviceMFT8380.dll and held only FrameServer before DeviceMFT execution continued.
4. Live host PID: 14784.
5. Live DeviceMFT base: 0x7ffd47cb0000.
6. KD bound to that exact FrameServer EPROCESS and armed process-specific absolute breakpoints against the live image.
7. The user-mode debugger released the DLL-load event.
8. FaceAuth initialization completed, then the proven profile streamed 12 real IR frames and stopped successfully.

## Live targets armed before DeviceMFT execution

- CreateCameraControls RVA 0x21cf0
- CaptureProperties::Initialize RVA 0x292f20
- RegisterPropertyObservers RVA 0x2f7458
- SecureMode property accessor RVA 0x309620
- CDeviceMFT::KsProperty RVA 0x18250
- CPinConfigurer::KsProperty RVA 0x4d540
- CCameraControls::KsProperty RVA 0x2d0d0
- CProperty_SecureMode::SetProperty RVA 0x43f60
- CProperty_SecureMode::GetProperty RVA 0x43ce0
- CaptureProperties::OnSetSecureMode RVA 0x302d20
- CaptureProperties::OnGetSecureMode RVA 0x302f40
- secure capture-usecase helper RVA 0x293ad8

All were armed process-specifically against the live FrameServer object before the held DLL-load event was released.

## FaceAuth control

Final held-load run used:

- profile {81361B22-700B-4546-A2D4-C52E907BFC27},0
- Surface IR Camera Front
- Infrared / VideoPreview
- NV12 644x604 at 60 fps
- InitializeAsync success
- StartAsync success
- 12 real TryAcquireLatestFrame() frames
- StopAsync success

The public VideoDeviceController SecureMode GET continued to return NotSupported, consistent with E004aj.

## Negative result

The raw KD trace contains the breakpoint definitions and the explicit final marker E004AO_FINAL_ZERO_HITS, but contains zero output lines beginning with E004AO_LHIT.

Therefore none of the armed DeviceMFT initialization, KS broker, SecureMode property, observer, or secure-usecase targets executed in the observed FaceAuth initialization/stream lifetime.

This is stronger than E004an's earlier timing-limited negative result because the final E004ao breakpoints were installed while FrameServer was frozen at the DeviceMFT DLL-load debug event, before DeviceMFT execution was released.

## Interpretation

The Windows FaceAuth media profile by itself is not the trusted trigger for Qualcomm DeviceMFT SecureMode. Selecting the FaceAuth profile and successfully receiving IR frames does not exercise the mapped SecureMode control chain and does not justify Linux SecureISP runtime.

The next investigation should move one layer outward and identify the Windows component / topology condition that instantiates or drives the secure DeviceMFT path (for example the actual biometric/Windows Hello consumer rather than a generic MediaCapture client), before another dynamic SecureISP trace.

## Evidence

- recovered-windows/E004AO-FrameServerLoadHold.ps1 — user-mode LOAD_DLL event hold.
- recovered-windows/job_iI7vPkpqZRkzawGpBW7spNrg/ — successful FrameServer load hold, PID 14784, base 0x7ffd47cb0000.
- recovered-windows/job_5x5HkWSlMWMF49hNVAVDbIa2/ — final FaceAuth run, 12 frames.
- recovered-sp7/E004AO_LOADHELD_TRACE.log — final KD breakpoint set and explicit zero-hit closeout.
- recovered-sp7/E004AO_PREINIT_TRACE.log — failed deferred-symbol strategy retained as diagnostic evidence.
- recovered-sp7/E004AO_TRACE.log — first post-init zero-hit trace.
- recovered-sp7/E004AO-KD-TERMINAL.utf8.txt — normalized complete KD terminal transcript.
- POST-RETURN-GOLDEN.txt — exact protected Golden return evidence.

## Safety / return

Windows code integrity was not weakened and no driver or binary was patched. After the bounded one-shot pass SP11 returned to the protected Linux Golden:

- kernel 7.1.5-sp11-render-parity-v4+
- sp11_entry=7.1.5-sp11-fullio-v19c
- saved_entry=sp11-audio-fullio-v19c
- next_entry empty
- BootCurrent 0005
- no /dev/media* or /dev/video* nodes
- no camera modules loaded.
