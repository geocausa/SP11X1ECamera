# E004ah — reload-safe Windows SecureISP dynamic trace

## Result

**PASS as a valid negative dynamic result. It does not authorize Linux SecureISP runtime.**

The same-machine Windows IR source was exercised with the proven holder:

- Surface IR Camera Front
- Infrared / VideoPreview
- NV12 644x604 at 60 fps
- StartAsync = Success
- 12 real TryAcquireLatestFrame() frames
- StopAsync = Success

SP7 KDNET caught two separate qccamsecureisp8380.sys loads during the cold boot.

Load 1:
- base 0xfffff8037c6d0000
- exact E004z RVAs armed
- module unloaded without an accepted OP/TASK/FNTABLE/SECURECFG runtime marker

Load 2:
- base 0xfffff803813d0000
- exact E004z RVAs armed before the IR holder
- live disassembly mechanically confirmed all four RVAs were the expected functions:
  - +0x3350 outer camera-control operation dispatcher
  - +0x4a90 WdfCompanionTargetSendTaskSynchronously helper
  - +0x24f0 exported 0x2e/0x2f lane-protection dispatcher
  - +0x1b08 ConfigSecureCamera
- the module remained loaded through StartAsync, 12 real frames, StopAsync, and the post-stop check
- zero accepted runtime marker lines occurred at all four functions

Therefore this exact WinRT real-frame holder does **not** exercise the E004z qccamsecureisp camera-control ABI during the observed start/frame/stop lifecycle. The static ABI remains valid authority for what qccamsecureisp can do, but E004ah invalidates the assumption that this holder is the dynamic trigger for that ABI.

This is stronger than the aborted E004aa attempt and the preparation-only E004ab/ac/af/ag directories, but it is deliberately a negative boundary, not a recovered task sequence.

## Safety

After capture SP11 was immediately rebooted back to protected Golden FullIO v19c:

- kernel 7.1.5-sp11-render-parity-v4+
- saved_entry=sp11-audio-fullio-v19c
- next_entry empty
- BootCurrent GRUB
- no camera nodes
- no camera modules

Linux SecureISP runtime remains NOT AUTHORIZED.

## Evidence

- E004AH-COLD2_TRACE.log — final raw WinDbg Unicode log from SP7
- E004AH-COLD2_TRACE.utf8.txt — normalized UTF-8 analysis copy
- E004AH-COLD2-IR-HOLDER.txt — normalized holder transcript
- POST-RETURN-GOLDEN.txt — post-return machine proof
- PREBOOT-LINUX.txt / COLD2-ARMED-WINDOWS.txt — one-shot boot evidence
- E004AH-IR-Holder.ps1 — exact proven holder copied from E004y

The original Windows UTF-16 holder log was 2238 bytes with SHA-256
72aa879de1e20f539fe90be2ec0115e8419b17aa494f4fff899dc41408eefc25.
Its normalized transcript is stored here.

## Next gate

Do not repeat the same qccamsecureisp task-helper trace with the same WinRT trigger.

Identify the actual Windows consumer/trigger of the protected IR route. The next justified work is to:

1. statically map surfacecamavs8380.sys / DeviceMFT references to SecureISP, secure services, and the qccamsecureisp device/control interface;
2. recover the qccamsecureisp EvtIoControl RVA and any open/IOCTL callers;
3. if needed, run a bounded same-machine Windows trace at the IOCTL boundary and the surfacecamavs call sites to determine whether the proven IR holder touches qccamsecureisp at all or follows a different protected path.

No Linux SecureISP runtime work is authorized by E004ah.
