# E003i-H — integrated front LSC chain

This checkpoint connects the E003i-G clean-room IMX681 pre-Tintless producer directly to the validated sequential Surface Tintless state machine and then to the E003i-E template-free capsule composer.

The upstream path is generated from the installed front tuning, nominal IMX681 golden table, the preserved physical-front OTP slot and request interpolation state. It does **not** read captured `req*_input_mesh.bin`. Tintless output memory is initialized deterministically and does **not** read captured `req*_output_mesh_pre.bin`; zero, `0xA5`, and float-1 initializations all produce the same descriptor-addressed `0xdd0` output. The extra `0x20` capture tail is proven unreferenced and remains untouched. Captured LSC staging is also absent from the chain.

The remaining raw atomic fixtures are limited to the still-native Tintless ABI/state inputs (constructor wrapper state, x1 config, x2 statistics and x3/x4 descriptors) plus Windows post-output/core state used only for validation. DeviceMFT is now used only to execute the Tintless callback itself.

Generated R4/R5/R6 LSC0/LSC1/LSC2/GIC wire is identical to the accepted 0076 stream, and the unchanged template-free composer reproduces all three accepted 41,088-byte capsule SHA256 identities.

No Linux camera runtime is authorized or executed by this checkpoint. The next producer gate is a clean-room Tintless implementation and Linux acquisition of physical OTP/live trigger/statistics state.
