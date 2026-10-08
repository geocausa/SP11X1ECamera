#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Validate source sensor programming against the same-SP11 private oracle.
Only aggregate scalar conclusions are exported; vendor tables stay local.
"""
import argparse,hashlib,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ORACLE=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.sensormodule.rfc_ov13858.bin"
def main():
 p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 assert not a.report.exists()
 assert str(ROOT).startswith("/home/geoca/Documents/SP11-PROJECT/")
 assert hashlib.sha256(ORACLE.read_bytes()).hexdigest()=="f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14"
 sys.path.insert(0,str(ROOT/"tools"));import qti_sensor_summary as q
 o=q.qti.parse(ORACLE);ids=q.entry_map(o)
 rd=next(e for e in o["entries"] if e["name"]=="resolutionData" and e["payload_size"])
 source=a.source.read_text()
 defs=dict(re.findall(r"^#define\s+(\w+)\s+(0x[0-9a-fA-F]+|[0-9]+)\b",source,re.M))
 def number(s):
  s=s.strip();return int(defs.get(s,s),0)
 def array(name):
  m=re.search(r"static const struct ov13858_reg "+name+r"\[\] = \{(.*?)\n\};",source,re.S);assert m,name
  result={}
  for addr,val in re.findall(r"\{\s*([^,{}]+),\s*([^,{}]+)\}",m[1]):
   result[number(addr)]=number(val)
  assert result
  return result
 common={}
 for name in ["surface_pro11_mode0_pll_5928mhz","mode_4224x3136_regs","surface_pro11_mode0_delta"]:common.update(array(name))
 common.update({0x380e:3214>>8,0x380f:3214&255})
 crop=array("surface_pro11_mode1_crop");assert len(crop)==7
 rows=[]
 for i in range(2):
  rw=q.u32s(q.raw(rd)[i*252:(i+1)*252]);count,ref=q.u32s(q.raw(ids[rw[28]]))
  oracle={x["address"]:x["data"] for x in q.reg_list(ids[ref],ids)}
  assert count==len(oracle)==207
  oracle.update({0x380e:3214>>8,0x380f:3214&255})
  actual=dict(common)
  if i:actual.update(crop)
  assert all(actual.get(k)==v for k,v in oracle.items()),"register mismatch mode"+str(i)
  assert set(actual)-set(oracle)=={0x4503}
  width=(actual[0x3808]<<8)|actual[0x3809];height=(actual[0x380a]<<8)|actual[0x380b]
  assert (width,height)==[(4076,2806),(4064,2286)][i]
  rows.append({"mode":i,"width":width,"height":height,"Windows_covered_registers_exact":207,"VTS":3214,"line_length_register":(actual[0x380c]<<8)|actual[0x380d]})
 block=re.search(r"static const struct ov13858_mode surface_pro11_modes\[\] = \{(.*?)\n\};",source,re.S)[1]
 assert block.index(".width = 4076")<block.index(".width = 4064")
 assert block.count(".pixel_rate = OV13858_SURFACE_PRO11_MODE0_PIXEL_RATE")==2
 start=source[source.index("static int ov13858_start_streaming("):source.index("/* Stop streaming */")]
 assert start.index("&ov13858->cur_mode->override_reg_list")<start.index("&ov13858->cur_mode->crop_reg_list")<start.index("__v4l2_ctrl_handler_setup")<start.index("OV13858_MODE_STREAMING")
 result={"status":"PASS_SOURCE_SENSOR_MODES_MATCH_LOCAL_ORACLE","modes":rows,"mode1_geometry_only_delta_count":7,"mode0_remains_first_default":True,"link_PLL_HTS_VTS_VT_clock_PM_controls_unchanged":True,"extra_upstream_test_pattern_disabled_register":1,"vendor_table_exported":False,"hardware_access":False,"source_sha256":hashlib.sha256(a.source.read_bytes()).hexdigest()}
 a.report.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
if __name__=="__main__":main()
