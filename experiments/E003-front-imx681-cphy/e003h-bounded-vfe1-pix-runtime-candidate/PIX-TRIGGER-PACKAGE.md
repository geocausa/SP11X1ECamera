# E003h disposable PIX trigger package

Prepared 2026-08-29. Runtime is **not armed** by this checkpoint.

- 0035 patch: `7c7f33340fcd698e422729ee6cb4ad5c7611b97cc4227a6d69e40d199dd2ca38`
- candidate qcom-camss.ko: `5a09b33c73feb7060c9e0f504cf893fc2e120f6225c4f8b222765c57fc135c79`, Golden vermagic
- front-only PIX DTB: `083fd7d3a207cb329938c561aee84c8642cb02e52034b753b36aaff599a381ed`; only CAMSS port@2, VFE0/VFE1 spans 0xf000, RT-CDM1 0x0ac26000/0x1000 + GIC_SPI 287
- local capsule: `6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20`, 41088 bytes; remains local/ignored
- IMX681 runtime module: `389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388`
- userspace one-shot helper binary: `d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09`; source `98c97a468e3ab120b99e329f88e6b55dd8742a8f063e0f43c99c4d8600cff140`; it allocates/maps exactly two QC10C buffers and contains no VIDIOC_QBUF or VIDIOC_STREAMON call
- trigger package inspection: `7f08beebd6df54bd22bc6a1afacc8abea19c02fea309fbc606d52e6e7c181033`

The boot entry `sp11-camera-e003h-pix-one-shot` is installed using byte-exact Golden kernel/initrd plus the front-only DTB. It blacklists qcom_camss/imx681/ov13858 for manual controlled loading and points `firmware_class.path` at the local experiment firmware tree. Installer never calls grub-reboot. Current GRUB remains `saved_entry=sp11-audio-fullio-v19c`, empty `next_entry`.

Manual candidate load requires `e003h_pix_runtime_arm=1`; without that load-time parameter the write-only sysfs trigger is not created. The only trigger command is `RUN`. The trigger requires exactly two preallocated DEQUEUED buffers, validates contiguous SG DMA, synchronizes caches explicitly, and calls the irreversible 0034 latch. No normal vb2 QBUF/STREAMON path is used.
