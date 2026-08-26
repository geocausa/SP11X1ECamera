# E002 — Rear OV13858 D-PHY bring-up

Goal: bring up the SP11 rear camera from Windows-derived board evidence while preserving FullIO v19c as immutable Golden.

## Staging

- **E002a infrastructure only:** add CCI0 + integrated X1E CAMSS receive fabric to an overlay/merged copy of the exact v19c DT. No sensor node, no camera regulator votes, no reset GPIO writes.
- **E002b rear probe:** add only the Windows-proven OV13858 power/reset/MCLK/control-bus node on CCI0 master1 and prove chip ID. No stream.
- **E002c rear stream:** add/audit the Microsoft 592.8 MHz OV13858 PLL/link profile and endpoint; obtain first RAW10 frame.

## Hard safety rules

- Never modify `/boot/sp11-7.1.5-audio-fullio-v19c/*`.
- Every candidate gets a separate DTB/boot directory and GRUB ID.
- Experimental boots are one-shot only until mechanically accepted.
- Do not enable front IMX681 or IR VD55G0 in E002.
- Do not import the newer standalone X1E CSI2-PHY binding into the v4 kernel. This kernel uses integrated CAMSS CSIPHY resources.

## E002a acceptance

1. candidate DT differs from Golden only by the camera infrastructure nodes/properties intended by E002a;
2. kernel reaches userspace with audio/touch baseline unaffected;
3. CCI0 and qcom-camss probe without fatal errors;
4. `/dev/media*` appears if the driver exposes the media controller without a sensor, or logs prove CAMSS successfully initialized if it defers external registration;
5. no sensor rail/reset/MCLK transition occurs because no sensor node exists.
