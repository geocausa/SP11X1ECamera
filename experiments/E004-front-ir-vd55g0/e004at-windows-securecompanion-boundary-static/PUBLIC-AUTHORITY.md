# Public Windows authority note

Microsoft's Windows driver documentation provides the same SecureCompanion INF model used by the installed SP11 package: a UMDF service with `ServiceType = SecureCompanion` and a required `TrustletIdentity`. Microsoft's UVC secure-camera example uses `TrustletIdentity = 4096`.

Microsoft also documents Windows trustlets as Isolated User Mode (IUM) / secure processes running in the VTL1 Virtual Secure Mode environment.

A Microsoft AVStream sample describes a secure companion driver as a trustlet used to process secure camera buffers.

These public references corroborate the installed-package evidence. They do not establish any Qualcomm QTEE service-UID mapping.

Authority consulted 2026-09-13:
- Microsoft Learn: "Providing a UVC INF File"
- Microsoft Learn: "Isolated User Mode (IUM) Processes"
- Microsoft Windows-driver-samples: AVStream sample DeviceMFT secure-buffer path
