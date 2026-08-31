#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct,subprocess,re
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
O=R/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-vfe1-ubwc-static-ownership'
B=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B)=='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
def fileoff(rva): return rva-0x1000+0x400
b=B.read_bytes()
# qccamisp generation-table initializer: qword at RVA 0x1d608 is dwords 0x50,0x58,
# stored at object +0x3454; therefore object +0x3458 == BUS-common relative offset 0x58.
q=struct.unpack_from('<Q',b,fileoff(0x1d608))[0]
assert q==0x0000005800000050
D=subprocess.check_output(['llvm-objdump','-d','--no-show-raw-insn',str(B)],text=True)
need=[
 '14001d574:     \tmov\tx9, #0x3454',
 '14001d578:     \tldr\tx8, 0x14001d608',
 '14001d57c:     \tstr\tx8, [x0, x9]',
 '14001e558:     \tcmp\tw2, #0x8',
 '14001e55c:     \tmov\tw8, #0x1000',
 '14001e584:     \tcmp\tw3, #0x11',
 '14001e58c:     \torr\tw8, w8, #0x40',
 '14001e5a8:     \torr\tw4, w8, #0x6',
 '14001e5cc:     \tldr\tx8, [x19, #0x150]',
 '14001e5d4:     \tldr\tw9, [x19, #0x3458]',
 '14001e5e0:     \tstr\tw4, [x8, w9, uxtw]',
]
for s in need: assert s in D,s
# Previously accepted active IFE1 callback proves x0/x19 +0x150 is BUS sub-base:
# it writes BUS mask0 at relative +0x18 and BUS CGC override at relative +0x08.
for s in [
 '14001bec8:     \tldr\tx9, [x0, #0x150]',
 '14001bed0:     \tstr\tw8, [x9, #0x18]',
 '14001bed4:     \tldr\tx9, [x0, #0x150]',
 '14001bedc:     \tstr\tw8, [x9, #0x8]',
]: assert s in D,s
# Live Windows oracle binds the generic branch uniquely to 0x1046.
import csv
csvp=R/'experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/vfe1-route-live-nonzero.csv'
rows={r['offset']:r for r in csv.DictReader(csvp.open())}
assert rows['0x0c58']['live1']=='0x00001046' and rows['0x0c58']['live2']=='0x00001046' and rows['0x0c58']['stable']=='1'
linux=json.loads((R/'experiments/E003-front-imx681-cphy/e003h-vfe1-bus-progress-readonly-0060-candidate/runtime-0060-analysis.json').read_text())
assert linux['linux_bus_common']['ubwc_static_ctrl']=='0x00000006' and linux['ubwc_static_ctrl_xor_delta']=='0x00001040'
out={
 'schema':'sp11-e003h-windows-vfe1-ubwc-static-ownership-v1','accepted':True,'date':'2026-08-31','qccamisp_sha256':sha(B),'windows_live_oracle_sha256':sha(csvp),'linux_0060_analysis_sha256':sha(R/'experiments/E003-front-imx681-cphy/e003h-vfe1-bus-progress-readonly-0060-candidate/runtime-0060-analysis.json'),
 'proof':{'bus_subbase_object_field':'0x150','ubwc_offset_object_field':'0x3458','ubwc_relative_offset':'0x58','sp11_value_formula':'0x1000 | 0x40 | 0x6','sp11_computed_value':'0x00001046','qccamisp_direct_write_rva':'0x1e5e0','windows_live_value':'0x00001046','linux_0060_value':'0x00000006','missing_linux_bits':'0x00001040'},
 'classification':{'qccamisp_owns_bus_ubwc_static_write':True,'windows_value_computation_proven':True,'windows_live_value_matches_computation':True,'linux_programming_delta_proven':True,'causality_for_missing_vfe_epoch0':False,'bounded_linux_candidate_justified':True,'candidate_scope':'X1E80100 VFE1 BUS common +0xc58 exact Windows value 0x00001046 before BUS client enable; retain read-only 0060 telemetry'},
 'runtime_authorized':False}
(O/'windows-vfe1-ubwc-static-ownership.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
# Preserve only decisive disassembly lines, generated from exact binary.
sel=[]
for line in D.splitlines():
 try: a=int(line.split(':',1)[0].strip(),16)
 except: continue
 if 0x14001be80<=a<=0x14001bee8 or 0x14001d570<=a<=0x14001d584 or 0x14001e550<=a<=0x14001e5f0: sel.append(line)
(O/'qccamisp-decisive-disassembly.txt').write_text('\n'.join(sel)+'\n')
print(json.dumps(out,indent=2,sort_keys=True)); print('ORACLE_SHA='+sha(O/'windows-vfe1-ubwc-static-ownership.json')); print('EXTRACTOR_SHA='+sha(O/'extract_windows_vfe1_ubwc_static_ownership.py')); print('DISASM_SHA='+sha(O/'qccamisp-decisive-disassembly.txt'))
