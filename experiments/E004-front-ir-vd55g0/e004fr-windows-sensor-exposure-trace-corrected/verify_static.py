#!/usr/bin/env python3
from pathlib import Path
import hashlib, re, struct, subprocess, sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
TOOLS=REPO/'tools'
sys.path.insert(0,str(TOOLS))
import qti_parameter_bin as qti
import qti_sensor_summary as qs

PKG=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor_extension8380.inf_arm64_84ddd55dc933cac9/com.surface.sensormodule.aux_vd55g0_MSHW0492.bin')
AUX=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor8380.inf_arm64_7d23cd8fdfa9b39f/surfacecamauxsensor8380.sys')
ST=REPO/'src/front-ir-vd55g0/st-vd55g0/vd55g0.c'
PKG_SHA='e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794'
AUX_SHA='e5b6b064f39cf239ab07e22ca2434e3c08c93b691dc7d27cebb90861226efa75'

def need(x,msg):
    if not x: raise SystemExit('E004FR_STATIC_FAIL '+msg)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def disasm(a,b):
    return subprocess.check_output(['llvm-objdump','-d','--start-address='+hex(0x140000000+a),'--stop-address='+hex(0x140000000+b),str(AUX)],text=True)

need(sha(PKG)==PKG_SHA,'package hash')
need(sha(AUX)==AUX_SHA,'aux hash')
obj=qti.parse(PKG); ids={e['id']:e for e in obj['entries']}
regsets=[]
for e in obj['entries']:
    if e['name']=='regSetting' and e['payload_size']:
        try: regsets.append((e['id'],qs.reg_list(e,ids)))
        except Exception: pass
need(regsets,'regsets')
_,rows=max(regsets,key=lambda z:len(z[1]))
by={}
for r in rows: by.setdefault(r['address'],[]).append(r)
def one(a):
    need(len(by.get(a,[]))==1,'unique reg '+hex(a)); return by[a][0]['data']
need(one(0x044c)==2,'manual exposure mode')
need(one(0x044d)==0,'analog gain')
need(one(0x044e)==100 and one(0x044f)==0,'100-line initial exposure')
need(one(0x0468)==2,'GPIO1 strobe')
need(one(0x046d)==0 and one(0x046e)==0,'zero strobe shifts')
# Sensor-driver structure contains the direct coarse-integration address and empty optional strobe leaves.
drv=bytes.fromhex(ids[1]['raw_hex'])
need(struct.unpack_from('<I',drv,0x68)[0]==0x044e,'coarse integration address')
for name in ('strobeStartAddr','strobeWidthAddr'):
    es=[e for e in obj['entries'] if e['name']==name]
    need(len(es)==1 and es[0]['payload_size']==0,name+' absent')
# Exact helper calling convention: internal element {u16 reg,u16 data,...} -> w0,w1 -> helper +0xa350.
s=disasm(0x9410,0x9434)
need(re.search(r'ldrh\s+w1, \[x26, #0x2\]',s) is not None,'caller data load')
need(re.search(r'ldrh\s+w0, \[x26\]',s) is not None,'caller register load')
need('0x14000a350' in s,'caller to write helper')
h=disasm(0xa350,0xa380)
need(re.search(r'mov\s+w8, w0',h) is not None,'helper preserves register')
need(re.search(r'uxth\s+w11, w1',h) is not None,'helper preserves data')
# Mechanical reference check against the pinned vendored ST source.
t=ST.read_text()
for token in ('VD55G0_REG_MANUAL_COARSE_EXPOSURE','VD55G0_REG_16BIT(0x044e)','VD55G0_REG_GPIO_1_CTRL','VD55G0_REG_8BIT(0x0468)','VD55G0_GPIO_MODE_STROBE'):
    need(token in t,'ST token '+token)

# Keep the future live action mechanically narrow and read-only.
capture=(HERE/'capture.ps1').read_text()
for token in ("DisplayName -eq 'Surface IR Camera Front'", "Name -eq 'Surface IR Camera Front'",
              'Width -ne 644', 'Height -ne 604', 'AddSeconds(5)', '$frames -lt 12',
              'TryAcquireLatestFrame()', 'ExposureControl'):
    need(token in capture,'capture token '+token)
for forbidden in ('SetAutoAsync','SetValueAsync','TrySetAuto','ExposureControl.Set','FlashControl','TorchControl',
                  'FocusControl','WhiteBalanceControl','ZoomControl','AddEffectAsync','SetFormatAsync'):
    need(forbidden not in capture,'capture mutator '+forbidden)
need('Save' not in capture and 'BitmapEncoder' not in capture and 'FileIO' not in capture,'capture image persistence')

gen=(HERE/'generate-kd.ps1').read_text()
for token in ('+ 0xa350','0x0200 & @w0 <= 0x0202','0x044c & @w0 <= 0x0451',
              '0x0458 & @w0 <= 0x0459','0x0467 & @w0 <= 0x046e','0n128','E004FR_SENSOR_WRITE'):
    need(token in gen,'KD generator token '+token)
need(gen.count('bp0 ')==1,'exactly one live breakpoint')
print('E004FR_STATIC=PASS PACKAGE_INIT_EXPOSURE=100 GPIO1=STROBE DELAYS=0 AUX_WRITE_HELPER_RVA=0xa350 CAPTURE=READ_ONLY_12F_5S')
