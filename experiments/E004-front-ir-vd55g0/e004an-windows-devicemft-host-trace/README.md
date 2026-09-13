# E004an — Windows DeviceMFT host / FaceAuth correlation

## Result

PASS for DeviceMFT host identity and trusted FaceAuth correlation.

This checkpoint was reconstructed after the chat UI lost the middle of the Windows/KD session. The authoritative data survived in the SP11 Windows connector job-retention directory and in SP7's retained KD terminal output.

## Proven host

QcDeviceMFT8380.dll is hosted by the Windows Camera Frame Server:
- process: C:\WINDOWS\System32\svchost.exe
- command line: C:\WINDOWS\System32\svchost.exe -k Camera -s FrameServer
- service: FrameServer
- display name: Windows Camera Frame Server
- session: 0

## Repeated FaceAuth correlation

Run 1 used FaceAuth profile {81361B22-700B-4546-A2D4-C52E907BFC27},0, IR NV12 644x604 at 60 fps, StartAsync Success, 12 real frames, StopAsync Success. The watcher saw QcDeviceMFT8380.dll in PID 3676, svchost, base 0x7ff80a360000.

Run 2 repeated the 12-frame FaceAuth control. The watcher saw PID 12512, svchost, base 0x7ffff8640000 and resolved it to svchost.exe -k Camera -s FrameServer / Windows Camera Frame Server.

## Gated post-init run

A third helper initialized the same FaceAuth profile and stopped deliberately at a post-InitializeAsync console gate before starting the reader. While held, the watcher saw PID 8180, svchost, base 0x7ffff8640000, command line svchost.exe -k Camera -s FrameServer, service FrameServer.

SP7 KD then ran !process 0n8180 1 and independently reported Cid 1ff4 and Image: svchost.exe. This is the KD pause that made SP11 disappear from PiMaster. The machine was later manually restarted to Linux, so this gated helper is not claimed as a completed stream run.

## Not yet proven

E004an does not yet prove runtime execution of CDeviceMFT::KsProperty, CPinConfigurer::KsProperty, CCameraControls::KsProperty, SecureMode SetProperty, or CaptureProperties::OnSetSecureMode. The hidden session reached the correct FrameServer process and paused KD before those user-mode breakpoints were armed.

Static RVAs from E004ak/E004al/E004am remain:
- CDeviceMFT::KsProperty RVA 0x18250
- CPinConfigurer::KsProperty RVA 0x4d540
- CCameraControls::KsProperty RVA 0x2d0d0
- SecureMode SetProperty RVA 0x43f60
- CaptureProperties::OnSetSecureMode RVA 0x302d20

## Safety / return

The interrupted Windows session returned to protected Linux Golden by manual restart. Linux SecureISP runtime remains NOT AUTHORIZED.

## Next gate

One bounded Windows pass: hold the proven FaceAuth helper after init, identify the exact FrameServer PID/module base, trace the DeviceMFT user-mode RVAs in that process, release the gate, finish capture, close the trace, and return to Golden.