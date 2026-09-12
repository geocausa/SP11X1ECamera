#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, re, shutil, struct, subprocess, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SRC=REPO/'src/front-ir-vd55g0/sp11-vd55g0-native'
C=SRC/'sp11-vd55g0.c'
GEN=SRC/'generate_windows_header.py'
HEADER=SRC/'surface-windows.generated.h'
MAKEFILE=SRC/'Makefile'
PROV=SRC/'PROVENANCE.md'
BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
HVB=REPO/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hv-current-golden-camera-dtb-merge/build-hv-dtb.py'
PARENT=REPO/'experiments/E004-front-ir-vd55g0/e004h-safe42-config-authority/x1e80100-microsoft-denali-sp11-e004h-config42.dtb'
DTB=HERE/'x1e80100-microsoft-denali-sp11-e004l-native-bind.dtb'
BUILDER=HERE/'build-e004l-dtb.py'

C_SHA='20bca88eb4333f386e76e17d800268511dcf30fbc0b642d39e425e00703d6745'
GEN_SHA='c430516b496f41780d45cbef08cb0698c7619410cc8ada6df1552bbfaa2d7167'
HEADER_SHA='40f9731061ba327c423da3322abdc9a20e07251073c39c266027dac55de1fd9e'
MAKE_SHA='41d9f14e276a79819f1a456a04b9a13b3632061326fb2d74e862c11af1d67c06'
PROV_SHA='11b48aa983a99b248f1db10a51b613f0d37f52dca7e4ee383e5e349b2cfad5f2'
MODULE_SHA='4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72'
PARENT_SHA='e29c787acf9e2f1330a4e73fd8014aba118a2f0a59be51c86859a9ab7fed4ef2'
DTB_SHA='dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b'
PATCH_SHA='5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321'
SAFE42_SHA='159647774f45331210044d0680e50bf16e8aaeeb8c3e98449d2cef7adeffacb2'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
NODE='/soc@0/cci@ac15000/i2c-bus@0/camera@60'

ALLOWED_UNDEFINED={
 'clk_disable','clk_enable','clk_get_rate','clk_prepare','clk_set_rate','clk_unprepare',
 '_dev_err','dev_err_probe','_dev_info','devm_clk_get','devm_gpiod_get','devm_kmalloc',
 'devm_regulator_get','_dev_warn','gpiod_set_value_cansleep','i2c_del_driver',
 'i2c_register_driver','i2c_transfer','media_entity_pads_init','memcmp',
 '__pm_runtime_disable','pm_runtime_enable','pm_runtime_force_resume',
 'pm_runtime_force_suspend','__pm_runtime_idle','__pm_runtime_set_status',
 'regulator_disable','regulator_enable','regulator_get_voltage','__stack_chk_fail',
 '__ubsan_handle_load_invalid_value','__ubsan_handle_out_of_bounds',
 'usleep_range_state','v4l2_async_register_subdev_sensor',
 'v4l2_async_unregister_subdev','v4l2_ctrl_handler_free',
 'v4l2_ctrl_handler_init_class','v4l2_ctrl_new_int_menu','v4l2_ctrl_new_std',
 'v4l2_i2c_subdev_init','v4l2_subdev_cleanup','v4l2_subdev_get_fmt',
 '__v4l2_subdev_init_finalize','__v4l2_subdev_state_get_format',
}

def need(v,m):
    if not v: raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

spec=importlib.util.spec_from_file_location('hv',HVB)
hv=importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)

def dt_warnings(p):
    with tempfile.TemporaryDirectory(prefix='e004l-dtc-') as td:
        cp=subprocess.run(['dtc','-I','dtb','-O','dtb',str(p),'-o',str(Path(td)/'x.dtb')],
                          text=True,capture_output=True,check=True)
    return sorted(x.split(': Warning ',1)[1] for x in cp.stderr.splitlines() if ': Warning ' in x)

def parse_header():
    s=HEADER.read_text()
    patch_sec=s.split('static const u8 sp11_surface_patch',1)[1].split('};',1)[0]
    patch=bytes(int(x,16) for x in re.findall(r'0x([0-9a-fA-F]{2})',patch_sec))
    safe_sec=s.split('static const struct sp11_reg8 sp11_windows_safe42',1)[1].split('};',1)[0]
    safe=[(int(a,16),int(v,16)) for a,v in re.findall(r'0x([0-9a-fA-F]{4}),\s*0x([0-9a-fA-F]{2})',safe_sec)]
    return patch,safe

def seqhash(rows):
    return hashlib.sha256(b''.join(struct.pack('<HB',a,v) for a,v in rows)).hexdigest()

def build_once(log):
    subprocess.run(['make','-C',str(BUILD),f'M={SRC}','clean'],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['python3',str(GEN)],check=True,stdout=subprocess.DEVNULL)
    with open(log,'w') as f:
        subprocess.run(['make','-C',str(BUILD),f'M={SRC}','modules','V=0'],check=True,stdout=f,stderr=subprocess.STDOUT)
    return SRC/'sp11-vd55g0.ko'

need(sha(C)==C_SHA,'native source identity')
need(sha(GEN)==GEN_SHA,'generator identity')
need(sha(MAKEFILE)==MAKE_SHA,'Makefile identity')
need(sha(PROV)==PROV_SHA,'provenance identity')
need(sha(PARENT)==PARENT_SHA,'parent DTB identity')
need(sha(DTB)==DTB_SHA,'native DTB identity')

subprocess.run(['python3',str(GEN)],check=True,stdout=subprocess.DEVNULL)
need(sha(HEADER)==HEADER_SHA,'generated header identity')
patch,safe=parse_header()
need(len(patch)==552 and hashlib.sha256(patch).hexdigest()==PATCH_SHA,'Surface patch')
need(len(safe)==42 and seqhash(safe)==SAFE42_SHA,'safe42 sequence')
need(all(a not in (0x0201,0x0202,0x0468) for a,_ in safe),'safe42 contains stream/strobe register')

c=C.read_text()
for token in (
 '#define SP11_VD55G0_LINK_FREQ_HZ        420000000LL',
 '#define SP11_VD55G0_PIXEL_RATE_HZ        84000000LL',
 '#define SP11_VD55G0_LINE_LENGTH               1200',
 '#define SP11_VD55G0_FRAME_LENGTH              1955',
 'MEDIA_BUS_FMT_Y10_1X10',
 'config->type = V4L2_MBUS_CSI2_DPHY;',
 'config->bus.mipi_csi2.num_data_lanes = 1;',
 'config->link_freq = SP11_VD55G0_LINK_FREQ_HZ;',
 'SP11_VD55G0_NATIVE_STROBE_BASELINE=PASS',
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596',
 'SP11_VD55G0_NATIVE_STREAM_BLOCK=PASS',
 'return -EOPNOTSUPP;',
 'v4l2_async_register_subdev_sensor',
 '"microsoft,sp11-vd55g0"',
):
    need(token in c,'source contract '+token)
need('0x0201' not in c and '0x0202' not in c,'source contains direct stream register')
need('V4L2_CID_LINK_FREQ' in c and 'V4L2_CID_PIXEL_RATE' in c,'required controls')
need('SP11_WINDOWS_ISOLATED_STROBE_VALUE' in c and
     'gpio_before != SP11_WINDOWS_ISOLATED_STROBE_VALUE' in c,'post-boot strobe baseline gate')
need('writes != 596' in c,'exact init write count gate')

parent=hv.parse_fdt(PARENT); out=hv.parse_fdt(DTB)
need(set(parent)==set(out),'DT node set changed')
changes=[]
for p in parent:
    for k in set(parent[p])|set(out[p]):
        if parent[p].get(k)!=out[p].get(k):
            changes.append((p,k,parent[p].get(k),out[p].get(k)))
need(len(changes)==1 and changes[0][0]==NODE and changes[0][1]=='compatible','DT change not compatible-only')
need(out[NODE]['compatible'].rstrip(b'\0')==b'microsoft,sp11-vd55g0','native compatible')
need(dt_warnings(DTB)==dt_warnings(PARENT),'DTC warning regression')
with tempfile.TemporaryDirectory(prefix='e004l-dtb-rebuild-') as td:
    q=Path(td)/'out.dtb'
    subprocess.run(['python3',str(BUILDER),'--parent',str(PARENT),'--out',str(q)],check=True,stdout=subprocess.DEVNULL)
    need(sha(q)==DTB_SHA,'DT deterministic rebuild')

# Endpoint contract: CAMSS receiver consumes lane position 0; sensor endpoint carries one-lane/420MHz.
with tempfile.TemporaryDirectory(prefix='e004l-dts-') as td:
    dts=Path(td)/'x.dts'
    subprocess.run(['dtc','-I','dtb','-O','dts',str(DTB),'-o',str(dts)],check=True,
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    t=dts.read_text()
    cam=t.split('port@0 {',1)[1].split('};',1)[0]
    need('data-lanes = <0x00>;' in cam and 'bus-type = <0x04>;' in cam,'CSIPHY0 receiver lane0 DPHY')
    sens=t.split('camera@60 {',1)[1].split('clock-controller@100000',1)[0]
    need('link-frequencies = <0x00 0x1908b100>;' in sens,'sensor 420MHz endpoint')
    need('data-lanes = <0x01>;' in sens and 'bus-type = <0x04>;' in sens,'sensor one-lane DPHY endpoint')

with tempfile.TemporaryDirectory(prefix='e004l-build-') as td:
    td=Path(td)
    a=build_once(td/'a.log'); ac=td/'a.ko'; shutil.copyfile(a,ac)
    b=build_once(td/'b.log'); bc=td/'b.ko'; shutil.copyfile(b,bc)
    need(sha(ac)==sha(bc)==MODULE_SHA,'native module hashes')
    need(ac.read_bytes()==bc.read_bytes(),'native module byte reproducibility')
    mi=subprocess.check_output(['modinfo',str(bc)],text=True)
    verm=next(x for x in mi.splitlines() if x.startswith('vermagic:')).split(':',1)[1].strip()
    need(verm==VERMAGIC,'Golden vermagic')
    need('alias:          i2c:sp11-vd55g0' in mi,'i2c alias')
    nm=subprocess.check_output(['nm','-u',str(bc)],text=True)
    undefined={x.split()[-1] for x in nm.splitlines() if x.strip()}
    need(undefined==ALLOWED_UNDEFINED,'undefined symbol drift '+repr(sorted(undefined^ALLOWED_UNDEFINED)))
    st=subprocess.check_output(['strings',str(bc)],text=True,errors='replace')
    for marker in (
      PATCH_SHA, 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596',
      'SP11_VD55G0_NATIVE_STREAM_BLOCK=PASS',
      'SP11_VD55G0_NATIVE_BIND=PASS format=Y10_1X10',
    ):
        need(marker in st,'module marker '+marker)

need(not Path('/sys/module/sp11_vd55g0').exists(),'native module must remain unloaded')
need(not Path('/sys/module/qcom_camss').exists(),'CAMSS must remain unloaded')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')

result={
 'schema':'sp11-camera-e004l-native-vd55g0-bind-only-v1',
 'status':'PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY',
 'parent_e004k_commit':'76b8640',
 'source_sha256':C_SHA,
 'generated_header_sha256':HEADER_SHA,
 'module_sha256':MODULE_SHA,
 'module_two_builds_byte_reproducible':True,
 'dtb_sha256':DTB_SHA,
 'dt_delta':'compatible only',
 'sensor_authority':{
   'model':'0x3047','revision':'0x1111 CUT1',
   'surface_patch_sha256':PATCH_SHA,'surface_patch_bytes':552,
   'init_sensor_data_writes':596,'isolated_strobe_writes':0,
   'final_state':'SW_STBY','stream':False,'illumination':False,
 },
 'v4l2_contract':{
   'format':'MEDIA_BUS_FMT_Y10_1X10','width':644,'height':604,
   'phy':'DPHY','data_lanes':1,'link_freq_hz':420000000,
   'pixel_rate_hz':84000000,'line_length':1200,'frame_length':1955,
   'hblank':556,'vblank':1351,'stream_on':'-EOPNOTSUPP',
 },
 'receiver_endpoint':{'csiphy':0,'data_lane_position':0,'bus':'DPHY'},
 'runtime_performed':False,
 'runtime_authorized':False,
 'next_gate':'Package a disposable native-bind one-shot using E004l DTB + native module + E004k CAMSS module. Load CAMSS with E004j parity gate armed, bind sensor, inspect media graph/controls, explicitly verify stream-on is refused, then return Golden.'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('E004L_VERIFY=PASS NATIVE_MODULE_SHA256='+MODULE_SHA+' DTB_SHA256='+DTB_SHA)
print('E004L_SENSOR=WINDOWS_PATCH_552 + SAFE42_42 -> WRITES=596 SW_STBY STREAM=NO ILLUMINATION=NO')
print('E004L_V4L2=Y10_1X10 644x604 DPHY1 LINK=420000000 PIXEL=84000000 STREAM_ON=BLOCKED')
print('E004L_RUNTIME=NO')
