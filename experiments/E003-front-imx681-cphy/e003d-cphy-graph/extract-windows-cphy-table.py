#!/usr/bin/env python3
from pathlib import Path
import argparse,csv,hashlib,struct
EXPECTED='033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407'
FILE_OFF=0xf650
COUNT=121
REC=12
p=argparse.ArgumentParser(); p.add_argument('--driver',required=True); p.add_argument('--oracle',required=True); p.add_argument('--out',required=True); a=p.parse_args()
data=Path(a.driver).read_bytes(); h=hashlib.sha256(data).hexdigest()
if h != EXPECTED: raise SystemExit(f'driver SHA mismatch {h}')
rows=[]
for i in range(COUNT):
    pos=FILE_OFF+i*REC
    off,val,aux=struct.unpack_from('<III',data,pos)
    rows.append((i,pos,off,val,aux))
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
with (out/'windows-cphy-121.csv').open('w',newline='') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(['index','file_offset','reg_offset','value','aux'])
    for i,pos,off,val,aux in rows: w.writerow([i,f'0x{pos:x}',f'0x{off:04x}',f'0x{val:02x}',aux])
# last-write-wins map and compare against two KD snapshots
final={}
for i,pos,off,val,aux in rows: final[off]=(val,i,aux)
kd={}
with Path(a.oracle).open() as f:
    for r in csv.DictReader(f): kd[int(r['offset'],16)]=(int(r['live1'],16),int(r['live2'],16),int(r['post'],16))
match=[]; mismatch=[]; missing=[]
for off,(val,i,aux) in sorted(final.items()):
    if off not in kd: missing.append((off,val,i)); continue
    l1,l2,post=kd[off]
    item=(off,val,l1,l2,i,aux)
    (match if l1==val and l2==val else mismatch).append(item)
with (out/'windows-cphy-validation.txt').open('w') as f:
    f.write(f'driver_sha256={h}\nfile_offset=0x{FILE_OFF:x}\nrecord_count={COUNT}\nunique_offsets={len(final)}\n')
    f.write(f'last_write_matches_both_live={len(match)}\nlast_write_mismatches={len(mismatch)}\nmissing_in_kd_dump={len(missing)}\n')
    for x in mismatch: f.write('MISMATCH off=0x%04x table=0x%02x live1=0x%08x live2=0x%08x index=%d aux=%d\n'%x)
    for x in missing: f.write('MISSING off=0x%04x table=0x%02x index=%d\n'%x)
print((out/'windows-cphy-validation.txt').read_text(),end='')
