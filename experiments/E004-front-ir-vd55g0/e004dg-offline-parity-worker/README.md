# E004dg — source-controlled parity worker, offline compile/test

## Result

**PASS / PARTIAL: the first source-controlled Hexagon parity worker now exists and reproduces the Windows synthetic/fill and early-request copy branches exactly at the byte-operation level. It compiles directly for Hexagon v73 as a freestanding object with no unresolved symbols, and native synthetic-vector tests pass. The later `request_id >= 10` SWABF→SWASF branch intentionally fails closed with a dedicated status until its exact algorithm is ported.**

This is an offline engineering artifact only. It is not signed, admitted, installed or loaded into CPZ.

## 1. Worker ABI

The worker request carries only the information already proven by the Windows/Linux contracts:

- source pointer + extent;
- destination base + extent;
- width / height;
- request ID;
- payload offset;
- captured extent;
- serialized extent;
- synthetic-fill selector.

The worker never allocates memory, performs syscalls, opens FastRPC, changes ownership, or assumes HLOS access. It is pure bounded memory processing over mappings supplied by a future trusted runtime.

## 2. Strict extent validation

Before touching pixels it validates:

- non-null source/destination;
- non-zero width and height;
- overflow-safe `width * height`;
- `frame_size = Y + Y/2`;
- payload offset + frame size within serialized/captured/destination extents;
- source extent large enough for the luma input.

This keeps E004db's mapping/lifetime boundary separate from the worker algorithm.

## 3. Synthetic branch is byte-exact to the oracle

For the Windows synthetic branch:

- first `width * height` bytes become decimal `100`;
- following `width * height / 2` bytes become `0x80`;
- source contents are ignored.

The host vector test confirms the prefix before `payload_offset` is untouched and the two payload regions have the exact expected values.

## 4. Early-request copy branch is byte-exact to the oracle

For `request_id < 10`:

- exactly `width * height` source bytes are moved to the destination payload;
- the following half-size region is filled with `0x80`.

A local overlap-safe move implementation is used so the Hexagon object has no libc dependency.

## 5. Later SWAB branch is deliberately not faked

For `request_id >= 10`, Windows executes:

`SWABF(source -> scratch) -> SWASF(scratch -> destination) -> 0x80 tail`

E004dg currently returns:

`SP11_WORKER_ESWAB_PENDING`

without modifying the output.

This is intentional. Replacing that branch with ordinary copy would produce visually plausible data while silently losing Windows parity. The architecture closure in E004df explicitly forbids such a fallback.

## 6. Hexagon build proof

The same C source compiles with the installed LLVM toolchain using:

`clang --target=hexagon -mcpu=hexagonv73 -ffreestanding -fno-builtin`

Result:

- ELF32 Qualcomm DSP6 relocatable;
- `.text = 908` bytes;
- zero unresolved symbols;
- exported `sp11_parity_worker_run`;
- no runtime/OS dependency.

This proves the implementation is suitable for the exact CDSP ISA family independent of the unresolved production signing/admission issue.

## 7. Host synthetic vectors

Native tests cover:

- synthetic branch contents;
- early request copy branch contents;
- payload-offset preservation;
- 0x80 tail fill;
- later request fail-closed behavior with no output mutation;
- insufficient source extent;
- insufficient serialized extent;
- invalid payload offset;
- zero dimension rejection.

All tests pass.

## Safety boundary

No protected buffer, dma-heap runtime allocation, FastRPC ioctl, CPZ process, secure CB9, ownership transition, camera runtime or Linux SecureISP runtime was touched. The Hexagon object exists only as an offline build product.

## Next gate

**E004dh — exact SWABF/SWASF algorithm extraction and offline port.**

Recover the later-request two-pass transform far enough to replace `SP11_WORKER_ESWAB_PENDING` without approximation:

1. recover pass descriptors/configuration and constant tables;
2. reconstruct edge handling and the four worker partitions;
3. port a scalar reference implementation first;
4. validate with deterministic synthetic vectors against the recovered Windows equations/constants;
5. only then optimize for Hexagon/HVX if useful.

Do not use a generic bilateral/gaussian substitute and do not enable protected runtime.
