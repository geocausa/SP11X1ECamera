#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json, re, shutil, subprocess, tempfile

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
D=REPO/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-static'
BASE=REPO/'experiments/E003-front-imx681-cphy/e003h-bounded-front-first-frame-runtime'
CAP=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-imx681-mode-selection-capture-20260831'
K=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src')
GOLDEN='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
WINDOWS_ORACLE_SHA='4520699c754e131af6126587da87086c973201a9c273df252c279b93ad5916c4'
BLOB_SHA='f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c'
EXPECT_DIFF=[(12,0x0347,0x00,0xf0),(15,0x034a,0x0b,0x0a),(16,0x034b,0x4f,0x5f),
             (31,0x040e,0x0a,0x08),(32,0x040f,0x50,0x70),(35,0x034e,0x0a,0x08),(36,0x034f,0x50,0x70)]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,msg):
    if not x: raise SystemExit('FAIL: '+msg)
def rows(path, value_col):
    out=[]
    with Path(path).open(newline='') as f:
        for r in csv.DictReader(f): out.append((int(r['index']),int(r['address'],16),int(r[value_col],16)))
    return out
def vermagic(p): return subprocess.check_output(['modinfo','-F','vermagic',str(p)],text=True).strip()
def apply_git(repo, patch, reverse=False):
    cmd=['git','apply','--check']+(['--reverse'] if reverse else [])+[str(patch)]
    subprocess.run(cmd,cwd=repo,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def main():
    summary=json.loads((D/'MODE2-SUMMARY.json').read_text())
    need(summary['accepted'] and summary['selected_resolution_index']==2,'mode2 summary not accepted/index2')
    need(summary['sensor_blob_sha256']==BLOB_SHA,'sensor blob SHA')
    need(summary['windows_mode_selection_oracle_sha256']==WINDOWS_ORACLE_SHA,'Windows oracle SHA in mode2 summary')
    gotdiff=[(x['index'],int(x['address'],16),int(x['mode0'],16),int(x['mode2'],16)) for x in summary['mode0_mode2_value_differences']]
    need(gotdiff==EXPECT_DIFF and summary['changed_register_count']==7,'seven-value mode delta')
    need(summary['mode2_records']==68 and summary['mode_select_writes']==0,'mode2 record/MODE_SELECT invariant')
    need((summary['geometry'],summary['fps'],summary['line_length'],summary['frame_length'],summary['pixel_rate_hz'])==('3840x2160',30.0,6752,3554,548570000),'mode2 metadata')

    win=json.loads((CAP/'windows-imx681-mode-selection-oracle.json').read_text())
    need(sha(CAP/'windows-imx681-mode-selection-oracle.json')==WINDOWS_ORACLE_SHA and win['accepted'],'accepted Windows oracle')
    need(win['full_firmware_match']['matching_resolution_indices']==[2] and win['capture']['pair_count']==68,'Windows unique mode2 selection')
    linux_rows=rows(D/'mode2-registers.csv','data'); win_rows=rows(CAP/'captured-resolution-pairs.csv','value')
    need(linux_rows==win_rows and len(linux_rows)==68,'all 68 Linux mode2 pairs equal captured Windows packet')

    src=(D/'imx681.c').read_text(); hdr=(D/'imx681-sp11-mode2-regs.h').read_text()
    need('{ 3840, 2160, 6752, 3554, 548570000, 30 }' in src,'sensor advertises mode2 geometry')
    need('imx681_program_mode2_standby' in src and 'imx681_sp11_mode2_regs' in src,'sensor selects mode2 table')
    need('CCI_REG8(0x0100)' not in hdr,'MODE_SELECT appears in generated table')
    need(hdr.count('static const struct cci_reg_sequence imx681_sp11_mode2_regs[]')==1,'mode2 array')

    camss=(K/'drivers/media/platform/qcom/camss/camss.c').read_text(); csid=(K/'drivers/media/platform/qcom/camss/camss-csid-680.c').read_text()
    need('fmt->width != 3840 || fmt->height != 2160)' in camss,'RT-CDM validator 2160')
    need('csid->fmt[MSM_CSID_PAD_PIX].height != 2160)' in camss,'front runner validator 2160')
    need('fmt->width == 3840 && fmt->height == 2160;' in csid,'CSID front predicate 2160')
    cpatch=(D/'0054-x1e-front-mode2-geometry-contract.patch').read_text()
    plus=[x for x in cpatch.splitlines() if x.startswith('+') and not x.startswith('+++')]
    minus=[x for x in cpatch.splitlines() if x.startswith('-') and not x.startswith('---')]
    need(sum('2160' in x for x in plus)==3 and sum('2640' in x for x in minus)==3,'exactly three CAMSS geometry substitutions')
    need(not any(re.search(r'\b(writel|writeq|cci_write|regmap_write)\s*\(',x) for x in plus),'new CAMSS hardware write in patch')

    spatch=(D/'0054-imx681-mode0-to-windows-mode2.patch').read_text()
    added_regs=[]
    for x in spatch.splitlines():
        if x.startswith('+') and not x.startswith('+++'):
            m=re.search(r'CCI_REG8\(0x([0-9a-fA-F]{4})\), 0x([0-9a-fA-F]{2})',x)
            if m: added_regs.append((int(m.group(1),16),int(m.group(2),16)))
    need(added_regs==[(a,n) for _,a,_,n in EXPECT_DIFF],'sensor patch added register values are exactly seven mode2 deltas')
    need((0x0100,0x01) not in added_regs and (0x0100,0x00) not in added_regs,'sensor patch adds MODE_SELECT')

    # Git-apply semantics: sensor forward from accepted mode0, then reverse from mode2.
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); subprocess.run(['git','init','-q'],cwd=t,check=True)
        shutil.copy2(BASE/'imx681.c',t/'imx681.c'); shutil.copy2(BASE/'imx681-sp11-mode0-regs.h',t/'imx681-sp11-mode0-regs.h')
        subprocess.run(['git','add','.'],cwd=t,check=True); apply_git(t,D/'0054-imx681-mode0-to-windows-mode2.patch')
        subprocess.run(['git','apply',str(D/'0054-imx681-mode0-to-windows-mode2.patch')],cwd=t,check=True)
        need(sha(t/'imx681.c')==sha(D/'imx681.c') and sha(t/'imx681-sp11-mode2-regs.h')==sha(D/'imx681-sp11-mode2-regs.h'),'sensor forward patch hashes')
        apply_git(t,D/'0054-imx681-mode0-to-windows-mode2.patch',reverse=True)
    # CAMSS reverse from live 0054 gives exact pre-0054 hashes, then forward returns exact live hashes.
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); subprocess.run(['git','init','-q'],cwd=t,check=True); p=t/'drivers/media/platform/qcom/camss'; p.mkdir(parents=True)
        shutil.copy2(K/'drivers/media/platform/qcom/camss/camss.c',p/'camss.c'); shutil.copy2(K/'drivers/media/platform/qcom/camss/camss-csid-680.c',p/'camss-csid-680.c')
        subprocess.run(['git','add','.'],cwd=t,check=True); apply_git(t,D/'0054-x1e-front-mode2-geometry-contract.patch',reverse=True)
        subprocess.run(['git','apply','--reverse',str(D/'0054-x1e-front-mode2-geometry-contract.patch')],cwd=t,check=True)
        base_hashes={'camss.c':sha(p/'camss.c'),'camss-csid-680.c':sha(p/'camss-csid-680.c')}
        need(base_hashes=={'camss.c':'b8cb256514337f1767ba5dab002cc59ff4f0c8f73f9be03f83de77ab8b3507c9','camss-csid-680.c':'683c0d5c042d3a8f24be211cda7dc02d06befe31e42aeb29fcd14f117397c81c'},'pre-0054 CAMSS hashes')
        apply_git(t,D/'0054-x1e-front-mode2-geometry-contract.patch')
        subprocess.run(['git','apply',str(D/'0054-x1e-front-mode2-geometry-contract.patch')],cwd=t,check=True)
        need(sha(p/'camss.c')==sha(K/'drivers/media/platform/qcom/camss/camss.c') and sha(p/'camss-csid-680.c')==sha(K/'drivers/media/platform/qcom/camss/camss-csid-680.c'),'CAMSS forward patch hashes')

    need(vermagic(D/'imx681.ko')==GOLDEN,'sensor vermagic')
    need(vermagic(D/'qcom-camss.ko')==GOLDEN,'CAMSS vermagic')
    out={
      'schema':'sp11-e003h-imx681-mode2-parity-0054-static-v1','accepted':True,'runtime_authorized':False,'hardware_execution_performed':False,
      'windows_oracle_sha256':WINDOWS_ORACLE_SHA,'sensor_blob_sha256':BLOB_SHA,'selected_resolution_index':2,'geometry':'3840x2160@30',
      'sensor':{'source_sha256':sha(D/'imx681.c'),'table_sha256':sha(D/'imx681-sp11-mode2-regs.h'),'module_sha256':sha(D/'imx681.ko'),'module_vermagic':vermagic(D/'imx681.ko'),'mode_pairs':68,'windows_pair_equality':True,'changed_values':7,'mode_select_table_writes':0},
      'camss':{'camss_c_sha256':sha(K/'drivers/media/platform/qcom/camss/camss.c'),'csid680_sha256':sha(K/'drivers/media/platform/qcom/camss/camss-csid-680.c'),'module_sha256':sha(D/'qcom-camss.ko'),'module_vermagic':vermagic(D/'qcom-camss.ko'),'geometry_gate_changes':3,'new_mmio_writes':0,'hardware_programming_values_changed':False},
      'patches':{'sensor_sha256':sha(D/'0054-imx681-mode0-to-windows-mode2.patch'),'camss_sha256':sha(D/'0054-x1e-front-mode2-geometry-contract.patch'),'sensor_forward_reverse_exact':True,'camss_forward_reverse_exact':True},
      'next_gate':'publish static checkpoint, then construct a separate unarmed bounded 0054 one-shot package; no runtime until separate authorization'
    }
    blob=json.dumps(out,indent=2,sort_keys=True)+'\n'; (D/'0054-static-inspection.json').write_text(blob); print(blob,end='')
if __name__=='__main__': main()
