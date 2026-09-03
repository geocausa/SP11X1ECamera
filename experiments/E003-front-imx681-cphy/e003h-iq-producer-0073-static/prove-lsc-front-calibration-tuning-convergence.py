#!/usr/bin/env python3
"""Fail-closed proof that SP11 front LSC calibration provenance converges on the tuning-tree gate.

This proves three distinct facts together:
  * verified-front raw OTP is physical front-module EEPROM (via the accepted upstream proof),
    and both IMX681/OV13858 modules use the generic EEPROM formatter;
  * the historical Aug-4 raw EEPROM-looking cache is mechanically OV13858/rear and therefore
    cannot be used to resolve the remaining three front averaged-green raw-value ambiguities;
  * IFELSC411 resolves both lsc41_ife_v2 and lscgolden41_ife_v2 from the exact same request
    tuning-manager/root.  Hence the observed rear/default x22 and golden authorities are one
    tuning-tree provenance problem, not a separate EEPROM-formatting crossover.

No camera runtime and no Linux request6 are performed.
"""
from __future__ import annotations
import argparse, bisect, hashlib, json, mmap, struct
from pathlib import Path

from decode_imx681_chromatix import parse_header, parse_symbol_table, data_bytes

HERE = Path(__file__).resolve().parent
ARCHIVE = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump')
FRONT_MODULE = ARCHIVE / 'surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin'
REAR_MODULE = ARCHIVE / 'surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.sensormodule.rfc_ov13858.bin'
DEVICEMFT = ARCHIVE / 'surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'
REAR_KMD = ARCHIVE / 'surfacecamrearsensor8380.inf_arm64_8fbcacb272007d57/surfacecamrearsensor8380.sys'
DEFAULT_DUMP = Path('/mnt/windows/Windows/LiveKernelReports/NetAdapterCx-20260804-1913.dmp')

SHA = {
    'front_module': 'f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c',
    'rear_module': 'f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14',
    'devicemft': 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35',
    'rear_kmd': 'b7d7a278c5e7b92ebf35f870a7e06cbad670ffb35bfaf40106e27b09bf33fabb',
    'dump': '2ca55e2a058df20936068bd5dfe4c111769ee2d0758c96072adbd3c71a27db40',
    'lsc_lightinfo': 'bbe16d1678d41c05bb885d4b1680b6be9b86e32e20a67d15576b5a6e764d4599',
    'wb_lightinfo': '747eda7709d4c829b93adbc224aa61dce1a85a9b0dc6526598da7722eb7a9a9c',
    'rear_raw_carve': '1d6297455b1afd0184089668020a3b2d99e2758dea30bec1fbda4980a317cd21',
    'rear_raw_lsc': '679fc75878367f717cea2dbd99f704109adcc48c86b82e7b8ba260cc7eb260fe',
    'rear_kmd_ref_page': '9fbdf7c2050266871a5ef5676d2b96eb989a1594ef91debe7d5855ab7c06b6d4',
    'rear_heap_ref_page': '8308296a82e4d4c3da184029a6ecb4f2948bcbe12a97655305df7f89a542bf24',
}

PLUGIN_NAMES = [
    'sunny_gt24p64b_imx519', 'ofilm_ohs0443_ov12a10', 'gt24c64a_qtech',
    'a16n21b_imx481', 'a48n01e_imx586', 'a13s07a_s5k3m5', 'p24c64e_imx563',
    'gt24p64b_ov2740', 'cat24c64_ov5675', 'gt24p64b_ShineTech_ov2740',
    'fm24c64c_shinetech_ov08x',
]

CODE = {
    # EEPROMData::GetMemorySizeBytes inline loop in EEPROMData construction.
    0x714384: '680a40f9', 0x71438c: '095140b9', 0x714394: '082d40f9',
    0x71439c: '0a1140b9', 0x7143a0: '5f0d0071', 0x7143a8: '0a0140f9',
    0x7143b0: '94422a8b', 0x714420: '748203b9',
    # IFELSC411 tuning manager/root + lookups.
    0xA02448: '97f64ff9', 0xA02464: 'ea0240f9', 0xA0246C: '480140f9',
    0xA024A0: '400140f9', 0xA024A8: '01410e91', 0xA024B4: '51c5f397',
    0xA0250C: 'e80240f9', 0xA02514: '000140f9', 0xA02520: '883250f9',
    0xA02530: '01610c91', 0xA02534: '31c5f397',
}


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def u16(b: bytes, o: int) -> int:
    return struct.unpack_from('<H', b, o)[0]


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def u64(b: bytes, o: int) -> int:
    return struct.unpack_from('<Q', b, o)[0]


def parse_module(p: Path, eeprom_sid: int) -> tuple[bytes, dict, bytes, bytes, bytes]:
    b = p.read_bytes()
    h = parse_header(b)
    recs, _ = parse_symbol_table(b, h['sections'][0], h['sections'][1])
    obj = h['sections'][1]
    root = data_bytes(b, obj, recs[eeprom_sid])
    return b, recs, obj, root, data_bytes(b, obj, recs[u16(root, 0x122)])


def decode_eeprom_contract(p: Path, eeprom_sid: int) -> dict:
    b, recs, obj, root, lsc = parse_module(p, eeprom_sid)
    if recs[eeprom_sid]['type'] != 'EEPROMDriverData':
        raise ValueError('EEPROM root type mismatch')
    name_sid = u16(root, 0x10)
    name = data_bytes(b, obj, recs[name_sid]).rstrip(b'\0').decode('ascii')
    reg_sid = u16(root, 0x36)
    rs = data_bytes(b, obj, recs[reg_sid])
    if len(rs) != 40:
        raise ValueError('regSetting length mismatch')
    slave_sid, regdata_sid, delay_sid = u32(rs, 4), u32(rs, 0x10), u32(rs, 0x24)
    slave = u16(data_bytes(b, obj, recs[slave_sid]), 0)
    read_bytes = u32(data_bytes(b, obj, recs[regdata_sid]), 0)
    delay = u32(data_bytes(b, obj, recs[delay_sid]), 0)
    contract = {
        'eeprom_name': name,
        'eeprom_name_symbol': name_sid,
        'memory_map_regsetting_symbol': reg_sid,
        'regsetting_sha256': sha_bytes(rs),
        'entry_count': u32(rs, 0),
        'slave_addr': hex(slave),
        'register_addr': hex(u32(rs, 8)),
        'register_addr_type': u32(rs, 0x14),
        'register_data_type': u32(rs, 0x18),
        'operation': u32(rs, 0x1c),
        'read_bytes': hex(read_bytes),
        'delay_us': delay,
        'lsc_light_symbol': u16(root, 0x122),
        'lsc_light_sha256': sha_bytes(lsc),
        'lsc_mesh': u16(root, 0x126),
        'lsc_strides': [u16(root, 0x128 + 2*i) for i in range(4)],
    }
    wb_sid = u16(root, 0xF2)
    wb = data_bytes(b, obj, recs[wb_sid])
    contract['wb_light_symbol'] = wb_sid
    contract['wb_light_sha256'] = sha_bytes(wb)
    # Exact generic LSC raw byte descriptors.
    desc = []
    for i in range(8):
        o = 4 + 12*i
        desc.append((u32(lsc, o), u32(lsc, o+4), u32(lsc, o+8)))
    contract['lsc_descriptors'] = [[hex(a), hex(m), s] for a,m,s in desc]
    return contract


class PE:
    def __init__(self, b: bytes):
        self.b = b
        pe = u32(b, 0x3c)
        if b[pe:pe+4] != b'PE\0\0':
            raise ValueError('bad PE')
        self.nsec = u16(b, pe+6)
        opt = u16(b, pe+20)
        self.sh = pe + 24 + opt
        self.image_base = u64(b, pe + 24 + 24)  # PE32+ ImageBase
    def off(self, rva: int) -> int:
        for i in range(self.nsec):
            o = self.sh + 40*i
            vsz, va, rsz, raw = struct.unpack_from('<IIII', self.b, o+8)
            if va <= rva < va + max(vsz, rsz):
                return raw + rva - va
        raise ValueError(f'RVA 0x{rva:x} unmapped')
    def at(self, rva: int, n: int) -> bytes:
        o = self.off(rva)
        return self.b[o:o+n]
    def cstr_va(self, va: int) -> str:
        rva = va - self.image_base
        o = self.off(rva)
        e = self.b.index(0, o)
        return self.b[o:e].decode('ascii')


def bl_target(rva: int, insn: int) -> int | None:
    if insn & 0xFC000000 != 0x94000000:
        return None
    imm = insn & 0x03FFFFFF
    if imm & (1 << 25):
        imm -= 1 << 26
    return rva + (imm << 2)


class ActiveDump:
    ADDR_MASK = 0x0000FFFFFFFFF000
    def __init__(self, path: Path):
        self.path = path
        with path.open('rb') as f:
            self.hdr = f.read(0x2000)
            f.seek(0x2000); sh = f.read(0x38)
        if self.hdr[:8] != b'PAGEDU64' or u32(self.hdr, 3992) != 6 or sh[:8] != b'SDMPDUMP':
            raise ValueError('not expected ARM64 active dump')
        self.filebase = u64(sh, 0x20)
        self.pages = u64(sh, 0x28)
        self.bits = u64(sh, 0x30)
        with path.open('rb') as f:
            f.seek(0x2038); self.bitmap = f.read(self.bits // 8)
        if sum(x.bit_count() for x in self.bitmap) != self.pages:
            raise ValueError('SDMP bitmap page count mismatch')
        self.prefix = [0] * (len(self.bitmap) + 1)
        for i, v in enumerate(self.bitmap):
            self.prefix[i+1] = self.prefix[i] + v.bit_count()
        self.dtb = u64(self.hdr, 0x10) & ~0xfff
    def pa_to_file(self, pa: int) -> int | None:
        page, off = pa >> 12, pa & 0xfff
        bi, bit = page >> 3, page & 7
        if bi >= len(self.bitmap) or not (self.bitmap[bi] & (1 << bit)):
            return None
        rank = self.prefix[bi] + (self.bitmap[bi] & ((1 << bit)-1)).bit_count()
        return self.filebase + rank * 0x1000 + off
    def read_pa(self, pa: int, n: int) -> bytes | None:
        out = bytearray()
        with self.path.open('rb') as f:
            while n:
                take = min(n, 0x1000 - (pa & 0xfff))
                fo = self.pa_to_file(pa)
                if fo is None:
                    return None
                f.seek(fo); x = f.read(take)
                if len(x) != take:
                    return None
                out += x; pa += take; n -= take
        return bytes(out)
    def va_to_pa(self, va: int) -> int | None:
        x, tp = va & ((1 << 48)-1), self.dtb
        for level, shift in enumerate((39, 30, 21, 12)):
            pg = self.read_pa(tp, 0x1000)
            if pg is None:
                return None
            d = u64(pg, ((x >> shift) & 0x1ff) * 8)
            typ = d & 3
            if typ == 0:
                return None
            if level < 3 and typ == 1:
                size = 1 << shift
                return ((d & self.ADDR_MASK) & ~(size-1)) + (x & (size-1))
            if typ != 3:
                return None
            if level == 3:
                return (d & self.ADDR_MASK) | (x & 0xfff)
            tp = d & self.ADDR_MASK
        return None
    def read_va(self, va: int, n: int) -> bytes | None:
        out = bytearray()
        while n:
            pa = self.va_to_pa(va)
            if pa is None:
                return None
            take = min(n, 0x1000 - (va & 0xfff))
            x = self.read_pa(pa, take)
            if x is None:
                return None
            out += x; va += take; n -= take
        return bytes(out)
    def uq(self, va: int) -> int | None:
        b = self.read_va(va, 8)
        return u64(b, 0) if b else None
    def ud(self, va: int) -> int | None:
        b = self.read_va(va, 4)
        return u32(b, 0) if b else None
    def unicode_string(self, va: int) -> str | None:
        b = self.read_va(va, 16)
        if not b:
            return None
        ln = u16(b, 0); ptr = u64(b, 8)
        if not ptr or ln > 2048:
            return ''
        s = self.read_va(ptr, ln)
        return s.decode('utf-16le', 'replace') if s else None
    def loaded_modules(self) -> list[dict]:
        head = u64(self.hdr, 0x20)
        cur = self.uq(head); seen = set(); out = []
        while cur and cur != head and cur not in seen and len(out) < 1000:
            seen.add(cur)
            base, size = self.uq(cur + 0x30), self.ud(cur + 0x40)
            out.append({'entry': cur, 'base': base, 'size': size,
                        'full': self.unicode_string(cur + 0x48),
                        'name': self.unicode_string(cur + 0x58)})
            cur = self.uq(cur)
        return out


def assert_eq(got, want, msg: str):
    if got != want:
        raise ValueError(f'{msg}: {got!r} != {want!r}')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dump', type=Path, default=DEFAULT_DUMP)
    ap.add_argument('--out', type=Path, default=HERE/'lsc-front-calibration-tuning-convergence-oracle.json')
    a = ap.parse_args()

    for p, key in [(FRONT_MODULE,'front_module'),(REAR_MODULE,'rear_module'),(DEVICEMFT,'devicemft'),(REAR_KMD,'rear_kmd')]:
        assert_eq(sha_file(p), SHA[key], f'{key} SHA')

    front = decode_eeprom_contract(FRONT_MODULE, 3)
    rear = decode_eeprom_contract(REAR_MODULE, 4)
    assert_eq(front['eeprom_name'], 'gt24p128f_imx681', 'front EEPROM name')
    assert_eq(rear['eeprom_name'], 'st_m24c64', 'rear EEPROM name')
    for c, read_bytes in [(front,'0x1762'),(rear,'0x174a')]:
        assert_eq(c['entry_count'], 1, 'memoryMap entry count')
        assert_eq(c['slave_addr'], '0xa0', 'EEPROM slave')
        assert_eq(c['register_addr'], '0x0', 'EEPROM register addr')
        assert_eq(c['register_addr_type'], 2, 'reg addr type')
        assert_eq(c['register_data_type'], 1, 'reg data type')
        assert_eq(c['operation'], 3, 'READ opcode')
        assert_eq(c['read_bytes'], read_bytes, 'READ byte count')
        assert_eq(c['delay_us'], 0, 'READ delay')
        assert_eq(c['lsc_light_sha256'], SHA['lsc_lightinfo'], 'LSC lightInfo SHA')
        assert_eq(c['wb_light_sha256'], SHA['wb_lightinfo'], 'WB lightInfo SHA')
        assert_eq(c['lsc_mesh'], 221, 'LSC mesh')
        assert_eq(c['lsc_strides'], [2,2,2,2], 'LSC strides')
    assert_eq(front['lsc_descriptors'], rear['lsc_descriptors'], 'front/rear LSC descriptors')

    pe_bytes = DEVICEMFT.read_bytes(); pe = PE(pe_bytes)
    # Exact built-in EEPROM plugin table.
    plugins = []
    table_rva = 0x1151f60
    for i in range(11):
        ent = pe.at(table_rva + i*16, 16)
        name_ptr, fn_ptr = struct.unpack('<QQ', ent)
        plugins.append({'name': pe.cstr_va(name_ptr), 'function_va': hex(fn_ptr)})
    assert_eq([x['name'] for x in plugins], PLUGIN_NAMES, 'EEPROM plugin table')
    if front['eeprom_name'] in PLUGIN_NAMES or rear['eeprom_name'] in PLUGIN_NAMES:
        raise ValueError('front/rear unexpectedly selects custom EEPROM plugin')

    code = {}
    for rva, hx in CODE.items():
        got = pe.at(rva, len(bytes.fromhex(hx))).hex()
        assert_eq(got, hx, f'code @0x{rva:x}')
        code[hex(rva)] = got
    assert_eq(bl_target(0xA024B4, u32(pe.at(0xA024B4,4),0)), 0x6F39F8, 'lsc41 lookup target')
    assert_eq(bl_target(0xA02534, u32(pe.at(0xA02534,4),0)), 0x6F39F8, 'golden lookup target')
    assert_eq(pe.cstr_va(0x181375390), 'lsc41_ife_v2', 'LSC tree name')
    assert_eq(pe.cstr_va(0x181375318), 'lscgolden41_ife_v2', 'golden tree name')

    # Generic FormatLSCData must not itself jump into TuningDataManager lookup.
    format_bl = []
    for rva in range(0x723E40, 0x7243D0, 4):
        ins = u32(pe.at(rva,4),0)
        tgt = bl_target(rva, ins)
        if tgt is not None:
            format_bl.append([hex(rva), hex(tgt)])
    if any(int(t,16) == 0x6F39F8 for _,t in format_bl):
        raise ValueError('FormatLSCData unexpectedly calls tuning lookup')

    # Upstream accepted proofs constrain front physical ownership and the 3-point green ambiguity.
    raw_otp = json.loads((HERE/'lsc-front-raw-otp-provenance-oracle.json').read_text())
    assert_eq(raw_otp['status'], 'PASS', 'raw OTP prerequisite')
    if 'physical EEPROM' not in raw_otp['classification'] or 'Rear camera0 raw-OTP' not in raw_otp['classification']:
        raise ValueError('raw OTP prerequisite classification changed')
    auth = json.loads((HERE/'lsc-front-rear-calibration-authority-oracle.json').read_text())
    assert_eq(auth['status'], 'PASS', 'calibration authority prerequisite')
    amb = auth['inverse_crosscheck']['three_two-solution_green_points']
    assert_eq(set(amb), {'19','57','94'}, 'green ambiguity indices')
    if any(len(v['equation_candidates']) != 2 for v in amb.values()):
        raise ValueError('green ambiguity candidate cardinality changed')
    front_raw_candidate_count = 2 ** len(amb)
    assert_eq(front_raw_candidate_count, 8, 'front raw LSC candidate count')

    owner = json.loads((HERE/'lsc-tuning-manager-ownership-oracle.json').read_text())
    if not owner.get('accepted') or 'same CaptureDevice private DataManager' not in owner.get('classification',''):
        raise ValueError('tuning-manager ownership prerequisite changed')

    # Durable carves plus full source dump revalidation.
    carve_dir = HERE/'oracle-aug4-rear-eeprom'
    raw = (carve_dir/'RAW_EEPROM_REAR_174A.bin').read_bytes()
    kmd_page = (carve_dir/'KMD_REAR_REF_PAGE_1000.bin').read_bytes()
    heap_page = (carve_dir/'HEAP_REAR_REF_PAGE_1000.bin').read_bytes()
    assert_eq(len(raw), 0x174A, 'rear carve bytes')
    assert_eq(sha_bytes(raw), SHA['rear_raw_carve'], 'rear carve SHA')
    assert_eq(sha_bytes(raw[0x103D:0x1725]), SHA['rear_raw_lsc'], 'rear carve LSC SHA')
    assert_eq(sha_bytes(kmd_page), SHA['rear_kmd_ref_page'], 'rear KMD ref page SHA')
    assert_eq(sha_bytes(heap_page), SHA['rear_heap_ref_page'], 'rear heap ref page SHA')
    raw_va = 0xffff94826f130000
    assert_eq(u64(kmd_page, 0x7E8), raw_va, 'rear KMD raw pointer')
    assert_eq(u32(kmd_page, 0x7FA), 0x174A, 'rear KMD cached size')
    assert_eq(u64(heap_page, 0x330), raw_va, 'rear heap raw pointer')
    assert_eq(u64(heap_page, 0x338), 0x174A, 'rear heap raw size')
    if heap_page.count(b'com.surface.tuned.rfc_ov13858.bin') < 2:
        raise ValueError('rear heap filename evidence missing')

    # Generic-format replay: carved rear raw LSC bytes reproduce preserved rear VSS slot exactly.
    slot = (HERE/'oracle-vss-20260902-local/REQ1_LSC_CAL_SLOT_0DF0.bin').read_bytes()
    assert_eq(struct.unpack_from('<III',slot,0), (1,3,221), 'rear slot header')
    channel_raw = [0x103D,0x11F7,0x13B1,0x156B]
    channel_slot = [0x0C,0x380,0x6F4,0xA68]
    for ro, so in zip(channel_raw, channel_slot):
        vals = struct.unpack_from('<221H', raw, ro)
        floats = struct.unpack_from('<221f', slot, so)
        if any(float(v) != f for v,f in zip(vals,floats)):
            raise ValueError('rear generic LSC formatting replay mismatch')

    if sha_file(a.dump) != SHA['dump']:
        raise ValueError('source Aug-4 dump SHA mismatch')
    dump = ActiveDump(a.dump)
    assert_eq(dump.filebase, 0x483000, 'SDMP filebase')
    assert_eq(dump.pages, 787224, 'SDMP page count')
    assert_eq(dump.bits, 12582912, 'SDMP bit count')
    # Raw buffer VA -> expected PA -> source file page.
    raw_pa = dump.va_to_pa(raw_va)
    assert_eq(raw_pa, 0x9B2330000, 'rear raw physical address')
    assert_eq(dump.pa_to_file(raw_pa), 0x2F78B000, 'rear raw source file offset')
    # Heap evidence VA -> source file hit.
    heap_va = 0xffff94825fccf330
    heap_pa = dump.va_to_pa(heap_va)
    assert_eq(dump.pa_to_file(heap_pa), 0x6B94B330, 'rear heap hit file offset')
    # Parse loaded module list and prove the second raw pointer reference lives in rear KMD, not front KMD.
    mods = dump.loaded_modules()
    rear_mod = next((m for m in mods if m['name'] == 'surfacecamrearsensor8380.sys'), None)
    front_mod = next((m for m in mods if m['name'] == 'surfacecamfrontsensor8380.sys'), None)
    if rear_mod is None or front_mod is None:
        raise ValueError('camera KMDs missing from loaded module list')
    assert_eq(rear_mod['base'], 0xfffff80039440000, 'loaded rear KMD base')
    assert_eq(rear_mod['size'], 0x42000, 'loaded rear KMD size')
    assert_eq(front_mod['base'], 0xfffff80039490000, 'loaded front KMD base')
    rear_ref_va = rear_mod['base'] + 0x1F7E8
    rear_ref_pa = dump.va_to_pa(rear_ref_va)
    assert_eq(dump.pa_to_file(rear_ref_pa), 0x6B3C77E8, 'rear KMD raw pointer reference file offset')
    if not (rear_mod['base'] <= rear_ref_va < rear_mod['base'] + rear_mod['size']):
        raise ValueError('rear pointer ref not inside rear KMD')
    if front_mod['base'] <= rear_ref_va < front_mod['base'] + front_mod['size']:
        raise ValueError('rear pointer ref aliases front KMD')

    result = {
        'schema': 'sp11-e003h-lsc-front-calibration-tuning-convergence-v1',
        'status': 'PASS',
        'classification': (
            'CLOSED CALIBRATION/TUNING CONVERGENCE: verified-front raw OTP remains physical front-module EEPROM; '
            'both front and rear use the generic EEPROM formatter with byte-identical LSC decoding descriptors; '
            'the historical Aug-4 raw cache is conclusively OV13858 rear and is excluded as front raw evidence; '
            'and IFELSC411 resolves lsc41_ife_v2 plus lscgolden41_ife_v2 from the same request-private tuning manager/root. '
            'Therefore the observed rear/default x22 and rear/default golden authorities are one remaining live front tuning-tree provenance problem, not a separate EEPROM-formatting crossover.'
        ),
        'binaries': {
            'front_sensor_module_sha256': SHA['front_module'],
            'rear_sensor_module_sha256': SHA['rear_module'],
            'device_mft_sha256': SHA['devicemft'],
            'rear_sensor_kmd_sha256': SHA['rear_kmd'],
        },
        'eeprom_contracts': {'front': front, 'rear': rear},
        'custom_eeprom_plugin_table': {
            'table_va': '0x181151f60', 'entries': plugins,
            'front_match': False, 'rear_match': False,
            'classification': 'both modules fall through to generic EEPROMData formatters',
        },
        'generic_formatter': {
            'format_lsc_rva': '0x723e40',
            'direct_tuning_lookup_calls': 0,
            'call_targets': format_bl,
            'lsc_raw_range': '0x103d..0x1724',
            'front_rear_lsc_descriptor_sha256': SHA['lsc_lightinfo'],
            'front_rear_wb_descriptor_sha256': SHA['wb_lightinfo'],
        },
        'same_request_tuning_tree': {
            'manager_field': 'ISPInputData+0x1fe8',
            'lookup_rva': '0x6f39f8',
            'lsc41_lookup_call_rva': '0xa024b4',
            'golden_lookup_call_rva': '0xa02534',
            'lsc41_name': 'lsc41_ife_v2',
            'golden_name': 'lscgolden41_ife_v2',
            'same_manager_root': True,
            'exact_code_bytes': code,
        },
        'aug4_rear_cache': {
            'source_dump_sha256': SHA['dump'],
            'source_dump_bytes': a.dump.stat().st_size,
            'sdmp': {'filebase':'0x483000','pages':787224,'bits':12582912,'dtb':hex(dump.dtb)},
            'raw_va': hex(raw_va), 'raw_pa': hex(raw_pa), 'source_file_offset':'0x2f78b000',
            'raw_bytes': len(raw), 'raw_sha256': SHA['rear_raw_carve'],
            'lsc_subrange_sha256': SHA['rear_raw_lsc'],
            'heap_reference': {'va':hex(heap_va),'source_file_offset':'0x6b94b330','size':'0x174a','rear_tuning_filename_coresident':True},
            'kmd_reference': {'va':hex(rear_ref_va),'source_file_offset':'0x6b3c77e8','owner':'surfacecamrearsensor8380.sys','owner_rva':'0x1f7e8'},
            'loaded_rear_kmd': {'base':hex(rear_mod['base']),'size':hex(rear_mod['size'])},
            'loaded_front_kmd': {'base':hex(front_mod['base']),'size':hex(front_mod['size'])},
            'classification': 'conclusively rear OV13858 cache; forbidden as a front physical-EEPROM discriminator',
        },
        'front_raw_lsc_boundary': {
            'physical_source_class': 'front physical EEPROM (accepted upstream proof)',
            'direct_red_blue_points_unique': auth['inverse_crosscheck']['direct_unique_points'],
            'averaged_green_two_solution_points': amb,
            'remaining_raw_byte_candidates': front_raw_candidate_count,
            'parity_effect': 'all 8 candidates are equivalent at the accepted Windows x23 averaged-green boundary; do not select the rear candidate as physical-front bytes without new evidence',
        },
        'remaining_gates': [
            'live verified-front private DataManager source buffer/tree identity (+0x38/+0x30; manager +0x28) if static parsing cannot close it',
            'genuine verified-front sequential Tintless state/stats/output bridging request4 pre-Tintless into front staging',
            'one atomic front integrated producer/output capsule before any Linux request6 review',
        ],
        'safety': {'offline_only': True, 'camera_runtime_performed': False, 'linux_request6_authorized': False, 'linux_request6_executed': False},
    }
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS front calibration/tuning convergence')
    print('  front/rear EEPROM read bytes', front['read_bytes'], rear['read_bytes'])
    print('  generic formatter; custom plugin matches', False, False)
    print('  Aug4 cache -> rear KMD RVA 0x1f7e8 + rear heap size 0x174a')
    print('  lsc41 + golden -> same request tree lookup 0x6f39f8')
    print('  front raw LSC candidates remain', front_raw_candidate_count)
    print('  oracle', a.out)

if __name__ == '__main__':
    main()
