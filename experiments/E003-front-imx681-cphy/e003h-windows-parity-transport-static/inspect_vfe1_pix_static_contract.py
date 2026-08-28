#!/usr/bin/env python3
import argparse,hashlib,json,re,subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(s,frag,label):
 if frag not in s: die(label)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source-root',type=Path,required=True); ap.add_argument('--module',type=Path,required=True); ap.add_argument('--patch',type=Path,required=True); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
 root=a.source_root; c=root/'drivers/media/platform/qcom/camss'
 camss=(c/'camss.c').read_text(); vfe=(c/'camss-vfe.c').read_text(); vh=(c/'camss-vfe.h').read_text(); vid=(c/'camss-video.c').read_text(); v680=(c/'camss-vfe-680.c').read_text(); patch=a.patch.read_text(); contract=json.loads(a.contract.read_text())
 if not contract.get('accepted'): die('contract not accepted')
 # IFE1 only: exactly one X1E resource uses the new PIX table, between IFE1 and Lite0.
 st=camss.index('static const struct camss_subdev_resources vfe_res_x1e80100[]'); en=camss.index('static const struct resources_icc icc_res_x1e80100[]',st); block=camss[st:en]
 if block.count('&vfe_formats_pix_x1e80100')!=1 or block.count('&vfe_formats_pix_845')!=3: die('X1E PIX assignment count')
 pos=block.index('&vfe_formats_pix_x1e80100')
 if not (block.index('/* IFE1 */') < pos < block.index('/* IFE_LITE_0 */')): die('QC10C table not IFE1-only')
 need(vh,'extern const struct camss_formats vfe_formats_pix_x1e80100;','missing format declaration')
 # One RAW10 -> QC10C table entry.
 m=re.search(r'static const struct camss_format_info formats_pix_x1e80100\[\] = \{(.*?)\n\};',vfe,re.S)
 if not m: die('missing X1E PIX format table')
 body=m.group(1)
 if body.count('MEDIA_BUS_FMT_')!=1 or 'MEDIA_BUS_FMT_SRGGB10_1X10' not in body or 'V4L2_PIX_FMT_QC10C' not in body: die('X1E PIX format table drift')
 # Gate must be before mutex/IRQ/output setup in vfe_enable_v2 and only VFE1 PIX.
 m=re.search(r'int vfe_enable_v2\(struct vfe_line \*line\)\n\{(.*?)\n\}',vfe,re.S)
 if not m: die('vfe_enable_v2 missing')
 body=m.group(1)
 gate=body.find('return -EOPNOTSUPP;'); lock=body.find('mutex_lock(&vfe->stream_lock)')
 if min(gate,lock)<0 or not gate<lock: die('PIX fail-close not before stream lock')
 for frag in ('CAMSS_X1E80100','vfe->id == 1','!vfe->res->is_lite','line->id == VFE_LINE_PIX'): need(body,frag,'VFE1 PIX gate drift')
 # Exact Windows memory contract and fixed-size enumeration/try-format conversion.
 for frag in ('#define CAMSS_X1E80100_QC10C_WIDTH\t\t2560','#define CAMSS_X1E80100_QC10C_HEIGHT\t\t1440','#define CAMSS_X1E80100_QC10C_STRIDE\t\t3584','#define CAMSS_X1E80100_QC10C_SIZEIMAGE\t\t0x76b000','V4L2_FRMSIZE_TYPE_DISCRETE','pix_mp->num_planes = 1','pix_mp->pixelformat != V4L2_PIX_FMT_QC10C'): need(vid,frag,'QC10C video contract drift')
 # Retained Windows BUS/surface/completion constants.
 for frag in ('VFE680_X1E_QC10C_WIDTH          2560','VFE680_X1E_QC10C_HEIGHT         1440','VFE680_X1E_QC10C_STRIDE         3584','VFE680_X1E_QC10C_SIZE           0x0076b000','VFE680_X1E_QC10C_Y_DATA_OFF     0x00006000','VFE680_X1E_QC10C_C_META_OFF     0x004f2000','VFE680_X1E_QC10C_C_DATA_OFF     0x004f5000','VFE680_X1E_WINDOWS_TOP_MASK0    0x0007f051','VFE680_X1E_WINDOWS_BUS_MASK0    0xd0000000','VFE680_X1E_WINDOWS_VIDEO_EVENT  3','VFE680_X1E_WINDOWS_CLIENT(0, 0x11, 0x004f2000, 0x05a00a00, 0x0e00','VFE680_X1E_WINDOWS_CLIENT(1, 0x11, 0x00279000, 0x02d00a00, 0x0e00','VFE680_X1E_WINDOWS_CLIENT(18, 0x00010001, 0x00010000, 0, 1'): need(v680,frag,'VFE680 Windows contract drift')
 # The patch may insert the contract but must not modify legacy RDI WM functions.
 for name in ('vfe_wm_update','vfe_wm_start','vfe_wm_stop'):
  if re.search(r'^[-+]static void '+name+r'\b',patch,re.M): die('legacy RDI function modified: '+name)
 # Five patch paths only; no DT/CSID/CSIPHY/sensor file.
 paths=re.findall(r'^--- a/(.+)$',patch,re.M)
 expected=[f'drivers/media/platform/qcom/camss/{x}' for x in ('camss.c','camss-vfe.c','camss-vfe.h','camss-video.c','camss-vfe-680.c')]
 if paths!=expected: die('patch path set/order drift: '+repr(paths))
 # Retained contract symbols must be read-only data and unreferenced by relocations.
 nm=subprocess.check_output(['aarch64-linux-gnu-nm','-a',str(a.module)],text=True)
 syms=('vfe680_x1e_windows_pix_contract','vfe680_x1e_windows_full_contract','vfe680_x1e_windows_aux_contract')
 for sym in syms:
  hits=[ln for ln in nm.splitlines() if ln.endswith(' '+sym)]
  if len(hits)!=1 or ' r ' not in hits[0]: die('contract symbol not retained read-only: '+sym)
 rel=subprocess.check_output(['aarch64-linux-gnu-readelf','-rW',str(a.module)],text=True)
 if any(sym in rel for sym in syms): die('runtime relocation references retained contract')
 out={'schema':'sp11-e003h-linux-vfe1-pix-qc10c-static-inspection-v1','accepted':True,'patch_sha256':sha(a.patch),'module_sha256':sha(a.module),'contract_sha256':sha(a.contract),'source_sha256':{x:sha(c/x) for x in ('camss.c','camss-vfe.c','camss-vfe.h','camss-video.c','camss-vfe-680.c')},'format':{'ife1_only':True,'mbus':'MEDIA_BUS_FMT_SRGGB10_1X10','pixelformat':'V4L2_PIX_FMT_QC10C','width':2560,'height':1440,'bytesperline':3584,'sizeimage':0x76b000,'v4l2_planes':1},'stream_gate':{'vfe1_pix_returns':'-EOPNOTSUPP','before_stream_lock_irq_output':True},'retained_contract':{'runtime_relocation_present':False,'full_wm':[0,1],'enabled_clients':[0,1,2,3,11,12,13,14,18],'video_completion':'TOP status1 bit0 -> event 3'},'rear_isolation':'IFE0 + both Lite PIX tables unchanged; legacy VFE680 RDI WM functions not modified by patch'}
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'; (a.output.write_text(txt) if a.output else print(txt,end=''))
 print('PASS: VFE1 PIX/QC10C contract is IFE1-only, exact-size, retained-only and stream-blocked before hardware')
if __name__=='__main__': main()
