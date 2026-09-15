#!/usr/bin/env python3
"""Read existing package/build evidence; write derived metadata in this experiment only."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys
D=Path(__file__).resolve().parent; R=D.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data): (D/'evidence'/name).write_text(json.dumps(data,indent=2)+'\n')
known=json.loads((D/'evidence/KNOWN-DIRTY.json').read_text())
for p,h in known.items(): assert sha(R/p)==h, 'pre-existing edit changed: '+p
subprocess.run(['git','merge-base','--is-ancestor','fe3d73ce218cd10846170bd4a35a1959e67d7a3a','HEAD'],cwd=R,check=True)
ex=Path('/tmp/sp11-e004eq-official-package-20260915/SurfaceUpdate')
old=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump')
msi=Path('/home/geoca/Downloads/SurfacePro11_ARM_Win11_26100_26.041.12746.0.msi')
assert sha(msi)=='0c3966bb6f3d39673ae3d2bbd785967d36db149e6c0fa8baa5fa3abd4ccd249b'
rows=[]
for folder,archived in [('qccamsecureisp','qccamsecureisp8380.inf_arm64_e0daad652520462e'),('qcnspmcdmextcdsp8380','qcnspmcdm_ext_cdsp8380.inf_arm64_4a8c3ebe3aad408a')]:
    for f in sorted((ex/folder).rglob('*')):
        if not f.is_file(): continue
        rel=f.relative_to(ex/folder); o=old/archived/rel
        rows.append({'package':folder,'path':str(rel),'bytes':f.stat().st_size,'msi_sha256':sha(f),'archive_sha256':sha(o),'equal':sha(f)==sha(o)})
assert len(rows)==29 and all(r['equal'] for r in rows)
fw=Path('/lib/firmware/qcom/x1e80100/microsoft/Denali/qccdsp8380.mbn')
assert sha(fw)=='4a67a03367f2eff2f8a0e867ca25d2bf2fcd5aee3e41e2c9f436c804e257c789'
save('PACKAGE-COMPARISON.json',{'cached_msi':str(msi),'msi_sha256':sha(msi),'msi_bytes':msi.stat().st_size,'fresh_network_download':False,'msi_authenticode_verified_this_turn':False,'official_listing':'https://www.microsoft.com/en-us/download/details.aspx?id=106119','extract_only_no_install':True,'file_count':len(rows),'different_count':sum(not r['equal'] for r in rows),'golden_cdsp_sha256':sha(fw),'files':rows})
build=Path('/tmp/sp11-e004eq-worker-audit-20260915')
obj=build/'sp11-camera-protected-worker.hexagon-v73.o'; b=obj.read_bytes()
assert sha(obj)=='4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48'
assert b[:6]==b'\x7fELF\x01\x01'
et,machine=struct.unpack_from('<HH',b,16); phnum=struct.unpack_from('<H',b,44)[0]
assert et==1 and machine==164 and phnum==0
imports=[l.split()[-1] for l in (build/'UNRESOLVED.txt').read_text().splitlines()]
prov=json.loads((R/'src/sp11-camera-protected-worker/PROVENANCE.json').read_text())
assert sorted(imports)==sorted(prov['hexagon']['unresolved_symbols'])
full=(build/'FULLFRAME-DIFFERENTIAL.txt').read_text()
assert 'GAUSSIAN_WIRE_FULL_LUMA_DIFF=0' in full and 'GAUSSIAN_WIRE_NEUTRAL_TAIL_DIFF=0' in full
save('WORKER-AUDIT.json',{'object_sha256':sha(obj),'elf_class':'ELF32','elf_type':'ET_REL','machine':machine,'program_headers':phnum,'runtime_imports':imports,'wire_vectors':(build/'WIRE-VECTORS.txt').read_text().strip(),'proxy_contract':(build/'PROXY-CONTRACT.txt').read_text().strip(),'fullframe_differential':full.strip(),'final_loadable_module_proven':False,'signed':False,'admitted':False,'runtime_executed':False,'canonical_source_file_sha256':{str(p.relative_to(R)):sha(p) for p in sorted((R/'src/sp11-camera-protected-worker').glob('*')) if p.is_file()}})
print('E004eq evidence: 29/29 package files unchanged; worker offline exact; ET_REL and 10 runtime imports; no production admission.')
