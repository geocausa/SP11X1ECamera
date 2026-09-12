#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, subprocess, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PARENT=REPO/'experiments/E004-front-ir-vd55g0/e004l-native-bind-only-authority/x1e80100-microsoft-denali-sp11-e004l-native-bind.dtb'
DTB=HERE/'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb'
BUILDER=HERE/'build-e004o-dtb.py'
HVB=REPO/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hv-current-golden-camera-dtb-merge/build-hv-dtb.py'

PARENT_SHA='dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b'
DTB_SHA='fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742'
IR_SENSOR='/soc@0/cci@ac15000/i2c-bus@0/camera@60'
IR_EP=IR_SENSOR+'/port/endpoint'
CAMSS_PORTS='/soc@0/isp@acb7000/ports'
IR_CAM_EP=CAMSS_PORTS+'/port@0/endpoint'
REMOVE_ROOTS=[
 CAMSS_PORTS+'/port@1',
 CAMSS_PORTS+'/port@2',
 '/soc@0/cci@ac15000/i2c-bus@1/camera@10',
 '/soc@0/cci@ac16000/i2c-bus@1/camera@10',
]

def need(v,m):
    if not v:
        raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

spec=importlib.util.spec_from_file_location('hv',HVB)
hv=importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)

need(sha(PARENT)==PARENT_SHA,'parent identity')
need(sha(DTB)==DTB_SHA,'IR-only DT identity')

parent=hv.parse_fdt(PARENT)
out=hv.parse_fdt(DTB)

expected_removed={p for p in parent for root in REMOVE_ROOTS if p==root or p.startswith(root+'/')}
actual_removed=set(parent)-set(out)
need(actual_removed==expected_removed,
     'removed node set drift expected=%r actual=%r' % (sorted(expected_removed),sorted(actual_removed)))
need(not (set(out)-set(parent)),'unexpected added nodes')

changed=[]
for p in out:
    for k in set(parent[p])|set(out[p]):
        if parent[p].get(k)!=out[p].get(k):
            changed.append((p,k,parent[p].get(k),out[p].get(k)))
need(changed==[],'surviving properties changed '+repr(changed))

ports=subprocess.check_output(['fdtget','-l',str(DTB),CAMSS_PORTS],text=True).split()
need(ports==['port@0'],'CAMSS must advertise only IR port0')
need(subprocess.check_output(['fdtget','-t','s',str(DTB),IR_SENSOR,'compatible'],text=True).strip()
     =='microsoft,sp11-vd55g0','IR compatible')
need(subprocess.check_output(['fdtget','-t','i',str(DTB),IR_CAM_EP,'data-lanes'],text=True).strip()=='0',
     'receiver lane position 0')
need(subprocess.check_output(['fdtget','-t','i',str(DTB),IR_CAM_EP,'bus-type'],text=True).strip()=='4',
     'receiver DPHY')
need(subprocess.check_output(['fdtget','-t','i',str(DTB),IR_EP,'data-lanes'],text=True).strip()=='1',
     'sensor one-lane convention')
need(subprocess.check_output(['fdtget','-t','i',str(DTB),IR_EP,'bus-type'],text=True).strip()=='4',
     'sensor DPHY')
# link-frequencies is a two-cell 64-bit number; preserve the exact parent bytes.
need(out[IR_EP]['link-frequencies']==parent[IR_EP]['link-frequencies'],'IR 420MHz endpoint changed')
need(out[IR_EP]['remote-endpoint']==parent[IR_EP]['remote-endpoint'],'IR sensor remote changed')
need(out[IR_CAM_EP]['remote-endpoint']==parent[IR_CAM_EP]['remote-endpoint'],'IR CAMSS remote changed')

# Camera-only phandles removed with RGB graph; IR pair remains.
for ph in (0x2ca,0x2cb,0x2cc,0x2cd):
    raw=ph.to_bytes(4,'big')
    need(all(raw not in props.values() for props in out.values()),f'old RGB camera phandle {ph:#x} still referenced')
need(out[IR_EP]['phandle']==(0x2d2).to_bytes(4,'big'),'IR sensor endpoint phandle')
need(out[IR_CAM_EP]['phandle']==(0x2d3).to_bytes(4,'big'),'IR CAMSS endpoint phandle')

with tempfile.TemporaryDirectory(prefix='e004o-dts-') as td:
    dts=Path(td)/'x.dts'
    cp=subprocess.run(['dtc','-I','dtb','-O','dts',str(DTB),'-o',str(dts)],
                      text=True,capture_output=True,check=True)
    t=dts.read_text()
    need('compatible = "sony,imx681";' not in t,'front RGB sensor remains')
    need('compatible = "ovti,ov13858";' not in t,'rear RGB sensor remains')
    need('compatible = "microsoft,sp11-vd55g0";' in t,'IR sensor missing')
    need('remote-endpoint = <0x2ca>' not in t and 'remote-endpoint = <0x2cb>' not in t and
         'remote-endpoint = <0x2cc>' not in t and 'remote-endpoint = <0x2cd>' not in t,
         'orphaned RGB remote-endpoint remains')
    warnings=[x for x in cp.stderr.splitlines() if ': Warning ' in x]

with tempfile.TemporaryDirectory(prefix='e004o-rebuild-') as td:
    q=Path(td)/'out.dtb'
    subprocess.run(['python3',str(BUILDER),'--parent',str(PARENT),'--out',str(q)],
                   check=True,stdout=subprocess.DEVNULL)
    need(sha(q)==DTB_SHA,'deterministic rebuild')

result={
 'schema':'sp11-camera-e004o-ir-only-graph-authority-v1',
 'status':'PASS_OFFLINE_IR_ONLY_CAMSS_GRAPH_AUTHORITY',
 'parent_e004l_dtb_sha256':PARENT_SHA,
 'dtb_sha256':DTB_SHA,
 'removed_roots':REMOVE_ROOTS,
 'removed_node_count':len(expected_removed),
 'added_nodes':0,
 'changed_surviving_properties':0,
 'camss_external_ports':['port@0'],
 'ir_sensor':{
   'compatible':'microsoft,sp11-vd55g0',
   'sensor_data_lanes':[1],
   'receiver_data_lane_positions':[0],
   'bus':'DPHY',
   'link_frequency_hz':420000000,
 },
 'rgb_camera_nodes_present':False,
 'orphaned_rgb_remote_endpoints':False,
 'internal_camss_fabric_changed':False,
 'runtime_performed':False,
 'runtime_authorized':False,
 'next_gate':'Package a fresh bind-only one-shot using this IR-only DT, E004l native sensor, E004k CAMSS and the E004n V4L2 contract harness. Require notifier completion, immutable IR->CSIPHY0 link, subdev node, runtime suspend and direct stream refusal.'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(f'E004O_VERIFY=PASS REMOVED_NODES={len(expected_removed)} SURVIVING_PROPERTY_CHANGES=0')
print('E004O_CAMSS_PORTS=IR_ONLY_PORT0 RGB_SENSOR_NODES=ABSENT ORPHAN_RGB_PHANDLES=NO')
print('E004O_IR_GRAPH=VD55G0->CSIPHY0 DPHY SENSOR_LANE1 RECEIVER_POS0 LINK=420000000')
print('E004O_RUNTIME=NO')
