#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile

D=Path(__file__).resolve().parent
R=D.parents[2]
J=D.parent/'e004j-csiphy0-dphy-authority'
K=D.parent/'e004k-csiphy0-dphy-parity-module'
S=D.parent/'e004s-dynamic-ir-bind-runtime-r4'
BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
CAMSS_INC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss')

WIN=J/'WINDOWS-CSIPHY0-LIVE2.normalized.txt'
GEN=D/'generate_expected.py'
HDR=D/'csiphy0-windows-expected.generated.h'
SRC=D/'e004t_csiphy_readback_test.c'
MK=D/'Makefile'

def need(v,m):
    if not v: raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

need(sha(WIN)=='fc3994ea2a2d607d8028ed0881b8056e510287d5831fe22b5ea635f1ec109a26','Windows normalized authority')
need(sha(GEN)=='7de2b3ac8dd8025b680c09924538129d7c65f065c4ff8ee02c90cdccaa802917','generator')
need(sha(HDR)=='95007de362b9e10d1369dd255c06e0950fced412169de5e83930bb0afec1e770','expected header')
need(sha(SRC)=='fa0f85ba8163eab7ef5fac7853656df71dae825e1d49587a56e832515d9c5c3b','harness source')
need(sha(MK)=='80cfd2b5ee7a84c8fa03453cc92063a7847976a54b03581968c56e4b3629a2cd','Makefile')

# Regenerate in place and require byte identity.
before=HDR.read_bytes()
subprocess.run(['python3',str(GEN)],check=True,stdout=subprocess.DEVNULL)
need(HDR.read_bytes()==before,'generated table not deterministic')

win={int(a,16):int(v,16) for a,v in (x.split() for x in WIN.read_text().splitlines())}
hs=HDR.read_text()
pairs=[(int(a,16),int(v,16)) for a,v in re.findall(r'\{ 0x([0-9a-fA-F]{4}), 0x([0-9a-fA-F]{8}) \}',hs)]
need(len(pairs)==96,'expected table count')
need(len({o for o,_ in pairs})==96,'duplicate offsets')
bad=[(o,v,win.get(o)) for o,v in pairs if win.get(o)!=v]
need(bad==[],'expected table differs from Windows '+repr(bad))
need(dict(pairs)[0x1014]==0x81,'lane mask')
need(dict(pairs)[0x0008]==0x10 and dict(pairs)[0x0408]==0x10 and
     dict(pairs)[0x0808]==0x10 and dict(pairs)[0x0c08]==0x10 and
     dict(pairs)[0x0e08]==0x10,'settle counts')
need([dict(pairs)[o] for o in range(0x102c,0x1058,4)]==
     [0xff,0xfe,0xe6,0xdf,0xdf,0xfc,0xfb,0x9b,0x7f,0xbf,0xff],
     'Windows common CTRL11..21')

kr=json.load(open(K/'RESULT.json'))
need(kr['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k authority')
need(kr['modeled_windows_receiver_match']=='96/96','E004k model')
sr=json.load(open(S/'RESULT.json'))
need(sr['status']=='PASS_DYNAMIC_ID_NATIVE_BIND_GRAPH_CONTROLS_STREAM_BLOCK_GOLDEN_RETURN_RETIRED','E004s parent')
need(sr['graph']['pass'] is True and sr['sensor']['runtime_pm']=='suspended','E004s graph/runtime')

src=SRC.read_text()
for token in (
 'of_find_compatible_node(NULL, NULL, E004T_COMPAT)',
 'bus_find_device_by_of_node(&i2c_bus_type, np)',
 'client->addr != E004T_ADDR',
 'pm_runtime_status_suspended(&client->dev)',
 'media_pad_remote_pad_first(&sensor_sd->entity.pads[0])',
 'strcmp(remote->entity->name, "msm_csiphy0")',
 'csiphy->id != 0',
 'csiphy->cfg.csi2->lane_cfg.phy_cfg != V4L2_MBUS_CSI2_DPHY',
 'csiphy->cfg.csi2->lane_cfg.num_data != 1',
 'csiphy->cfg.csi2->lane_cfg.data[0].pos != 0',
 'media_pad_remote_pad_first(&csiphy->pads[MSM_CSIPHY_PAD_SRC])',
 'v4l2_subdev_call(csiphy_sd, pad, set_fmt, NULL, &fmt)',
 'v4l2_subdev_call(csiphy_sd, core, s_power, 1)',
 'v4l2_subdev_call(csiphy_sd, video, s_stream, 1)',
 'readl_relaxed(csiphy->base +',
 'v4l2_subdev_call(csiphy_sd, video, s_stream, 0)',
 'v4l2_subdev_call(csiphy_sd, core, s_power, 0)',
 'E004T_CSIPHY0_READBACK',
 'E004T_RECEIVER_END',
):
    need(token in src,'harness token '+token)
need('v4l2_subdev_call(sensor_sd, video, s_stream' not in src,'sensor stream call present')
need('csid' not in src.lower() or 'csid_stream_call=0' in src,'unexpected CSID action')
need('vfe_stream_call=0' in src,'VFE safety marker')
need('illumination=0' in src,'illumination safety marker')
need('MEDIA_BUS_FMT_Y10_1X10' in src and '.width = 644' in src and '.height = 604' in src,'receiver format')

# Makefile must compile against the exact private CAMSS header tree.
mk=MK.read_text()
need(str(CAMSS_INC) in mk,'CAMSS private include path')

# Rebuild twice and require exact bytes.
with tempfile.TemporaryDirectory(prefix='e004t-build-') as td:
    td=Path(td); copies=[]
    for n in ('a','b'):
        subprocess.run(['make','-C',str(BUILD),f'M={D}','clean'],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['make','-C',str(BUILD),f'M={D}','modules','V=0'],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        q=D/'e004t_csiphy_readback_test.ko'; cp=td/f'{n}.ko'
        shutil.copyfile(q,cp); copies.append(cp)
    need(sha(copies[0])==sha(copies[1])=='6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e',
         'module reproducibility')
    need(copies[0].read_bytes()==copies[1].read_bytes(),'module bytes differ')
    mi=subprocess.check_output(['modinfo',str(copies[1])],text=True)
    need('name:           e004t_csiphy_readback_test' in mi,'module name')
    need('7.1.5-sp11-render-parity-v4+' in mi,'Golden vermagic')
    nm=subprocess.check_output(['nm','-u',str(copies[1])],text=True)
    for sym in ('bus_find_device','media_pad_remote_pad_first','of_find_compatible_node',
                'v4l2_subdev_call_wrappers'):
        need((' U '+sym+'\n') in nm,'missing symbol '+sym)
subprocess.run(['make','-C',str(BUILD),f'M={D}','clean'],check=True,stdout=subprocess.DEVNULL)

need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden')
need(not Path('/sys/module/qcom_camss').exists(),'CAMSS loaded during offline stage')
need(not Path('/sys/module/e004t_csiphy_readback_test').exists(),'harness loaded during offline stage')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='PASS_OFFLINE_RECEIVER_ONLY_READBACK_HARNESS_AUTHORITY','result')
need(r['expected_register_count']==96 and r['modeled_windows_matches']==96,'result model')
need(r['sensor_stream_call'] is False and r['capture'] is False and r['illumination'] is False,'result safety')

print('E004T_VERIFY=PASS EXPECTED_REGISTERS=96 WINDOWS_MATCH=96/96')
print('E004T_HARNESS=REPRODUCIBLE SHA256=6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e')
print('E004T_RECEIVER_ONLY=YES SENSOR_STREAM=NO CSID_STREAM=NO VFE_STREAM=NO ILLUMINATION=NO')
print('E004T_RUNTIME=NO')
