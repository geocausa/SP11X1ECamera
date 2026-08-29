#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(text, *parts):
    for p in parts:
        if p not in text: die('missing source contract: '+p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--camss',type=Path,required=True)
    ap.add_argument('--video',type=Path,required=True)
    ap.add_argument('--vfe',type=Path,required=True)
    ap.add_argument('--csid',type=Path,required=True)
    ap.add_argument('--csid680',type=Path,required=True)
    ap.add_argument('--csiphy',type=Path,required=True)
    ap.add_argument('--object',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    c=a.camss.read_text(); v=a.video.read_text(); vf=a.vfe.read_text(); cs=a.csid.read_text(); c680=a.csid680.read_text(); phy=a.csiphy.read_text()
    need(c,
         'camss_x1e_pix_hw_order_contract __used',
         '.pipeline_pm_owns_resource_power = true',
         '.vfe1_resource_power_reuses_vfe_get = true',
         '.csid1_power_reuses_subdev_power = true',
         '.csid1_ipp_reuses_hw_configure_stream = true',
         '.csiphy2_power_reuses_subdev_power = true',
         '.csiphy2_lanes_reuse_subdev_stream = true',
         '.sensor_reuses_subdev_stream = true',
         '.generic_vfe1_pix_stream_forbidden = true',
         '.replay01_before_isp_done = true',
         '.replay23_after_isp_done = true',
         '.replay01_vs_csid_start_closed = false',
         '.replay23_vs_mipi_sensor_start_closed = false',
         '.callable_runner_authorized = false')
    need(v, 'v4l2_pipeline_pm_get(&vdev->entity)', 'v4l2_pipeline_pm_put(&vdev->entity)')
    need(vf, 'ret = vfe_get(vfe);', 'vfe_put(vfe);', 'line->id == VFE_LINE_PIX)', 'return -EOPNOTSUPP;')
    need(cs, 'ret = csid->res->parent_dev_ops->get(camss, csid->id);', 'csid->phy.need_vc_update = true;', 'csid->res->hw_ops->configure_stream(csid, enable);', '.s_power = csid_set_power', '.s_stream = csid_set_stream')
    need(c680, '__csid_sp11_front_ipp_mode0', '__csid_configure_ipp_stream', '__csid_ctrl_ipp(csid, enable);', '__csid_configure_rx(csid, &csid->phy, 0);')
    need(phy, '.s_power = csiphy_set_power', '.s_stream = csiphy_set_stream', 'csiphy->res->hw_ops->lanes_enable', 'csiphy->res->hw_ops->lanes_disable')
    nm=subprocess.check_output(['nm','-an',str(a.object)],text=True)
    if ' camss_x1e_pix_hw_order_contract' not in nm: die('contract symbol missing')
    rel=subprocess.check_output(['objdump','-r',str(a.object)],text=True)
    refs=[x for x in rel.splitlines() if 'camss_x1e_pix_hw_order_contract' in x]
    if refs: die('runtime relocation references contract')
    out={
      'accepted':True,
      'schema':'sp11-e003h-pix-hardware-order-contract-v1',
      'source_sha256':sha(a.camss),
      'object_sha256':sha(a.object),
      'contract_symbol_retained':True,
      'contract_relocation_references':0,
      'power_boundary':'reuse video_prepare_streaming v4l2_pipeline_pm_get/put; do not duplicate resource refs in PIX runner',
      'vfe1':'reuse vfe_get/put for resource power only; generic VFE1 PIX s_stream stays fail-closed',
      'csid1':'reuse existing subdev power; IPP start uses existing X1E CSID680 configure_stream path',
      'csiphy2':'reuse existing subdev power + stream lane enable/disable',
      'steady_order':'Epoch0 raw poll -> BUS IOVA update -> five-BL RT-CDM submit -> VIDEO raw poll/retirement',
      'stop_order':'CSID1 IPP stop -> VFE1 BUS stop -> RT-CDM mask/close -> one observed-valid CSIPHY2/sensor tail',
      'rollback':'sensor -> CSIPHY2 -> CSID1 -> BUS -> RT-CDM -> capsule DMA -> pipeline PM',
      'open_gaps':['replay0/1 exact placement versus CSID1 start','replay2/3 exact placement versus CSIPHY2/sensor start'],
      'callable_runner_authorized':False,
      'runtime_reachable':False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: cross-file PIX power/start/stop reuse and rollback contract retained with two priming placement gaps explicit')
if __name__=='__main__': main()
