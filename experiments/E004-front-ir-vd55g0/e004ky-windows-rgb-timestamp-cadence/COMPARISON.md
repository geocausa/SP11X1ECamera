# Windows versus Linux RGB cadence

| Camera | Windows advertised | Windows observed source-timestamp cadence | Linux independent app |
|---|---:|---:|---:|
| Front1080p |30fps|14.99fps over30s|30.02fps overabout60s (E004kr)|
| Rear4K |30fps|14.96fps over30s|30.07fps overabout60s (E004kp)|

E004kx independently saw451/450 distinct full NV12 payloads over30s, but rear observer work averaged45.84ms. E004ky removed copying/hashing:450/449 unique monotonic timestamps, observer work1.42/4.32ms, and arrival rates14.99/14.95fps. Thus copy/hash cost alone does not explain the15fps observation. Source timestamps describe acquired frames; sensor sequence/drop counters are unavailable.

All7front and8rear enumerated VideoRecord NV12 modes advertise30fps. Front includes2560x1440; rear includes3840x2160. No60fps mode observed, no absolute silicon limit inferred.

Lighting/exposure/ISP processing and observers are not matched across OSes; no claim that Linux is twice as fast or has Windows quality. Windows nominal auto-exposure properties are not proven sensor register readings. A low-light/adaptive frame-interval explanation remains a hypothesis requiring a controlled scene. Linux already improved rear transport from13.78fps (E004km app) to30.07fps by removing intermediate copies/processes. Next optimize conversion/copy CPU cost and latency while implementing calibrated ISP output; unsupported sensor timing changes are not justified by this comparison.
