# E004hy — genuine original UEFI protocol clients, bounded non-use of candidate +0x240

**OFFLINE ORIGINAL FIRMWARE PASS, 2026-09-20.** A further original-
firmware distinction after E004hw/HX: mere presence of the protocol GUID
can be replaced by concrete compiled client code that references the exact
GUID and conditionally loads a protocol method. No pre-OS execution on
this actual SP11 boot is claimed.

The original PmicDxe publishes protocol GUID
ae6ae96e-483f-42ae-9cc1-9fac1b584728, table base PmicDxe+0x38b58;
E004hv's proposed computed-address writer lies at method offset +0x240.
Six independently SHA-pinned original UEFI client PE images genuinely
construct this exact GUID as an argument to a boot-services +0x140
protocol lookup (UEFI LocateProtocol ABI) and contain these *different*
compiled method call sites:

| Original client | Original lookup/method callsite RVAs | Original method slot |
| --- | --- | --- |
| QcomChargerDxeWp | +0x286c/+0x2880 then +0x2894/+0x289c; additionally +0x112b0 | +0x180; additional +0x270 |
| ChargerExDxe | +0x257c/+0x2590 then +0x25a4/+0x25ac | +0x180 |
| PlatformEntMgtPolicyDxe | +0x7d6c/+0x7d80 then +0x7d9c/+0x7da8 | +0x180 |
| BdsDxe | +0x36820/+0x36834 then +0x36850/+0x3685c | +0x180 |
| DisplayDxe | +0x4d01c/+0x4d030 then +0x4d04c/+0x4d058 | +0x180 |
| UsbPwrCtrlDxe | +0x4e88/+0x4e9c; separate +0x4ec4/+0x4ec8 tailcall | +0x80 |

These are specific compiled lookup and alternate-method code routes,
not proof the calls executed on the current machine. A narrowly defined
one-instruction-form scan of each of the **six** original executable
images finds zero direct literal LDR Xn,[Xm,#0x240] loads. **This does not
exclude other instructions, register-computed slot arithmetic, other
firmware clients, earlier boot stages, or actual invocation of +0x240.**
In particular, non-use by the six clients is NOT an established negative
result; only the explicitly bounded instruction pattern is absent.

verify_clients.py pins every selected PE SHA256, actual original GUID RVA,
selected original ARM64 instruction identities, the six true boot-services
lookup routes, positive alternate method routes and six bounded literal-LDR
counts. test_clients.py exercises **46 independent in-memory original
client-code/GUID mutations** without editing the original firmware archive
or operating a device.

Next: only elevate +0x240 as a timer candidate on a *genuine* original
callsite/argument or boot-time register-address record. Continue safe
offline camera productionization in parallel, instead of treating repeated
post-Windows-boot no-hit timer observers as dispositive about pre-OS writes.
The first idle timer 0x93 writer remains unknown, and actual emitter
current/irradiance/physical autonomous failure-off validation remains blocked.
Golden Linux is protected; native Linux IR emitter and biometric login OFF.
