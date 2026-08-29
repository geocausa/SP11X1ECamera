#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

import capstone
import pefile

DRIVER_SHA = '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
ORDER_LOG_SHA = '3a2dd357e994f8f5d52668f7c914ad27a2dda6fdee8804e55daa3fcde1c5bed6'
WRITER_LOG_SHA = '64e5a4e4f682829497f0868f00d2d0ff76b235f22d22c375184aaf37f2a788bc'
DYNAMIC_REQUEST_SHA = 'ac68f99ad39bca7042c3f954eb3602040ba861cd0b0d276966d9f591f5305f5c'
LIVE_CORRELATE_SHA = '102761bf27d562dc863843f79fc6e5f87b4be27140becfc5cc250f613c2b04ae'

CONFIG_ORDER = [('3000', 0), ('3000', 1), ('3001', 0), ('3002', 0),
                ('301c', 0), ('3010', 0), ('300f', 0), ('300e', 0), ('300c', 0)]
RESOURCE_ORDER = ['3000', '3001', '3002', '301c', '3010', '300f', '300e', '300c']
ADDRESS_ORDER = [('3000', 0), ('3000', 1), ('3001', 0), ('3002', 0),
                 ('301c', 0), ('3010', 0), ('300f', 0), ('300e', 0), ('300c', 0)]
FRAME_INCR = {
    ('3001', 0): 0x84000,
    ('3002', 0): 0xc000,
    ('301c', 0): 0xa0000,
    ('3010', 0): 0x10000,
    ('300f', 0): 0x1800,
    ('300e', 0): 0x151800,
    ('300c', 0): 0x48000,
}


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_hash(path, expected, label):
    got = sha(path)
    if got != expected:
        die(f'{label} sha256 {got} != {expected}')
    return got


def read_utf16(path):
    return path.read_text(encoding='utf-16').splitlines()


def parse_order_log(path):
    lines = read_utf16(path)
    events = []
    pending_config = False
    for line in lines:
        if line.startswith('BUS_CONFIG rid=Unable to load image'):
            pending_config = True
            continue
        if pending_config:
            m = re.fullmatch(r'([0-9a-f]{4}) idx=([0-9a-f]+)', line)
            if not m:
                die('split first BUS_CONFIG did not resume on next line')
            events.append(('config', m.group(1), int(m.group(2), 16)))
            pending_config = False
            continue
        m = re.fullmatch(r'BUS_CONFIG rid=([0-9a-f]{4}) idx=([0-9a-f]+)', line)
        if m:
            events.append(('config', m.group(1), int(m.group(2), 16)))
            continue
        m = re.fullmatch(r'BUS_SET_ENABLE rid=([0-9a-f]{4}) enable=([01])', line)
        if m:
            events.append(('enable', m.group(1), int(m.group(2))))
            continue
        m = re.fullmatch(r'ADDR rid=([0-9a-f]{4}) sel=([0-9a-f]+) image=([0-9a-f]{8}) meta=([0-9a-f]{8}) hasmeta=([01])', line)
        if m:
            events.append(('addr', m.group(1), int(m.group(2), 16),
                           int(m.group(3), 16), int(m.group(4), 16), int(m.group(5))))
            continue
        if line == 'ISP_START_DONE':
            events.append(('isp_start_done',))

    configs = [(e[1], e[2]) for e in events if e[0] == 'config']
    if configs != CONFIG_ORDER:
        die('BUS config order drift: ' + repr(configs))
    enables = [e[1] for e in events if e[0] == 'enable' and e[2] == 1]
    disables = [e[1] for e in events if e[0] == 'enable' and e[2] == 0]
    if enables != RESOURCE_ORDER or disables != RESOURCE_ORDER:
        die(f'BUS enable/disable order drift: {enables!r} / {disables!r}')

    idx_done = next(i for i, e in enumerate(events) if e[0] == 'isp_start_done')
    before_done = [e for e in events[:idx_done] if e[0] == 'addr']
    after_done = [e for e in events[idx_done + 1:] if e[0] == 'addr']
    if [(e[1], e[2]) for e in before_done] != ADDRESS_ORDER:
        die('initial address set is not exactly one complete Windows set before ISP_START_DONE')
    if len(after_done) < 9 or [(e[1], e[2]) for e in after_done[:9]] != ADDRESS_ORDER:
        die('first post-start address set order drift')

    last_enable = max(i for i, e in enumerate(events) if e[0] == 'enable' and e[2] == 1)
    first_addr = next(i for i, e in enumerate(events) if e[0] == 'addr')
    first_config = next(i for i, e in enumerate(events) if e[0] == 'config')
    if not first_config < last_enable < first_addr < idx_done:
        die('lifecycle order is not config -> enable -> initial addresses -> ISP_START_DONE')

    first = before_done
    second = after_done[:9]
    # FULL is one contiguous QC10C allocation: Y meta is allocation base.
    y0, c0 = first[0], first[1]
    if y0[5] != 1 or c0[5] != 1:
        die('FULL metadata flags missing')
    # tuple = kind,rid,sel,image,meta,hasmeta; Y meta is allocation base.
    base = y0[4]
    if y0[3] - base != 0x6000:
        die('FULL Y data offset drift')
    if c0[4] - base != 0x4f2000 or c0[3] - base != 0x4f5000:
        die('FULL C meta/data offset drift')

    slot_stride = second[0][4] - first[0][4]
    if slot_stride != 0x76c000:
        die(f'QC10C slot stride drift: 0x{slot_stride:x}')

    aux_slot = {}
    for a, b in zip(first[2:], second[2:]):
        key = (a[1], a[2])
        stride = b[3] - a[3]
        expected = (FRAME_INCR[key] + 0x3fff) & ~0x3fff
        if stride != expected:
            die(f'aux slot stride {key} 0x{stride:x} != ALIGN(frame_incr,0x4000)=0x{expected:x}')
        if a[5] or b[5]:
            die('aux address unexpectedly marked metadata-bearing')
        aux_slot[f'0x{key[0]}'] = {'frame_incr': FRAME_INCR[key], 'observed_slot_stride': stride}

    return events, first, second, slot_stride, aux_slot


def verify_driver(driver):
    check_hash(driver, DRIVER_SHA, 'driver')
    pe = pefile.PE(str(driver))
    base = pe.OPTIONAL_HEADER.ImageBase
    text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
    blob = text.get_data()
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_LITTLE_ENDIAN)

    def one(rva):
        off = rva - text.VirtualAddress
        ins = list(md.disasm(blob[off:off+4], base+rva, 1))
        if len(ins) != 1:
            die(f'cannot disassemble RVA 0x{rva:x}')
        return ins[0].mnemonic + ' ' + ins[0].op_str

    required = {
        0x1dea4: 'ldr w8, [x19, #0x3408]',
        0x1deac: 'str w21, [x25, w8, uxtw]',
        0x1dee8: 'ldr w8, [x19, #0x3450]',
        0x1def4: 'str w23, [x25, w8, uxtw]',
        0x1d92c: 'mov x1, #0x200',
        0x1d94c: 'mov x1, #0x300',
    }
    got = {rva: one(rva) for rva in required}
    for rva, expect in required.items():
        if got[rva] != expect:
            die(f'driver instruction RVA 0x{rva:x}: {got[rva]!r} != {expect!r}')
    return {f'0x{rva:x}': text for rva, text in got.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--driver', type=Path, required=True)
    ap.add_argument('--order-log', type=Path, required=True)
    ap.add_argument('--writer-log', type=Path, required=True)
    ap.add_argument('--dynamic-request-log', type=Path, required=True)
    ap.add_argument('--live-correlate-log', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()

    hashes = {
        'driver': check_hash(a.driver, DRIVER_SHA, 'driver'),
        'order_log': check_hash(a.order_log, ORDER_LOG_SHA, 'order log'),
        'writer_log': check_hash(a.writer_log, WRITER_LOG_SHA, 'writer log'),
        'dynamic_request_log': check_hash(a.dynamic_request_log, DYNAMIC_REQUEST_SHA, 'dynamic request log'),
        'live_correlate_log': check_hash(a.live_correlate_log, LIVE_CORRELATE_SHA, 'live correlate log'),
    }
    instructions = verify_driver(a.driver)
    events, first, second, qc10c_stride, aux_slot = parse_order_log(a.order_log)

    writer_lines = read_utf16(a.writer_log)
    writer_hits = [line for line in writer_lines if line.startswith('ADDR_WRITE ctx=1 ')]
    if len(writer_hits) < 18:
        die('too few ctx=1 live writer hits')

    result = {
        'schema': 'sp11-e003h-windows-vfe1-dynamic-address-v1',
        'accepted': True,
        'hashes': hashes,
        'driver_rvas': {
            'dynamic_writer_function': '0x1dd20',
            'image_write_site': '0x1dea4',
            'meta_write_site': '0x1dee8',
            'bus_enable_disable': '0x1d830',
            'isp_start_done': '0x16220',
        },
        'instruction_anchors': instructions,
        'register_offsets': {'image_addr': '0x04', 'meta_addr': '0x40'},
        'client_address_order': ['FULL_Y/0x3000:0', 'FULL_C/0x3000:1', 'DS4/0x3001', 'DS16/0x3002',
                                 'AEC_BE/0x301c', 'RS/0x3010', 'BHIST/0x300f', 'AWB_BG/0x300e', 'TL_BG/0x300c'],
        'resource_enable_disable_order': ['FULL/0x3000', 'DS4/0x3001', 'DS16/0x3002', 'AEC_BE/0x301c',
                                          'RS/0x3010', 'BHIST/0x300f', 'AWB_BG/0x300e', 'TL_BG/0x300c'],
        'full_internal_enable_order': ['WM0', 'WM1'],
        'lifecycle': 'BUS static config -> BUS enable -> initial dynamic IOVA set -> ISP_START_DONE -> repeated per-frame dynamic IOVA sets -> BUS disable',
        'qc10c': {
            'allocation_base_is_y_meta': True,
            'y_meta_offset': 0,
            'y_data_offset': 0x6000,
            'c_meta_offset': 0x4f2000,
            'c_data_offset': 0x4f5000,
            'sizeimage': 0x76b000,
            'observed_windows_slot_stride': qc10c_stride,
            'slot_stride_interpretation': 'Windows allocator observation only; Linux must use each queued DMA IOVA, not reproduce the Windows ring',
        },
        'auxiliary_slots': aux_slot,
        'first_pre_start_set': [
            {'port': '0x'+e[1], 'selector': e[2], 'image': f'0x{e[3]:08x}', 'meta': f'0x{e[4]:08x}', 'has_meta': bool(e[5])}
            for e in first
        ],
        'first_post_start_set': [
            {'port': '0x'+e[1], 'selector': e[2], 'image': f'0x{e[3]:08x}', 'meta': f'0x{e[4]:08x}', 'has_meta': bool(e[5])}
            for e in second
        ],
        'writer_hits_ctx1': len(writer_hits),
        'negative_result': 'RVA 0x27920 payloads are not the live WM address writer; direct writer is RVA 0x1dd20 and live MMIO changes correlate to its +0x04/+0x40 stores',
        'linux_consequence': 'Keep PIX runtime blocked; compile dynamic-I/O recipe with Linux DMA IOVAs only. Never freeze captured Windows addresses or Windows allocator slot strides.',
    }
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(text)
    else:
        print(text, end='')
    print('PASS: Windows VFE1 dynamic writer, initial/pre-start timing, per-frame order and QC10C/aux slot relationships are pinned')


if __name__ == '__main__':
    main()
