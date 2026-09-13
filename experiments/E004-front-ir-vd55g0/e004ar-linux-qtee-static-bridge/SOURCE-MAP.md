# E004ar source map

## Linux kernel source

Tree:
`/home/geoca/Documents/SP11-PROJECT/02-kernel/linux-7.1.5`

Relevant files:

- `drivers/firmware/qcom/qcom_scm.c`
  - `qcom_scm_qtee_invoke_smc()`
  - `qcom_scm_qtee_callback_response()`
  - `qcom_scm_qtee_init()`
  - `qcom_scm_assign_mem()`
- `drivers/firmware/qcom/Kconfig`
  - QCOM_SCM
  - QCOM_TZMEM
  - QCOM_TZMEM_MODE_SHMBRIDGE
  - QCOM_QSEECOM
- `drivers/tee/qcomtee/*`
  - QTEE object transport
  - client-environment service open by UID
  - SHM/TZMem-backed message buffers
  - primordial memory-object mapping callback
- `include/dt-bindings/firmware/qcom,scm.h`
  - `QCOM_SCM_VMID_CP_CAMERA = 0x0d`
  - `QCOM_SCM_VMID_CP_CAMERA_PREVIEW = 0x1d`
- `arch/arm64/boot/dts/qcom/hamoa.dtsi`
  - camera reserved region `0x8e100000 / 8 MiB`
  - QTEE reserved region `0xd80e0000 / 5.125 MiB`
  - TA reserved region `0xd8600000 / 138 MiB`

## Windows authority reused

- E004z: SecureCompanion trustlet identity 4096; SecureISP task and lane-protection ABI.
- E004aq: source-controller SecureMode trigger dynamically reaches CameraSecureISP.

## Interpretation boundary

QTEE service UID and Windows SecureCompanion TrustletIdentity are not assumed to be the same namespace.
