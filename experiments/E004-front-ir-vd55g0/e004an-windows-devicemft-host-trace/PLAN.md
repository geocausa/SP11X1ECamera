# E004an — Windows DeviceMFT host / trusted-trigger trace

Goal: identify the exact Windows process that hosts QcDeviceMFT8380.dll and determine
whether a trusted IR/FaceAuth-oriented trigger reaches the DeviceMFT KS property path.

Static authority from E004am/E004al/E004ak:
- QcDeviceMFT8380.dll CLSID {4C2331F0-66BE-4177-9841-2FCBA8CCF5CA}
- CDeviceMFT::KsProperty RVA 0x18250
- CPinConfigurer::KsProperty RVA 0x4d540
- CCameraControls::KsProperty RVA 0x2d0d0
- SecureMode SetProperty RVA 0x43f60
- CaptureProperties::OnSetSecureMode RVA 0x302d20

Phase 1 acceptance:
1. identify process(es) loading QcDeviceMFT8380.dll;
2. exercise the proven FaceAuth/IR route;
3. correlate module host lifetime with the trigger;
4. do not claim SecureMode activation unless the DeviceMFT Set/observer path is actually hit.

Safety:
- one-shot Windows boot only;
- do not weaken code integrity;
- no Linux SecureISP runtime;
- return to protected Golden after the trace.
