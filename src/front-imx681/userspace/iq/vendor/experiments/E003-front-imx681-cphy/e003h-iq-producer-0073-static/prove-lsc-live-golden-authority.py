#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROJECT = REPO.parent.parent
DRIVERDUMP = PROJECT / '00-RE-archive' / 'sp11-driverdump'
CARVE = HERE / 'oracle-carved-20260902'
OUT = HERE / 'lsc-live-golden-authority-oracle.json'

EXPECTED_CANDIDATES = 10
WINNER_FILE = 'com.surface.tuned.rfc_ov13858.bin'
WINNER_TUNING_SHA = '4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635'
WINNER_REGION_SID = 0x2AE
WINNER_GOLDEN_SHA = 'f771e54d183281251bf0ef6d94e94a0d439c641f8b8ed9a3ad60ead4094487d6'
FRONT_FILE = 'com.surface.tuned.ffc_imx681.bin'
FRONT_TUNING_SHA = '2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
FRONT_GOLDEN_SHA = 'b0023db8b7254a9922c60506db58fd9bf2d717e09a8f088d31f33b2316538f6e'
CAPTURE = {
    5: {
        'x22': ('REQ5_X22_RAW_0DF0.bin', 'e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de'),
        'x23': ('REQ5_X23_RAW_0DF0.bin', '94cbaac591fabf97ebff4a005b02fbcfa7a2bfff5783134794e1c52f0bcead71'),
    },
    6: {
        'x22': ('REQ6_X22_RAW_0DF0.bin', '3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8'),
        'x23': ('REQ6_X23_RAW_0DF0.bin', '62b39d4ee8f66dc4931c0a99bf4c51cc7069ea4829f78df6c80dbfa82b48ad15'),
    },
}


def need(c: bool, m: str) -> None:
    if not c: raise RuntimeError(m)

def sha_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha_file(p: Path) -> str: return sha_bytes(p.read_bytes())
def u32(b: bytes, o: int) -> int: return struct.unpack_from('<I', b, o)[0]
def f32(v: float) -> float: return struct.unpack('<f', struct.pack('<f', v))[0]
def fbits(v: float) -> bytes: return struct.pack('<f', v)

def parse_golden(path: Path):
    blob = path.read_bytes()
    if not blob.startswith(b'QTI Chromatix Header'): return None
    hs, ns = u32(blob, 0xA0), u32(blob, 0xA4)
    if hs != 0xA8 or ns != 3: return None
    secs=[]
    for i in range(3):
        tag,off,size=struct.unpack_from('<3I',blob,hs+i*12)
        need(tag==i, f'{path.name}: section tag drift')
        secs.append((off,size))
    sym_off,sym_size=secs[0]; obj_off,obj_size=secs[1]
    if sym_size % 56: return None
    rec={}
    for o in range(sym_off,sym_off+sym_size,56):
        sid=u32(blob,o); typ=blob[o+4:o+36].split(b'\0',1)[0].decode('ascii','replace')
        ver,mid,msid,do,db=struct.unpack_from('<5I',blob,o+36)
        rec[sid]={'symbol_id':sid,'type':typ,'version_raw':ver,'mode_id':mid,'mode_symbol_id':msid,
                  'data_abs_offset':obj_off+do,'data_bytes':db}
    roots=[r for r in rec.values() if r['type']=='lscgolden41_ife_v2']
    if not roots: return None
    need(len(roots)==1, f'{path.name}: multiple golden roots')
    def data(r): return blob[r['data_abs_offset']:r['data_abs_offset']+r['data_bytes']]
    root=roots[0]; rd=data(root)
    mods=[]
    for o in range(0,len(rd)-3,4):
        sid=u32(rd,o)
        if sid in rec and rec[sid]['type']=='mod_lscgolden41_trigger_data':mods.append(rec[sid])
    mods={x['symbol_id']:x for x in mods}
    need(len(mods)==1, f'{path.name}: golden trigger root ambiguity')
    mod=next(iter(mods.values())); md=data(mod)
    regs=[]
    for o in range(0,len(md)-3,4):
        sid=u32(md,o)
        if sid in rec and rec[sid]['type']=='region' and rec[sid]['data_bytes']==4*221*4:
            regs.append(rec[sid])
    regs={x['symbol_id']:x for x in regs}
    need(len(regs)==1, f'{path.name}: golden region ambiguity {list(regs)}')
    region=next(iter(regs.values())); gd=data(region)
    vals=struct.unpack('<884f',gd)
    need(all(v == float(int(v)) for v in vals), f'{path.name}: golden not integer-valued float32')
    return {
        'file': path.name, 'path': str(path), 'tuning_sha256': sha_bytes(blob),
        'golden_root_sid': root['symbol_id'], 'golden_trigger_sid': mod['symbol_id'],
        'golden_region_sid': region['symbol_id'], 'golden_region_abs_offset': region['data_abs_offset'],
        'golden_region_sha256': sha_bytes(gd), 'golden_min': min(vals), 'golden_max': max(vals),
        'values': vals,
    }


def calc(g: float, e: int, x: float) -> float:
    # Exact direct-channel Surface sequence: float32 fdiv, then float32 fmul.
    return f32(f32(g / f32(float(e))) * x)


def candidates(g: float, x: float, y: float):
    # calc() is monotone non-increasing for positive g/x/e. Find the first
    # EEPROM u16 value whose result is <= target, then collect its exact float32 plateau.
    lo,hi=1,65535
    while lo < hi:
        mid=(lo+hi)//2
        if calc(g,mid,x) <= y: hi=mid
        else: lo=mid+1
    e=lo
    if fbits(calc(g,e,x)) != fbits(y): return ()
    out=[]
    while e <= 65535 and fbits(calc(g,e,x)) == fbits(y):
        out.append(e); e += 1
    return tuple(out)


def main():
    x22={}; x23={}; capture={}
    for req in (5,6):
        for kind,dst in [('x22',x22),('x23',x23)]:
            name,expected=CAPTURE[req][kind]; p=CARVE/name
            need(p.exists() and p.stat().st_size==0xDF0, f'missing {name}')
            actual=sha_file(p); need(actual==expected, f'{name}: SHA mismatch')
            dst[req]=struct.unpack('<884f',p.read_bytes()[:0xDD0])
            capture[f'request{req}_{kind}']={'file':name,'bytes':0xDF0,'sha256':actual}

    # Direct channels only: plane0 and plane3. These do not participate in the
    # Windows-specific two-green averaging, so each point is independently invertible.
    direct_indices=list(range(221))+list(range(663,884))
    rows=[]
    for p in sorted(DRIVERDUMP.rglob('*.bin')):
        try: g=parse_golden(p)
        except RuntimeError: raise
        except Exception: continue
        if not g: continue
        vals=g.pop('values')
        passed=unique=multi=0; inferred=[]; fails=[]
        for idx in direct_indices:
            c5=set(candidates(vals[idx],x22[5][idx],x23[5][idx]))
            c6=set(candidates(vals[idx],x22[6][idx],x23[6][idx]))
            both=sorted(c5 & c6)
            if both:
                passed += 1; unique += (len(both)==1); multi += (len(both)>1); inferred.extend(both)
            elif len(fails)<8:
                fails.append(idx)
        row={**g,'direct_constraints':442,'passed':passed,'unique':unique,'multi':multi,
             'failed':442-passed,'first_failed_indices':fails,
             'inferred_eeprom_min':min(inferred) if inferred else None,
             'inferred_eeprom_max':max(inferred) if inferred else None}
        rows.append(row)

    need(len(rows)==EXPECTED_CANDIDATES, f'installed golden candidate count {len(rows)} != {EXPECTED_CANDIDATES}')
    winners=[r for r in rows if r['passed']==442]
    need(len(winners)==1, f'golden winner ambiguity: {[r["file"] for r in winners]}')
    w=winners[0]
    need(w['file']==WINNER_FILE and w['tuning_sha256']==WINNER_TUNING_SHA, 'winner tuning identity drift')
    need(w['golden_region_sid']==WINNER_REGION_SID and w['golden_region_sha256']==WINNER_GOLDEN_SHA, 'winner golden region identity drift')
    need((w['unique'],w['multi'],w['failed'])==(442,0,0), 'winner constraints not all unique')
    need((w['inferred_eeprom_min'],w['inferred_eeprom_max'])==(181,1023), 'winner EEPROM range drift')
    losers=[r for r in rows if r is not w]
    need(all(r['failed']>0 for r in losers), 'a losing golden unexpectedly has zero failures')
    fr=[r for r in rows if r['file']==FRONT_FILE and r['tuning_sha256']==FRONT_TUNING_SHA]
    need(len(fr)==1, 'front IMX681 golden candidate missing/ambiguous')
    need(fr[0]['golden_region_sha256']==FRONT_GOLDEN_SHA, 'front golden SHA drift')
    need((fr[0]['passed'],fr[0]['failed'])==(9,433), 'front golden discriminator counts drift')

    oracle={
      'schema':'sp11-e003h-lsc-live-golden-authority-v1','accepted':True,'offline_only':True,
      'classification':'CLOSED BYTE-EXACT LIVE GOLDEN AUTHORITY: recovered front LSCTRIGSRC x22/x23 direct-channel equations uniquely select the OV13858 rear/default lscgolden41 region among every installed Surface/QTI tuning candidate.',
      'capture_authority':capture,
      'math':{
        'direct_planes':[0,3],'direct_mesh_points':442,'requests':[5,6],
        'equation':'x23 = float32(float32(golden / float32(EEPROM_u16)) * x22)',
        'eeprom_domain':[1,65535],
        'why_greens_excluded':'Windows independently calibrates the two green planes and then averages them; red/blue remain direct one-equation planes and avoid that ambiguity.',
        'acceptance':'For each direct mesh point, the same integer EEPROM_u16 must reproduce both request5 and request6 x23 bit-for-bit.'},
      'installed_candidates':rows,
      'winner':w,
      'nominal_front_candidate':fr[0],
      'impact':{
        'live_front_lsc_golden':'com.surface.tuned.rfc_ov13858.bin / lscgolden41 region 0x2ae / '+WINNER_GOLDEN_SHA,
        'nominal_front_golden_rejected':'com.surface.tuned.ffc_imx681.bin golden satisfies only 9/442 direct constraints and fails 433.',
        'physical_sensor_identity':'This is a tuning/golden provenance result only. The verified physical stream remains IMX681 by independent sensor programming and 4048x3152 -> 3840x2160 geometry.',
        'calibration_algorithm_boundary':'The existing calibration proof remains valid for ratio direction, green averaging, and placement, but its nominal-front golden object is not the live golden authority for LSCTRIGSRC.'},
      'safety':{'linux_camera_runtime':False,'linux_request6_executed':False,'runtime_authorized':False}
    }
    OUT.write_text(json.dumps(oracle,indent=2)+'\n')
    print('PASS live LSC golden authority: rear/default OV13858 golden uniquely satisfies 442/442 direct constraints')
    print('winner',w['golden_region_sha256'],'sid',hex(w['golden_region_sid']),'EEPROM',w['inferred_eeprom_min'],w['inferred_eeprom_max'])
    print('front nominal',fr[0]['passed'],'pass',fr[0]['failed'],'fail')
    print('oracle',OUT,sha_file(OUT))

if __name__=='__main__': main()
