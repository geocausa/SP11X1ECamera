#!/usr/bin/env python3
"""Bounded original TLS initialization and reverse-byte search. Private bytes never leave SP11."""
from pathlib import Path
import importlib.util,hashlib,json,struct,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011cy-original-outer-return/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='030a3a9b27c2806a2a7e7d7bee7bfd9faae5ec2e0ad7b8f34ae40391aaa43091'
s=importlib.util.spec_from_file_location('cz_cy',P);CY=importlib.util.module_from_spec(s);s.loader.exec_module(CY)
CF=CY.CF;N=CY.CW.CV.CO.N;CV=CY.CW.CV
A=OUT/'RUNTIME-HELPER-AUTHORITY-V2-SAFE.json'
assert hashlib.sha256(A.read_bytes()).hexdigest()=='0181252c5c120eef9a083a6bd10b2ce1cc9583983b4fd947edae1f0913206812'
AUTH=json.loads(A.read_text())
class Proof:
 def __init__(self):
  self.n=N.Native();self.u=self.n.u;self.teb_region=0x96000000;self.array_region=0x96100000;self.block_region=0x96200000
  for at in (self.teb_region,self.array_region,self.block_region):self.u.mem_map(at,65536)
  self.regions=[('image',self.n.base,(CF.p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095),('heap',self.n.heap,0x30000),('stack',self.n.stack,65536),
   ('TEB',self.teb_region,65536),('TLS_array',self.array_region,65536),('TLS_block',self.block_region,65536)]
  self.instructions={}
  for row in AUTH['source_authority']:
   r=int(row['RVA'],16);z=row['bytes'];raw=CF.p.get_data(r,z);assert hashlib.sha256(raw).hexdigest()==row['sha256']
   for i in CF.c.disasm(raw,self.n.base+r):self.instructions[i.address]=i
  assert CF.p.DIRECTORY_ENTRY_TLS.struct.AddressOfIndex-self.n.base==0x16a3740
  assert CF.p.get_qword_at_rva(0xf7f438)==0
  i=next(CF.c.disasm(CF.p.get_data(0xce7d90,4),0xce7d90));assert i.mnemonic=='ldr' and CF.c.reg_name(i.operands[0].reg).startswith('q')
  for row in AUTH['actual_original_caller_sites']:
   site=int(row['return_RVA'],16)-4;i=next(CF.c.disasm(CF.p.get_data(site,4),site));assert i.mnemonic=='bl' and i.operands[0].imm==0xce7c98
  self.negative_count=0;self.rows=[]
  self.u.hook_add(UC_HOOK_CODE,self.code);self.u.hook_add(UC_HOOK_MEM_WRITE,self.memory);self.u.hook_add(UC_HOOK_MEM_READ,self.read)
 def snapshot(self):return {name:bytes(self.u.mem_read(at,z)) for name,at,z in self.regions}
 def contract(self,site,args):
  assert site==self.entry and args==self.request
  if site==0xcfe600:
   teb,array,block,slot,flag=args
   assert slot in [0,1,37,63] and flag in [0,1]
   assert self.u.reg_read(UC_ARM64_REG_X18)==teb and self.q(teb+88)==array and self.q(array+8*slot)==block
   assert int.from_bytes(self.u.mem_read(self.n.base+0x16a3740,4),'little')==slot and self.u.mem_read(block+20,1)==bytes([flag])
   assert self.q(self.n.base+0xf7f438)==0
  else:
   src,value,z=args;assert value in [0,92,97,122] and z==len(self.raw) and self.u.mem_read(src,z)==self.raw and self.raw[-1:]==bytes(1)
 def q(self,at):return int.from_bytes(self.u.mem_read(at,8),'little')
 def negatives(self):
  requests=[(self.entry+4,self.request),(self.entry,self.request+[0])]
  for k in range(len(self.request)):
   bad=self.request.copy();bad[k]+=1;requests.append((self.entry,bad))
  before=self.snapshot();regs={r:self.u.reg_read(r) for r in [UC_ARM64_REG_SP,UC_ARM64_REG_X0,UC_ARM64_REG_X18,UC_ARM64_REG_LR]}
  for req in requests:
   try:self.contract(*req)
   except AssertionError:pass
   else:raise AssertionError('invalid helper scope request admitted')
  assert before==self.snapshot() and all(self.u.reg_read(r)==v for r,v in regs.items())
  self.negative_count+=len(requests)
 def reset(self):
  u=self.u;n=self.n
  for name,at,z in self.regions:
   if name!='image':u.mem_write(at,bytes([0xa5])*z)
  for k in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0x111000+k)
  for k in range(8,16):u.reg_write(globals()['UC_ARM64_REG_D'+str(k)],0x222000+k)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  self.incoming={k:u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(19,30)}
  self.incoming_float={k:u.reg_read(globals()['UC_ARM64_REG_D'+str(k)]) for k in range(8,16)}
  self.pending={};self.visits=0;self.writes=0;self.seen=collections.Counter()
 def run(self):
  self.contract(self.entry,self.request);self.negatives();self.before=self.snapshot()
  self.models={'stack':bytearray(self.before['stack'])}
  if self.entry==0xcfe600:
   self.models['TLS_block']=bytearray(self.before['TLS_block']);self.models['TLS_block'][self.block-self.block_region+20]=1
  self.u.emu_start(self.n.base+self.entry,self.n.end,count=20000)
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.end and not self.pending
  after=self.snapshot();assert all(after[k]==self.models.get(k,v) for k,v in self.before.items()),'entire independent helper memory model'
  assert self.u.reg_read(UC_ARM64_REG_SP)==self.n.stack+0xf000
  assert all(self.u.reg_read(globals()['UC_ARM64_REG_X'+str(k)])==v for k,v in self.incoming.items())
  assert all(self.u.reg_read(globals()['UC_ARM64_REG_D'+str(k)])==v for k,v in self.incoming_float.items())
  if self.entry==0xcfe600:
   assert self.visits==(34 if self.flag==0 else 24) and self.writes==(6 if self.flag==0 else 5)
   assert self.u.reg_read(UC_ARM64_REG_W0)==0
   assert self.seen[0xcfe5a4]==(1 if self.flag==0 else 0)
  else:
   nul=self.raw.index(0);index=(self.raw[:nul].rfind(bytes([self.value])) if self.value else nul)
   expected=self.src+index if index>=0 else 0;assert self.u.reg_read(UC_ARM64_REG_X0)==expected
   assert self.writes==0
  self.rows.append({'entry_RVA':hex(self.entry),'instructions':self.visits,'store_chunks':self.writes,'whole_memory_and_caller_checks':True,
   'case_kind':self.kind,'scope':self.scope})
 def code(self,u,pc,z,user):
  assert not self.pending and pc in self.instructions,('unqualified helper instruction',hex(pc-self.n.base))
  r=pc-self.n.base;assert bytes(u.mem_read(pc,4))==CF.p.get_data(r,4);i=self.instructions[pc];self.visits+=1;self.seen[r]+=1
  if i.mnemonic.startswith(('str','stp','stur')):
   op=next(o for o in i.operands if o.type==3);assert not op.mem.index
   at=CV.reg(u,CF.c.reg_name(op.mem.base))+op.mem.disp;name=CF.c.reg_name(i.operands[0].reg)
   width=1 if i.mnemonic.endswith('b') else 2 if i.mnemonic.endswith('h') else 16 if name.startswith('q') else 8 if name.startswith(('x','d')) or name in ('fp','lr') else 4
   operands=i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
   for k,o in enumerate(operands):
    address=at+k*width;value=CV.reg(u,CF.c.reg_name(o.reg))&((1<<(8*width))-1)
    if self.n.stack<=address and address+width<=self.n.stack+65536:
     off=address-self.n.stack;self.models['stack'][off:off+width]=value.to_bytes(width,'little')
    else:assert self.entry==0xcfe600 and (r,address,width,value)==(0xcfe5a4,self.block+20,1,1) and self.flag==0
    for j in range(0,width,8):z=min(width-j,8);self.pending[address+j,z]=(value>>(8*j))&((1<<(8*z))-1)
  self.pending_pc=pc
 def memory(self,u,access,at,z,value,user):
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,z) in self.pending
  assert value&((1<<(8*z))-1)==self.pending.pop((at,z));self.writes+=1
 def read(self,u,access,at,z,value,user):
  if self.n.stack<=at and at+z<=self.n.stack+65536:return
  if self.entry==0xcfe600:
   assert (at,z) in {(self.n.base+0x16a3740,4),(self.teb+88,8),(self.array+8*self.slot,8),(self.block+20,1),(self.n.base+0xf7f438,8)},'unqualified TLS read'
  else:
   # Original reverse search reads containing aligned 16-byte SIMD words; canaries remain immutable.
   assert self.read_start<=at and at+z<=self.read_end,('search outside exact aligned-word source window',hex(u.reg_read(UC_ARM64_REG_PC)-self.n.base),at-self.src,z,len(self.raw))
 def TLS_case(self,bias,slot,flag):
  self.reset();self.entry=0xcfe600;self.kind='empty_initializer_table_TLS_wrapper';self.slot=slot;self.flag=flag
  self.teb=self.teb_region+bias;self.array=self.array_region+bias;self.block=self.block_region+bias
  u=self.u;u.mem_write(self.teb+88,struct.pack('<Q',self.array));u.mem_write(self.array+8*slot,struct.pack('<Q',self.block));u.mem_write(self.block+20,bytes([flag]))
  u.mem_write(self.n.base+0x16a3740,struct.pack('<I',slot));u.reg_write(UC_ARM64_REG_X18,self.teb)
  self.request=[self.teb,self.array,self.block,slot,flag];self.scope={'bias':bias,'owned_loader_index':slot,'initial_flag20':flag}
  self.run()
 def search_case(self,raw,value,bias,image_RVA=None):
  self.reset();self.entry=0xce7c98;self.raw=raw;self.value=value
  self.src=self.n.base+image_RVA if image_RVA is not None else self.n.heap+0x1000+bias
  self.kind='actual_private_image_literal' if image_RVA is not None else 'owned_ASCII_literal'
  if image_RVA is None:self.u.mem_write(self.src,raw)
  else:assert bytes(self.u.mem_read(self.src,len(raw)))==raw
  self.u.reg_write(UC_ARM64_REG_X0,self.src);self.u.reg_write(UC_ARM64_REG_W1,value)
  self.read_start=self.src&~15;self.read_end=(self.src+len(raw)+15)&~15
  assert any(a<=self.read_start and self.read_end<=a+z for name,a,z in self.regions if name in ('heap','image'))
  self.request=[self.src,value,len(raw)];self.scope={'input_RVA':hex(image_RVA) if image_RVA is not None else None,'owned_bias':bias if image_RVA is None else None,'source_bytes_with_NUL':len(raw),'search_byte':value,'aligned_source_read_bytes':self.read_end-self.read_start}
  self.run()
def main():
 proof=Proof()
 for bias in [0,16,128,512]:
  for slot in [0,1,37,63]:
   for flag in [0,1]:proof.TLS_case(bias,slot,flag)
 print(json.dumps({'TLS_wrapper_cases':32,'original_TLS_instructions':sum(x['instructions'] for x in proof.rows),'original_TLS_store_chunks':sum(x['store_chunks'] for x in proof.rows),'status':'PASS_BOUNDED_EMPTY_INITIALIZER_TABLE_TLS_WRAPPER'}),flush=True)
 for raw in [bytes(1),b'camera-stack\0',b'a\\dir\\tail\0',b'aaaa\0']:
  for bias in [0,1,15,40]:
   for value in [0,92,97,122]:proof.search_case(raw,value,bias)
 for row in AUTH['private_source_literals']:
  r=int(row['input_RVA'],16);raw=CF.p.get_data(r,row['bytes_with_NUL'])
  assert hashlib.sha256(raw).hexdigest()==row['sha256'] and raw[-1:]==bytes(1)
  assert raw[:-1].rfind(bytes([92]))==row['last_backslash_offset']
  proof.search_case(raw,92,0,r)
 tls=[x for x in proof.rows if x['entry_RVA']=='0xcfe600'];search=[x for x in proof.rows if x['entry_RVA']=='0xce7c98']
 result={'experiment':'E011CZ','status':'PASS_BOUNDED_ORIGINAL_TLS_WRAPPER_AND_REVERSE_BYTE_SEARCH','base_commit':'a844f42bab052ccaf0dad7b86f6fd352d28c5550',
  'TLS_wrapper_cases':len(tls),'owned_reverse_search_cases':64,'actual_private_image_literal_cases':8,'original_TLS_instructions':sum(x['instructions'] for x in tls),
  'original_reverse_search_instructions':sum(x['instructions'] for x in search),'exact_TLS_store_chunks':sum(x['store_chunks'] for x in tls),
  'invalid_scope_requests_rejected':proof.negative_count,'whole_image_heap_stack_TEB_array_block_and_actual_caller_checks':True,
  'original_PE_TLS_index_address_matches_source_global':True,'TLS_index_and_layout_are_owned_loader_ABI_fixtures':True,
  'original_flag20_transition_under_null_file_initializer_table':True,'original_reverse_search_returns_last_match_or_NUL_or_NULL':True,'source_containing_aligned_16byte_SIMD_words_and_canaries_checked':True,
  'misleading_inherited_owned_diagnostic_context_label_corrected':True,
  'actual_original_caller_sites':AUTH['actual_original_caller_sites'],'private_source_literal_authority':AUTH['private_source_literals'],
  'source_authority':AUTH['source_authority'],'cases':proof.rows,
  'original_CFE600_qualified_for_empty_file_initializer_table_only':True,'full_original_CFE600_runtime_bootstrap_qualified':False,
  'original_helpers_integrated_in_actual_camera_harness':False,'full_Windows_loader_TLS_Default_locale_concurrency_qualified':False,
  'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'production_C_or_kernel_changed':False,'next_experiment':'E011DA'}
 assert len(proof.rows)==104 and len(tls)==32 and len(search)==72 and result['original_TLS_instructions']==928 and result['exact_TLS_store_chunks']==176
 (OUT/'RUNTIME-HELPERS-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}),flush=True)
if __name__=='__main__':main()
