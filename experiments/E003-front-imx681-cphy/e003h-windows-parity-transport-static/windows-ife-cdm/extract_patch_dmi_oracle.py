#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import argparse, csv, hashlib, importlib.util, json, re, struct

RAW_SHA = '719043805efd57d26483497c0c1964251e77461ccdb7213e5fdc1947defbffc7'
RAW_BYTES = 5832792
MARK = '===E003H_PATCH_DMI_803==='
PATCH_MARK = '===E003H_PATCHSET==='
SRC_MARK = '===E003H_SRCMAP==='
SRC_CAPTURE = 0x20000
QREF = '0f16924ff6a7f9bb56a7e958016da2ed8a174f2f'
KMD_SHA = '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
EXP_USED = [0xe94, 0xe34, 0x904, 0x4e8]
EXP_DMI = [18, 16, 11, 1]
DD = re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+((?:[0-9a-f]{8}\s+){3}[0-9a-f]{8})$', re.I)
DQ = re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+([0-9a-f]{8})`([0-9a-f]{8})\s+([0-9a-f]{8})`([0-9a-f]{8})$', re.I)
DB = re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+((?:[0-9a-f]{2}\s+){7}[0-9a-f]{2})-((?:[0-9a-f]{2}\s+){7}[0-9a-f]{2})', re.I)

def sha(b): return hashlib.sha256(b).hexdigest()

def parse_dd(block):
    out = {}
    for line in block:
        m = DD.match(line)
        if not m: continue
        a = int(m.group(1) + m.group(2), 16)
        for i, v in enumerate(m.group(3).split()): out[a + 4*i] = int(v, 16)
    return out

def parse_dq(block):
    out = {}
    for line in block:
        m = DQ.match(line)
        if not m: continue
        a = int(m.group(1) + m.group(2), 16)
        out[a] = (int(m.group(3) + m.group(4), 16), int(m.group(5) + m.group(6), 16))
    return out

def bytes_at(block, start, length):
    out = bytearray(length); seen = bytearray(length)
    for line in block:
        m = DB.match(line)
        if not m: continue
        a = int(m.group(1) + m.group(2), 16)
        chunk = bytes(int(x,16) for x in (m.group(3) + ' ' + m.group(4)).split())
        if a >= start + length or a + 16 <= start: continue
        s, e = max(a, start), min(a + 16, start + length)
        out[s-start:e-start] = chunk[s-a:e-a]
        seen[s-start:e-start] = b'\1' * (e-s)
    if not all(seen):
        missing = [i for i,v in enumerate(seen) if not v]
        raise ValueError(f'incomplete KD db range start=0x{start:x} length=0x{length:x}; first missing=0x{missing[0]:x}')
    return bytes(out)

def load_decoder(base):
    p = base / 'extract_initial_ife_cdm.py'
    spec = importlib.util.spec_from_file_location('e003h_main_cdm', p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.decode

def hx(v, width=0): return f'0x{v:0{width}x}' if width else f'0x{v:x}'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('raw', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    raw = a.raw.read_bytes()
    if len(raw) != RAW_BYTES: raise SystemExit(f'raw byte mismatch: {len(raw)} != {RAW_BYTES}')
    if sha(raw) != RAW_SHA: raise SystemExit('raw SHA mismatch')
    lines = raw.decode('utf-16').splitlines()
    marks = [i for i,l in enumerate(lines) if l == MARK]
    if len(marks) != 4: raise SystemExit(f'expected 4 runtime markers, got {len(marks)}')
    a.out.mkdir(parents=True, exist_ok=True)
    decode = load_decoder(a.raw.parent.parent)
    prior_path = a.raw.parent.parent / 'initial-ife-cdm-summary.json'
    prior = json.loads(prior_path.read_text())
    packets=[]; all_rows=[]; source_windows=[]; unique_payloads={}
    source_handle_global = source_iova_global = source_cpu_global = None

    for pi, mi in enumerate(marks):
        block = lines[mi:marks[pi+1] if pi+1 < len(marks) else len(lines)]
        if PATCH_MARK not in block or SRC_MARK not in block: raise SystemExit(f'packet {pi}: missing capture submarker')
        dd, dq = parse_dd(block), parse_dq(block)
        xm = re.search(r'x2=([0-9a-f]+) x8=([0-9a-f]+)', next(l for l in block if l.startswith('x2=')), re.I)
        x2 = int(xm.group(1),16); handler = int(xm.group(2),16)
        packet_index = dd[x2+8]
        cmd_off, num_cmd = dd[x2+0x18], dd[x2+0x1c]
        patch_off, num_patch = dd[x2+0x28], dd[x2+0x2c]
        if packet_index != pi or num_cmd != 3: raise SystemExit(f'packet {pi}: outer packet mismatch')
        if num_patch != EXP_DMI[pi]: raise SystemExit(f'packet {pi}: patch count {num_patch} != expected DMI count {EXP_DMI[pi]}')
        d0 = x2 + 0x74 + cmd_off
        main_handle = dd[d0] | (dd[d0+4] << 32)
        main_offset, main_capacity, main_used = dd[d0+8], dd[d0+0xc], dd[d0+0x10]
        if main_used != EXP_USED[pi]: raise SystemExit(f'packet {pi}: main used mismatch')
        if main_handle not in dq: raise SystemExit(f'packet {pi}: main mapping record absent')
        main_iova0, main_cpu0 = dq[main_handle]
        main_cpu = main_cpu0 + main_offset
        main = bytes_at(block, main_cpu, 0xf00)[:main_used]
        cmds, writes, dmis = decode(main)
        if len(dmis) != num_patch: raise SystemExit(f'packet {pi}: decoded DMI count {len(dmis)} != patch count {num_patch}')

        patch_start = x2 + 0x74 + patch_off
        patch_bytes = bytes_at(block, patch_start, num_patch * 24)
        patches=[]
        for i in range(num_patch):
            o=i*24
            dst_handle=struct.unpack_from('<Q',patch_bytes,o)[0]
            dst_offset=struct.unpack_from('<I',patch_bytes,o+8)[0]
            src_handle=struct.unpack_from('<Q',patch_bytes,o+12)[0]
            src_offset=struct.unpack_from('<I',patch_bytes,o+20)[0]
            patches.append((dst_handle,dst_offset,src_handle,src_offset))

        src_handles={p[2] for p in patches}
        if len(src_handles)!=1: raise SystemExit(f'packet {pi}: expected one DMI source handle, got {len(src_handles)}')
        src_handle=next(iter(src_handles))
        if src_handle not in dq: raise SystemExit(f'packet {pi}: source mapping record absent for 0x{src_handle:x}')
        src_iova, src_cpu = dq[src_handle]
        source = bytes_at(block, src_cpu, SRC_CAPTURE)
        source_windows.append(source)
        if source_handle_global is None:
            source_handle_global, source_iova_global, source_cpu_global = src_handle, src_iova, src_cpu
        elif (src_handle,src_iova,src_cpu)!=(source_handle_global,source_iova_global,source_cpu_global):
            raise SystemExit(f'packet {pi}: DMI source mapping changed during four-packet start')

        rows=[]
        for i,(dmi,patch) in enumerate(zip(dmis,patches)):
            dst_handle,dst_offset,p_src_handle,src_offset=patch
            payload_len=dmi['length']+1
            if dst_handle != main_handle: raise SystemExit(f'packet {pi} patch {i}: dst handle != main handle')
            expected_dst = main_offset + dmi['stream_offset'] + 4
            if dst_offset != expected_dst: raise SystemExit(f'packet {pi} patch {i}: dst offset 0x{dst_offset:x} != main-slot DMI address field 0x{expected_dst:x}')
            if p_src_handle != src_handle: raise SystemExit(f'packet {pi} patch {i}: source handle mismatch')
            if dmi['data_iova'] != src_iova + src_offset: raise SystemExit(f'packet {pi} patch {i}: patched IOVA mismatch')
            if src_offset + payload_len > SRC_CAPTURE: raise SystemExit(f'packet {pi} patch {i}: payload exceeds captured source window')
            payload=source[src_offset:src_offset+payload_len]
            ph=sha(payload); unique_payloads.setdefault(ph,payload)
            row={
                'packet':pi,'dmi_index':i,'stream_offset':dmi['stream_offset'],'command':dmi['command'],
                'dmi_register_offset':dmi['dmi_register_offset'],'dmi_sel':dmi['dmi_sel'],
                'length_field':dmi['length'],'payload_bytes':payload_len,
                'dst_offset':dst_offset,'src_offset':src_offset,'data_iova':dmi['data_iova'],'payload_sha256':ph,
            }
            rows.append(row); all_rows.append(row)

        prior_dmi=prior['packets'][pi]['dmi_commands']
        if len(prior_dmi)!=len(dmis): raise SystemExit(f'packet {pi}: prior-run DMI count mismatch')
        for i,(old,new) in enumerate(zip(prior_dmi,dmis)):
            for key in ('stream_offset','command','length','dmi_register_offset','dmi_sel'):
                if old[key]!=new[key]: raise SystemExit(f'packet {pi} DMI {i}: prior-run structural mismatch at {key}')

        packets.append({
            'packet':pi,'packet_index':packet_index,'handler':hx(handler,16),'cmd_buffers_offset':cmd_off,'num_cmd_buffers':num_cmd,
            'patchset_offset':patch_off,'num_patches':num_patch,'main_handle':hx(main_handle,16),'main_iova':hx(main_iova0+main_offset,8),
            'main_cpu_va':hx(main_cpu,16),'main_used_length':main_used,'main_sha256':sha(main),'decoded_command_count':len(cmds),
            'decoded_register_write_count':len(writes),'decoded_dmi_count':len(dmis),'source_handle':hx(src_handle,16),
            'source_iova':hx(src_iova,8),'source_cpu_va':hx(src_cpu,16),'source_capture_bytes':SRC_CAPTURE,'source_capture_sha256':sha(source),
            'dmi':[{k:(hx(v) if k in ('stream_offset','dmi_register_offset','dst_offset','src_offset','data_iova') else v) for k,v in r.items()} for r in rows]
        })

    source_hashes={sha(x) for x in source_windows}
    if len(source_hashes)!=1: raise SystemExit('DMI source window changed between packet hits')
    source=source_windows[0]
    max_end=max(r['src_offset']+r['payload_bytes'] for r in all_rows)
    if max_end != 0x1bccc: raise SystemExit(f'unexpected DMI covered end 0x{max_end:x}')
    (a.out/'dmi-source-window.bin').write_bytes(source)

    with (a.out/'dmi-payloads.csv').open('w',newline='') as f:
        fields=['packet','dmi_index','stream_offset','command','dmi_register_offset','dmi_sel','length_field','payload_bytes','dst_offset','src_offset','data_iova','payload_sha256']
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader()
        for r in all_rows:
            z=dict(r)
            for k in ('stream_offset','dmi_register_offset','dst_offset','src_offset','data_iova'): z[k]=hx(z[k])
            w.writerow(z)

    payload_dir=a.out/'dmi-payloads'
    payload_dir.mkdir(exist_ok=True)
    for h,payload in sorted(unique_payloads.items()): (payload_dir/f'{h}.bin').write_bytes(payload)

    groups=[]
    grouped={}
    for r in all_rows:
        k=(r['dmi_register_offset'],r['dmi_sel'],r['payload_bytes'],r['payload_sha256'])
        grouped.setdefault(k,[]).append({'packet':r['packet'],'dmi_index':r['dmi_index'],'src_offset':r['src_offset'],'data_iova':r['data_iova']})
    for (reg,sel,n,h),refs in sorted(grouped.items()):
        groups.append({'dmi_register_offset':hx(reg),'dmi_sel':sel,'payload_bytes':n,'payload_sha256':h,
            'references':[{**x,'src_offset':hx(x['src_offset']),'data_iova':hx(x['data_iova'])} for x in refs]})

    summary={
        'status':'PASS',
        'policy':'Same-machine Windows is the behavioral oracle; exact qccamisp8380.sys disassembly defines the Windows patch record mechanics. Qualcomm public source is used only to confirm CDM DMI length semantics (length field + 1 bytes).',
        'raw':{'bytes':len(raw),'sha256':RAW_SHA,'encoding':'UTF-16LE KD text log','runtime_breaks':4},
        'windows_isp':{'binary_sha256':KMD_SHA,'device_start_ife_0x803_callsite_rva':'0x16094','ife_handler_rva':'0x22cd0','patch_processor_rva':'0x28618..0x2870c'},
        'qualcomm_cdm_reference_commit':QREF,
        'mechanical_patch_layout':{'record_bytes':24,'fields':['u64 dst_handle','u32 dst_offset','u64 src_handle (packed at +0x0c)','u32 src_offset'],'payload_base_from_windows_handler':'packet + 0x74','patchset_address':'packet + 0x74 + patchsetOffset','source_mapping_record':'[src_handle+0] IOVA, [src_handle+8] CPU VA','patched_value':'low32(source IOVA + src_offset) written to destination CPU VA + dst_offset'},
        'closure':{'total_patches':sum(p['num_patches'] for p in packets),'total_dmi_commands':len(all_rows),'patch_count_equals_dmi_count_per_packet':True,'all_patch_destinations_are_exact_dmi_address_fields':True,'all_patched_iovas_equal_source_iova_plus_src_offset':True,'all_payloads_captured':True,'dmi_length_semantics':'payload bytes = encoded length + 1','max_source_end':hx(max_end),'captured_source_window_bytes':SRC_CAPTURE,'source_window_sha256':sha(source),'source_window_identical_at_all_four_hits':True,'dmi_register_selector_payload_groups':len(groups),'unique_payload_sha256_count':len(unique_payloads)},
        'dmi_groups':groups,
        'packets':packets,
        'next_required_work':'Classify the exact captured DMI/LUT payloads by VFE register/selector and combine them with the already-decoded main CDM register programming into a static Windows-parity VFE1 PIX/ISP implementation plan. No Linux runtime is authorized by this parser alone.'
    }
    (a.out/'patch-dmi-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary['closure'],indent=2))

if __name__=='__main__': main()
