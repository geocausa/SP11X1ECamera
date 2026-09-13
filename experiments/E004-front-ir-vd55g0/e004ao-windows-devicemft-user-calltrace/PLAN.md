# E004ao — Windows DeviceMFT user-mode call trace

Goal: dynamically prove which internal DeviceMFT property path executes during the trusted FaceAuth trigger.

Targets from static authority:
- CDeviceMFT::KsProperty RVA 0x18250
- CPinConfigurer::KsProperty RVA 0x4d540
- CCameraControls::KsProperty RVA 0x2d0d0
- SecureMode::SetProperty RVA 0x43f60
- CaptureProperties::OnSetSecureMode RVA 0x302d20

Method:
- one-shot Windows boot
- hold FaceAuth immediately after MediaCapture initialization
- identify FrameServer PID and live QcDeviceMFT8380.dll base
- bind KD to that exact process and arm process-specific user-mode breakpoints
- release gate, acquire frames, record accepted hits
- return immediately to protected Golden

Safety: code integrity unchanged; no Linux SecureISP runtime.
