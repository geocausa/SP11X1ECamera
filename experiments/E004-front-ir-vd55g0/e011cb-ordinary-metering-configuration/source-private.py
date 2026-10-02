#!/usr/bin/env python3
"""Same-SP11 original ordinary metering configuration reader; emit scalar evidence only."""
from pathlib import Path
import importlib.util,struct,json,hashlib
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');EX=ROOT/'experiments/E004-front-ir-vd55g0'
OUT=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
CA=load('cb_ca',EX/'e011ca-rear-source-statistics-collection/source-private.py')
BP=load('cb_bp',EX/'e011bp-rear-aec-output-ownership/source-private.py')
KEY='aecxdb1dmeterweight'
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def authority():
 p,c,old=CA.authority();d={}
 for i in c.disasm(p.get_data(0x3ca588,20),0x3ca588):
  o=i.operands
  if i.mnemonic=='adrp':d[c.reg_name(o[0].reg)]=o[1].imm
  elif i.mnemonic=='add' and o[-1].type==2 and c.reg_name(o[1].reg) in d:d[c.reg_name(o[0].reg)]=d[c.reg_name(o[1].reg)]+o[-1].imm
 assert p.get_data(d['x1'],128).split(b'\0',1)[0].decode()==KEY
 return p,c,{'original_DLL_sha256':old['original_DLL_sha256'],'cache_producer_RVA':'0x3ca4a0',
 'configuration_GetTag_call_RVA':'0x3ca59c','configuration_store_RVA':'0x3ca5b0',
 'core_configuration_slot_offset':0xf20,'parent_reader_RVA':'0x1c0a80','parent_reader_bytes':1660,
 'parent_reader_sha256':hashlib.sha256(p.get_data(0x1c0a80,1660)).hexdigest(),
 'module_vtable_RVA':'0x1335e38','module_allocation_bytes':368,'payload_offset':288,
 'wire_data_record_bytes':4112,'native_data_record_bytes':4120,'numeric_bytes_per_record':4100,
 'following_setup_RVA':'0x39faf8','following_setup_bytes':3168}
def model(blob,sy):
 ids=[i for i,r in sy.items() if r['type']==KEY];assert len(ids)==1
 root=ids[0]
 def wire(si,kind):
  r=sy[si];assert r['type']==kind
  return blob[r['data_abs_offset']:r['data_abs_offset']+r['data_bytes']]
 w=wire(root,KEY);assert len(w)==40
 rev=u32(w,16);pri=u32(w,28);data=u32(w,36)
 rw=wire(rev,'revision');pw=wire(pri,'priorityMap');dw=wire(data,'data')
 assert u32(w,12)==u32(w,20)==len(rw)
 assert len(pw)==u32(w,24)*16 and len(dw)==u32(w,32)*4112
 priorities=[];descriptions=[];consumed={root,rev,pri,data}
 for k in range(u32(w,24)):
  q=pw[k*16:(k+1)*16];ct=u32(q,4);cw=wire(ct,'context')
  assert len(cw)==u32(q,0)*4
  priorities.append((q,ct,cw));consumed.add(ct)
 for k in range(u32(w,32)):
  q=dw[k*4112:(k+1)*4112];ds=u32(q,8);sw=wire(ds,'description')
  assert u32(q,4)==len(sw)
  descriptions.append((q,ds,sw));consumed.add(ds)
 return root,w,rw,priorities,descriptions,consumed,rev,pri,data
def run(blob,pin):
 f=BP.Production(blob,0)
 # Capacity for the original symbol table, source profile nodes, factory and guarded alignment.
 needed=((len(f.sy)*288+len(f.records)*224+0x800000+4095)//4096)*4096
 if needed>f.arena_size:
  extra=needed-f.arena_size;f.n.u.mem_map(f.arena+f.arena_size,extra)
  f.n.u.mem_write(f.arena+f.arena_size,b'\xa5'*extra);f.arena_size=needed
 print(json.dumps({'symbol_readers':len(f.sy),'arena_capacity_bytes':f.arena_size}),flush=True)
 f.build();n=f.n;u=n.u
 root,w,rw,priorities,descriptions,consumed,rev,pri,data=model(blob,f.sy)
 rr=f.table+root*224
 f.phase='lookup';f.invoke_low(0xd2a20,[f.manager,rr+12]);proto=u.reg_read(UC_ARM64_REG_X0)
 assert proto in dict(f.allocs) and f.name_bytes(proto+16,32).decode()==KEY
 assert f.readq(f.readq(proto)+8)==n.base+0x1c0a80
 assert f.readq(proto+60)==f.readq(rr+52)==10
 cases=[];retained=[]
 for bias in [0,1,40,1230]:
  # New independent output placement; preserve original live builder/context.
  for si in consumed:u.mem_write(f.table+si*224+216,bytes(8))
  f.next=((f.next+4095)//4096)*4096+bias
  before=len(f.allocs);arena_before=bytes(u.mem_read(f.arena,f.arena_size))
  heap_before=bytes(u.mem_read(n.heap,0x30000));context_before=bytes(u.mem_read(f.context,48))
  f.phase='selected_parent';f.invoke_low(0x1c0a80,[proto,rr,1]);module=u.reg_read(UC_ARM64_REG_X0)
  new=f.allocs[before:];sizes=dict(new)
  assert module in sizes and sizes[module]==368
  assert f.readq(module)==n.base+0x1335e38
  assert f.name_bytes(module+16,32).decode()==KEY
  assert f.name_bytes(f.readq(module+8),32).decode()==KEY
  assert f.readi(module+56)==root and f.readq(module+60)==f.readq(rr+52)
  assert f.readi(module+68)==f.readi(rr+68) and f.readq(module+72)==f.readq(rr+60)
  assert f.name_bytes(module+80,127)==f.name_bytes(rr+72,127)
  assert f.name_bytes(module+208,64)==f.name_bytes(f.readq(f.context),64)
  assert f.readq(module+280)==0
  payload=module+288;rp=f.readq(payload+32);pp=f.readq(payload+56);dp=f.readq(payload+72)
  expected=bytearray(80)
  struct.pack_into('<I',expected,0,root);expected[8:20]=w[:12]
  struct.pack_into('<Q',expected,32,rp);expected[40:48]=w[20:28]
  struct.pack_into('<I',expected,48,root);struct.pack_into('<Q',expected,56,pp)
  expected[64:68]=w[32:36];struct.pack_into('<I',expected,68,root);struct.pack_into('<Q',expected,72,dp)
  assert bytes(u.mem_read(payload,80))==expected
  assert sizes[rp]==len(rw) and bytes(u.mem_read(rp,len(rw)))==rw
  assert sizes[pp]==len(priorities)*24 and sizes[dp]==len(descriptions)*4120
  for k,(q,ct,cw) in enumerate(priorities):
   at=pp+k*24;cp=f.readq(at+8);expected=bytearray(24)
   expected[:4]=q[:4];struct.pack_into('<I',expected,4,pri);struct.pack_into('<Q',expected,8,cp);expected[16:24]=q[8:16]
   assert bytes(u.mem_read(at,24))==expected
   assert sizes[cp]==len(cw) and bytes(u.mem_read(cp,len(cw)))==cw
  for k,(q,ds,sw) in enumerate(descriptions):
   at=dp+k*4120;sp=f.readq(at+8);expected=bytearray(4120)
   expected[:4]=q[:4];struct.pack_into('<Q',expected,8,sp);expected[16:4116]=q[12:]
   assert bytes(u.mem_read(at,4120))==expected
   assert sizes[sp]==len(sw) and bytes(u.mem_read(sp,len(sw)))==sw
  assert bytes(u.mem_read(f.map,f.map_size))==f.file_before
  assert bytes(u.mem_read(n.heap,0x30000))==heap_before and bytes(u.mem_read(f.context,48))==context_before
  # Complete arena delta: only new owned allocations and exact consumed cursors.
  after=bytes(u.mem_read(f.arena,f.arena_size));expected=bytearray(arena_before)
  for at,z in new:expected[at-f.arena:at-f.arena+z]=after[at-f.arena:at-f.arena+z]
  for si,row in f.sy.items():
   cur=f.readq(f.table+si*224+216)
   assert cur==(row['data_bytes'] if si in consumed else 0)
   at=f.table+si*224+216-f.arena;struct.pack_into('<Q',expected,at,cur)
  assert after==expected
  for ptr,span in retained:assert bytes(u.mem_read(ptr,len(span)))==span
  for ptr,z in new:
   assert bytes(u.mem_read(ptr-32,32))==bytes(u.mem_read(ptr+z,32))==b'\xa5'*32
   retained.append((ptr,bytes(u.mem_read(ptr,z))))
  cases.append({'placement_bias':bias,'parent_return_pass':True,'new_allocation_count':len(new),
   'revision_bytes':len(rw),'priority_records':len(priorities),'data_records':len(descriptions),
   'exact_numeric_bytes':4100*len(descriptions),'exact_consumed_readers':len(consumed)})
 f.bounds()
 # Deliberately invalid owned source models reject before native execution.
 negatives=0
 for off in [16,28,36]:
  bad=bytearray(blob);struct.pack_into('<I',bad,f.sy[root]['data_abs_offset']+off,0xffffffff)
  try:model(bad,f.sy)
  except (AssertionError,KeyError):negatives+=1
  else:raise AssertionError('bad child accepted')
 return {'source_sha256':pin,'original_symbol_reader_returns':f.returns,'factory_registrations':f.factory_registrations,
 'parent_cases':cases,'owned_preflight_rejections':negatives,'source_and_preexisting_arena_preserved':True}
def main():
 p,c,facts=authority();rows=[]
 for name,pin in CA.BB.AZ.AV.FILES:
  blob=(CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  row=run(blob,pin);rows.append(row)
  print(json.dumps({'source_sha256':pin,'parent_returns':len(row['parent_cases']),'data_records':sum(r['data_records'] for r in row['parent_cases'])}),flush=True)
 result={'status':'PASS_BOUNDED_ORDINARY_METERING_CONFIGURATION_PARENT','authority':facts,'sources':rows,
 'original_parent_returns':sum(len(r['parent_cases']) for r in rows),
 'exact_data_records':sum(c['data_records'] for r in rows for c in r['parent_cases']),
 'exact_numeric_bytes':sum(c['exact_numeric_bytes'] for r in rows for c in r['parent_cases']),
 'owned_preflight_rejections':sum(r['owned_preflight_rejections'] for r in rows),
 'following_setup_qualified':False,'whole_core_cache_population_qualified':False,'runtime_or_image_test':False,
 'originals_private_on_SP11':True,'new_semantic_parser_stubs':0}
 (OUT/'CONFIGURATION-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','original_parent_returns','exact_data_records','exact_numeric_bytes','owned_preflight_rejections']}),flush=True)
if __name__=='__main__':main()
