#!/usr/bin/env python3
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'E003H_PRIMING_MIPI_CROSSORDER_20260829.log'
OUT=ROOT/'priming-mipi-crossorder-oracle.json'
RAW_BYTES=7420
RAW_SHA='06127e46dca5759cfded698b1a1a8dc0dcd40dd04ca271d515a54fbed42987ee'
ISP_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
MIPI_SHA='033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407'
SENSOR_SHA='80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03'
REPLAY_LEN={'e93':'replay0','e33':'replay1','903':'replay2','4e7':'replay3'}
MARK_RE=re.compile(r'^===E003H_(CDM_MAIN_[0-9a-f]+|CSID_START_CALL|ISP_START_DONE|MIPI_START_ENTER|MIPI_START_DONE|SENSOR_STREAM_ON_APPLY|CYCLE2_ARMED)===$',re.I)
EXPECTED=[
 'CDM_MAIN_e93','CDM_MAIN_e33','CSID_START_CALL','ISP_START_DONE',
 'MIPI_START_ENTER','MIPI_START_DONE','SENSOR_STREAM_ON_APPLY',
 'CDM_MAIN_903','CDM_MAIN_4e7','CDM_MAIN_957','CDM_MAIN_957','CDM_MAIN_957','CDM_MAIN_957'
]

def die(s): raise SystemExit('FAIL: '+s)
def main():
    raw=RAW.read_bytes()
    if len(raw)!=RAW_BYTES: die(f'raw bytes {len(raw)} != {RAW_BYTES}')
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=RAW_SHA: die(f'raw sha {sha} != {RAW_SHA}')
    text=raw.decode('utf-16')
    events=[]
    for line_no,line in enumerate(text.splitlines(),1):
        m=MARK_RE.fullmatch(line.strip())
        if m: events.append((line_no,m.group(1)))
    armed=[i for i,(_,x) in enumerate(events) if x.upper()=='CYCLE2_ARMED']
    if len(armed)!=1: die(f'expected one cycle2 separator, got {len(armed)}')
    k=armed[0]
    chunks=[events[:k],events[k+1:]]
    cycles=[]
    for ci,ch in enumerate(chunks,1):
        names=[x for _,x in ch]
        if names!=EXPECTED: die(f'cycle {ci} marker order/census drift: {names}')
        pos={}
        for i,(ln,name) in enumerate(ch):
            pos.setdefault(name,i)
        relation=[
          'replay0','replay1','csid1_start','isp_start_done','mipi_start_enter',
          'mipi_start_done','sensor_stream_on','replay2','replay3','steady_0x958'
        ]
        idx=[0,1,2,3,4,5,6,7,8,9]
        if idx!=sorted(idx): die('internal order failure')
        cycles.append({'cycle':ci,'markers':names,'lines':[ln for ln,_ in ch],
                       'total_order':relation})
    out={
      'schema':'sp11-e003h-windows-priming-mipi-crossorder-v1',
      'accepted':True,
      'source':{'log':RAW.name,'bytes':len(raw),'sha256':sha,'encoding':'UTF-16LE KD log'},
      'drivers':{
        'qccamisp8380.sys':{'sha256':ISP_SHA,'replay_main_probe_rva':'0x287e4','csid_start_call_rva':'0x16208','isp_start_done_rva':'0x16220'},
        'qccammipicsi8380.sys':{'sha256':MIPI_SHA,'start_enter_rva':'0x2068','start_done_rva':'0x2398'},
        'surfacecamfrontsensor8380.sys':{'sha256':SENSOR_SHA,'stream_on_apply_rva':'0x7e94'},
      },
      'replay_main_encoded_lengths':{
        'replay0':'0xe93 -> 0xe94 bytes','replay1':'0xe33 -> 0xe34 bytes',
        'replay2':'0x903 -> 0x904 bytes','replay3':'0x4e7 -> 0x4e8 bytes',
        'first_steady':'0x957 -> 0x958 bytes'},
      'cycle_count':2,
      'cycles':cycles,
      'proven_total_order':[
        'replay0','replay1','CSID1 start','ISP_START_DONE','MIPI/CSIPHY start enter',
        'MIPI/CSIPHY start done','sensor MODE_SELECT=1 apply','replay2','replay3','first steady 0x958 batch'],
      'closure':{
        'replay01_vs_csid_start_closed':True,
        'replay01_relation':'replay0 -> replay1 -> CSID1 start',
        'replay23_vs_mipi_sensor_start_closed':True,
        'replay23_relation':'MIPI start done -> sensor stream-on -> replay2 -> replay3',
        'two_cycles_identical':True,
      },
      'linux_consequence':'The two 0030 priming placement blockers are closed. A bounded PIX runner may place replay0/1 before CSID1 start, then complete ISP/MIPI/sensor start, then replay2/3 before the first steady Epoch0 0x958 batch. This oracle does not by itself authorize Linux runtime; the callable runner still requires static composition/inspection and rollback gating.'
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
    print('PASS: two cycles prove replay0/1 -> CSID1 -> ISP -> MIPI -> sensor-on -> replay2/3 -> first steady')
if __name__=='__main__': main()
