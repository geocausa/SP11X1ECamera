#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from capstone.arm64 import ARM64_OP_IMM, ARM64_OP_MEM, ARM64_OP_REG

EXPECTED_BIN_SHA256 = "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
EXPECTED_BIN_BYTES = 376560
EXPECTED_LOG_SHA256 = "458b05c41718c7d01d0efb2921d1f6e2e4323e94e24447e379499544ca21cc1a"
EXPECTED_LOG_BYTES = 27014
IMAGE_BASE = 0x140000000
TEXT_RAW = 0x400
TEXT_RVA = 0x1000
TEXT_SIZE = 0x3D48C


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


def require_string(data, text):
    if text.encode() not in data:
        die(f"missing diagnostic string {text!r}")


def mmio_field_accesses(xs, lo_rva, hi_rva, disp=0x48):
    out = []
    for x in xs:
        rva = x.address - IMAGE_BASE
        if not (lo_rva <= rva < hi_rva) or x.mnemonic == '.byte':
            continue
        try:
            for op in x.operands:
                if op.type == ARM64_OP_MEM and op.mem.disp == disp:
                    out.append({"rva": rva, "instruction": f"{x.mnemonic} {x.op_str}"})
                    break
        except Exception:
            pass
    return out


def stop_block_mmio_stores(xs):
    # Follow the direct RT-CDM base load in the command-0x805 block only.
    out = []
    lo, hi = 0x28540, 0x285C8
    for i, x in enumerate(xs):
        rva = x.address - IMAGE_BASE
        if not (lo <= rva < hi) or x.mnemonic != 'ldr' or len(x.operands) != 2:
            continue
        d, mem = x.operands
        if d.type != ARM64_OP_REG or mem.type != ARM64_OP_MEM or mem.mem.disp != 0x48:
            continue
        dest = d.reg
        for y in xs[i + 1:min(i + 18, len(xs))]:
            yrva = y.address - IMAGE_BASE
            if yrva >= hi:
                break
            try:
                if y.mnemonic in ('str', 'stur') and len(y.operands) == 2 and y.operands[1].type == ARM64_OP_MEM:
                    mm = y.operands[1].mem
                    if mm.base == dest and mm.index == 0:
                        out.append({
                            "store_rva": yrva,
                            "offset": mm.disp,
                            "instruction": f"{y.mnemonic} {y.op_str}",
                        })
                if (y.operands and y.operands[0].type == ARM64_OP_REG and
                        y.operands[0].reg == dest and y.mnemonic not in
                        ('str', 'stur', 'cmp', 'tst', 'cbz', 'cbnz', 'tbz', 'tbnz', 'b', 'bl', 'blr')):
                    break
            except Exception:
                pass
    return out


def parse_post_section(text, start, end):
    try:
        body = text.split(start, 1)[1].split(end, 1)[0]
    except IndexError:
        die(f"missing post section {start}..{end}")
    values = []
    for line in body.splitlines():
        if '`' not in line:
            continue
        toks = re.findall(r'\b[0-9a-fA-F]{8}\b', line)
        # First token can be part of the address only when the address lacks a
        # backtick; KD output here contains a backtick, so all 8-hex tokens
        # after it are the four DWORD values.
        after = line.split(None, 1)
        if len(after) < 2:
            continue
        vals = re.findall(r'\b[0-9a-fA-F]{8}\b', after[1])
        values.extend(int(v, 16) for v in vals)
    if len(values) != 64:
        die(f"{start}: expected 64 DWORDs, got {len(values)}")
    if any(v != 0x80000000 for v in values):
        die(f"{start}: post sentinel mismatch")
    return values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('binary', type=Path)
    ap.add_argument('hwcdm_log', type=Path)
    ap.add_argument('-o', '--output', type=Path)
    args = ap.parse_args()

    data = args.binary.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_BIN_SHA256 or len(data) != EXPECTED_BIN_BYTES:
        die(f"binary identity mismatch sha={sha} bytes={len(data)}")

    raw = args.hwcdm_log.read_bytes()
    log_sha = hashlib.sha256(raw).hexdigest()
    if log_sha != EXPECTED_LOG_SHA256 or len(raw) != EXPECTED_LOG_BYTES:
        die(f"HW-CDM log identity mismatch sha={log_sha} bytes={len(raw)}")
    text = raw.decode('utf-16le', 'ignore')

    xs = disassemble(data)
    m = by_rva(xs)

    # Stream-level DEVICE_STOP 0x805: direct RT-CDM action is mask-zero only.
    for rva, mn, sub in [
        (0x2853C, 'cmp', 'w1, #0x805'),
        (0x2854C, 'ldr', '[x19, #0x48]'),
        (0x28550, 'str', 'wzr, [x8, #0x30]'),
    ]:
        need(m, rva, mn, sub)
    stores = stop_block_mmio_stores(xs)
    if stores != [{"store_rva": 0x28550, "offset": 0x30, "instruction": "str wzr, [x8, #0x30]"}]:
        die('command 0x805 MMIO store census drift: ' + repr(stores))

    # Camera control 0x80e is the later manager-delete/session-teardown path.
    for rva, mn, sub in [
        (0x050DC, 'cmp', 'w22, #0x80e'),
        (0x050E4, 'ldr', 'x0, [x24, #0x10]'),
        (0x050EC, 'bl', '#0x1400196f8'),
    ]:
        need(m, rva, mn, sub)
    require_string(data, 'DAL_ife_mgr_delete is failed with result 0x%x')

    # CDM public wrapper vtable: method +8 is exact close function 0x28a90.
    for rva, mn, sub in [
        (0x1834C, 'add', 'x10, x8, #0x480'),
        (0x18354, 'add', 'x9, x8, #0xa90'),
        (0x1835C, 'stp', 'x10, x9, [x8]'),
        (0x18364, 'add', 'x9, x9, #0xd10'),
        (0x18368, 'str', 'x9, [x8, #0x10]'),
    ]:
        need(m, rva, mn, sub)

    # Manager delete releases the CDM object before explicit CSID/IFE power-off.
    for rva, mn, sub in [
        (0x19970, 'ldr', 'x0, [x8, x24]'),
        (0x19978, 'ldr', 'x8, [x0, #8]'),
        (0x1998C, 'blr', 'x15'),
        (0x199A8, 'str', 'xzr, [x24, x8]'),
        (0x19AB0, 'mov', 'w1, #3'),
        (0x19AC4, 'blr', 'x15'),
        (0x19B00, 'mov', 'w1, #0xc'),
        (0x19B20, 'blr', 'x15'),
        (0x19B4C, 'blr', 'x15'),
        (0x19C4C, 'mov', 'w1, #3'),
        (0x19C60, 'blr', 'x15'),
        (0x19C98, 'mov', 'x15, x8'),
        (0x19CA8, 'blr', 'x15'),
    ]:
        need(m, rva, mn, sub)
    for s in [
        'CDM driver closed for core%d',
        'CSID Core%x IFE_CMD_ID_POWER_OFF is failed with result =0x%x',
        'IFE Core%x IFE_CMD_ID_POWER_OFF is failed with result =0x%x',
    ]:
        require_string(data, s)

    # The CDM close + cleanup path does not touch the RT-CDM MMIO field +0x48.
    close_mmio = mmio_field_accesses(xs, 0x28A90, 0x28D10, 0x48)
    if close_mmio:
        die('CDM close/cleanup unexpectedly accesses RT-CDM MMIO field +0x48: ' + repr(close_mmio))
    for rva, mn, sub in [
        (0x28AD0, 'ldr', 'x19, [x21, #0x20]'),
        (0x28AD4, 'ldr', 'w8, [x19, #0x7e4]'),
        (0x28ADC, 'str', 'w3, [x19, #0x7e4]'),
        (0x28AEC, 'ldr', 'x0, [x19, #0x50]'),
        (0x28B20, 'bl', '#0x140028b80'),
    ]:
        need(m, rva, mn, sub)

    # CSID/IFE explicit POWER_OFF paths converge on the same refcounted
    # platform power-off helper 0x12fd0.
    for rva, mn, sub in [
        (0x21350, 'ldr', 'w0, [x8, #0xf44]'),
        (0x21354, 'mov', 'w1, #2'),
        (0x21358, 'bl', '#0x140012fd0'),
        (0x22DF0, 'ldr', 'w0, [x19, #0x120]'),
        (0x22DF4, 'bl', '#0x14002b108'),
        (0x2B190, 'mov', 'w1, #2'),
        (0x2B198, 'bl', '#0x140012fd0'),
    ]:
        need(m, rva, mn, sub)
    require_string(data, 'CSID%d: CSID powered off and clocks disabled successfully')
    require_string(data, 'IFE%d: IFE powered off and clocks disabled successfully')

    # Refcounted platform power-off: atomic decrement; invoke callback only at 0.
    for rva, mn, sub in [
        (0x13054, 'ldaxr', 'w9, [x10]'),
        (0x13058, 'add', 'w9, w9, w8'),
        (0x1305C, 'stlxr', 'w17, w9, [x10]'),
        (0x13064, 'dmb', 'ish'),
        (0x13068, 'cbnz', 'w9, #0x140013084'),
        (0x1306C, 'ldr', 'x0, [x20, #8]'),
        (0x13074, 'ldr', 'x8, [x8, #0x1f8]'),
        (0x13080, 'blr', 'x8'),
    ]:
        need(m, rva, mn, sub)

    rt0 = parse_post_section(text, '===E003H_RTCDM0_POST===', '===E003H_RTCDM1_POST===')
    rt1 = parse_post_section(text, '===E003H_RTCDM1_POST===', '===E003H_RTCDM_POST_DONE===')

    out = {
        'schema': 'sp11-e003h-windows-rtcdm1-stop-power-v1',
        'accepted': True,
        'source': {
            'binary': 'qccamisp8380.sys',
            'binary_bytes': len(data),
            'binary_sha256': sha,
            'hwcdm_log': 'E003H_HWCDM_ORACLE_20260828.log',
            'hwcdm_log_bytes': len(raw),
            'hwcdm_log_sha256': log_sha,
        },
        'stream_stop_0x805': {
            'isp_manager_order': 'CSID stop -> IFE stop -> CDM stop',
            'rtcdm_direct_mmio_writes': [
                {'offset': '0x30', 'register': 'IRQ0_MASK', 'value': '0x00000000', 'rva': '0x28550'}
            ],
            'core_en_zero_write_proven': False,
            'reset_write_proven': False,
            'classification': 'stream-level stop; do not invent CORE_EN=0 or reset',
        },
        'session_delete_0x80e': {
            'manager_delete_rva': '0x196f8',
            'dispatch_call_rva': '0x50ec',
            'order': [
                'release per-block CDM associations',
                'CDM software-object close',
                'clear manager CDM slot',
                'CSID POWER_OFF',
                'CSID object close',
                'IFE POWER_OFF',
                'IFE object close',
            ],
            'cdm_close_method_rva': '0x28a90',
            'cdm_close_rtcdm_mmio_field_accesses': [],
            'cdm_close_mmio_shutdown_write': False,
        },
        'platform_power_off': {
            'helper_rva': '0x12fd0',
            'reference_counted': True,
            'callback_only_when_refcount_reaches_zero': True,
            'callback_rva': '0x13080',
            'csid_calls_helper': True,
            'ife_calls_helper': True,
        },
        'post_stop_dispose_oracle': {
            'rtcdm0_first_0x100_dwords': len(rt0),
            'rtcdm1_first_0x100_dwords': len(rt1),
            'rtcdm0_all': '0x80000000',
            'rtcdm1_all': '0x80000000',
            'timing_scope': 'post normal StopAsync/dispose/session teardown; not sampled exactly at the 0x805 boundary',
        },
        'conclusion': 'Windows separates stream stop from power collapse. DEVICE_STOP 0x805 stops CSID then IFE then CDM and the CDM command only masks IRQ0 to zero. Later control 0x80e deletes the manager/session: CDM software object is closed without RT-CDM MMIO shutdown, then CSID/IFE explicit POWER_OFF paths use a shared reference-counted platform power-off helper. The post StopAsync/dispose 0x80000000 RT-CDM sentinel is therefore consistent with this later platform power-collapse phase, not evidence for an invented CORE_EN=0/reset write.',
        'linux_consequence': 'Model stream-stop and final runtime/power teardown as separate layers. Do not add unobserved RT-CDM CORE_EN=0 or reset writes. Preserve Windows stop order and IRQ-mask-zero behavior; only collapse the platform/power domain through a proven equivalent ownership path after resource teardown/refcounts permit it.',
        'remaining_blockers_before_linux_rtcdm_mmio': [
            'positive same-machine origin/timing of FE_CFG +0x20 = 0x07ff000f',
            'positive same-machine origin/timing of FIFO0_CFG +0x5c = 0x01000000',
            'exact component/power transition that first changes RT-CDM1 to the 0x80000000 sentinel, if required for Linux runtime-PM ordering',
        ],
    }

    text_out = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text_out)
    else:
        print(text_out, end='')
    print('PASS: Windows RT-CDM stream stop separated from later manager-delete/platform power collapse')


if __name__ == '__main__':
    main()
