#!/usr/bin/env python3
import argparse, hashlib, json, re, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
DRIVER_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
DRIVER_BYTES=376560
LOG_SHA='7a182c14f2f797fef4143177e2c9e17dae885766a6c2a4781564a3f5250a974c'
LOG_BYTES=26760

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()
def pe_text(data):
 pe=struct.unpack_from('<I',data,0x3c)[0]; n=struct.unpack_from('<H',data,pe+6)[0]; opt=struct.unpack_from('<H',data,pe+20)[0]; sh=pe+24+opt
 for i in range(n):
  o=sh+i*40; name=data[o:o+8].rstrip(b'\0').decode('ascii',errors='ignore'); vs,va,rs,raw=struct.unpack_from('<IIII',data,o+8)
  if name=='.text': return va,raw,rs
 die('.text missing')
def verify_driver(path):
 data=path.read_bytes()
 if len(data)!=DRIVER_BYTES or sha(data)!=DRIVER_SHA: die('driver identity drift')
 va,raw,rs=pe_text(data); md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.skipdata=True
 ins={x.address-0x140000000:(x.mnemonic,x.op_str) for x in md.disasm(data[raw:raw+rs],0x140000000+va) if x.mnemonic!='.byte'}
 anchors={
  0x25ec0:('mov','x2, #0'),0x25ec4:('mov','w1, #2'),0x25ec8:('bl','#0x140028480'),
  0x25ecc:('ldr','x23, [sp, #0x60]'),0x25ee8:('ldr','w20, [sp, #0x68]'),
  0x25ef4:('mov','x3, x23'),0x25f20:('str','x23, [x21, #0xc80]'),
  0x25f34:('stp','w20, w9, [x8]'),0x25f78:('str','x23, [x8]'),0x25f80:('str','x9, [x8, #8]'),
  0x287e4:('ldr','w22, [sp, #0x20]'),0x287e8:('ldr','w20, [sp, #0x30]'),
  0x2896c:('cbz','x22, #0x140028980'),0x28970:('sxtw','x2, w23'),0x2897c:('bl','#0x14002dca0')}
 out={}
 for r,(mn,frag) in anchors.items():
  x=ins.get(r)
  if not x or x[0]!=mn or frag not in x[1]: die(f'anchor drift 0x{r:x}: {x}')
  out[f'0x{r:x}']=f'{x[0]} {x[1]}'
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--driver',type=Path,required=True); ap.add_argument('--log',type=Path,required=True); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
 anchors=verify_driver(a.driver); b=a.log.read_bytes()
 if len(b)!=LOG_BYTES or sha(b)!=LOG_SHA: die('live log identity drift')
 text=b.decode('utf-16')
 events=[]
 for line in text.splitlines():
  m=re.fullmatch(r'TAG userdata=([0-9a-f]+)',line,re.I)
  if m: events.append(('tag',int(m.group(1),16),None)); continue
  m=re.fullmatch(r'REQ id=([0-9a-f]{16}) sub=([0-9a-f]+)',line,re.I)
  if m: events.append(('req',int(m.group(1),16),int(m.group(2),16)))
 tags=[x[1] for x in events if x[0]=='tag']; req=[(x[1],x[2]) for x in events if x[0]=='req']
 if len(tags)!=246 or len(req)!=245: die(f'count drift tags={len(tags)} req={len(req)}')
 if tags!=list(range(1,0xf7)): die('tag sequence is not 1..0xf6')
 if req!=[(i,0) for i in range(2,0xf7)]: die('request/subrequest sequence drift')
 # Accepted runtime sequence: two address/batch slots are primed before the first
 # completion/Epoch0 consume. Hence TAG 1 and TAG 2 appear before REQ 2; after
 # that every next tag N immediately precedes the selector-2 returned REQ N.
 if events[:3] != [('tag',1,None),('tag',2,None),('req',2,0)]: die('prime prefix drift')
 for i in range(3,len(events),2):
  n=(i+1)//2+1
  if events[i] != ('tag',n,None) or events[i+1] != ('req',n,0): die(f'pair drift at {n}')
 out={
  'schema':'sp11-e003h-vfe1-genirq-request-tag-v1','accepted':True,
  'driver':{'bytes':DRIVER_BYTES,'sha256':DRIVER_SHA,'anchors':anchors},
  'live_log':{'bytes':len(b),'sha256':sha(b),'tag_count':len(tags),'request_count':len(req),'tag_range':'0x1..0xf6','request_range':'0x2..0xf6','subrequest_values':[0]},
  'startup_prime':{'unmatched_initial_tags':['0x1','0x2'],'interpretation':'consistent with already-proven two-bundle priming before first Epoch0 completion/consume; first consumed selector-2 request is 0x2'},
  'steady_correlation':{'pairs':245,'rule':'GEN_IRQ userdata == low32(requestId)','first':'0x2','last':'0xf6','all_match':True,'observed_subrequest':0},
  'kmd_handoff':{'epoch0_selector2_call_rva':'0x25ec8','selector2_request_load_rva':'0x25ecc','selector2_subrequest_load_rva':'0x25ee8','request_saved_for_epoch_state_rvas':['0x25f20','0x25f78'],'subrequest_saved_rvas':['0x25f34','0x25f80']},
  'linux_consequence':'For the accepted front stream, steady GEN_IRQ userdata is the requestId tag, not an independent CDM-local counter. Keep it caller/request-derived; do not freeze captured tag values.',
  'policy':'oracle only; no Linux RT-CDM submission or front runtime authorized'}
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if a.output:a.output.write_text(txt)
 else:print(txt,end='')
 print('PASS: 245 consumed front requests prove GEN_IRQ userdata == requestId; subRequest is zero in this stream')
if __name__=='__main__':main()
