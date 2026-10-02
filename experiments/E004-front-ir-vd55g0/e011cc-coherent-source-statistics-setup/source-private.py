#!/usr/bin/env python3
"""Private original selected cache fragments and coherent statistics setup, scalar output only."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections
from types import SimpleNamespace
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');EX=ROOT/'experiments/E004-front-ir-vd55g0'
OUT=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
CA=load('cc_ca',EX/'e011ca-rear-source-statistics-collection/source-private.py')
BP=load('cc_bp',EX/'e011bp-rear-aec-output-ownership/source-private.py')
CA.NUMERIC.update({0x39fb40:{0x3a8730},0x39fb60:{0x3a8730},
 0x3a021c:{0x3a5870,0x3a62f0,0x3a71d0},0x3a0660:{0x39d8c0,0x39da00}})
CA.LOG.update({0x39fd04,0x39fee0,0x3a00bc,0x3a0304,0x3a03ac,0x3a0448,0x3a04d0,0x3a0554})
RANGES=[(0x39faf8,3168),(0x39d8c0,132),(0x39da00,132),(0x3a5870,124),(0x3a62f0,60),
 (0x3a71d0,4),(0x3a41d8,224),(0xce7b98,140),(0x3a0760,96),(0x388630,316)]
class Setup(CA.Collection):
 def __init__(self,p,c):
  super().__init__(p,c);self.following=False
  for r,z in RANGES:
   for i in c.disasm(p.get_data(r,z),r):self.instructions[i.address]=i
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if r in CA.INIT:
   at=u.reg_read(UC_ARM64_REG_X1);assert any(ptr<=at<ptr+z for ptr,z in self.source_ranges)
   self.events['Init_'+hex(r)]+=1;return
  if r==0x39faf8:self.following=True;self.events['following_setup_entries']+=1
  if r==0x3a0760:self.events['element_initializer_entries']+=1
  if r==0xce7bf0:self.events['element_initializer_returns']+=1
  if r in [0x39d8c0,0x39da00]:self.events['configuration_setter_entries']+=1
  if r==0x3a0668:self.events['configuration_setter_returns']+=1
  if r==0xce7be8:
   assert u.reg_read(UC_ARM64_REG_X15)==self.n.base+0x3a0760
   self.events['element_initializer_dispatches']+=1;u.reg_write(UC_ARM64_REG_PC,pc+4);return
  if self.following and r==0xcae740:
   count=u.reg_read(UC_ARM64_REG_X0);assert count in [648,504,488,160,152]
   at=self.cursor+32;self.cursor=at+((count+31)&~31)+32;assert self.cursor<self.n.heap+0x68000
   u.mem_write(at-32,b'\xa5'*32);u.mem_write(at+count,b'\xa5'*32)
   self.allocs.append((at,count));self.freed[at]=False;self.ret(at);return
  i=self.instructions.get(r)
  if i and i.mnemonic=='blr' and self.c.reg_name(i.operands[0].reg)=='x17':
   assert r in CA.NUMERIC or r in CA.LOG,'unqualified checked source RVA '+hex(r)
  return super().hook(u,pc,size,user)
def authority():
 p,c,old=CA.authority()
 for call,store,slot,name in [(0x3ca574,0x3ca588,0xf18,b'aecxcorestatsconfig'),(0x3ca984,0x3ca998,0xfe8,b'aecxhwstatsconfig')]:
  d={}
  for i in c.disasm(p.get_data(call-20,20),call-20):
   o=i.operands
   if i.mnemonic=='adrp':d[c.reg_name(o[0].reg)]=o[1].imm
   elif i.mnemonic=='add' and o[-1].type==2 and c.reg_name(o[1].reg) in d:d[c.reg_name(o[0].reg)]=d[c.reg_name(o[1].reg)]+o[-1].imm
  assert p.get_data(d['x1'],128).split(b'\0',1)[0]==name
  i=next(c.disasm(p.get_data(call,4),call));assert i.mnemonic=='bl' and i.operands[0].imm==0x6f39f8
  i=next(c.disasm(p.get_data(store,4),store));assert i.mnemonic=='str' and i.operands[-1].mem.disp==slot and c.reg_name(i.operands[-1].mem.base)=='x22'
 # Source constructor call uses the bank subobject, primary allocation+8.
 regs={'x0':0}
 for i in c.disasm(p.get_data(0x3a8d8c,0x3a9774-0x3a8d8c),0x3a8d8c):
  o=i.operands
  if i.mnemonic=='mov' and o[1].type==1:
   src=c.reg_name(o[1].reg);dst=c.reg_name(o[0].reg)
   if src in regs:regs[dst]=regs[src]
   else:regs.pop(dst,None)
  elif i.mnemonic=='add' and o[-1].type==2:
   src=c.reg_name(o[1].reg);dst=c.reg_name(o[0].reg)
   if src in regs:regs[dst]=regs[src]+o[-1].imm
   else:regs.pop(dst,None)
  elif i.mnemonic=='ldr':regs.pop(c.reg_name(o[0].reg),None)
  elif i.mnemonic=='adrp':regs.pop(c.reg_name(o[0].reg),None)
  if i.address==0x3a9770:assert i.mnemonic=='bl' and o[0].imm==0x3c8380 and regs.get('x0')==8
  if i.mnemonic=='bl':regs.pop('x0',None)
 facts={'original_DLL_sha256':old['original_DLL_sha256'],'source_setup_receiver_primary_offset':8,
 'configuration_name':'aecxcorestatsconfig','configuration_cache_primary_slot':0xf20,'configuration_cache_secondary_slot':0xf18,
 'hardware_name':'aecxhwstatsconfig','hardware_cache_primary_slot':0xff0,'hardware_cache_secondary_slot':0xfe8,
 'previous_E011CB_meterweight_primary_slot_corrected_to':0xf28,'bank_accessor_receiver_addend':0xef8,
 'full_following_setup_RVA':'0x39faf8','secondary_object_bytes_by_family':[648,504,488],
 'configuration_object_bytes':152,'element_initializer_RVA':'0x3a0760','embedded_rings_per_object':9,
 'source_ranges':[{'RVA':hex(r),'bytes':z,'sha256':hashlib.sha256(p.get_data(r,z)).hexdigest()} for r,z in RANGES+[(0x3ca564,40),(0x3ca974,40)]]}
 return p,c,facts
def verify_configuration(f,module):
 u=f.n.u;sizes=dict(f.allocs);sid=f.readi(module+56);row=f.sy[sid]
 assert row['type']=='aecxcorestatsconfig' and sizes[module]==352
 def wire(si):r=f.sy[si];return f.blob[r['data_abs_offset']:r['data_abs_offset']+r['data_bytes']]
 w=wire(sid);assert len(w)==32
 rev=struct.unpack_from('<I',w,16)[0];data=struct.unpack_from('<I',w,28)[0]
 assert f.sy[rev]['type']=='revision' and f.sy[data]['type']=='coreStatsConfig'
 payload=module+288;rp=f.readq(payload+32);ap=f.readq(payload+56);count=f.readi(payload+44)
 expected=bytearray(64);struct.pack_into('<I',expected,0,sid);expected[8:20]=w[:12]
 struct.pack_into('<Q',expected,32,rp);expected[40:48]=w[20:28];struct.pack_into('<I',expected,48,sid);struct.pack_into('<Q',expected,56,ap)
 assert bytes(u.mem_read(payload,64))==expected
 rw=wire(rev);assert sizes[rp]==len(rw) and bytes(u.mem_read(rp,len(rw)))==rw
 sw=wire(data);assert len(sw)==64*count and sizes[ap]==72*count
 names=0;extensions=0
 for k in range(count):
  q=sw[k*64:(k+1)*64];at=ap+k*72;expected=bytearray(b'\xa5'*72);expected[:40]=q[:40]
  namebytes,nsid,ecount,esid=struct.unpack_from('<4I',q,40)
  text=wire(nsid);assert f.sy[nsid]['type']=='outChannelName' and namebytes==len(text)
  np=f.readq(at+40);assert sizes[np]==namebytes and bytes(u.mem_read(np,namebytes))==text
  ew=wire(esid);assert f.sy[esid]['type']=='extensionParam' and len(ew)==16*ecount
  ep=f.readq(at+56);assert sizes[ep]==24*ecount
  for j in range(ecount):
   e=ew[j*16:(j+1)*16];ea=ep+j*24;enbytes,ensid,dcount,dsid=struct.unpack('<4I',e)
   en=wire(ensid);dw=wire(dsid);assert f.sy[ensid]['type']=='Name' and f.sy[dsid]['type']=='data'
   assert len(en)==enbytes and len(dw)==4*dcount
   enp=f.readq(ea);dp=f.readq(ea+16)
   assert sizes[enp]==len(en) and bytes(u.mem_read(enp,len(en)))==en
   assert sizes[dp]==len(dw) and bytes(u.mem_read(dp,len(dw)))==dw
   ee=bytearray(b'\xa5'*24);struct.pack_into('<Q',ee,0,enp);ee[8:12]=e[8:12];struct.pack_into('<I',ee,12,esid);struct.pack_into('<Q',ee,16,dp)
   assert bytes(u.mem_read(ea,24))==ee;extensions+=1
  struct.pack_into('<Q',expected,40,np);expected[48:52]=q[48:52];struct.pack_into('<I',expected,52,data);struct.pack_into('<Q',expected,56,ep);expected[64:72]=q[56:64]
  assert bytes(u.mem_read(at,72))==expected;names+=1
 return {'source_configuration_records':count,'exact_configuration_records':count,'exact_channel_name_allocations':names,'exact_extension_records':extensions,'source_record_bytes':64,'native_record_bytes':72}
def prepare(blob,pin):
 f=BP.Production(blob,0)
 needed=((len(f.sy)*320+len(f.records)*224+2*len(blob)+0x800000+4095)//4096)*4096
 assert needed<0x8000000
 if needed>f.arena_size:
  extra=needed-f.arena_size;f.n.u.mem_map(f.arena+f.arena_size,extra);f.n.u.mem_write(f.arena+f.arena_size,b'\xa5'*extra);f.arena_size=needed
 f.run_full();n=f.n;u=n.u
 core=0x90000000;u.mem_map(core,0x10000);u.mem_write(core,b'\xa5'*0x10000);u.mem_write(core,bytes(5152))
 module=None
 for start,stop,slot,name in [(0x3ca564,0x3ca58c,0xf20,b'aecxcorestatsconfig'),(0x3ca974,0x3ca99c,0xff0,b'aecxhwstatsconfig')]:
  for k in range(8):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
  u.reg_write(UC_ARM64_REG_X20,core+168);u.reg_write(UC_ARM64_REG_X21,f.manager);u.reg_write(UC_ARM64_REG_X22,core+8)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xd000);u.reg_write(UC_ARM64_REG_LR,n.end);f.phase='cache_fragment'
  before=bytes(u.mem_read(core,5152));u.emu_start(n.base+start,n.base+stop,count=1000000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+stop
  payload=f.readq(core+slot);selected=payload-288
  assert selected in dict(f.allocs) and f.name_bytes(selected+16,32)==name
  expected=bytearray(before);struct.pack_into('<Q',expected,slot,payload);assert bytes(u.mem_read(core,5152))==expected
  assert bytes(u.mem_read(core+5152,0x10000-5152))==b'\xa5'*(0x10000-5152)
  if slot==0xf20:module=selected
  else:assert selected==f.actual_module
 shape=verify_configuration(f,module);f.bounds()
 return f,core,shape
def run(blob,pin,p,c):
 f,core,shape=prepare(blob,pin);u=f.n.u
 source=SimpleNamespace(n=f.n,allocs=[(f.actual_module,dict(f.allocs)[f.actual_module]),
 (f.readq(f.actual_module+288+56),dict(f.allocs)[f.readq(f.actual_module+288+56)])])
 s=Setup(p,c);v=s.u;v.mem_map(f.arena,f.arena_size);source_arena=bytes(u.mem_read(f.arena,f.arena_size));v.mem_write(f.arena,source_arena)
 s.source_ranges=[(ptr,z) for ptr,z in f.allocs if ptr not in f.released];cases=[]
 for bias in [0,1,40,1230]:
  s.following=False;s.build(source,bias);v.mem_write(s.core+0xf20,struct.pack('<Q',f.readq(core+0xf20)))
  before=bytes(v.mem_read(s.n.heap,0x100000));alloc_before=len(s.allocs)
  v.reg_write(UC_ARM64_REG_X0,s.manager);v.reg_write(UC_ARM64_REG_SP,s.n.stack+0xf000);v.reg_write(UC_ARM64_REG_LR,s.n.end)
  v.emu_start(s.n.base+0x39faf8,s.n.end,count=1000000);assert v.reg_read(UC_ARM64_REG_PC)==s.n.end
  ev=dict(s.events);new=s.allocs[alloc_before:];objects=[ptr for ptr,z in new if z in [648,504,488]];records=[ptr for ptr,z in new if z==152]
  assert len(objects)==s.expected_count
  assert [z for ptr,z in new if z in [648,504,488]]==[648]*s.source_counts[0]+[504]*s.source_counts[1]+[488]*s.source_counts[2]
  assert ev['element_initializer_entries']==ev['element_initializer_returns']==ev['element_initializer_dispatches']==9*s.expected_count
  assert ev['configuration_setter_entries']==ev['configuration_setter_returns']==len(records)>0
  secondary=struct.unpack('<Q',v.mem_read(s.manager+0x620,8))[0]
  assert struct.unpack('<3I',v.mem_read(s.manager+0x628,12))==(0,s.expected_count,20)
  ring=struct.pack('<'+'Q'*len(objects),*objects)+bytes(160-8*len(objects));assert bytes(v.mem_read(secondary,160))==ring
  counts=[];members=[]
  for obj,table in zip(objects,[0x1338180]*s.source_counts[0]+[0x13382c0]*s.source_counts[1]+[0x1338280]*s.source_counts[2]):
   assert struct.unpack('<Q',v.mem_read(obj,8))[0]==s.n.base+table
   rp=struct.unpack('<Q',v.mem_read(obj+8,8))[0];head,used,cap=struct.unpack('<3I',v.mem_read(obj+16,12));assert head==0 and cap==20 and used<=cap
   assert dict(new)[rp]==160;got=list(struct.unpack('<'+'Q'*used,v.mem_read(rp,used*8)));assert all(ptr in records for ptr in got)
   assert bytes(v.mem_read(rp+used*8,160-used*8))==bytes(160-used*8);members+=got;counts.append(used)
  assert len(set(members))==len(members)==len(records) and set(members)==set(records)
  after=bytes(v.mem_read(s.n.heap,0x100000));expected=bytearray(before)
  for ptr,z in new:
   off=ptr-s.n.heap;expected[off:off+z]=after[off:off+z];expected[off-32:off]=b'\xa5'*32;expected[off+z:off+z+32]=b'\xa5'*32
  off=secondary-s.n.heap;expected[off:off+160]=ring
  struct.pack_into('<I',expected,s.manager+0x62c-s.n.heap,s.expected_count)
  struct.pack_into('<I',expected,s.manager+0x638-s.n.heap,f.readi(f.readq(core+0xf20)))
  struct.pack_into('<I',expected,s.manager+0x63c-s.n.heap,f.readi(f.readq(core+0xff0)))
  assert after==expected,'unexpected complete following-setup heap delta'
  assert bytes(v.mem_read(f.arena,f.arena_size))==source_arena;s.guards();s.following=False
  for context in [0,1,0xffffffff]:
   for selector in [12,20]:s.query(selector,context)
  assert bytes(v.mem_read(f.arena,f.arena_size))==source_arena
  cases.append({'placement_bias':bias,'primary_and_secondary_objects':s.expected_count,'configuration_records':len(records),
   'per_object_configuration_counts':counts,'element_initializer_returns':9*s.expected_count,'full_query_returns':6,
   'complete_heap_delta_and_input_immutability':True})
 return {'source_sha256':pin,'selected_cache_fragments':2,'full_loader_dispatches':f.dispatches,'source_configuration':shape,'cases':cases}
def main():
 p,c,facts=authority();rows=[]
 for name,pin in CA.BB.AZ.AV.FILES:
  blob=(CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  row=run(blob,pin,p,c);rows.append(row);print(json.dumps({'source_sha256':pin,'cases':len(row['cases']),'attached_records':sum(v['configuration_records'] for v in row['cases'])}),flush=True)
 result={'status':'PASS_BOUNDED_COHERENT_ORIGINAL_STATS_SETUP','authority':facts,'sources':rows,
 'full_following_setup_returns':sum(len(r['cases']) for r in rows),'attached_configuration_records':sum(v['configuration_records'] for r in rows for v in r['cases']),
 'element_initializer_returns':sum(v['element_initializer_returns'] for r in rows for v in r['cases']),
 'full_query_returns':sum(v['full_query_returns'] for r in rows for v in r['cases']),
 'whole_core_outer_constructor_qualified':False,'live_default_mode_descriptor_qualified':False,'runtime_or_image_test':False,
 'originals_private_on_SP11':True,'numeric_callbacks_unmodified':True}
 (OUT/'SETUP-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','full_following_setup_returns','attached_configuration_records','element_initializer_returns','full_query_returns']}),flush=True)
if __name__=='__main__':main()
