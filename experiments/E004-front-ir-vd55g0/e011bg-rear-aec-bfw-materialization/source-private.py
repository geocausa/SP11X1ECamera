#!/usr/bin/env python3
"""E011BG: original BFW sibling and ROI readers, owned same-SP11 fixtures only."""
from pathlib import Path
import importlib.util,hashlib,json,random,struct,pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BF=load("bg_histogram",EX/"e011bf-rear-aec-histogram-materialization/source-private.py")
def source(blob):
 h,sy,wire,info=BF.source(blob);root=sy[info["root_symbol_id"]]
 count,sid=struct.unpack_from("<II",blob,root["data_abs_offset"]+40)
 assert count==1 and sid in sy,"unsupported BFW root shape"
 bfw=sy[sid]
 assert (bfw["type"],bfw["version_major"],bfw["version_minor"],bfw["mode_id"],bfw["mode_symbol_id"],bfw["data_bytes"])==("bfwStatsConfig",0,0,0,0xffffffff,140),"unsupported BFW symbol"
 raw=blob[bfw["data_abs_offset"]:bfw["data_abs_offset"]+140]
 ccount,csid=struct.unpack_from("<II",raw,12);dcount,dsid=struct.unpack_from("<II",raw,132)
 assert ccount==5 and dcount==1 and csid in sy and dsid in sy,"unsupported BFW nested shape"
 for child_id,kind,nbytes in [(csid,"BFWROICombo",160),(dsid,"data",4)]:
  child=sy[child_id]
  assert (child["type"],child["version_major"],child["version_minor"],child["mode_id"],child["mode_symbol_id"],child["data_bytes"])==(kind,0,0,0,0xffffffff,nbytes),"unsupported BFW nested symbol"
 return h,sy,wire,dict(info,bfw_symbol_id=sid,bfw_count=count,combo_symbol_id=csid,combo_count=ccount,bfw_data_symbol_id=dsid)
def facts():
 b=BF.BE.BASE.DLL.read_bytes();assert hashlib.sha256(b).hexdigest()==BF.BE.BASE.SHA
 pe=pefile.PE(data=b);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 def ins(r):return next(c.disasm(pe.get_data(r,4),r))
 i=ins(0x124a14);assert i.mnemonic=="str" and c.reg_name(i.operands[-1].mem.base)=="x20" and i.operands[-1].mem.disp==88
 for r in [0x124d80,0x124d90]:
  i=ins(r);assert i.mnemonic=="bl" and i.operands[0].imm==0xe8cc8
 i=ins(0x125414);assert i.mnemonic=="bl" and i.operands[0].imm==0xea758
 spans=[(0x124ea0,32,44,12),(0x124f0c,44,56,20),(0x124f6c,64,76,20)]
 for r,wire,out,nbytes in spans:
  i=ins(r);assert i.mnemonic=="bl" and i.operands[0].imm==0xf5d480
 return {"BFW_array_payload_store_rva":"0x124A14","BFW_array_payload_offset":88,"original_ROI_reader_rva":"0xE8CC8","ROI_reader_calls":["0x124D80","0x124D90"],"original_nested_data_reader_rva":"0xEA758","nested_data_reader_call_rva":"0x125414","original_scalar_memcpy_spans":[{"callsite":hex(r),"wire_offset":wire,"runtime_offset":out,"bytes":nbytes} for r,wire,out,nbytes in spans]}
class BFW(BF.Histogram):
 def __init__(self,blob):
  _,_,_,info=source(blob);super().__init__(blob);self.info=info
  self.combo_entries=[];self.combo_returns=[];self.bfw_data_entries=[];self.bfw_data_returns=[];self.bfw_pending=None
  def hook(u,pc,size,_):
   r=pc-self.n.base
   if r in (0xe8cc8,0xea758):
    call=u.reg_read(UC_ARM64_REG_LR)-self.n.base-4
    if call in (0x124d80,0x124d90,0x125414):
     rr=u.reg_read(UC_ARM64_REG_X0);sid=(rr-self.table)//224
     assert rr==self.table+sid*224 and sid in self.sy
     cursor=int.from_bytes(u.mem_read(rr+216,8),"little")
     bfw_reader=self.table+self.info["bfw_symbol_id"]*224
     parent_cursor=int.from_bytes(u.mem_read(bfw_reader+216,8),"little")
     if call==0x125414:self.bfw_data_entries.append((sid,cursor,u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2),parent_cursor))
     else:self.combo_entries.append((call,sid,cursor,u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2),parent_cursor))
     self.bfw_pending=(u.reg_read(UC_ARM64_REG_LR),call,sid,rr)
   if self.bfw_pending and pc==self.bfw_pending[0]:
    _,call,sid,rr=self.bfw_pending
    result=(sid,u.reg_read(UC_ARM64_REG_X0),int.from_bytes(u.mem_read(rr+216,8),"little"))
    if call==0x125414:self.bfw_data_returns.append(result)
    else:self.combo_returns.append((call,)+result)
    self.bfw_pending=None
  self.n.u.hook_add(UC_HOOK_CODE,hook)
 def run(self,bias):
  self.combo_entries.clear();self.combo_returns.clear();self.bfw_data_entries.clear();self.bfw_data_returns.clear();self.bfw_pending=None
  histogram=super().run(bias,full_parent=True)
  u=self.n.u;base_index=8+2*self.info["hist_count"];array,combo,data=[self.allocs[base_index+j][0] for j in range(3)]
  assert len(self.allocs)==base_index+3
  assert [n for _,n in self.allocs[base_index:]]==[160,160,4]
  assert u.reg_read(UC_ARM64_REG_X0)==self.allocs[0][0],"original parent did not return its module"
  payload=self.allocs[0][0]+288
  assert int.from_bytes(u.mem_read(payload+80,4),"little")==1
  assert bytes(u.mem_read(payload+84,4))==bytes(4)
  assert int.from_bytes(u.mem_read(payload+88,8),"little")==array
  bfw=self.sy[self.info["bfw_symbol_id"]];wire=self.data[bfw["data_offset"]:bfw["data_offset"]+140];out=bytes(u.mem_read(array,160))
  assert out[:16]==wire[:16] and out[32:144]==wire[20:132] and out[144:148]==wire[132:136]
  assert out[16:24]==bytes(8) and out[148:152]==bytes(4)
  assert int.from_bytes(out[24:32],"little")==combo and int.from_bytes(out[152:160],"little")==data
  combo_source=self.sy[self.info["combo_symbol_id"]];data_source=self.sy[self.info["bfw_data_symbol_id"]]
  assert bytes(u.mem_read(combo,160))==self.data[combo_source["data_offset"]:combo_source["data_offset"]+160]
  assert bytes(u.mem_read(data,4))==self.data[data_source["data_offset"]:data_source["data_offset"]+4]
  expected_entries=[];expected_returns=[]
  for i in range(10):
   call=0x124d80 if i%2==0 else 0x124d90
   expected_entries.append((call,self.info["combo_symbol_id"],16*i,combo+16*i,1,20))
   expected_returns.append((call,self.info["combo_symbol_id"],1,16*(i+1)))
  assert self.combo_entries==expected_entries and self.combo_returns==expected_returns
  assert self.bfw_data_entries==[(self.info["bfw_data_symbol_id"],0,1,1,140)]
  assert self.bfw_data_returns==[(self.info["bfw_data_symbol_id"],data,4)]
  scalar_copy_index=16+7*self.info["hist_count"]
  for j,(wireoff,outoff,nbytes) in enumerate([(32,44,12),(44,56,20),(64,76,20)]):
   assert self.copies[scalar_copy_index+j]==(array+outoff,self.datas+bfw["data_offset"]+wireoff,nbytes)
  assert self.copies[scalar_copy_index+3]==(data,self.datas+data_source["data_offset"],4)
  assert len(self.copies)==scalar_copy_index+4
  for sid,nbytes in [(self.info["bfw_symbol_id"],140),(self.info["combo_symbol_id"],160),(self.info["bfw_data_symbol_id"],4)]:
   assert int.from_bytes(u.mem_read(self.table+sid*224+216,8),"little")==nbytes
  return dict(histogram,BFW_records=1,ROI_combinations=5,ROI_reader_returns=10,nested_data_arrays=1)
def negatives(blob):
 _,sy,_,info=source(blob);root=sy[info["root_symbol_id"]];bfw=sy[info["bfw_symbol_id"]];cases=[]
 fields=[(root["data_abs_offset"]+40,0),(root["data_abs_offset"]+40,2),(root["data_abs_offset"]+44,0),(root["data_abs_offset"]+44,max(sy)+1),(root["data_abs_offset"]+44,info["hist_symbol_id"])]
 for off,val in [(12,0),(12,4),(12,6),(16,0),(16,max(sy)+1),(16,info["bfw_data_symbol_id"]),(132,0),(132,2),(136,0),(136,max(sy)+1),(136,info["combo_symbol_id"])]:
  fields.append((bfw["data_abs_offset"]+off,val))
 for sid in [info["bfw_symbol_id"],info["combo_symbol_id"],info["bfw_data_symbol_id"]]:
  r=sy[sid];fields.extend([(r["record_offset"]+36,1),(r["record_offset"]+40,1),(r["record_offset"]+44,6),(r["record_offset"]+52,r["data_bytes"]-1),(r["record_offset"]+52,r["data_bytes"]+1)])
 for off,val in fields:
  b=bytearray(blob);struct.pack_into("<I",b,off,val);cases.append(bytes(b))
 for sid in [info["bfw_symbol_id"],info["combo_symbol_id"],info["bfw_data_symbol_id"]]:
  r=sy[sid];b=bytearray(blob);b[r["record_offset"]+4:r["record_offset"]+36]=b"unsupported".ljust(32,b"\0");cases.append(bytes(b))
 for b in cases:
  try:source(b)
  except (AssertionError,ValueError,KeyError):pass
  else:raise AssertionError("unsupported BFW source accepted")
 return len(cases)
def main():
 anchors=facts();roots=[];audit=[]
 for name,sha in BF.BE.BASE.AV.FILES:
  blob=(BF.BE.BASE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  _,sy,_,info=source(blob);roots.append(blob)
  audit.append({"path":name,"sha256":sha,"BFW_symbol_id":info["bfw_symbol_id"],"ROI_combo_symbol_id":info["combo_symbol_id"],"nested_data_symbol_id":info["bfw_data_symbol_id"],"BFW_count":1,"ROI_combo_count":5})
 _,sy,_,info=source(roots[-1]);bfw=sy[info["bfw_symbol_id"]];combo=sy[info["combo_symbol_id"]];data=sy[info["bfw_data_symbol_id"]];rng=random.Random(0xe011b6)
 cases=list(roots)
 for _ in range(8):
  b=bytearray(roots[-1]);off=bfw["data_abs_offset"];b[off:off+12]=rng.randbytes(12);b[off+20:off+132]=rng.randbytes(112);cases.append(bytes(b))
 for _ in range(8):
  b=bytearray(roots[-1]);off=combo["data_abs_offset"];b[off:off+160]=rng.randbytes(160);cases.append(bytes(b))
 for _ in range(8):
  b=bytearray(roots[-1]);off=data["data_abs_offset"];b[off:off+4]=rng.randbytes(4);cases.append(bytes(b))
 totals={"original_full_parent_returns":0,"BFW_records_verified":0,"ROI_combinations_verified":0,"original_ROI_reader_returns":0,"nested_BFW_data_arrays_verified":0,"inherited_histogram_entries_verified":0}
 for blob in cases:
  f=BFW(blob)
  for bias in [0,0x200,0x1230,0x8010]:
   r=f.run(bias);totals["original_full_parent_returns"]+=1;totals["BFW_records_verified"]+=r["BFW_records"];totals["ROI_combinations_verified"]+=r["ROI_combinations"];totals["original_ROI_reader_returns"]+=r["ROI_reader_returns"];totals["nested_BFW_data_arrays_verified"]+=r["nested_data_arrays"];totals["inherited_histogram_entries_verified"]+=r["histogram_entries"]
 rejected=negatives(roots[-1])
 result={"experiment":"E011BG","status":"PASS_BOUNDED_ORIGINAL_BFW_ROI_SIBLING_MATERIALIZATION","base_commit":"68ef6146734b7056acaacd85d7fd194ffb66b0b6","original_DLL_sha256":BF.BE.BASE.SHA,"source_files":audit,"anchors":anchors,"unique_source_cases":len(cases),"owned_BFW_scalar_variants":8,"owned_ROI_variants":8,"owned_nested_data_variants":8,"fixture_placements":4,**totals,"source_scope_rejections":rejected,"BFW_wire_bytes":140,"BFW_runtime_bytes":160,"BFW_root_count_wire_offset":40,"BFW_root_symbol_wire_offset":44,"BFW_runtime_count_payload_offset":80,"BFW_runtime_array_pointer_payload_offset":88,"ROI_combo_count_wire_offset":12,"ROI_combo_symbol_wire_offset":16,"ROI_runtime_pointer_offset":24,"ROI_combo_wire_and_runtime_stride":32,"ROI_component_reader_bytes":16,"BFW_data_count_wire_offset":132,"BFW_data_symbol_wire_offset":136,"BFW_data_runtime_pointer_offset":152,"original_ROI_and_data_readers_stubbed":False,"new_helper_stubs_added":False,"source_data_reader_non_cursor_bytes_and_allocation_canaries_preserved":True,"revision_four_grid_histogram_checks_retained":True,"bounded_BFW_materialization_closed_for_typed_one_record_five_ROI_scope":True,"remaining_stubs":["0x11D0","0x11F0","0x6F4AC0","0x6F45D8","0xF5DF00","0xCAE740","0xF5E600"],"whole_parent_metadata_materialization_closed":False,"whole_profile_materialization_closed":False,"exact_opened_tuning_filename_closed":False,"whole_loader_alignment_policy_closed":False,"cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,"complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,"Linux_optical_parity_closed":False,"captured_scalars_used_as_producer_inputs":False,"private_original_bytes_exported":False,"production_C_changed":False,"new_kernel_build_performed":False,"runtime_actions_performed":False,"observer_armed":False,"new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"BFW-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="source_files"},indent=2))
if __name__=="__main__":main()
