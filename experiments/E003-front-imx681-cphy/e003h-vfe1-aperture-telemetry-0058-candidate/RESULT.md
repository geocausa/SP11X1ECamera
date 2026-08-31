# E003h 0058 result — external VFE1 aperture transport unusable

0058 executed the frozen 0057 camera path exactly once with zero camera-programming delta and returned to Golden. RT-CDM completed FIFO 25 without fault; CSID1 remained healthy at 3840x2160 with no line/ECC/CRC error; VFE1 raw Epoch0 and QC10C remained absent.

The read-only external sampler targeted the DT-confirmed VFE1 physical base 0x0ac71000, but all 3854 samples reported no powered VFE1 aperture and the captured 0x4000 snapshot was entirely zero. In-driver reads during the same run simultaneously reported live VFE1 state. Therefore /dev/mem is not a usable observation transport for this device/kernel; this does **not** imply the Linux VFE1 base is wrong.

No new programming write is justified. The next diagnostic should read the unresolved VFE680 configuration cluster from inside the already-powered CAMSS timeout path, read-only.
