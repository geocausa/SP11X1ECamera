savedcmd_fastrpc-e004cv.o := gcc -Wp,-MMD,./.fastrpc-e004cv.o.d -nostdinc -I/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include -I/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated -I/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include -I/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/include -I/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi -I/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi -I/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi -I/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/include/generated/uapi -include /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/compiler-version.h -include /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kconfig.h -include /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/compiler_types.h -D__KERNEL__ -mlittle-endian -DCC_USING_PATCHABLE_FUNCTION_ENTRY -DKASAN_SHADOW_SCALE_SHIFT= -fshort-wchar -funsigned-char -fno-common -fno-PIE -fno-strict-aliasing -std=gnu11 -fms-extensions -mgeneral-regs-only -DCONFIG_CC_HAS_K_CONSTRAINT=1 -Wno-psabi -mabi=lp64 -fno-asynchronous-unwind-tables -fno-unwind-tables -mbranch-protection=pac-ret -Wa,-march=armv8.5-a -DARM64_ASM_ARCH='"armv8.5-a"' -DKASAN_SHADOW_SCALE_SHIFT= -fno-delete-null-pointer-checks -O2 -fno-allow-store-data-races -fstack-protector-strong -fno-omit-frame-pointer -fno-optimize-sibling-calls -ftrivial-auto-var-init=zero -fzero-init-padding-bits=all -fno-stack-clash-protection -fzero-call-used-regs=used-gpr -fpatchable-function-entry=4,2 -fmin-function-alignment=8 -fstrict-flex-arrays=3 -fno-strict-overflow -fno-stack-check -fconserve-stack -fno-builtin-wcslen -Wall -Wextra -Wundef -Werror=implicit-function-declaration -Werror=implicit-int -Werror=return-type -Werror=strict-prototypes -Wno-format-security -Wno-trigraphs -Wno-frame-address -Wno-address-of-packed-member -Wmissing-declarations -Wmissing-prototypes -Wframe-larger-than=1024 -Wno-main -Wno-type-limits -Wno-dangling-pointer -Wvla-larger-than=1 -Wno-pointer-sign -Wcast-function-type -Wno-unterminated-string-initialization -Wno-array-bounds -Wno-stringop-overflow -Wno-alloc-size-larger-than -Wimplicit-fallthrough=5 -Werror=date-time -Werror=incompatible-pointer-types -Werror=designated-init -Wenum-conversion -Wunused -Wno-unused-but-set-variable -Wno-unused-const-variable -Wno-packed-not-aligned -Wno-format-overflow -Wno-format-truncation -Wno-stringop-truncation -Wno-override-init -Wno-missing-field-initializers -Wno-shift-negative-value -Wno-maybe-uninitialized -Wno-sign-compare -Wno-unused-parameter -g -gdwarf-5 -mstack-protector-guard=sysreg -mstack-protector-guard-reg=sp_el0 -mstack-protector-guard-offset=1720  -fsanitize=bounds-strict -fsanitize=shift -fsanitize=bool -fsanitize=enum    -DMODULE  -DKBUILD_BASENAME='"fastrpc_e004cv"' -DKBUILD_MODNAME='"fastrpc_e004cv"' -D__KBUILD_MODNAME=fastrpc_e004cv -c -o fastrpc-e004cv.o fastrpc-e004cv.c  

source_fastrpc-e004cv.o := fastrpc-e004cv.c

deps_fastrpc-e004cv.o := \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/compiler-version.h \
    $(wildcard include/config/CC_VERSION_TEXT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kconfig.h \
    $(wildcard include/config/CPU_BIG_ENDIAN) \
    $(wildcard include/config/BOOGER) \
    $(wildcard include/config/FOO) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/compiler_types.h \
    $(wildcard include/config/DEBUG_INFO_BTF) \
    $(wildcard include/config/PAHOLE_HAS_BTF_TAG) \
    $(wildcard include/config/FUNCTION_ALIGNMENT) \
    $(wildcard include/config/CC_HAS_SANE_FUNCTION_ALIGNMENT) \
    $(wildcard include/config/X86_64) \
    $(wildcard include/config/ARM64) \
    $(wildcard include/config/LD_DEAD_CODE_DATA_ELIMINATION) \
    $(wildcard include/config/LTO_CLANG) \
    $(wildcard include/config/HAVE_ARCH_COMPILER_H) \
    $(wildcard include/config/KCSAN) \
    $(wildcard include/config/CC_HAS_ASSUME) \
    $(wildcard include/config/CC_HAS_COUNTED_BY) \
    $(wildcard include/config/FORTIFY_SOURCE) \
    $(wildcard include/config/UBSAN_BOUNDS) \
    $(wildcard include/config/CC_HAS_COUNTED_BY_PTR) \
    $(wildcard include/config/CC_HAS_MULTIDIMENSIONAL_NONSTRING) \
    $(wildcard include/config/CFI) \
    $(wildcard include/config/ARCH_USES_CFI_GENERIC_LLVM_PASS) \
    $(wildcard include/config/CC_HAS_BROKEN_COUNTED_BY_REF) \
    $(wildcard include/config/CC_HAS_ASM_INLINE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/compiler-context-analysis.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/compiler_attributes.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/compiler-gcc.h \
    $(wildcard include/config/ARCH_USE_BUILTIN_BSWAP) \
    $(wildcard include/config/SHADOW_CALL_STACK) \
    $(wildcard include/config/KCOV) \
    $(wildcard include/config/CC_HAS_TYPEOF_UNQUAL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/compiler.h \
    $(wildcard include/config/ARM64_PTR_AUTH_KERNEL) \
    $(wildcard include/config/ARM64_PTR_AUTH) \
    $(wildcard include/config/BUILTIN_RETURN_ADDRESS_STRIPS_PAC) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/capability.h \
    $(wildcard include/config/MULTIUSER) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/capability.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/types.h \
    $(wildcard include/config/HAVE_UID16) \
    $(wildcard include/config/UID16) \
    $(wildcard include/config/ARCH_DMA_ADDR_T_64BIT) \
    $(wildcard include/config/PHYS_ADDR_T_64BIT) \
    $(wildcard include/config/64BIT) \
    $(wildcard include/config/ARCH_32BIT_USTAT_F_TINODE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi/asm/types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/int-ll64.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/int-ll64.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/bitsperlong.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitsperlong.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/bitsperlong.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/posix_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/stddef.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/stddef.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/posix_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/posix_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/uidgid.h \
    $(wildcard include/config/USER_NS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/uidgid_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/highuid.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/bits.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/bits.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/const.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/const.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/bits.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/build_bug.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/compiler.h \
    $(wildcard include/config/TRACE_BRANCH_PROFILING) \
    $(wildcard include/config/PROFILE_ALL_BRANCHES) \
    $(wildcard include/config/OBJTOOL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/rwonce.h \
    $(wildcard include/config/LTO) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/rwonce.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kasan-checks.h \
    $(wildcard include/config/KASAN_GENERIC) \
    $(wildcard include/config/KASAN_SW_TAGS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kcsan-checks.h \
    $(wildcard include/config/KCSAN_WEAK_MEMORY) \
    $(wildcard include/config/KCSAN_IGNORE_ATOMICS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/overflow.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/limits.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/limits.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/limits.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/const.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/completion.h \
    $(wildcard include/config/LOCKDEP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/swait.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/list.h \
    $(wildcard include/config/LIST_HARDENED) \
    $(wildcard include/config/DEBUG_LIST) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/container_of.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/poison.h \
    $(wildcard include/config/ILLEGAL_POINTER_VALUE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/barrier.h \
    $(wildcard include/config/ARM64_PSEUDO_NMI) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/alternative-macros.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/cpucaps.h \
    $(wildcard include/config/ARM64_EPAN) \
    $(wildcard include/config/ARM64_SVE) \
    $(wildcard include/config/ARM64_SME) \
    $(wildcard include/config/ARM64_CNP) \
    $(wildcard include/config/ARM64_MTE) \
    $(wildcard include/config/ARM64_BTI) \
    $(wildcard include/config/ARM64_TLB_RANGE) \
    $(wildcard include/config/ARM64_POE) \
    $(wildcard include/config/ARM64_GCS) \
    $(wildcard include/config/ARM64_HAFT) \
    $(wildcard include/config/UNMAP_KERNEL_AT_EL0) \
    $(wildcard include/config/ARM64_ERRATUM_843419) \
    $(wildcard include/config/ARM64_ERRATUM_1742098) \
    $(wildcard include/config/ARM64_ERRATUM_2645198) \
    $(wildcard include/config/ARM64_ERRATUM_2658417) \
    $(wildcard include/config/CAVIUM_ERRATUM_23154) \
    $(wildcard include/config/NVIDIA_CARMEL_CNP_ERRATUM) \
    $(wildcard include/config/ARM64_WORKAROUND_REPEAT_TLBI) \
    $(wildcard include/config/ARM64_ERRATUM_3194386) \
    $(wildcard include/config/ARM64_ERRATUM_4193714) \
    $(wildcard include/config/HW_PERF_EVENTS) \
    $(wildcard include/config/ARM64_LSUI) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/cpucap-defs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/insn-def.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/brk-imm.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/stringify.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/barrier.h \
    $(wildcard include/config/SMP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/spinlock.h \
    $(wildcard include/config/DEBUG_SPINLOCK) \
    $(wildcard include/config/PREEMPTION) \
    $(wildcard include/config/DEBUG_LOCK_ALLOC) \
    $(wildcard include/config/PREEMPT_RT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/typecheck.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/preempt.h \
    $(wildcard include/config/PREEMPT_COUNT) \
    $(wildcard include/config/DEBUG_PREEMPT) \
    $(wildcard include/config/TRACE_PREEMPT_TOGGLE) \
    $(wildcard include/config/PREEMPT_NOTIFIERS) \
    $(wildcard include/config/PREEMPT_DYNAMIC) \
    $(wildcard include/config/PREEMPT_NONE) \
    $(wildcard include/config/PREEMPT_VOLUNTARY) \
    $(wildcard include/config/PREEMPT) \
    $(wildcard include/config/PREEMPT_LAZY) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/linkage.h \
    $(wildcard include/config/ARCH_USE_SYM_ANNOTATIONS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/export.h \
    $(wildcard include/config/MODVERSIONS) \
    $(wildcard include/config/GENDWARFKSYMS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/linkage.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/cleanup.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/err.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi/asm/errno.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/errno.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/errno-base.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/args.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/preempt.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/thread_info.h \
    $(wildcard include/config/THREAD_INFO_IN_TASK) \
    $(wildcard include/config/GENERIC_ENTRY) \
    $(wildcard include/config/ARCH_HAS_PREEMPT_LAZY) \
    $(wildcard include/config/HAVE_ARCH_WITHIN_STACK_FRAMES) \
    $(wildcard include/config/SH) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/bug.h \
    $(wildcard include/config/GENERIC_BUG) \
    $(wildcard include/config/PRINTK) \
    $(wildcard include/config/BUG_ON_DATA_CORRUPTION) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/bug.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/asm-bug.h \
    $(wildcard include/config/DEBUG_BUGVERBOSE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bug.h \
    $(wildcard include/config/DEBUG_BUGVERBOSE_DETAILED) \
    $(wildcard include/config/BUG) \
    $(wildcard include/config/GENERIC_BUG_RELATIVE_POINTERS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/instrumentation.h \
    $(wildcard include/config/NOINSTR_VALIDATION) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/once_lite.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/panic.h \
    $(wildcard include/config/PANIC_TIMEOUT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/stdarg.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/printk.h \
    $(wildcard include/config/MESSAGE_LOGLEVEL_DEFAULT) \
    $(wildcard include/config/CONSOLE_LOGLEVEL_DEFAULT) \
    $(wildcard include/config/CONSOLE_LOGLEVEL_QUIET) \
    $(wildcard include/config/EARLY_PRINTK) \
    $(wildcard include/config/PRINTK_INDEX) \
    $(wildcard include/config/DYNAMIC_DEBUG) \
    $(wildcard include/config/DYNAMIC_DEBUG_CORE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/init.h \
    $(wildcard include/config/MEMORY_HOTPLUG) \
    $(wildcard include/config/HAVE_ARCH_PREL32_RELOCATIONS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kern_levels.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/ratelimit_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/param.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/param.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/param.h \
    $(wildcard include/config/HZ) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/param.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/spinlock_types_raw.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/spinlock_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/qspinlock_types.h \
    $(wildcard include/config/NR_CPUS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/qrwlock_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/byteorder.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/byteorder/little_endian.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/byteorder/little_endian.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/swab.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/swab.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi/asm/swab.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/swab.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/byteorder/generic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/lockdep_types.h \
    $(wildcard include/config/PROVE_RAW_LOCK_NESTING) \
    $(wildcard include/config/LOCK_STAT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dynamic_debug.h \
    $(wildcard include/config/JUMP_LABEL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/jump_label.h \
    $(wildcard include/config/HAVE_ARCH_JUMP_LABEL_RELATIVE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/jump_label.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/insn.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/restart_block.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/time64.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/math64.h \
    $(wildcard include/config/ARCH_SUPPORTS_INT128) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/math.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/div64.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/div64.h \
    $(wildcard include/config/CC_OPTIMIZE_FOR_PERFORMANCE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/kernel.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/sysinfo.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/math64.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/time64.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/time.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/time_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/errno.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/errno.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/current.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/bitops.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/generic-non-atomic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/bitops.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/builtin-__ffs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/builtin-ffs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/builtin-__fls.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/builtin-fls.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/ffz.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/fls64.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/sched.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/hweight.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/arch_hweight.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/const_hweight.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/atomic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/atomic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/atomic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/cmpxchg.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/lse.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/atomic_ll_sc.h \
    $(wildcard include/config/CC_HAS_K_CONSTRAINT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/alternative.h \
    $(wildcard include/config/MODULES) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/atomic_lse.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/atomic/atomic-arch-fallback.h \
    $(wildcard include/config/GENERIC_ATOMIC64) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/atomic/atomic-long.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/atomic/atomic-instrumented.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/instrumented.h \
    $(wildcard include/config/DEBUG_ATOMIC) \
    $(wildcard include/config/DEBUG_ATOMIC_LARGEST_ALIGN) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kmsan-checks.h \
    $(wildcard include/config/KMSAN) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/instrumented-atomic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/lock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/instrumented-lock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/non-atomic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/non-instrumented-non-atomic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/le.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/bitops/ext2-atomic-setbit.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/thread_info.h \
    $(wildcard include/config/ARM64_SW_TTBR0_PAN) \
    $(wildcard include/config/ARM64_MPAM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/memory.h \
    $(wildcard include/config/ARM64_VA_BITS) \
    $(wildcard include/config/ARM64_16K_PAGES) \
    $(wildcard include/config/KASAN_SHADOW_OFFSET) \
    $(wildcard include/config/KASAN) \
    $(wildcard include/config/ARM64_4K_PAGES) \
    $(wildcard include/config/RANDOMIZE_BASE) \
    $(wildcard include/config/KASAN_HW_TAGS) \
    $(wildcard include/config/DEBUG_VIRTUAL) \
    $(wildcard include/config/EFI) \
    $(wildcard include/config/ARM_GIC_V3_ITS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sizes.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/page-def.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/page.h \
    $(wildcard include/config/PAGE_SHIFT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mmdebug.h \
    $(wildcard include/config/DEBUG_VM) \
    $(wildcard include/config/DEBUG_VM_IRQSOFF) \
    $(wildcard include/config/DEBUG_VM_PGFLAGS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/boot.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/sections.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/sections.h \
    $(wildcard include/config/HAVE_FUNCTION_DESCRIPTORS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/sysreg.h \
    $(wildcard include/config/BROKEN_GAS_INST) \
    $(wildcard include/config/ARM64_PA_BITS_52) \
    $(wildcard include/config/ARM64_64K_PAGES) \
    $(wildcard include/config/AMPERE_ERRATUM_AC04_CPU_23) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kasan-tags.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/gpr-num.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/sysreg-defs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/bitfield.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/memory_model.h \
    $(wildcard include/config/FLATMEM) \
    $(wildcard include/config/SPARSEMEM_VMEMMAP) \
    $(wildcard include/config/SPARSEMEM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pfn.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/stack_pointer.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irqflags.h \
    $(wildcard include/config/PROVE_LOCKING) \
    $(wildcard include/config/TRACE_IRQFLAGS) \
    $(wildcard include/config/IRQSOFF_TRACER) \
    $(wildcard include/config/PREEMPT_TRACER) \
    $(wildcard include/config/DEBUG_IRQFLAGS) \
    $(wildcard include/config/TRACE_IRQFLAGS_SUPPORT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irqflags_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/irqflags.h \
    $(wildcard include/config/ARM64_DEBUG_PRIORITY_MASKING) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/ptrace.h \
    $(wildcard include/config/COMPAT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/cpufeature.h \
    $(wildcard include/config/ARM64_BTI_KERNEL) \
    $(wildcard include/config/ARM64_PA_BITS) \
    $(wildcard include/config/ARM64_HW_AFDBM) \
    $(wildcard include/config/ARM64_AMU_EXTN) \
    $(wildcard include/config/ARM64_LPA2) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/cputype.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/hwcap.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/hwcap.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/log2.h \
    $(wildcard include/config/ARCH_HAS_ILOG2_U32) \
    $(wildcard include/config/ARCH_HAS_ILOG2_U64) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/kernel-hwcap.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kernel.h \
    $(wildcard include/config/PREEMPT_VOLUNTARY_BUILD) \
    $(wildcard include/config/HAVE_PREEMPT_DYNAMIC_CALL) \
    $(wildcard include/config/HAVE_PREEMPT_DYNAMIC_KEY) \
    $(wildcard include/config/PREEMPT_) \
    $(wildcard include/config/DEBUG_ATOMIC_SLEEP) \
    $(wildcard include/config/MMU) \
    $(wildcard include/config/DYNAMIC_FTRACE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/align.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/align.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/array_size.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kstrtox.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/minmax.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sprintf.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/static_call_types.h \
    $(wildcard include/config/HAVE_STATIC_CALL) \
    $(wildcard include/config/HAVE_STATIC_CALL_INLINE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/trace_printk.h \
    $(wildcard include/config/TRACING) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/instruction_pointer.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/util_macros.h \
    $(wildcard include/config/FOO_SUSPEND) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/wordpart.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/cpumask.h \
    $(wildcard include/config/FORCE_NR_CPUS) \
    $(wildcard include/config/HOTPLUG_CPU) \
    $(wildcard include/config/DEBUG_PER_CPU_MAPS) \
    $(wildcard include/config/CPUMASK_OFFSTACK) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/bitmap.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/find.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/string.h \
    $(wildcard include/config/BINARY_PRINTF) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/string.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/string.h \
    $(wildcard include/config/ARCH_HAS_UACCESS_FLUSHCACHE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/fortify-string.h \
    $(wildcard include/config/CC_HAS_KASAN_MEMINTRINSIC_PREFIX) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/bitmap-str.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/cpumask_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/threads.h \
    $(wildcard include/config/BASE_SMALL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/gfp_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/numa.h \
    $(wildcard include/config/NUMA_KEEP_MEMINFO) \
    $(wildcard include/config/NUMA) \
    $(wildcard include/config/HAVE_ARCH_NODE_DEV_GROUP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/nodemask.h \
    $(wildcard include/config/HIGHMEM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/nodemask_types.h \
    $(wildcard include/config/NODES_SHIFT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/random.h \
    $(wildcard include/config/VMGENID) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/random.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/ioctl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi/asm/ioctl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/ioctl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/ioctl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irqnr.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/irqnr.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/sparsemem.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/pgtable-prot.h \
    $(wildcard include/config/HAVE_ARCH_USERFAULTFD_WP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/pgtable-hwdef.h \
    $(wildcard include/config/PGTABLE_LEVELS) \
    $(wildcard include/config/ARM64_CONT_PTE_SHIFT) \
    $(wildcard include/config/ARM64_CONT_PMD_SHIFT) \
    $(wildcard include/config/ARM64_VA_BITS_52) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/pgtable-types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/rsi.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/rsi_cmds.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/arm-smccc.h \
    $(wildcard include/config/HAVE_ARM_SMCCC) \
    $(wildcard include/config/ARM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/uuid.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/rsi_smc.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/ptrace.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/sve_context.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irqchip/arm-gic-v3-prio.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/stacktrace/frame.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/percpu.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/percpu.h \
    $(wildcard include/config/HAVE_SETUP_PER_CPU_AREA) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/percpu-defs.h \
    $(wildcard include/config/ARCH_MODULE_NEEDS_WEAK_PER_CPU) \
    $(wildcard include/config/DEBUG_FORCE_WEAK_PER_CPU) \
    $(wildcard include/config/AMD_MEM_ENCRYPT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/bottom_half.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/lockdep.h \
    $(wildcard include/config/DEBUG_LOCKING_API_SELFTESTS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/smp.h \
    $(wildcard include/config/UP_LATE_INIT) \
    $(wildcard include/config/CSD_LOCK_WAIT_DEBUG) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/smp_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/llist.h \
    $(wildcard include/config/ARCH_HAVE_NMI_SAFE_CMPXCHG) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/smp.h \
    $(wildcard include/config/ARM64_ACPI_PARKING_PROTOCOL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/mmiowb.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/mmiowb.h \
    $(wildcard include/config/MMIOWB) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/spinlock_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rwlock_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/spinlock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/qspinlock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/qspinlock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/qrwlock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/qrwlock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/processor.h \
    $(wildcard include/config/KUSER_HELPERS) \
    $(wildcard include/config/ARM64_FORCE_52BIT) \
    $(wildcard include/config/HAVE_HW_BREAKPOINT) \
    $(wildcard include/config/ARM64_TAGGED_ADDR_ABI) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/cache.h \
    $(wildcard include/config/ARCH_HAS_CACHE_LINE_SIZE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/cache.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/cache.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kasan-enabled.h \
    $(wildcard include/config/ARCH_DEFER_KASAN) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/static_key.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/mte-def.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/processor.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/vdso/processor.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/hw_breakpoint.h \
    $(wildcard include/config/CPU_PM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/virt.h \
    $(wildcard include/config/KVM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/kasan.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/mte-kasan.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/pointer_auth.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/prctl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/spectre.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/fpsimd.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/sigcontext.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rwlock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/spinlock_api_smp.h \
    $(wildcard include/config/INLINE_SPIN_LOCK) \
    $(wildcard include/config/INLINE_SPIN_LOCK_BH) \
    $(wildcard include/config/INLINE_SPIN_LOCK_IRQ) \
    $(wildcard include/config/INLINE_SPIN_LOCK_IRQSAVE) \
    $(wildcard include/config/INLINE_SPIN_TRYLOCK) \
    $(wildcard include/config/INLINE_SPIN_TRYLOCK_BH) \
    $(wildcard include/config/UNINLINE_SPIN_UNLOCK) \
    $(wildcard include/config/INLINE_SPIN_UNLOCK_BH) \
    $(wildcard include/config/INLINE_SPIN_UNLOCK_IRQ) \
    $(wildcard include/config/INLINE_SPIN_UNLOCK_IRQRESTORE) \
    $(wildcard include/config/GENERIC_LOCKBREAK) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rwlock_api_smp.h \
    $(wildcard include/config/INLINE_READ_LOCK) \
    $(wildcard include/config/INLINE_WRITE_LOCK) \
    $(wildcard include/config/INLINE_READ_LOCK_BH) \
    $(wildcard include/config/INLINE_WRITE_LOCK_BH) \
    $(wildcard include/config/INLINE_READ_LOCK_IRQ) \
    $(wildcard include/config/INLINE_WRITE_LOCK_IRQ) \
    $(wildcard include/config/INLINE_READ_LOCK_IRQSAVE) \
    $(wildcard include/config/INLINE_WRITE_LOCK_IRQSAVE) \
    $(wildcard include/config/INLINE_READ_TRYLOCK) \
    $(wildcard include/config/INLINE_WRITE_TRYLOCK) \
    $(wildcard include/config/INLINE_READ_UNLOCK) \
    $(wildcard include/config/INLINE_WRITE_UNLOCK) \
    $(wildcard include/config/INLINE_READ_UNLOCK_BH) \
    $(wildcard include/config/INLINE_WRITE_UNLOCK_BH) \
    $(wildcard include/config/INLINE_READ_UNLOCK_IRQ) \
    $(wildcard include/config/INLINE_WRITE_UNLOCK_IRQ) \
    $(wildcard include/config/INLINE_READ_UNLOCK_IRQRESTORE) \
    $(wildcard include/config/INLINE_WRITE_UNLOCK_IRQRESTORE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/wait.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/device.h \
    $(wildcard include/config/GENERIC_MSI_IRQ) \
    $(wildcard include/config/ENERGY_MODEL) \
    $(wildcard include/config/PINCTRL) \
    $(wildcard include/config/ARCH_HAS_DMA_OPS) \
    $(wildcard include/config/DMA_DECLARE_COHERENT) \
    $(wildcard include/config/DMA_CMA) \
    $(wildcard include/config/SWIOTLB) \
    $(wildcard include/config/SWIOTLB_DYNAMIC) \
    $(wildcard include/config/ARCH_HAS_SYNC_DMA_FOR_DEVICE) \
    $(wildcard include/config/ARCH_HAS_SYNC_DMA_FOR_CPU) \
    $(wildcard include/config/ARCH_HAS_SYNC_DMA_FOR_CPU_ALL) \
    $(wildcard include/config/DMA_OPS_BYPASS) \
    $(wildcard include/config/DMA_NEED_SYNC) \
    $(wildcard include/config/IOMMU_DMA) \
    $(wildcard include/config/PM) \
    $(wildcard include/config/PM_SLEEP) \
    $(wildcard include/config/OF) \
    $(wildcard include/config/DEVTMPFS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dev_printk.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/ratelimit.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched.h \
    $(wildcard include/config/VIRT_CPU_ACCOUNTING_NATIVE) \
    $(wildcard include/config/SCHED_INFO) \
    $(wildcard include/config/SCHEDSTATS) \
    $(wildcard include/config/SCHED_CORE) \
    $(wildcard include/config/FAIR_GROUP_SCHED) \
    $(wildcard include/config/RT_GROUP_SCHED) \
    $(wildcard include/config/RT_MUTEXES) \
    $(wildcard include/config/UCLAMP_TASK) \
    $(wildcard include/config/UCLAMP_BUCKETS_COUNT) \
    $(wildcard include/config/KMAP_LOCAL) \
    $(wildcard include/config/MEM_ALLOC_PROFILING) \
    $(wildcard include/config/SCHED_CLASS_EXT) \
    $(wildcard include/config/CGROUP_SCHED) \
    $(wildcard include/config/CFS_BANDWIDTH) \
    $(wildcard include/config/BLK_DEV_IO_TRACE) \
    $(wildcard include/config/PREEMPT_RCU) \
    $(wildcard include/config/TASKS_RCU) \
    $(wildcard include/config/TASKS_TRACE_RCU) \
    $(wildcard include/config/TRIVIAL_PREEMPT_RCU) \
    $(wildcard include/config/MEMCG_V1) \
    $(wildcard include/config/LRU_GEN) \
    $(wildcard include/config/COMPAT_BRK) \
    $(wildcard include/config/CGROUPS) \
    $(wildcard include/config/BLK_CGROUP) \
    $(wildcard include/config/PSI) \
    $(wildcard include/config/PAGE_OWNER) \
    $(wildcard include/config/EVENTFD) \
    $(wildcard include/config/ARCH_HAS_CPU_PASID) \
    $(wildcard include/config/X86_BUS_LOCK_DETECT) \
    $(wildcard include/config/TASK_DELAY_ACCT) \
    $(wildcard include/config/STACKPROTECTOR) \
    $(wildcard include/config/ARCH_HAS_SCALED_CPUTIME) \
    $(wildcard include/config/VIRT_CPU_ACCOUNTING_GEN) \
    $(wildcard include/config/NO_HZ_FULL) \
    $(wildcard include/config/POSIX_CPUTIMERS) \
    $(wildcard include/config/POSIX_CPU_TIMERS_TASK_WORK) \
    $(wildcard include/config/KEYS) \
    $(wildcard include/config/SYSVIPC) \
    $(wildcard include/config/DETECT_HUNG_TASK) \
    $(wildcard include/config/IO_URING) \
    $(wildcard include/config/AUDIT) \
    $(wildcard include/config/AUDITSYSCALL) \
    $(wildcard include/config/DETECT_HUNG_TASK_BLOCKER) \
    $(wildcard include/config/UBSAN) \
    $(wildcard include/config/UBSAN_TRAP) \
    $(wildcard include/config/COMPACTION) \
    $(wildcard include/config/TASK_XACCT) \
    $(wildcard include/config/CPUSETS) \
    $(wildcard include/config/X86_CPU_RESCTRL) \
    $(wildcard include/config/FUTEX) \
    $(wildcard include/config/PERF_EVENTS) \
    $(wildcard include/config/NUMA_BALANCING) \
    $(wildcard include/config/ARCH_HAS_LAZY_MMU_MODE) \
    $(wildcard include/config/FAULT_INJECTION) \
    $(wildcard include/config/LATENCYTOP) \
    $(wildcard include/config/KUNIT) \
    $(wildcard include/config/FUNCTION_GRAPH_TRACER) \
    $(wildcard include/config/MEMCG) \
    $(wildcard include/config/UPROBES) \
    $(wildcard include/config/BCACHE) \
    $(wildcard include/config/VMAP_STACK) \
    $(wildcard include/config/LIVEPATCH) \
    $(wildcard include/config/SECURITY) \
    $(wildcard include/config/BPF_SYSCALL) \
    $(wildcard include/config/KSTACK_ERASE) \
    $(wildcard include/config/KSTACK_ERASE_METRICS) \
    $(wildcard include/config/X86_MCE) \
    $(wildcard include/config/KRETPROBES) \
    $(wildcard include/config/RETHOOK) \
    $(wildcard include/config/ARCH_HAS_PARANOID_L1D_FLUSH) \
    $(wildcard include/config/RV) \
    $(wildcard include/config/RV_PER_TASK_MONITORS) \
    $(wildcard include/config/USER_EVENTS) \
    $(wildcard include/config/UNWIND_USER) \
    $(wildcard include/config/SCHED_PROXY_EXEC) \
    $(wildcard include/config/MEM_ALLOC_PROFILING_DEBUG) \
    $(wildcard include/config/SCHED_MM_CID) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/sched.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pid_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sem_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/shm.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/page.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/personality.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/personality.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/getorder.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/shmparam.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/shmparam.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kmsan_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mutex_types.h \
    $(wildcard include/config/MUTEX_SPIN_ON_OWNER) \
    $(wildcard include/config/DEBUG_MUTEXES) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/osq_lock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/plist_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/hrtimer_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/timerqueue_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rbtree_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/timer_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/seccomp_types.h \
    $(wildcard include/config/SECCOMP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/refcount_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/resource.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/resource.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi/asm/resource.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/resource.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/resource.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/latencytop.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/prio.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/signal_types.h \
    $(wildcard include/config/OLD_SIGACTION) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/signal.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/signal.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/signal.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/signal.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/signal.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/signal-defs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi/asm/siginfo.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/siginfo.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/syscall_user_dispatch_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mm_types_task.h \
    $(wildcard include/config/ARCH_WANT_BATCHED_UNMAP_TLB_FLUSH) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/tlbbatch.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/netdevice_xmit.h \
    $(wildcard include/config/NET_ACT_MIRRED) \
    $(wildcard include/config/NET_EGRESS) \
    $(wildcard include/config/NF_DUP_NETDEV) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/task_io_accounting.h \
    $(wildcard include/config/TASK_IO_ACCOUNTING) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/posix-timers_types.h \
    $(wildcard include/config/POSIX_TIMERS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rseq_types.h \
    $(wildcard include/config/RSEQ) \
    $(wildcard include/config/RSEQ_SLICE_EXTENSION) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irq_work_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/workqueue_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/seqlock_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kcsan.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rv.h \
    $(wildcard include/config/RV_LTL_MONITOR) \
    $(wildcard include/config/RV_HA_MONITOR) \
    $(wildcard include/config/RV_REACTORS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/tracepoint-defs.h \
    $(wildcard include/config/TRACEPOINTS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/unwind_deferred_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/kmap_size.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/kmap_size.h \
    $(wildcard include/config/DEBUG_KMAP_LOCAL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/include/generated/rq-offsets.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/ext.h \
    $(wildcard include/config/EXT_GROUP_SCHED) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/energy_model.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kobject.h \
    $(wildcard include/config/UEVENT_HELPER) \
    $(wildcard include/config/DEBUG_KOBJECT_RELEASE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sysfs.h \
    $(wildcard include/config/SYSFS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kernfs.h \
    $(wildcard include/config/KERNFS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mutex.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/debug_locks.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/idr.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/radix-tree.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/percpu.h \
    $(wildcard include/config/RANDOM_KMALLOC_CACHES) \
    $(wildcard include/config/PAGE_SIZE_4KB) \
    $(wildcard include/config/NEED_PER_CPU_PAGE_FIRST_CHUNK) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/alloc_tag.h \
    $(wildcard include/config/MEM_ALLOC_PROFILING_ENABLED_BY_DEFAULT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/codetag.h \
    $(wildcard include/config/CODE_TAGGING) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rcupdate.h \
    $(wildcard include/config/TINY_RCU) \
    $(wildcard include/config/RCU_STRICT_GRACE_PERIOD) \
    $(wildcard include/config/RCU_LAZY) \
    $(wildcard include/config/RCU_STALL_COMMON) \
    $(wildcard include/config/VIRT_XFER_TO_GUEST_WORK) \
    $(wildcard include/config/RCU_NOCB_CPU) \
    $(wildcard include/config/TASKS_RCU_GENERIC) \
    $(wildcard include/config/TASKS_RUDE_RCU) \
    $(wildcard include/config/TREE_RCU) \
    $(wildcard include/config/DEBUG_OBJECTS_RCU_HEAD) \
    $(wildcard include/config/PROVE_RCU) \
    $(wildcard include/config/ARCH_WEAK_RELEASE_ACQUIRE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/context_tracking_irq.h \
    $(wildcard include/config/CONTEXT_TRACKING_IDLE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rcutree.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/xarray.h \
    $(wildcard include/config/XARRAY_MULTI) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/gfp.h \
    $(wildcard include/config/ZONE_DMA) \
    $(wildcard include/config/ZONE_DMA32) \
    $(wildcard include/config/ZONE_DEVICE) \
    $(wildcard include/config/CONTIG_ALLOC) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mmzone.h \
    $(wildcard include/config/ARCH_FORCE_MAX_ORDER) \
    $(wildcard include/config/PAGE_BLOCK_MAX_ORDER) \
    $(wildcard include/config/HAVE_GIGANTIC_FOLIOS) \
    $(wildcard include/config/HUGETLB_PAGE) \
    $(wildcard include/config/HUGETLB_PAGE_OPTIMIZE_VMEMMAP) \
    $(wildcard include/config/CMA) \
    $(wildcard include/config/MEMORY_ISOLATION) \
    $(wildcard include/config/ZSMALLOC) \
    $(wildcard include/config/UNACCEPTED_MEMORY) \
    $(wildcard include/config/IOMMU_SUPPORT) \
    $(wildcard include/config/SWAP) \
    $(wildcard include/config/TRANSPARENT_HUGEPAGE) \
    $(wildcard include/config/LRU_GEN_STATS) \
    $(wildcard include/config/LRU_GEN_WALKS_MMU) \
    $(wildcard include/config/MEMORY_FAILURE) \
    $(wildcard include/config/PAGE_EXTENSION) \
    $(wildcard include/config/DEFERRED_STRUCT_PAGE_INIT) \
    $(wildcard include/config/HAVE_MEMORYLESS_NODES) \
    $(wildcard include/config/SPARSEMEM_EXTREME) \
    $(wildcard include/config/SPARSEMEM_VMEMMAP_PREINIT) \
    $(wildcard include/config/HAVE_ARCH_PFN_VALID) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/list_nulls.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/seqlock.h \
    $(wildcard include/config/CC_IS_GCC) \
    $(wildcard include/config/GCC_VERSION) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pageblock-flags.h \
    $(wildcard include/config/HUGETLB_PAGE_SIZE_VARIABLE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/page-flags-layout.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/include/generated/bounds.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mm_types.h \
    $(wildcard include/config/HAVE_ALIGNED_STRUCT_PAGE) \
    $(wildcard include/config/SLAB_OBJ_EXT) \
    $(wildcard include/config/HUGETLB_PMD_PAGE_TABLE_SHARING) \
    $(wildcard include/config/SLAB_FREELIST_HARDENED) \
    $(wildcard include/config/USERFAULTFD) \
    $(wildcard include/config/ANON_VMA_NAME) \
    $(wildcard include/config/PER_VMA_LOCK) \
    $(wildcard include/config/HAVE_ARCH_COMPAT_MMAP_BASES) \
    $(wildcard include/config/MEMBARRIER) \
    $(wildcard include/config/FUTEX_PRIVATE_HASH) \
    $(wildcard include/config/ARCH_HAS_ELF_CORE_EFLAGS) \
    $(wildcard include/config/AIO) \
    $(wildcard include/config/MMU_NOTIFIER) \
    $(wildcard include/config/SPLIT_PMD_PTLOCKS) \
    $(wildcard include/config/IOMMU_MM_DATA) \
    $(wildcard include/config/KSM) \
    $(wildcard include/config/MM_ID) \
    $(wildcard include/config/CORE_DUMP_DEFAULT_ELF_HEADERS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/auxvec.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/auxvec.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/auxvec.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kref.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/refcount.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rbtree.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/maple_tree.h \
    $(wildcard include/config/MAPLE_RCU_DISABLED) \
    $(wildcard include/config/DEBUG_MAPLE_TREE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rwsem.h \
    $(wildcard include/config/RWSEM_SPIN_ON_OWNER) \
    $(wildcard include/config/DEBUG_RWSEMS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/uprobes.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/timer.h \
    $(wildcard include/config/DEBUG_OBJECTS_TIMERS) \
    $(wildcard include/config/NO_HZ_COMMON) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/ktime.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/jiffies.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/time.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/time32.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/timex.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/timex.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/timex.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/arch_timer.h \
    $(wildcard include/config/ARM_ARCH_TIMER_OOL_WORKAROUND) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/clocksource/arm_arch_timer.h \
    $(wildcard include/config/ARM_ARCH_TIMER) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/timecounter.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/timex.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/time32.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/time.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/jiffies.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/include/generated/timeconst.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/vdso/ktime.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/timekeeping.h \
    $(wildcard include/config/POSIX_AUX_CLOCKS) \
    $(wildcard include/config/GENERIC_CMOS_UPDATE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/clocksource_ids.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/debugobjects.h \
    $(wildcard include/config/DEBUG_OBJECTS) \
    $(wildcard include/config/DEBUG_OBJECTS_FREE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/uprobes.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/debug-monitors.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/esr.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/probes.h \
    $(wildcard include/config/KPROBES) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/workqueue.h \
    $(wildcard include/config/DEBUG_OBJECTS_WORK) \
    $(wildcard include/config/FREEZER) \
    $(wildcard include/config/WQ_WATCHDOG) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/percpu_counter.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/mmu.h \
    $(wildcard include/config/ARM64_E0PD) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/page-flags.h \
    $(wildcard include/config/PAGE_IDLE_FLAG) \
    $(wildcard include/config/ARCH_USES_PG_ARCH_2) \
    $(wildcard include/config/ARCH_USES_PG_ARCH_3) \
    $(wildcard include/config/MIGRATION) \
    $(wildcard include/config/DEBUG_KMAP_LOCAL_FORCE_MAP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/local_lock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/local_lock_internal.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/zswap.h \
    $(wildcard include/config/ZSWAP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/memory_hotplug.h \
    $(wildcard include/config/ARCH_HAS_ADD_PAGES) \
    $(wildcard include/config/MEMORY_HOTREMOVE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/notifier.h \
    $(wildcard include/config/TREE_SRCU) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/srcu.h \
    $(wildcard include/config/TINY_SRCU) \
    $(wildcard include/config/NEED_SRCU_NMI_SAFE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rcu_segcblist.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/srcutree.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rcu_node_tree.h \
    $(wildcard include/config/RCU_FANOUT) \
    $(wildcard include/config/RCU_FANOUT_LEAF) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/mmzone.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/mmzone.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/topology.h \
    $(wildcard include/config/USE_PERCPU_NUMA_NODE_ID) \
    $(wildcard include/config/SCHED_SMT) \
    $(wildcard include/config/GENERIC_ARCH_TOPOLOGY) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/arch_topology.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/topology.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/numa.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/numa.h \
    $(wildcard include/config/NUMA_EMU) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/topology.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/mm.h \
    $(wildcard include/config/MMU_LAZY_TLB_REFCOUNT) \
    $(wildcard include/config/ARCH_HAS_MEMBARRIER_CALLBACKS) \
    $(wildcard include/config/ARCH_HAS_SYNC_CORE_BEFORE_USERMODE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sync_core.h \
    $(wildcard include/config/ARCH_HAS_PREPARE_SYNC_CORE_CMD) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/coredump.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kobject_ns.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/stat.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/stat.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi/asm/stat.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/stat.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/compat.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/compat.h \
    $(wildcard include/config/COMPAT_FOR_U64_ALIGNMENT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/task_stack.h \
    $(wildcard include/config/STACK_GROWSUP) \
    $(wildcard include/config/DEBUG_STACK_USAGE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/magic.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kasan.h \
    $(wildcard include/config/KASAN_STACK) \
    $(wildcard include/config/KASAN_VMALLOC) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/stat.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/cpufreq.h \
    $(wildcard include/config/CPU_FREQ) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/topology.h \
    $(wildcard include/config/SCHED_CLUSTER) \
    $(wildcard include/config/SCHED_MC) \
    $(wildcard include/config/CPU_FREQ_GOV_SCHEDUTIL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/idle.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/sd_flags.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/ioport.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/klist.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pm.h \
    $(wildcard include/config/VT_CONSOLE_SLEEP) \
    $(wildcard include/config/CXL_SUSPEND) \
    $(wildcard include/config/PM_CLK) \
    $(wildcard include/config/PM_GENERIC_DOMAINS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/device/bus.h \
    $(wildcard include/config/ACPI) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/device/class.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/device/devres.h \
    $(wildcard include/config/HAS_IOMEM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/device/driver.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/module.h \
    $(wildcard include/config/MODULES_TREE_LOOKUP) \
    $(wildcard include/config/STACKTRACE_BUILD_ID) \
    $(wildcard include/config/ARCH_USES_CFI_TRAPS) \
    $(wildcard include/config/MODULE_SIG) \
    $(wildcard include/config/KALLSYMS) \
    $(wildcard include/config/BPF_EVENTS) \
    $(wildcard include/config/DEBUG_INFO_BTF_MODULES) \
    $(wildcard include/config/EVENT_TRACING) \
    $(wildcard include/config/MODULE_UNLOAD) \
    $(wildcard include/config/CONSTRUCTORS) \
    $(wildcard include/config/FUNCTION_ERROR_INJECTION) \
    $(wildcard include/config/MITIGATION_RETPOLINE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/buildid.h \
    $(wildcard include/config/VMCORE_INFO) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kmod.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/umh.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sysctl.h \
    $(wildcard include/config/SYSCTL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/sysctl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/elf.h \
    $(wildcard include/config/ARCH_HAVE_EXTRA_ELF_NOTES) \
    $(wildcard include/config/ARCH_USE_GNU_PROPERTY) \
    $(wildcard include/config/ARCH_HAVE_ELF_PROT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/elf.h \
    $(wildcard include/config/COMPAT_VDSO) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/user.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/user.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/elf.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/elf-em.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/fs.h \
    $(wildcard include/config/FANOTIFY_ACCESS_PERMISSIONS) \
    $(wildcard include/config/READ_ONLY_THP_FOR_FS) \
    $(wildcard include/config/FS_POSIX_ACL) \
    $(wildcard include/config/CGROUP_WRITEBACK) \
    $(wildcard include/config/IMA) \
    $(wildcard include/config/FILE_LOCKING) \
    $(wildcard include/config/FSNOTIFY) \
    $(wildcard include/config/EPOLL) \
    $(wildcard include/config/FS_DAX) \
    $(wildcard include/config/BLOCK) \
    $(wildcard include/config/UNICODE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/fs/super.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/fs/super_types.h \
    $(wildcard include/config/QUOTA) \
    $(wildcard include/config/FS_ENCRYPTION) \
    $(wildcard include/config/FS_VERITY) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/fs_dirent.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/errseq.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/list_lru.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/shrinker.h \
    $(wildcard include/config/SHRINKER_DEBUG) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/list_bl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/bit_spinlock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/percpu-rwsem.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rcuwait.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/signal.h \
    $(wildcard include/config/SCHED_AUTOGROUP) \
    $(wildcard include/config/BSD_PROCESS_ACCT) \
    $(wildcard include/config/TASKSTATS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rculist.h \
    $(wildcard include/config/PROVE_RCU_LIST) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/signal.h \
    $(wildcard include/config/DYNAMIC_SIGFRAME) \
    $(wildcard include/config/PROC_FS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/jobctl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/task.h \
    $(wildcard include/config/HAVE_EXIT_THREAD) \
    $(wildcard include/config/ARCH_WANTS_DYNAMIC_TASK_STRUCT) \
    $(wildcard include/config/HAVE_ARCH_THREAD_STRUCT_WHITELIST) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/uaccess.h \
    $(wildcard include/config/ARCH_HAS_SUBPAGE_FAULTS) \
    $(wildcard include/config/HARDENED_USERCOPY) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/fault-inject-usercopy.h \
    $(wildcard include/config/FAULT_INJECTION_USERCOPY) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/nospec.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/ucopysize.h \
    $(wildcard include/config/HARDENED_USERCOPY_DEFAULT_ON) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/uaccess.h \
    $(wildcard include/config/CC_HAS_ASM_GOTO_OUTPUT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/kernel-pgtable.h \
    $(wildcard include/config/RELOCATABLE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/asm-extable.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/mte.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/extable.h \
    $(wildcard include/config/BPF_JIT) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/access_ok.h \
    $(wildcard include/config/ALTERNATE_USER_ADDRESS_SPACE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/cred.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/key.h \
    $(wildcard include/config/KEY_NOTIFICATIONS) \
    $(wildcard include/config/NET) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/assoc_array.h \
    $(wildcard include/config/ASSOCIATIVE_ARRAY) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/user.h \
    $(wildcard include/config/VFIO_PCI_ZDEV_KVM) \
    $(wildcard include/config/IOMMUFD) \
    $(wildcard include/config/WATCH_QUEUE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pid.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rhashtable-types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/posix-timers.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/alarmtimer.h \
    $(wildcard include/config/RTC_CLASS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/hrtimer.h \
    $(wildcard include/config/HIGH_RES_TIMERS) \
    $(wildcard include/config/TIME_LOW_RES) \
    $(wildcard include/config/TIMERFD) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/hrtimer_defs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/timerqueue.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/hrtimer_rearm.h \
    $(wildcard include/config/HRTIMER_REARM_DEFERRED) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rcuref.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rcu_sync.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/quota.h \
    $(wildcard include/config/QUOTA_NETLINK_INTERFACE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/dqblk_xfs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dqblk_v1.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dqblk_v2.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dqblk_qtree.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/projid.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/quota.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/unicode.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dcache.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rculist_bl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/lockref.h \
    $(wildcard include/config/ARCH_USE_CMPXCHG_LOCKREF) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/stringhash.h \
    $(wildcard include/config/DCACHE_WORD_ACCESS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/hash.h \
    $(wildcard include/config/HAVE_ARCH_HASH) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/vfsdebug.h \
    $(wildcard include/config/DEBUG_VFS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/wait_bit.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/kdev_t.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/kdev_t.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/path.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/semaphore.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/fcntl.h \
    $(wildcard include/config/ARCH_32BIT_OFF_T) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/fcntl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/uapi/asm/fcntl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/fcntl.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/openat2.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/migrate_mode.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/delayed_call.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/ioprio.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sched/rt.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/iocontext.h \
    $(wildcard include/config/BLK_ICQ) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/ioprio.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mount.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mnt_idmapping.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/slab.h \
    $(wildcard include/config/FAILSLAB) \
    $(wildcard include/config/KFENCE) \
    $(wildcard include/config/SLUB_TINY) \
    $(wildcard include/config/SLUB_DEBUG) \
    $(wildcard include/config/SLAB_BUCKETS) \
    $(wildcard include/config/KVFREE_RCU_BATCHED) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/percpu-refcount.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rw_hint.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/file_ref.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/fs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/moduleparam.h \
    $(wildcard include/config/ALPHA) \
    $(wildcard include/config/PPC64) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rbtree_latch.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/error-injection.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/error-injection.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/module.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/module.h \
    $(wildcard include/config/HAVE_MOD_ARCH_SPECIFIC) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/device.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pm_wakeup.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dma-buf.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/iosys-map.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/io.h \
    $(wildcard include/config/HAS_IOPORT_MAP) \
    $(wildcard include/config/PCI) \
    $(wildcard include/config/STRICT_DEVMEM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/io.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pgtable.h \
    $(wildcard include/config/HIGHPTE) \
    $(wildcard include/config/ARCH_HAS_NONLEAF_PMD_YOUNG) \
    $(wildcard include/config/ARCH_HAS_HW_PTE_YOUNG) \
    $(wildcard include/config/GUP_GET_PXX_LOW_HIGH) \
    $(wildcard include/config/ARCH_WANT_PMD_MKWRITE) \
    $(wildcard include/config/HAVE_ARCH_TRANSPARENT_HUGEPAGE_PUD) \
    $(wildcard include/config/MEM_SOFT_DIRTY) \
    $(wildcard include/config/HAVE_ARCH_SOFT_DIRTY) \
    $(wildcard include/config/ARCH_ENABLE_THP_MIGRATION) \
    $(wildcard include/config/HAVE_ARCH_HUGE_VMAP) \
    $(wildcard include/config/X86_ESPFIX64) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/pgtable.h \
    $(wildcard include/config/ARCH_SUPPORTS_PMD_PFNMAP) \
    $(wildcard include/config/PAGE_TABLE_CHECK) \
    $(wildcard include/config/ARM64_CONTPTE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/proc-fns.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/tlbflush.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mmu_notifier.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mmap_lock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/interval_tree.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/fixmap.h \
    $(wildcard include/config/ACPI_APEI_GHES) \
    $(wildcard include/config/ARM_SDE_INTERFACE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/fixmap.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/por.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/page_table_check.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/pgtable_uffd.h \
    $(wildcard include/config/PTE_MARKER_UFFD_WP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/early_ioremap.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/early_ioremap.h \
    $(wildcard include/config/GENERIC_EARLY_IOREMAP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/io.h \
    $(wildcard include/config/GENERIC_IOMAP) \
    $(wildcard include/config/TRACE_MMIO_ACCESS) \
    $(wildcard include/config/HAS_IOPORT) \
    $(wildcard include/config/GENERIC_IOREMAP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/pci_iomap.h \
    $(wildcard include/config/NO_GENERIC_PCI_IOPORT_MAP) \
    $(wildcard include/config/GENERIC_PCI_IOMAP) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/logic_pio.h \
    $(wildcard include/config/INDIRECT_PIO) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/fwnode.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/file.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/scatterlist.h \
    $(wildcard include/config/NEED_SG_DMA_LENGTH) \
    $(wildcard include/config/NEED_SG_DMA_FLAGS) \
    $(wildcard include/config/DEBUG_SG) \
    $(wildcard include/config/SGL_ALLOC) \
    $(wildcard include/config/ARCH_NO_SG_CHAIN) \
    $(wildcard include/config/SG_POOL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mm.h \
    $(wildcard include/config/HAVE_ARCH_MMAP_RND_BITS) \
    $(wildcard include/config/HAVE_ARCH_MMAP_RND_COMPAT_BITS) \
    $(wildcard include/config/PPC32) \
    $(wildcard include/config/X86_USER_SHADOW_STACK) \
    $(wildcard include/config/RISCV_USER_CFI) \
    $(wildcard include/config/ARCH_HAS_PKEYS) \
    $(wildcard include/config/ARCH_PKEY_BITS) \
    $(wildcard include/config/PARISC) \
    $(wildcard include/config/SPARC64) \
    $(wildcard include/config/HAVE_ARCH_USERFAULTFD_MINOR) \
    $(wildcard include/config/MSEAL_SYSTEM_MAPPINGS) \
    $(wildcard include/config/FIND_NORMAL_PAGE) \
    $(wildcard include/config/SHMEM) \
    $(wildcard include/config/ARCH_HAS_PTE_SPECIAL) \
    $(wildcard include/config/ARCH_SUPPORTS_PUD_PFNMAP) \
    $(wildcard include/config/ASYNC_KERNEL_PGTABLE_FREE) \
    $(wildcard include/config/SPLIT_PTE_PTLOCKS) \
    $(wildcard include/config/DEBUG_VM_RB) \
    $(wildcard include/config/PAGE_POISONING) \
    $(wildcard include/config/INIT_ON_ALLOC_DEFAULT_ON) \
    $(wildcard include/config/INIT_ON_FREE_DEFAULT_ON) \
    $(wildcard include/config/DEBUG_PAGEALLOC) \
    $(wildcard include/config/ARCH_WANT_OPTIMIZE_DAX_VMEMMAP) \
    $(wildcard include/config/HUGETLBFS) \
    $(wildcard include/config/MAPPING_DIRTY_HELPERS) \
    $(wildcard include/config/PAGE_POOL) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pgalloc_tag.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/range.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/page_ext.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/stacktrace.h \
    $(wildcard include/config/ARCH_STACKWALK) \
    $(wildcard include/config/STACKTRACE) \
    $(wildcard include/config/HAVE_RELIABLE_STACKTRACE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/page_ref.h \
    $(wildcard include/config/DEBUG_PAGE_REF) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/memremap.h \
    $(wildcard include/config/DEVICE_PRIVATE) \
    $(wildcard include/config/PCI_P2PDMA) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/cacheinfo.h \
    $(wildcard include/config/ACPI_PPTT) \
    $(wildcard include/config/ARCH_HAS_CPU_CACHE_ALIASING) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/cpuhplock.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/iommu-debug-pagealloc.h \
    $(wildcard include/config/IOMMU_DEBUG_PAGEALLOC) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/huge_mm.h \
    $(wildcard include/config/PGTABLE_HAS_HUGE_LEAVES) \
    $(wildcard include/config/PERSISTENT_HUGE_ZERO_FOLIO) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/vmstat.h \
    $(wildcard include/config/VM_EVENT_COUNTERS) \
    $(wildcard include/config/DEBUG_TLBFLUSH) \
    $(wildcard include/config/PER_VMA_LOCK_STATS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/vm_event_item.h \
    $(wildcard include/config/BALLOON) \
    $(wildcard include/config/BALLOON_MIGRATION) \
    $(wildcard include/config/X86) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dma-mapping.h \
    $(wildcard include/config/DMA_API_DEBUG) \
    $(wildcard include/config/HAS_DMA) \
    $(wildcard include/config/NEED_DMA_MAP_STATE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dma-direction.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dma-fence.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pci-p2pdma.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pci.h \
    $(wildcard include/config/PCI_IOV) \
    $(wildcard include/config/PCIEAER) \
    $(wildcard include/config/PCIEPORTBUS) \
    $(wildcard include/config/PCIEASPM) \
    $(wildcard include/config/HOTPLUG_PCI_PCIE) \
    $(wildcard include/config/PCIE_PTM) \
    $(wildcard include/config/PCI_MSI) \
    $(wildcard include/config/PCIE_DPC) \
    $(wildcard include/config/PCI_ATS) \
    $(wildcard include/config/PCI_PRI) \
    $(wildcard include/config/PCI_PASID) \
    $(wildcard include/config/PCI_DOE) \
    $(wildcard include/config/PCI_NPEM) \
    $(wildcard include/config/PCI_IDE) \
    $(wildcard include/config/PCI_TSM) \
    $(wildcard include/config/PCIE_TPH) \
    $(wildcard include/config/PCI_DOMAINS_GENERIC) \
    $(wildcard include/config/CARDBUS) \
    $(wildcard include/config/HOTPLUG_PCI) \
    $(wildcard include/config/DEBUG_FS) \
    $(wildcard include/config/PCI_DOMAINS) \
    $(wildcard include/config/PCI_QUIRKS) \
    $(wildcard include/config/PCI_MMCONFIG) \
    $(wildcard include/config/ACPI_MCFG) \
    $(wildcard include/config/EEH) \
    $(wildcard include/config/S390) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/mod_devicetable.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/mei.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/mei_uuid.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/interrupt.h \
    $(wildcard include/config/IRQ_FORCED_THREADING) \
    $(wildcard include/config/GENERIC_IRQ_PROBE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irqreturn.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/hardirq.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/context_tracking_state.h \
    $(wildcard include/config/CONTEXT_TRACKING_USER) \
    $(wildcard include/config/CONTEXT_TRACKING) \
    $(wildcard include/config/RCU_DYNTICKS_TORTURE) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/ftrace_irq.h \
    $(wildcard include/config/HWLAT_TRACER) \
    $(wildcard include/config/OSNOISE_TRACER) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/vtime.h \
    $(wildcard include/config/VIRT_CPU_ACCOUNTING) \
    $(wildcard include/config/IRQ_TIME_ACCOUNTING) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/hardirq.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/irq.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/irq.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/kvm_arm.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/hardirq.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irq.h \
    $(wildcard include/config/GENERIC_IRQ_EFFECTIVE_AFF_MASK) \
    $(wildcard include/config/GENERIC_IRQ_IPI) \
    $(wildcard include/config/IRQ_DOMAIN_HIERARCHY) \
    $(wildcard include/config/DEPRECATED_IRQ_CPU_ONOFFLINE) \
    $(wildcard include/config/GENERIC_IRQ_MIGRATION) \
    $(wildcard include/config/GENERIC_PENDING_IRQ) \
    $(wildcard include/config/HARDIRQS_SW_RESEND) \
    $(wildcard include/config/GENERIC_IRQ_CHIP) \
    $(wildcard include/config/GENERIC_IRQ_MULTI_HANDLER) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irqhandler.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/irq_regs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/irq_regs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irqdesc.h \
    $(wildcard include/config/GENERIC_IRQ_STAT_SNAPSHOT) \
    $(wildcard include/config/GENERIC_IRQ_DEBUGFS) \
    $(wildcard include/config/SPARSE_IRQ) \
    $(wildcard include/config/IRQ_DOMAIN) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/irq_work.h \
    $(wildcard include/config/IRQ_WORK) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/irq_work.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/asm/hw_irq.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/hw_irq.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/resource_ext.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/msi_api.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/pci.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/pci_regs.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/pci_ids.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dmapool.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/arch/arm64/include/asm/pci.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/asm-generic/pci.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/dma-resv.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/ww_mutex.h \
    $(wildcard include/config/DEBUG_RT_MUTEXES) \
    $(wildcard include/config/DEBUG_WW_MUTEX_SLOWPATH) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rtmutex.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/miscdevice.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/major.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/of_address.h \
    $(wildcard include/config/OF_ADDRESS) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/of.h \
    $(wildcard include/config/OF_DYNAMIC) \
    $(wildcard include/config/SPARC) \
    $(wildcard include/config/OF_PROMTREE) \
    $(wildcard include/config/OF_KOBJ) \
    $(wildcard include/config/OF_NUMA) \
    $(wildcard include/config/OF_OVERLAY) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/property.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/platform_device.h \
    $(wildcard include/config/SUSPEND) \
    $(wildcard include/config/HIBERNATE_CALLBACKS) \
    $(wildcard include/config/SUPERH) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/sort.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/of_platform.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rpmsg.h \
    $(wildcard include/config/RPMSG) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/poll.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/poll.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826/arch/arm64/include/generated/uapi/asm/poll.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/asm-generic/poll.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/eventpoll.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/rpmsg/byteorder.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/rpmsg_types.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/uapi/linux/rpmsg.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/firmware/qcom/qcom_scm.h \
    $(wildcard include/config/QCOM_QSEECOM) \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/dt-bindings/firmware/qcom,scm.h \
  fastrpc-e004cv-uapi.h \
  sp11-cpz-dmabuf-query.h \
  /home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/of_reserved_mem.h \
    $(wildcard include/config/OF_RESERVED_MEM) \

fastrpc-e004cv.o: $(deps_fastrpc-e004cv.o)

$(deps_fastrpc-e004cv.o):
