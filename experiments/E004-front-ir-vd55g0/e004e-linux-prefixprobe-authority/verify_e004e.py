#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, re, shutil, subprocess, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
E004D=REPO/'experiments/E004-front-ir-vd55g0/e004d-windows-initialconfig-sequence'
E004B=REPO/'experiments/E004-front-ir-vd55g0/e004b-linux-probe-authority'
SRC=REPO/'src/front-ir-vd55g0/sp11-vd55g0-prefixprobe'
KERNEL=REPO.parents[1]/'02-kernel/build-runtime-v4-headers-20260826'
HVB=REPO/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hv-current-golden-camera-dtb-merge/build-hv-dtb.py'
PARENT=E004B/'x1e80100-microsoft-denali-sp11-e004b-ir-probe.dtb'
DTB=HERE/'x1e80100-microsoft-denali-sp11-e004e-prefixprobe.dtb'
BUILDER=HERE/'build-e004e-dtb.py'
C=SRC/'sp11-vd55g0-prefixprobe.c'
GEN=SRC/'generate_surface_patch_header.py'
HEADER=SRC/'surface-patch.generated.h'

PARENT_SHA='2b9ff2265606aa95006e3c952597c496367106e00aa1e2d1ec1e75b8f9e485e6'
DTB_SHA='d05c4d50a4e2aaaff2216aa765802578c78551d97217cd3e422c9eda6a9c95e9'
C_SHA='731240737947bf5c80238b76c4252b32b6bac13f07bfc4caaa00e6bdccc83ab7'
GEN_SHA='b5cd21276a11122959bb73f608aa9f17ae46d04600e6936756f724cbd4c587c9'
HEADER_SHA='2578a382a5ffd1785c4df4e2ae5cb1c3d7923970840dbafdcaad9e71a85d1f6d'
MODULE_SHA='b257ca820cface72f4d2d28836f3621d8620c2284e23405ce519c26dd3160b1b'
PATCH_SHA='5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
NODE='/soc@0/cci@ac15000/i2c-bus@0/camera@60'

ALLOWED_UNDEFINED={
 'clk_disable','clk_enable','clk_get_rate','clk_prepare','clk_set_rate','clk_unprepare',
 '_dev_err','dev_err_probe','_dev_info','devm_clk_get','devm_gpiod_get','devm_kmalloc',
 'devm_regulator_get','gpiod_set_value_cansleep','i2c_del_driver','i2c_register_driver',
 'i2c_transfer','regulator_disable','regulator_enable','regulator_get_voltage',
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
    with tempfile.TemporaryDirectory(prefix='e004e-dtc-') as td:
        cp=subprocess.run(['dtc','-I','dtb','-O','dtb',str(dt),'-o',str(Path(td)/'x.dtb')],
                          text=True,capture_output=True,check=True)
    return sorted(x.split(': Warning ',1)[1] for x in cp.stderr.splitlines() if ': Warning ' in x)

def build_once(log):
    subprocess.run(['make','-C',str(KERNEL),f'M={SRC}','clean'],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['python3',str(GEN)],check=True,stdout=subprocess.DEVNULL)
    with open(log,'w') as f:
        subprocess.run(['make','-C',str(KERNEL),f'M={SRC}','modules','V=0'],check=True,stdout=f,stderr=subprocess.STDOUT)
    return SRC/'sp11-vd55g0-prefixprobe.ko'

def main():
    subprocess.run(['python3',str(E004D/'verify_e004d.py')],check=True,stdout=subprocess.DEVNULL)

    need(sha(PARENT)==PARENT_SHA,'E004b DT parent')
    need(sha(DTB)==DTB_SHA,'E004e DT identity')
    need(sha(C)==C_SHA,'prefix source identity')
    need(sha(GEN)==GEN_SHA,'patch generator identity')

    parent=hv.parse_fdt(PARENT); out=hv.parse_fdt(DTB)
    need(set(parent)==set(out),'DT node set')
    changes=[]
    for p in parent:
        keys=set(parent[p])|set(out[p])
        for k in keys:
            if parent[p].get(k)!=out[p].get(k):
                changes.append((p,k,parent[p].get(k),out[p].get(k)))
    need(len(changes)==1 and changes[0][0]==NODE and changes[0][1]=='compatible','only compatible changes')
    need(out[NODE]['compatible'].rstrip(b'\0')==b'microsoft,sp11-vd55g0-prefixprobe','prefix compatible')
    need(warnings(DTB)==warnings(PARENT),'DTC warning regression')
    with tempfile.TemporaryDirectory(prefix='e004e-dtb-rebuild-') as td:
        q=Path(td)/'out.dtb'
        subprocess.run(['python3',str(BUILDER),'--parent',str(PARENT),'--out',str(q)],check=True,stdout=subprocess.DEVNULL)
        need(sha(q)==DTB_SHA,'DT deterministic rebuild')

    # Generated Surface patch must come only from exact Windows package.
    subprocess.run(['python3',str(GEN)],check=True,stdout=subprocess.DEVNULL)
    need(sha(HEADER)==HEADER_SHA,'generated patch header identity')
    text=HEADER.read_text()
    arr=text.split('static const u8 sp11_surface_patch',1)[1]
    vals=[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]{2})',arr)]
    need(len(vals)==552,'generated patch byte count')
    need(hashlib.sha256(bytes(vals)).hexdigest()==PATCH_SHA,'generated Surface patch hash')
    need(PATCH_SHA in text,'header patch identity string')

    s=C.read_text()
    need('"microsoft,sp11-vd55g0-prefixprobe"' in s,'private compatible')
    need('model[0] != 0x30 || model[1] != 0x47' in s,'model write gate')
    need('revision[0] != 0x11 || revision[1] != 0x11' in s,'CUT1 write gate')
    need(s.index('SP11_VD55G0_PREFIX_ID_GATE=PASS') < s.index('SP11_VD55G0_PREFIX_PATCH_BEGIN'),'identity before writes')

    # Exact E004d prefix order.
    order=[
      'sp11_poll8(client, VD55G0_REG_SYSTEM_FSM,\n\t\t\t VD55G0_FSM_READY_TO_BOOT, 6, "READY_TO_BOOT")',
      'sp11_write8(client, VD55G0_PATCH_START + i,',
      'sp11_write8(client, VD55G0_REG_BOOT, VD55G0_BOOT_PATCH_SETUP)',
      'sp11_poll8(client, VD55G0_REG_BOOT, 0x00, 28,',
      'sp11_write8(client, VD55G0_REG_BOOT, VD55G0_BOOT_BOOT)',
      'sp11_poll8(client, VD55G0_REG_BOOT, 0x00, 6,',
      'sp11_poll8(client, VD55G0_REG_SYSTEM_FSM,\n\t\t\t VD55G0_FSM_SW_STBY, 4, "SW_STBY")',
      'SP11_VD55G0_PREFIX_COMPLETE',
    ]
    positions=[s.index(x) for x in order]
    need(positions==sorted(positions),'Windows prefix operation order')
    need(s.count('sp11_write8(client,')==3,'only patch loop + setup + boot write sites')
    need('writes != 554' in s,'exact write count gate')
    need('final_config_writes=0' in s,'final config omitted marker')
    need('stream=0 illumination=0' in s,'stream/illumination prohibited marker')
    for forbidden in ('0x0220','0x0224','0x0300','0x044c','0x0467','0x0468','v4l2','media_entity','request_firmware','led_classdev','st,leds'):
        need(forbidden not in s,'forbidden prefix source token '+forbidden)

    # Poll shape: N reads, 1ms delay after mismatch.
    need('for (i = 0; i < attempts; i++)' in s,'bounded poll loop')
    need('usleep_range(1000, 1100);' in s,'1ms poll cadence')
    need('u8 buf[3] = { reg >> 8, reg & 0xff, data };' in s,'16-bit address + 8-bit data transaction')

    with tempfile.TemporaryDirectory(prefix='e004e-module-build-') as td:
        td=Path(td)
        a=build_once(td/'a.log'); acopy=td/'a.ko'; shutil.copyfile(a,acopy)
        b=build_once(td/'b.log'); bcopy=td/'b.ko'; shutil.copyfile(b,bcopy)
        need(sha(acopy)==sha(bcopy)==MODULE_SHA,'two-build module identity')
        need(acopy.read_bytes()==bcopy.read_bytes(),'module byte reproducibility')
        mi=subprocess.check_output(['modinfo',str(bcopy)],text=True)
        vermagic=next(x for x in mi.splitlines() if x.startswith('vermagic:')).split(':',1)[1].strip()
        need(vermagic==VERMAGIC,'Golden vermagic')
        nm=subprocess.check_output(['nm','-u',str(bcopy)],text=True)
        undefined={x.split()[-1] for x in nm.splitlines() if x.strip()}
        need(undefined==ALLOWED_UNDEFINED,'module undefined-symbol surface '+repr(sorted(undefined^ALLOWED_UNDEFINED)))
        st=subprocess.check_output(['strings',str(bcopy)],text=True,errors='replace')
        need(PATCH_SHA in st,'module carries exact Surface patch identity marker')
        need('SP11_VD55G0_PREFIX_COMPLETE' in st,'module completion marker')
        for bad in ('v4l2_async','request_firmware','media_entity','led_classdev'):
            need(bad not in st,'forbidden binary symbol/string '+bad)

    need(not Path('/sys/module/sp11_vd55g0_prefixprobe').exists(),'prefix module must remain unloaded')
    need('sp11_camera_e004e' not in Path('/proc/cmdline').read_text(),'E004e runtime not performed')

    result={
      'schema':'sp11-camera-e004e-linux-prefixprobe-authority-v1',
      'status':'PASS_OFFLINE_E004E_SURFACE_PATCH_BOOT_PREFIX_AUTHORITY',
      'parent':'E004d exact Windows InitialConfig sequence + E004c physical CUT1 identity',
      'dtb_sha256':DTB_SHA,
      'module_sha256':MODULE_SHA,
      'module_two_builds_byte_reproducible':True,
      'generated_patch_header_sha256':HEADER_SHA,
      'surface_patch':{'bytes':552,'sha256':PATCH_SHA,'committed_patch_bytes':False},
      'identity_gate':{'model_be':'0x3047','revision':'0x1111 CUT1','required_before_first_write':True},
      'windows_prefix':[
        'poll 0x002c==1, 6 x 1ms',
        'write 552 Surface patch bytes one transaction per register',
        'write 0x0200=2 PATCH_SETUP',
        'poll 0x0200==0, 28 x 1ms',
        'write 0x0200=1 BOOT',
        'poll 0x0200==0, 6 x 1ms',
        'poll 0x002c==2 SW_STBY, 4 x 1ms',
      ],
      'sensor_data_write_count_if_successful':554,
      'final_43_windows_config_writes':False,
      'sensor_gpio1_strobe_configured':False,
      'camss_activation':False,
      'v4l2_registration':False,
      'stream':False,
      'external_illumination':False,
      'linux_runtime_performed':False,
      'runtime_authorized':False,
      'next_gate':'Package/checkpoint a one-shot manual-load E004f runtime using this exact DTB/module; one attempt only; success ends at SW_STBY then powers off and returns Golden.'
    }
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('E004E_VERIFY=PASS MODULE_SHA256='+MODULE_SHA+' DTB_SHA256='+DTB_SHA)
    print('E004E_PREFIX=554_WRITES SURFACE_PATCH=552 PATCH_SETUP=1 BOOT=1 POLLS=6/28/6/4ms')
    print('E004E_SAFETY=PASS FINAL_CONFIG=NO STROBE_CONFIG=NO CAMSS=NO V4L2=NO STREAM=NO ILLUMINATION=NO')
    print('E004E_RUNTIME=NO')

if __name__=='__main__':
    main()
