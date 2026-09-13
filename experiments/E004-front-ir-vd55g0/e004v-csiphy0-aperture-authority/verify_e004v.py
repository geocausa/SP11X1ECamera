#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

D=Path(__file__).resolve().parent
P=D.parent
O=P/'e004o-ir-only-graph-authority'
U=P/'e004u-csiphy0-readback-runtime'
J=P/'e004j-csiphy0-dphy-authority'
PARENT=O/'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb'
OUT=D/'x1e80100-microsoft-denali-sp11-e004v-ir-csiphy0-8k.dtb'
BUILDER=D/'build-e004v-dtb.py'

def need(v,m):
    if not v:
        raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

need(sha(PARENT)=='fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742','parent SHA')
need(sha(BUILDER)=='58f38a853d4fe09f1aa0736b4a670cc3643b81316b92d02a639651ed4a492414','builder SHA')
need(sha(OUT)=='5547a43f06062053c7acdacbf8d6e103233f3d5e3ea7ebc8761bc32fbdcc0009','output SHA')

before=OUT.read_bytes()
subprocess.run(['python3',str(BUILDER)],check=True,stdout=subprocess.DEVNULL)
need(OUT.read_bytes()==before,'builder not deterministic')

a=PARENT.read_bytes()
b=OUT.read_bytes()
need(len(a)==len(b),'DTB size changed')
diff=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
need(diff==[0x365a],f'unexpected byte diffs {diff}')
need(a[0x364c:0x365c].hex()=='000000000ace40000000000000001000','old CSIPHY0 tuple')
need(b[0x364c:0x365c].hex()=='000000000ace40000000000000002000','new CSIPHY0 tuple')
need(a[0x365c:0x366c]==b[0x365c:0x366c]==bytes.fromhex('000000000ace60000000000000002000'),'CSIPHY1 tuple')

def resources(path):
    reg=subprocess.check_output(['fdtget','-t','x',str(path),'/soc@0/isp@acb7000','reg'],text=True).split()
    names=subprocess.check_output(['fdtget','-t','s',str(path),'/soc@0/isp@acb7000','reg-names'],text=True).split()
    cells=[int(x,16) for x in reg]
    out={}
    for i,n in enumerate(names):
        base=(cells[i*4]<<32)|cells[i*4+1]
        size=(cells[i*4+2]<<32)|cells[i*4+3]
        out[n]=(base,size)
    return out

pr=resources(PARENT)
vr=resources(OUT)
need(pr['csiphy0']==(0x0ace4000,0x1000),'parent CSIPHY0')
need(vr['csiphy0']==(0x0ace4000,0x2000),'new CSIPHY0')
need(vr['csiphy1']==(0x0ace6000,0x2000),'CSIPHY1')
need(0x0ace4000+0x2000==0x0ace6000,'resource boundary')
need(set(pr)==set(vr),'reg-names changed')
for name in pr:
    if name!='csiphy0':
        need(pr[name]==vr[name],'other resource changed '+name)

# Whole-DTB one-byte proof makes graph and every unrelated property byte-identical.
need(a[:0x365a]==b[:0x365a] and a[0x365b:]==b[0x365b:],'unrelated DT bytes changed')

ur=json.load(open(U/'RESULT.json'))
need(ur['status']=='FAIL_CSIPHY0_DT_APERTURE_4K_VS_REQUIRED_8K_GOLDEN_RETURN_RETIRED','E004u diagnosis')
need(ur['fault']['function']=='csiphy_reset' and ur['fault']['fault_va']=='ffff80008420e000','E004u fault')
need(ur['x1e_driver']['common_register_offset']=='0x1000','E004u driver offset')
need(ur['sensor_stream_callback_performed'] is False and ur['illumination_performed'] is False,'E004u safety')

jr=json.load(open(J/'RESULT.json'))
need(jr['windows_raw_sp7_log']['live_aperture']=='0x0ace4000..0x0ace5fff','Windows aperture')
need(jr['windows_raw_sp7_log']['dwords']==2048,'Windows aperture size')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='PASS_OFFLINE_CSIPHY0_8K_APERTURE_AUTHORITY','result')
need(r['binary_diff_count']==1 and r['graph_or_other_dt_change'] is False,'isolation result')
need(r['runtime_performed'] is False,'runtime result')

need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')

print('E004V_VERIFY=PASS DT_ONLY=YES BINARY_DIFF_BYTES=1')
print('E004V_CSIPHY0=0xACE4000+0x2000 WINDOWS_APERTURE_MATCH=YES')
print('E004V_CSIPHY1=0xACE6000+0x2000 OVERLAP=NO')
print('E004V_GRAPH_AND_ALL_OTHER_DT_BYTES=UNCHANGED')
print('E004V_RUNTIME=NO')
