#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json, hashlib, struct
from unicorn import UC_HOOK_MEM_READ
from unicorn.arm64_const import UC_ARM64_REG_PC, UC_ARM64_REG_X8

ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
P=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/private/E011EH-explore')
CM_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/source-private.py'
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
EG_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011eg-source-qualified-crt-startup-order/RESULT.json'

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
CM=load('eh_cm',CM_PATH); EC=load('eh_ec',EC_PATH)

def evidence():
 stream=json.loads((P/'STREAM-REFS-SAFE.json').read_text())
 life=json.loads((P/'LIFETIME-REFS-SAFE.json').read_text())
 destr=json.loads((P/'DESTRUCTOR-TABLE-SAFE.json').read_text())
 attach=json.loads((P/'ATTACH-DETACH-REFS-SAFE.json').read_text())
 eg=json.loads(EG_RESULT.read_text())
 # Only constructor/fallback-constructor and destructor write 16A2A58.
 writes=[x for x in stream['references'] if int(x['target_RVA'],16)==0x16a2a58 and x['reference_type']=='WRITE']
 assert {(int(x['source_RVA'],16),int(x['containing_function_RVA'],16)) for x in writes}=={
   (0xcb32b0,0xcb3260),(0xcb32d8,0xcb3260),(0xcb3400,0xcb33a0)}
 # Runtime camera site is a read, not a writer.
 assert any(int(x['source_RVA'],16)==0xcc6120 and x['reference_type']=='READ' for x in stream['references'])
 # Constructor/destructor are paired in attach/destructor tables.
 assert any(int(x['target'],16)==0xcb3260 and int(x['source'],16)==0xf7f448 for x in life['refs'])
 assert any(int(x['target'],16)==0xcb33a0 and int(x['source'],16)==0xf7f4b0 for x in life['refs'])
 cell=next(x for x in destr['cells'] if int(x['cell_RVA'],16)==0xf7f4b0)
 assert int(cell['value_RVA'],16)==0xcb33a0
 # Source detach chain to finalizer root.
 pairs={(int(x['source'],16),int(x['target'],16)) for x in attach['refs'] if x['type']=='UNCONDITIONAL_CALL'}
 for edge in [(0xca2b7c,0xca3178),(0xca31a4,0xcaf390),(0xcaf39c,0xcaf188),(0xcaf240,0xcaf040),(0xcaf068,0xcaf088)]:
  assert edge in pairs
 assert eg['startup_lowIO_precedes_stream_initializer_conditional_on_reach'] and eg['startup_lowIO_to_stream_state_handoff_qualified']
 return {
   'stream_pointer_writer_sites':[hex(x) for x in (0xcb32b0,0xcb32d8,0xcb3400)],
   'constructor_RVA':'0xcb3260','destructor_RVA':'0xcb33a0',
   'constructor_table_cell_RVA':'0xf7f448','destructor_table_cell_RVA':'0xf7f4b0',
   'camera_read_RVA':'0xcc6120',
   'inherited_E011EG_result_sha256':hashlib.sha256(EG_RESULT.read_bytes()).hexdigest(),
   'inherited_E011CM_source_sha256':hashlib.sha256(CM_PATH.read_bytes()).hexdigest(),
   'inherited_E011EC_source_sha256':hashlib.sha256(EC_PATH.read_bytes()).hexdigest(),
 }

def validate_read(site,addr,width,value,expected,lifetime_ok):
 assert lifetime_ok
 assert site==0xcc6120 and addr==0x16a2a58 and width==8 and value==expected and expected!=0

def one_case(bias,preset,imports):
 b=CM.Bootstrap(bias,preset,imports); brow=b.run()
 ptr=b.allocs[1][0]; cap=b.capacity
 vector=bytes(b.u.mem_read(ptr,8*cap))
 assert struct.unpack_from('<QQQ',vector,0)==tuple(b.stream(k) for k in range(3))
 c=EC.Case(0,0,0x80000000,0,0,0,0xa5); c.run()
 assert c.u.reg_read(UC_ARM64_REG_PC)==c.n.base+0xcc6120
 # Join only source-qualified startup-owned stream state.
 c.u.mem_map(b.own,b.extent)
 c.u.mem_write(b.own,b'\xa5'*b.extent)
 c.u.mem_write(ptr,vector)
 c.u.mem_write(c.n.base+0x16a2a50,struct.pack('<I',cap))
 c.u.mem_write(c.n.base+0x16a2a58,struct.pack('<Q',ptr))
 for k in range(3):
  c.u.mem_write(c.n.base+0x1607060+88*k+24,struct.pack('<I',0xfffffffe))
 before_img=bytes(c.u.mem_read(c.n.base,CM.CF.p.OPTIONAL_HEADER.SizeOfImage))
 before_vec=bytes(c.u.mem_read(ptr,8*cap))
 reads=[]
 def hook(u,access,at,size,value,user):
  if at==c.n.base+0x16a2a58:
   site=u.reg_read(UC_ARM64_REG_PC)-c.n.base
   val=int.from_bytes(bytes(u.mem_read(at,size)),'little')
   validate_read(site,at-c.n.base,size,val,ptr,True);reads.append((site,size,val))
 h=c.u.hook_add(UC_HOOK_MEM_READ,hook)
 try:
  c.u.emu_start(c.n.base+0xcc6120,c.n.base+0xcc6124,count=1)
 finally:c.u.hook_del(h)
 assert reads==[(0xcc6120,8,ptr)]
 assert c.u.reg_read(UC_ARM64_REG_X8)==ptr and c.u.reg_read(UC_ARM64_REG_PC)==c.n.base+0xcc6124
 assert bytes(c.u.mem_read(c.n.base,CM.CF.p.OPTIONAL_HEADER.SizeOfImage))==before_img
 assert bytes(c.u.mem_read(ptr,8*cap))==before_vec
 # Negative contracts reject before mutation.
 bad=[(0xcc6124,0x16a2a58,8,ptr,ptr,True),(0xcc6120,0x16a2a60,8,ptr,ptr,True),
      (0xcc6120,0x16a2a58,4,ptr,ptr,True),(0xcc6120,0x16a2a58,8,ptr+8,ptr,True),
      (0xcc6120,0x16a2a58,8,ptr,ptr,False)]
 rejected=0
 for x in bad:
  try:validate_read(*x)
  except AssertionError:rejected+=1
  else:raise AssertionError('altered dependency accepted')
 assert rejected==5
 return {'bias':bias,'preset':preset,'capacity':cap,'vector_pointer_owned_offset':ptr-b.own,
   'vector_bytes':8*cap,'camera_read_value_owned_offset':ptr-b.own,'negative_contract_rejections':rejected,
   'camera_memory_unchanged_by_read':True,'vector_unchanged_by_read':True,
   'first_three_entries_RVAs':[hex(b.stream(k)-b.n.base) for k in range(3)]}

def main():
 ev=evidence(); facts,imports=CM.authority(); rows=[]
 for preset in [0,128]:
  for bias in [0,1,40,1230]:
   row=one_case(bias,preset,imports);rows.append(row);print(json.dumps(row),flush=True)
 result={'status':'PASS_SOURCE_QUALIFIED_STREAM_LIFETIME_CAMERA_READ','experiment':'E011EH',
   'cases':rows,'case_count':len(rows),'source_lifetime_evidence':ev,
   'startup_stream_state_to_camera_read_join_qualified':True,
   'camera_stream_pointer_read_qualified':True,
   'camera_next_source_RVA':'0xcc6124','camera_next_dependency_RVA':'0x16a2a50',
   'destructor_not_executed_in_joined_runtime_interval':True,
   'lifetime_scope':'successful process attach through runtime camera call before process detach, under inherited loader lifecycle and owned OS contracts',
   'native_loader_internals_qualified':False,'native_allocator_implementation_qualified':False,
   'native_mutex_bytes_or_concurrency_qualified':False,'file_open_or_contents_qualified':False,
   'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'new_kernel_build':False}
 assert len(rows)==8 and sum(x['negative_contract_rejections'] for x in rows)==40
 (P/'SOURCE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2),flush=True)
if __name__=='__main__':main()
