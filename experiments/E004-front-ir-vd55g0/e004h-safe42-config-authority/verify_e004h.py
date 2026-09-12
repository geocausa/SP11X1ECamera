#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, re, shutil, struct, subprocess, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
E004D=REPO/'experiments/E004-front-ir-vd55g0/e004d-windows-initialconfig-sequence'
E004F=REPO/'experiments/E004-front-ir-vd55g0/e004f-bounded-prefix-runtime'
E004G=REPO/'experiments/E004-front-ir-vd55g0/e004g-windows-ir-strobe-authority'
E004E=REPO/'experiments/E004-front-ir-vd55g0/e004e-linux-prefixprobe-authority'
SRC=REPO/'src/front-ir-vd55g0/sp11-vd55g0-config42probe'
KERNEL=REPO.parents[1]/'02-kernel/build-runtime-v4-headers-20260826'
HVB=REPO/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hv-current-golden-camera-dtb-merge/build-hv-dtb.py'
PARENT=E004E/'x1e80100-microsoft-denali-sp11-e004e-prefixprobe.dtb'
DTB=HERE/'x1e80100-microsoft-denali-sp11-e004h-config42.dtb'
BUILDER=HERE/'build-e004h-dtb.py'
C=SRC/'sp11-vd55g0-config42probe.c'
GEN=SRC/'generate_windows_header.py'
HEADER=SRC/'surface-windows.generated.h'

PACKAGE=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor_extension8380.inf_arm64_84ddd55dc933cac9/com.surface.sensormodule.aux_vd55g0_MSHW0492.bin')
PACKAGE_SHA='e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794'
PARENT_SHA='d05c4d50a4e2aaaff2216aa765802578c78551d97217cd3e422c9eda6a9c95e9'
DTB_SHA='e29c787acf9e2f1330a4e73fd8014aba118a2f0a59be51c86859a9ab7fed4ef2'
C_SHA='3e6f28d15cfb03fccf01113dd1914ae38fe731017f7a224db89e63cd6dfe4cc0'
GEN_SHA='c430516b496f41780d45cbef08cb0698c7619410cc8ada6df1552bbfaa2d7167'
PROV_SHA='c98f93cc06437967d4b62e4970c90e247f67b62809706494ff38f1b3304ce911'
HEADER_SHA='40f9731061ba327c423da3322abdc9a20e07251073c39c266027dac55de1fd9e'
MODULE_SHA='75eccb1ac7a8a5f247ec03a9f56339527d2dcd7cfab77450b3ba1f8efe563c5c'
PATCH_SHA='5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321'
FULL43_SHA='9664529aab0c65d6f3ae9778c8c31f54fa1675bde748fdaafc8e2d2ab4ea387c'
SAFE42_SHA='159647774f45331210044d0680e50bf16e8aaeeb8c3e98449d2cef7adeffacb2'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
NODE='/soc@0/cci@ac15000/i2c-bus@0/camera@60'

ALLOWED_UNDEFINED={
 'clk_disable','clk_enable','clk_get_rate','clk_prepare','clk_set_rate','clk_unprepare',
 '_dev_err','dev_err_probe','_dev_info','devm_clk_get','devm_gpiod_get','devm_kmalloc',
 'devm_regulator_get','gpiod_set_value_cansleep','i2c_del_driver','i2c_register_driver',
 'i2c_transfer','memcmp','regulator_disable','regulator_enable','regulator_get_voltage',
 '__stack_chk_fail','__ubsan_handle_load_invalid_value','__ubsan_handle_out_of_bounds',
 'usleep_range_state',
}

def need(v,m):
    if not v: raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

spec=importlib.util.spec_from_file_location('hv',HVB)
hv=importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)

def warnings(dt):
    with tempfile.TemporaryDirectory(prefix='e004h-dtc-') as td:
        cp=subprocess.run(['dtc','-I','dtb','-O','dtb',str(dt),'-o',str(Path(td)/'x.dtb')],
                          text=True,capture_output=True,check=True)
    return sorted(x.split(': Warning ',1)[1] for x in cp.stderr.splitlines() if ': Warning ' in x)

def build_once(log):
    subprocess.run(['make','-C',str(KERNEL),f'M={SRC}','clean'],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['python3',str(GEN)],check=True,stdout=subprocess.DEVNULL)
    with open(log,'w') as f:
        subprocess.run(['make','-C',str(KERNEL),f'M={SRC}','modules','V=0'],check=True,stdout=f,stderr=subprocess.STDOUT)
    return SRC/'sp11-vd55g0-config42probe.ko'

def parse_generated():
    text=HEADER.read_text()
    psec=text.split('static const u8 sp11_surface_patch',1)[1].split('};',1)[0]
    patch=bytes(int(x,16) for x in re.findall(r'0x([0-9a-fA-F]{2})',psec))
    asec=text.split('static const struct sp11_reg8 sp11_windows_safe42',1)[1].split('};',1)[0]
    entries=[(int(a,16),int(v,16)) for a,v in re.findall(r'\{\s*0x([0-9a-fA-F]{4}),\s*0x([0-9a-fA-F]{2})\s*\}',asec)]
    return text,patch,entries

def seqhash(entries):
    return hashlib.sha256(b''.join(struct.pack('<HB',a,v) for a,v in entries)).hexdigest()

def main():
    subprocess.run(['python3',str(E004D/'verify_e004d.py')],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['python3',str(E004F/'verify-runtime.py')],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['python3',str(E004G/'verify_e004g.py')],check=True,stdout=subprocess.DEVNULL)

    need(sha(PACKAGE)==PACKAGE_SHA,'Surface package')
    need(sha(PARENT)==PARENT_SHA,'parent DTB')
    need(sha(DTB)==DTB_SHA,'E004h DTB')
    need(sha(C)==C_SHA,'source')
    need(sha(GEN)==GEN_SHA,'generator')
    need(sha(SRC/'PROVENANCE.md')==PROV_SHA,'provenance')

    parent=hv.parse_fdt(PARENT); out=hv.parse_fdt(DTB)
    need(set(parent)==set(out),'DT node set')
    changes=[]
    for p in parent:
        for k in set(parent[p])|set(out[p]):
            if parent[p].get(k)!=out[p].get(k):
                changes.append((p,k,parent[p].get(k),out[p].get(k)))
    need(len(changes)==1 and changes[0][0]==NODE and changes[0][1]=='compatible','only compatible changed')
    need(out[NODE]['compatible'].rstrip(b'\0')==b'microsoft,sp11-vd55g0-config42probe','compatible')
    need(warnings(DTB)==warnings(PARENT),'DTC warning regression')
    with tempfile.TemporaryDirectory(prefix='e004h-dtb-rebuild-') as td:
        q=Path(td)/'out.dtb'
        subprocess.run(['python3',str(BUILDER),'--parent',str(PARENT),'--out',str(q)],check=True,stdout=subprocess.DEVNULL)
        need(sha(q)==DTB_SHA,'DT deterministic rebuild')

    subprocess.run(['python3',str(GEN)],check=True,stdout=subprocess.DEVNULL)
    need(sha(HEADER)==HEADER_SHA,'generated header identity')
    text,patch,entries=parse_generated()
    need(len(patch)==552 and hashlib.sha256(patch).hexdigest()==PATCH_SHA,'Surface patch')
    need(len(entries)==42 and seqhash(entries)==SAFE42_SHA,'safe42 sequence')
    need(all(a!=0x0468 for a,_ in entries),'0x0468 excluded')
    need((0x0467,0x01) in entries and (0x0469,0x01) in entries and (0x046a,0x01) in entries,'other GPIO modes')
    need(f'#define SP11_WINDOWS_FULL43_SHA256 "{FULL43_SHA}"' in text,'full43 source identity')
    need('#define SP11_WINDOWS_ISOLATED_STROBE_REG 0x0468' in text,'isolated reg')
    need('#define SP11_WINDOWS_ISOLATED_STROBE_VALUE 0x02' in text,'isolated value')

    c=C.read_text()
    need('"microsoft,sp11-vd55g0-config42probe"' in c,'private compatible')
    need('model[0] != 0x30 || model[1] != 0x47' in c and
         'revision[0] != 0x11 || revision[1] != 0x11' in c,'identity gate')
    need(c.index('SP11_VD55G0_CONFIG42_ID_GATE=PASS') < c.index('SP11_VD55G0_CONFIG42_PATCH_BEGIN'),'identity before writes')
    need('if (sp11_windows_safe42[i].reg == SP11_WINDOWS_ISOLATED_STROBE_REG)' in c,'runtime strobe guard')
    need('ret = -EPERM;' in c,'runtime reject isolated strobe')
    need('gpio_before != gpio_after' in c,'strobe unchanged gate')
    need('gpio_ctrl[1] != gpio_before' in c,'GPIO1 readback unchanged')
    need('SP11_VD55G0_CONFIG42_READBACK=PASS' in c,'readback acceptance')
    need('writes != 596' in c,'exact total writes')
    need('safe_config_writes=42 isolated_strobe_writes=0' in c,'42/0 marker')
    need('stream=0 illumination=0' in c,'no stream illumination marker')
    for bad in ('v4l2','media_entity','request_firmware','led_classdev','qcom_camss'):
        need(bad not in c,'forbidden source token '+bad)

    with tempfile.TemporaryDirectory(prefix='e004h-module-build-') as td:
        td=Path(td)
        a=build_once(td/'a.log'); acopy=td/'a.ko'; shutil.copyfile(a,acopy)
        b=build_once(td/'b.log'); bcopy=td/'b.ko'; shutil.copyfile(b,bcopy)
        need(sha(acopy)==sha(bcopy)==MODULE_SHA,'module hashes')
        need(acopy.read_bytes()==bcopy.read_bytes(),'module byte reproducible')
        mi=subprocess.check_output(['modinfo',str(bcopy)],text=True)
        vermagic=next(x for x in mi.splitlines() if x.startswith('vermagic:')).split(':',1)[1].strip()
        need(vermagic==VERMAGIC,'Golden vermagic')
        nm=subprocess.check_output(['nm','-u',str(bcopy)],text=True)
        undefined={x.split()[-1] for x in nm.splitlines() if x.strip()}
        need(undefined==ALLOWED_UNDEFINED,'undefined symbol surface '+repr(sorted(undefined^ALLOWED_UNDEFINED)))
        st=subprocess.check_output(['strings',str(bcopy)],text=True,errors='replace')
        for marker in (PATCH_SHA,SAFE42_SHA,'SP11_VD55G0_CONFIG42_STROBE_ISOLATION_BEFORE',
                       'SP11_VD55G0_CONFIG42_STROBE_ISOLATION_AFTER','SP11_VD55G0_CONFIG42_READBACK=PASS'):
            need(marker in st,'module marker '+marker)
        for bad in ('v4l2_async','request_firmware','media_entity','led_classdev'):
            need(bad not in st,'forbidden binary symbol '+bad)

    need(not Path('/sys/module/sp11_vd55g0_config42probe').exists(),'module must remain unloaded')
    need('sp11_camera_e004h' not in Path('/proc/cmdline').read_text(),'runtime not performed')

    result={
      'schema':'sp11-camera-e004h-safe42-config-authority-v1',
      'status':'PASS_OFFLINE_SAFE42_WINDOWS_CONFIG_AUTHORITY',
      'parent':'E004f proven patch/boot prefix + E004g illumination isolation',
      'dtb_sha256':DTB_SHA,'module_sha256':MODULE_SHA,
      'module_two_builds_byte_reproducible':True,
      'surface_patch_sha256':PATCH_SHA,
      'windows_full43_sequence_sha256':FULL43_SHA,
      'safe42_sequence_sha256':SAFE42_SHA,
      'expected_total_sensor_data_writes':596,
      'safe_final_config_writes':42,
      'isolated_strobe':{'register':'0x0468','windows_value':'0x02','writes_authorized':False},
      'runtime_guards':[
        'read 0x0468 before safe42',
        'reject any safe42 table entry at 0x0468',
        'read 0x0468 after safe42 and require unchanged',
        'read back Windows transport/timing/exposure/ROI and GPIO0/2/3 settings',
        'remain in SW_STBY',
      ],
      'camss':False,'v4l2':False,'stream':False,'external_illumination':False,
      'linux_runtime_performed':False,'runtime_authorized':False,
      'next_gate':'Package/checkpoint a one-shot E004i runtime for the exact safe42 subset; one attempt only; success powers off and returns Golden.'
    }
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('E004H_VERIFY=PASS MODULE_SHA256='+MODULE_SHA+' DTB_SHA256='+DTB_SHA)
    print('E004H_WINDOWS_CONFIG=FULL43_SHA256='+FULL43_SHA+' SAFE42_SHA256='+SAFE42_SHA)
    print('E004H_SAFETY=PASS 0x0468_EXCLUDED=YES RUNTIME_GUARD=YES READBACK=YES CAMSS=NO STREAM=NO ILLUMINATION=NO')
    print('E004H_RUNTIME=NO')

if __name__=='__main__':
    main()
