#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from capstone.arm64 import ARM64_OP_MEM, ARM64_OP_REG

EXPECTED_SHA256 = "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
EXPECTED_BYTES = 376560
IMAGE_BASE = 0x140000000
TEXT_RAW = 0x400
TEXT_RVA = 0x1000
TEXT_SIZE = 0x3D48C
RESOURCE_GETTER_VA = 0x14002B568
MEMSET_VA = 0x14002DF80
MEMCPY_VA = 0x14002DCA0

EXPECTED_RESOURCE_GETTER_CALLS = {
    0x006E88, 0x007138, 0x009A70, 0x00BC30,
    0x017784, 0x017790, 0x018494, 0x022408,
    0x0294A0, 0x0294F4,
}


def die(msg):
    raise SystemExit("FAIL: " + msg)


def disassemble(data):
    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    md.skipdata = True
    return list(md.disasm(data[TEXT_RAW:TEXT_RAW + TEXT_SIZE], IMAGE_BASE + TEXT_RVA))


def by_rva(xs):
    return {x.address - IMAGE_BASE: x for x in xs if x.mnemonic != '.byte'}


def need(m, rva, mnemonic=None, contains=None):
    x = m.get(rva)
    if x is None:
        die(f"missing instruction at RVA 0x{rva:x}")
    if mnemonic is not None and x.mnemonic != mnemonic:
        die(f"RVA 0x{rva:x}: expected {mnemonic}, got {x.mnemonic}")
    if contains is not None and contains not in x.op_str:
        die(f"RVA 0x{rva:x}: expected {contains!r} in {x.op_str!r}")
    return x


def mem_accesses_with_disp(xs, disp):
    out = []
    for x in xs:
        if x.mnemonic == '.byte':
            continue
        try:
            for op in x.operands:
                if op.type == ARM64_OP_MEM and op.mem.disp == disp:
                    out.append({
                        'rva': x.address - IMAGE_BASE,
                        'mnemonic': x.mnemonic,
                        'op_str': x.op_str,
                    })
                    break
        except Exception:
            pass
    return out


def reg_store_width(x):
    # Conservative width for STR/STUR/STP store ranges. This is used only to
    # reject a store whose direct displacement range overlaps object +0xa38.
    if not x.operands or x.operands[0].type != ARM64_OP_REG:
        return 32
    name = x.reg_name(x.operands[0].reg)
    if name.startswith('q'):
        width = 16
    elif name.startswith(('x', 'd')):
        width = 8
    elif name.startswith(('w', 's')):
        width = 4
    elif name.startswith('h'):
        width = 2
    elif name.startswith('b'):
        width = 1
    else:
        width = 32
    if x.mnemonic.startswith('stp'):
        width *= 2
    return width


def direct_store_overlaps(xs, lo, hi, target):
    hits = []
    for x in xs:
        if x.mnemonic == '.byte' or not (IMAGE_BASE + lo <= x.address < IMAGE_BASE + hi):
            continue
        if not (x.mnemonic.startswith('str') or x.mnemonic.startswith('stur') or x.mnemonic.startswith('stp')):
            continue
        try:
            memops = [op for op in x.operands if op.type == ARM64_OP_MEM]
        except Exception:
            continue
        if not memops:
            continue
        width = reg_store_width(x)
        for op in memops:
            start = op.mem.disp
            end = start + width
            if start <= target < end:
                hits.append({
                    'rva': x.address - IMAGE_BASE,
                    'start': start,
                    'width': width,
                    'instruction': f"{x.mnemonic} {x.op_str}",
                })
    return hits


def resource_getter_calls(xs):
    out = []
    needle = f"#0x{RESOURCE_GETTER_VA:x}"
    for x in xs:
        if x.mnemonic == 'bl' and x.op_str == needle:
            out.append(x.address - IMAGE_BASE)
    return out


def mapped_base_direct_stores(xs):
    # Bounded CDM-driver negative proof. Track an RT-CDM base loaded from an
    # object field +0x48 into a register and record direct stores through that
    # exact register until it is overwritten. Stack +0x48 loads are excluded.
    out = []
    lo = IMAGE_BASE + 0x284C0
    hi = IMAGE_BASE + 0x29310
    for i, x in enumerate(xs):
        if not (lo <= x.address < hi) or x.mnemonic != 'ldr' or len(x.operands) != 2:
            continue
        d, mem = x.operands
        if d.type != ARM64_OP_REG or mem.type != ARM64_OP_MEM or mem.mem.disp != 0x48:
            continue
        base_name = x.reg_name(mem.mem.base)
        if base_name == 'sp':
            continue
        dest_name = x.reg_name(d.reg)
        if not dest_name.startswith('x'):
            continue
        br = d.reg
        for y in xs[i + 1:min(i + 80, len(xs))]:
            if y.mnemonic == '.byte':
                break
            try:
                if (y.mnemonic in ('str', 'stur') and len(y.operands) == 2 and
                        y.operands[1].type == ARM64_OP_MEM):
                    mm = y.operands[1].mem
                    if mm.base == br and mm.index == 0 and 0 <= mm.disp <= 0x400:
                        out.append({
                            'base_load_rva': x.address - IMAGE_BASE,
                            'store_rva': y.address - IMAGE_BASE,
                            'offset': mm.disp,
                            'instruction': f"{y.mnemonic} {y.op_str}",
                        })
                if (y.operands and y.operands[0].type == ARM64_OP_REG and
                        y.operands[0].reg == br and
                        y.mnemonic not in ('str', 'stur', 'cmp', 'tst', 'cbz', 'cbnz',
                                           'tbz', 'tbnz', 'bl', 'blr', 'b')):
                    break
            except Exception:
                pass
    uniq = []
    seen = set()
    for row in out:
        key = (row['store_rva'], row['offset'], row['instruction'])
        if key not in seen:
            seen.add(key)
            uniq.append(row)
    return sorted(uniq, key=lambda r: r['store_rva'])


def call_sites(xs, target_va, lo, hi):
    needle = f"#0x{target_va:x}"
    return [x.address - IMAGE_BASE for x in xs
            if IMAGE_BASE + lo <= x.address < IMAGE_BASE + hi
            and x.mnemonic == 'bl' and x.op_str == needle]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('binary', type=Path)
    ap.add_argument('-o', '--output', type=Path)
    args = ap.parse_args()

    data = args.binary.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_SHA256:
        die(f"SHA256 {sha} != {EXPECTED_SHA256}")
    if len(data) != EXPECTED_BYTES:
        die(f"byte count {len(data)} != {EXPECTED_BYTES}")

    xs = disassemble(data)
    m = by_rva(xs)

    # Exact object allocation + zeroing. The CDM object is 0xa40 bytes and the
    # whole object is zeroed before object-local initialization proceeds.
    object_checks = [
        (0x18328, 'mov', 'w1, #0xa40'),
        (0x18338, 'bl', '#0x14002a260'),
        (0x18384, 'ldr', 'x19, [x8, #0x20]'),
        (0x18390, 'mov', 'x2, #0xa40'),
        (0x18394, 'mov', 'w1, #0'),
        (0x18398, 'mov', 'x0, x19'),
        (0x1839C, 'bl', '#0x14002df80'),
        (0x183CC, 'str', '[x19, #0xa3c]'),
    ]
    for rva, mn, sub in object_checks:
        need(m, rva, mn, sub)

    # Exact RT-CDM resource mapping is acquired once in the CDM object init and
    # stored into object +0x48. The static parser's resource target is +0x838,
    # mechanically distinct from RT-CDM +0x48.
    mapping_checks = [
        (0x18438, 'add', 'w0, w22, #0x11'),
        (0x1846C, 'mov', 'w0, #0x13'),
        (0x18490, 'mov', 'w0, #0x14'),
        (0x18494, 'bl', '#0x14002b568'),
        (0x1849C, 'str', 'x0, [x19, #0x48]'),
        (0x294A0, 'bl', '#0x14002b568'),
        (0x294F4, 'bl', '#0x14002b568'),
        (0x294FC, 'str', 'x0, [x23, #0x838]'),
    ]
    for rva, mn, sub in mapping_checks:
        need(m, rva, mn, sub)

    calls = resource_getter_calls(xs)
    if set(calls) != EXPECTED_RESOURCE_GETTER_CALLS:
        die('resource getter call census drift: ' + ','.join(hex(x) for x in calls))
    cdm_init_getter_calls = [r for r in calls if 0x18248 <= r < 0x189A0]
    if cdm_init_getter_calls != [0x18494]:
        die('expected exactly one CDM-init resource getter at 0x18494')

    # CGC guard. The only fixed-offset +0xa38 access in the exact text must be
    # the read guarding CGC_CFG=7. Since the full 0xa40 object is already zeroed
    # and no direct store range in the CDM object code overlaps +0xa38, the
    # branch is statically not taken by the normal in-binary object lifecycle.
    cgc_checks = [
        (0x28F5C, 'ldrb', '[x20, #0xa38]'),
        (0x28F60, 'cbz', 'w8, #0x140028f70'),
        (0x28F64, 'ldr', '[x20, #0x48]'),
        (0x28F68, 'mov', 'w8, #7'),
        (0x28F6C, 'str', '[x9, #0x14]'),
    ]
    for rva, mn, sub in cgc_checks:
        need(m, rva, mn, sub)

    a38 = mem_accesses_with_disp(xs, 0xA38)
    if len(a38) != 1 or a38[0]['rva'] != 0x28F5C or a38[0]['mnemonic'] != 'ldrb':
        die('object +0xa38 access census is not exactly the expected single read')
    overlap = direct_store_overlaps(xs, 0x18248, 0x29310, 0xA38)
    if overlap:
        die('direct store overlaps object +0xa38: ' + repr(overlap))

    # Known bulk memory operations in the object-init function: one full-object
    # memset at 0x1839c, then unrelated subobject allocations/zeroes. Runtime
    # CDM commit uses bulk ops only on the +0x890 bookkeeping array.
    init_memsets = call_sites(xs, MEMSET_VA, 0x18248, 0x189A0)
    if init_memsets != [0x1839C, 0x18628, 0x18888]:
        die('CDM init memset census drift: ' + ','.join(hex(x) for x in init_memsets))
    runtime_memsets = call_sites(xs, MEMSET_VA, 0x284C0, 0x29310)
    if runtime_memsets != [0x28784, 0x28A80]:
        die('CDM runtime memset census drift: ' + ','.join(hex(x) for x in runtime_memsets))
    runtime_memcpys = call_sites(xs, MEMCPY_VA, 0x284C0, 0x29310)
    if runtime_memcpys != [0x28774, 0x2897C]:
        die('CDM runtime memcpy census drift: ' + ','.join(hex(x) for x in runtime_memcpys))
    for rva, mn, sub in [
        (0x28770, 'add', 'x1, x19, #0x890'),
        (0x28780, 'add', 'x0, x19, #0x890'),
        (0x28A5C, 'add', 'x1, x19, #0x890'),
        (0x28A7C, 'add', 'x0, x19, #0x890'),
    ]:
        need(m, rva, mn, sub)

    stores = mapped_base_direct_stores(xs)
    offsets = sorted(set(row['offset'] for row in stores))
    required = {0x10, 0x14, 0x1C, 0x30, 0x34, 0x38, 0x50, 0x54, 0x58,
                0x134, 0x138, 0x234, 0x238, 0x334, 0x338}
    # CORE_CFG +0x18 is in the open/init function before the runtime region.
    if not required.issubset(set(offsets)):
        die('runtime RT-CDM direct-store sweep lost expected offsets')
    if 0x20 in offsets:
        die('FE_CFG +0x20 direct store unexpectedly present')
    if 0x5C in offsets:
        die('FIFO0_CFG +0x5c direct store unexpectedly present')

    # Open/init direct write to CORE_CFG is separately pinned, and neither
    # FE_CFG nor FIFO0_CFG is written around it.
    need(m, 0x1880C, 'ldr', '[x26, #0x48]')
    need(m, 0x18814, 'str', '[x9, #0x18]')

    out = {
        'schema': 'sp11-e003h-windows-rtcdm1-config-ownership-v1',
        'accepted': True,
        'source': {
            'binary': 'qccamisp8380.sys',
            'bytes': len(data),
            'sha256': sha,
            'image_base': '0x140000000',
        },
        'cdm_object': {
            'bytes': 0xA40,
            'full_zero_before_init': True,
            'full_zero_rva': '0x1839c',
            'rtcdm_mmio_field_offset': '0x48',
            'rtcdm_resource_getter_rva': '0x18494',
            'rtcdm_mmio_store_rva': '0x1849c',
            'cdm_init_resource_getter_calls': ['0x18494'],
        },
        'resource_getter_census': {
            'function_va': '0x14002b568',
            'all_call_rvas': [f'0x{x:x}' for x in calls],
            'rtcdm_object_init_call_rva': '0x18494',
            'command_parser_calls': ['0x294a0', '0x294f4'],
            'command_parser_target_field': 'object +0x838, not RT-CDM object +0x48',
            'interpretation': 'no second in-binary RT-CDM object mapping path was found',
        },
        'cgc_cfg': {
            'register_offset': '0x14',
            'conditional_value': '0x00000007',
            'guard_object_offset': '0xa38',
            'guard_initial_value': 0,
            'guard_fixed_offset_accesses': a38,
            'direct_store_overlap_guard': False,
            'bulk_memory_census_preserves_guard_after_initial_zero': True,
            'normal_in_binary_lifecycle_branch_taken': False,
            'status': 'static not-taken: full object is zero-initialized and exact binary exposes no writer/overlapping bulk copy to guard byte +0xa38',
        },
        'fe_fifo_config_ownership': {
            'windows_live_fe_cfg_offset': '0x20',
            'windows_live_fe_cfg_value': '0x07ff000f',
            'windows_live_fifo0_cfg_offset': '0x5c',
            'windows_live_fifo0_cfg_value': '0x01000000',
            'direct_rtcdm_store_offsets_runtime': [f'0x{x:x}' for x in offsets],
            'fe_cfg_cpu_store_found': False,
            'fifo0_cfg_cpu_store_found': False,
            'alternate_in_binary_rtcdm_mapping_found': False,
            'command_parser_is_distinct_target_aperture': True,
            'classification': 'no in-binary CPU software write path found after mapped-base, alias/resource-getter, helper and command-parser separation',
            'positive_reset_default_proven': False,
            'positive_origin_timing_status': 'unresolved; hardware/reset origin remains candidate until same-machine timing evidence or equivalent positive proof',
        },
        'bulk_memory_calls': {
            'init_memset_rvas': [f'0x{x:x}' for x in init_memsets],
            'runtime_memset_rvas': [f'0x{x:x}' for x in runtime_memsets],
            'runtime_memcpy_rvas': [f'0x{x:x}' for x in runtime_memcpys],
            'runtime_bulk_bookkeeping_offset': '0x890',
        },
        'linux_consequence': 'Remove CGC_CFG +0x14=7 from the active-front unresolved set and do not write it. Keep FE_CFG +0x20 and FIFO0_CFG +0x5c unwritten: exact Windows binary exposes no in-binary CPU write path, but positive reset/hardware origin timing is still unresolved. 0014 remains inert.',
        'remaining_blockers_before_linux_rtcdm_mmio': [
            'positive same-machine origin/timing of FE_CFG +0x20 = 0x07ff000f',
            'positive same-machine origin/timing of FIFO0_CFG +0x5c = 0x01000000',
            'exact hardware/power semantics after CDM stop masks IRQ0 to zero',
        ],
    }

    text = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end='')
    print('PASS: RT-CDM config ownership narrowed; CGC write statically not-taken; FE_CFG/FIFO0_CFG have no in-binary CPU write path')


if __name__ == '__main__':
    main()
