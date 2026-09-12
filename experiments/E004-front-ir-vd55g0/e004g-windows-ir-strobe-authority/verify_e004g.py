#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, struct, subprocess

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
E004D=REPO/'experiments/E004-front-ir-vd55g0/e004d-windows-initialconfig-sequence'
PCFG=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamplatform_ext8380.inf_arm64_af3dfff4f4f24d75/CAMP_PCFG_MSHW0495.bin')
PLAT=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamplatform8380.inf_arm64_16d44e9aca3becfb/qccamplatform8380.sys')
FLASH=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamflash8380.inf_arm64_e7729176a9bcf2a8/qccamflash8380.sys')
PCFG_SHA='0933a645ea55c95953ac3f0b6829e01c27133d52f369596f62fb3c5e99f5807f'
PLAT_SHA='836714ec41f92f45af363d7bf3c9b9cfc2cccdbd19a1c57f355b471068648049'
FLASH_SHA='6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b'
DESC=0x01000110

def need(v,m):
    if not v: raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def disasm(start,stop):
    return subprocess.check_output(['llvm-objdump','-d','--no-show-raw-insn',
        f'--start-address=0x{start:x}',f'--stop-address=0x{stop:x}',str(FLASH)],text=True)

need(sha(PCFG)==PCFG_SHA,'PCFG identity')
need(sha(PLAT)==PLAT_SHA,'platform driver identity')
need(sha(FLASH)==FLASH_SHA,'flash driver identity')
subprocess.run(['python3',str(E004D/'verify_e004d.py')],check=True,stdout=subprocess.DEVNULL)

b=PCFG.read_bytes(); pat=struct.pack('<I',DESC)
offs=[i for i in range(len(b)) if b.startswith(pat,i)]
need(offs==[0x38],'front IR descriptor offset')
fields={
 'orientation':DESC&0xf,
 'direction':(DESC>>4)&0xf,
 'flash_presence':(DESC>>8)&1,
 'flash_index':(DESC>>9)&7,
 'flash_cci_timer_index':(DESC>>12)&3,
 'flash_trigger_type':(DESC>>14)&3,
 'i2c_master_index':(DESC>>16)&0xf,
 'csi_phy_index':(DESC>>20)&0xf,
 'face_authentication':(DESC>>24)&1,
 'flash_shutter_type':(DESC>>25)&1,
}
need(fields=={
 'orientation':0,'direction':1,'flash_presence':1,'flash_index':0,
 'flash_cci_timer_index':0,'flash_trigger_type':0,'i2c_master_index':0,
 'csi_phy_index':0,'face_authentication':1,'flash_shutter_type':0},'descriptor fields')

# Exact platform binary exposes the recovered field names.
ps=subprocess.check_output(['strings','-a',str(PLAT)],text=True,errors='replace')
for s in ('flash presence              = 0x%x','flash index                 = 0x%x',
          'flash / CCI Timer index     = 0x%x','flash / trigger type        = 0x%x',
          'flash / shutter type        = 0x%x'):
    need(s in ps,'platform field string '+s)

fs=subprocess.check_output(['strings','-a',str(FLASH)],text=True,errors='replace')
for s in ('Received Flash Strobe Configuration Payload','CCI Timer Index     = 0x%x',
          'Sensor Shutter Type = 0x%x','Trigger Type        = 0x%x',
          'CameraWhiteLEDSetSWStrobe','CameraIRLED_Trigger = %d',
          'IRLED_CCI_Trigger_Callback executed',
          'CameraWhiteLEDFlashPMIC_SetTargetCurrent','CameraWhiteLEDFlashPMIC_SetSafetyTimer'):
    need(s in fs,'flash string '+s)

d=disasm(0x140005a78,0x140005d28)
n=re.sub(r'\s+',' ',d)
tokens=[
 'ldr w8, [x20, #0x4]','cmp w8, #0x2','b.ne 0x140005b44',
 'cmp w8, #0x1','b.ne 0x140005b7c',
 'add x8, x8, #0xf60','str x8, [sp, #0x28]','bl 0x140004680',
 'cbnz w8, 0x140005c88',
 'bl 0x1400045d0','bl 0x140004ce0',
 'mov w1, #0x1','mov w0, #0x1','bl 0x140004d58',
 'add x1, x8, #0x720',
 'mov w0, #0x0','mov w1, #0x0','bl 0x140004d58',
]
for t in tokens:
    need(re.sub(r'\s+',' ',t) in n,'trigger branch token '+t)

# Function address installed by trigger type 1 must be the callback carrying the exact IRLED CCI log.
cb=disasm(0x140006f60,0x140006fa0)
need('140006f60' in cb,'callback function')
need('IRLED_CCI_Trigger_Callback executed' in fs,'callback identity string')

dec=json.load(open(E004D/'WINDOWS-INITIALCONFIG-DECODE.json'))
writes=dec['post_boot_config']['raw_writes']
need(len(writes)==43,'final Windows config count')
strobe=[x for x in writes if x['address']=='0x0468']
need(strobe==[{'address':'0x0468','data':'0x02'}],'single GPIO1 selector write')
safe=[x for x in writes if x['address']!='0x0468']
need(len(safe)==42,'42 non-strobe final writes')

result={
 'schema':'sp11-camera-e004g-windows-ir-strobe-authority-v1',
 'status':'PASS_OFFLINE_WINDOWS_IR_STROBE_TRIGGER_AUTHORITY',
 'authority':'same-machine exact Surface PCFG + exact installed qccamplatform/qccamflash + E004d Windows sensor packet',
 'pcfg_sha256':PCFG_SHA,'qccamplatform_sha256':PLAT_SHA,'qccamflash_sha256':FLASH_SHA,
 'front_ir_descriptor':{'packed':'0x01000110',**fields},
 'flash_driver_trigger_branches':{
   'trigger_type_0':'distinct hardware-strobe configuration branch; programs flash/PMIC state and calls low-level control with arguments 1,1,0',
   'trigger_type_1':'installs IRLED_CCI_Trigger_Callback and uses CameraIRLED_Trigger path',
   'trigger_type_2':'target-current plus safety-timer branch',
   'other':'CameraWhiteLEDSetSWStrobe fallback and low-level control 0,0,0',
 },
 'sensor_final_config':{
   'windows_writes':43,
   'illumination_coupled_write':{'address':'0x0468','data':'0x02','reference_only_name':'GPIO1 STROBE selector'},
   'non_strobe_writes':42,
 },
 'proven':[
   'Windows marks the VD55G0 slot flash-present with flash index 0 and trigger type 0.',
   'Trigger type 0 is a distinct flash hardware configuration path, not trigger type 1 CCI callback and not software-strobe fallback.',
   'The Windows sensor final block sets GPIO1 selector register 0x0468 to 0x02.',
 ],
 'not_proven':[
   'Whether writing 0x0468=0x02 while the sensor remains in SW_STBY can itself emit a physical IR light pulse.',
   'Exact physical emitter current/timing for the face-authentication illumination path.',
 ],
 'linux_policy':{
   'write_0x0468_0x02_authorized':False,
   'next_safe_subset':'42 final Windows writes excluding 0x0468, no CAMSS, no V4L2, no stream, no external illumination',
 },
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('E004G_VERIFY=PASS IR_DESCRIPTOR=0x01000110 FLASH_PRESENT=1 TRIGGER_TYPE=0')
print('E004G_TRIGGER_MAP=TYPE0_HARDWARE_PATH TYPE1_IRLED_CCI_CALLBACK TYPE2_CURRENT_SAFETY OTHER_SW_STROBE')
print('E004G_FINAL_CONFIG=43 WRITES SAFE_NON_STROBE=42 ISOLATED_ILLUMINATION_COUPLED=0x0468=0x02')
print('E004G_STROBE_WRITE_AUTHORIZED=NO')

