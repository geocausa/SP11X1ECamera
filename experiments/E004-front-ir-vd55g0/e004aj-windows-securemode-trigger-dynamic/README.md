# E004aj — Windows SecureMode client/broker boundary

## Result

**PASS as a valid negative dynamic boundary. This is not a successful SecureMode enable.**

E004ai established that surfacecamavs8380.sys has a real SecureMode setter and that the
secure CSI diversion is gated by the resulting state byte. E004aj tested whether ordinary
same-machine Windows camera clients can invoke that setter.

They cannot, within the paths tested.

The strongest accepted facts are:

- the Media Foundation source for Surface IR Camera Front exposes IKsControl;
- SecureMode GET succeeds with Version=1, PinId=0, Size=40,
  Flags=1 (disabled), Capability=3;
- SET with Flags=2 is rejected both before and after source-reader creation;
- rebuilding SET from the exact successful GET blob while preserving Capability=3
  is still rejected;
- KD sees three real SecureMode GET handler executions but zero SecureMode SET handler
  executions;
- consequently there are also zero secure-CSI and qccamsecureisp control-ABI runtime hits.

The FaceAuth capture profile remains a useful control: it starts the same IR source,
acquires 12 real NV12 644x604 frames at 60 fps, and stops cleanly, but it does not expose
a usable SecureMode property through VideoDeviceController. FaceAuth mode is therefore
not equivalent to SecureMode.

## Broker boundary

The companion static DeviceMFT authority now gives the next concrete direction.

QcDeviceMFT8380.dll contains:

- CProperty_SecureMode::GetProperty;
- CProperty_SecureMode::SetProperty;
- CaptureProperties::OnSetSecureMode;
- explicit SecureMode Enabled / SecureMode Disabled state handling;
- MFMediaType_Protected;
- IFE_LITE_SECURE_MODE;
- CameraSecureISP plumbing.

This makes the DeviceMFT / protected-capture broker the next justified owner to map.
Do not repeat generic IKsControl or WinRT SET attempts unless static evidence identifies
a materially different caller/context.

## Code-integrity discipline

A locally built diagnostic executable was blocked by the normal Windows code-integrity
policy. E004aj did not disable or weaken that policy. The accepted follow-up probes used
the existing signed PowerShell host.

## Safety

The Windows pass was a one-shot boot. It was closed through KD and SP11 returned to the
protected Golden FullIO v19c:

- kernel 7.1.5-sp11-render-parity-v4+;
- saved_entry=sp11-audio-fullio-v19c;
- next_entry empty;
- BootCurrent 0005 (GRUB);
- no /dev/media* or /dev/video*;
- no camera modules loaded.

**Linux SecureISP runtime remains NOT AUTHORIZED.**

## Evidence

- recovered-sp7/E004AJ_R2_TRACE.log — final raw R2 KDNET trace.
- R2-TRACE-MARKERS.txt — runtime-only marker counts; breakpoint-definition text is excluded.
- WINDOWS-PROBES.txt — consolidated same-machine Windows probe outcomes.
- POST-RETURN-GOLDEN.txt — exact post-run Golden proof.
- recovered-windows/ — earlier E004aj scripts/logs recovered during the pass.
- ghidra/SURFACECAMAVS-FACEAUTH-XREFS.txt — FaceAuth static control mapping.
- ../e004ai-secure-mode-owner-static/ghidra/DEVICEMFT-SECURE-XREFS.txt — DeviceMFT secure owner authority.

Raw R2 trace:
- bytes: 12935
- SHA-256: f495dae75e017e001146cc2317ef96cf4f4fba0921e60481753bf82d5b96b37f

## Next gate

Statically recover the DeviceMFT registration/caller chain that reaches
CProperty_SecureMode::SetProperty and CaptureProperties::OnSetSecureMode, including
the protected-media / IFE_LITE_SECURE_MODE route. Only after that mapping identifies
a concrete trusted trigger should another bounded Windows dynamic pass be armed.
