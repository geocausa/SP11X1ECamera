#!/usr/bin/env python3
from pathlib import Path
import re, json, hashlib

HERE=Path(__file__).resolve().parent
CSIPHY=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss/camss-csiphy-3ph-1-0.c')
CAMSS=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss/camss.c')
WIN=HERE/'WINDOWS-CSIPHY0-LIVE2.normalized.txt'

def load_win():
    out={}
    for line in WIN.read_text().splitlines():
        o,v=line.split()
        out[int(o,16)]=int(v,16)
    return out

def table():
    s=CSIPHY.read_text()
    blk=s.split('csiphy_lane_regs lane_regs_x1e80100[] = {',1)[1].split('};',1)[0]
    rows=[]
    for m in re.finditer(r'\{\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*([A-Z0-9_]+)\s*\}',blk):
        rows.append((int(m.group(1),16),int(m.group(2),16),int(m.group(3),16),m.group(4)))
    return rows

def settle(link_freq=420_000_000,timer=266_666_667):
    ui=1_000_000_000_000//link_freq
    ui//=2
    t=85_000+6*ui
    period=1_000_000_000_000//timer
    return t//period-6

w=load_win(); rows=table()
current={}
timeline=[]
# Exact current csiphy_lanes_enable order for X1E DPHY.
def put(off,val,why):
    current[off]=val
    timeline.append((off,val,why))
put(0x1014,0x81,'dynamic lane mask: BIT7 clock + BIT0 data lane 0')
put(0x1018,0x01,'COMMON_PWRDN_B')
put(0x101c,0x02,'DPHY common CTRL7 generic')
sc=settle()
for off,val,delay,typ in rows:
    if typ in ('CSIPHY_SKEW_CAL','CSIPHY_DNP_PARAMS'):
        continue
    if typ=='CSIPHY_SETTLE_CNT_LOWER_BYTE':
        val=sc
    put(off,val,'lane_regs_x1e80100 '+typ)
# Current DPHY code zeros CTRL11..CTRL21 after table.
for i in range(11,22):
    put(0x1000+4*i,0,'generic DPHY IRQ mask zeroing')

diff=[]
for off,val in sorted(current.items()):
    win=w.get(off)
    if win!=val:
        diff.append({'offset':f'0x{off:04x}','current_linux':f'0x{val:02x}','windows_live':None if win is None else f'0x{win:02x}'})

matches=sum(1 for off,val in current.items() if w.get(off)==val)

# Model the deliberately scoped E004j correction for X1E CSIPHY0 D-PHY only.
# The same-machine Windows dump is the authority for these receiver values.
proposed=dict(current)
for off in (0x0008,0x0408,0x0808,0x0c08,0x0e08):
    proposed[off]=0x10
proposed[0x1014]=0x81
for off in range(0x102c,0x1058,4):
    proposed[off]=w[off]
proposed_diff=[]
for off,val in sorted(proposed.items()):
    if w.get(off)!=val:
        proposed_diff.append({'offset':f'0x{off:04x}','proposed':f'0x{val:02x}','windows_live':None if w.get(off) is None else f'0x{w[off]:02x}'})
proposed_matches=sum(1 for off,val in proposed.items() if w.get(off)==val)
result={
 'schema':'sp11-camera-e004j-current-linux-vs-windows-csiphy0-v1',
 'windows_dump_sha256':hashlib.sha256(WIN.read_bytes()).hexdigest(),
 'linux_csiphy_source_sha256':hashlib.sha256(CSIPHY.read_bytes()).hexdigest(),
 'link_freq_hz':420_000_000,
 'timer_clk_rate_hz':266_666_667,
 'current_linux_settle_count':sc,
 'windows_live_settle_count':0x10,
 'lane_mask':{'windows_live':'0x81','linux_dynamic_for_data_lane_0':'0x81'},
 'modeled_final_registers':len(current),
 'matching_registers':matches,
 'mismatching_registers':len(diff),
 'diff':diff,
 'proposed_scoped_e004j': {
   'scope':'X1E80100 CSIPHY0 + DPHY only',
   'settle_count':'0x10',
   'preserve_dynamic_lane_mask':'0x81',
   'retain_windows_common_ctrl11_21':True,
   'matching_registers':proposed_matches,
   'mismatching_registers':len(proposed_diff),
   'diff':proposed_diff,
 },
}
(HERE/'CURRENT-LINUX-VS-WINDOWS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
