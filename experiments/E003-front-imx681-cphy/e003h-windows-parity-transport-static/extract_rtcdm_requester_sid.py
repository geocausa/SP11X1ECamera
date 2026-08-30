#!/usr/bin/env python3
import argparse, hashlib, json, re, struct, subprocess
from pathlib import Path

QCIOMMU_SHA='18e06ef557a9b0ef7d22fa3c8f97909699e915946aeec0a758f3e32cb9676a6c'
QCIOMMU_BYTES=22974
IORT_SHA='c561d68b2c3e731c927481ca37bc97302a2f3dcd24747ebf530b8be19795445b'
IORT_BYTES=5366
QCSMMU_REL='experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-qcsmmu-camera-sid-oracle.json'
HWCDM_REL='experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-ife-cdm/hwcdm-oracle-summary.json'
PUBLIC_V11='https://www.spinics.net/lists/kernel/msg6121499.html'

def die(s): raise SystemExit('FAIL: '+s)
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def git_blob(root, rel): return subprocess.check_output(['git','-C',str(root),'show','HEAD:'+rel])
def git_sha(root, rel): return sha_bytes(git_blob(root, rel))

def parse_iort(raw):
    if raw[:4] != b'IORT': die('IORT signature')
    decl=struct.unpack_from('<I',raw,4)[0]
    if decl != len(raw): die('IORT declared length')
    count, off = struct.unpack_from('<II',raw,36)[:2]
    mappings={}
    pos=off
    for _ in range(count):
        if pos+16>len(raw): die('IORT node header overrun')
        typ=raw[pos]; length=struct.unpack_from('<H',raw,pos+1)[0]
        mcount=struct.unpack_from('<I',raw,pos+8)[0]
        moff=struct.unpack_from('<I',raw,pos+12)[0]
        if not length or pos+length>len(raw): die('IORT node length')
        if mcount:
            base=pos+moff
            for i in range(mcount):
                r=base+i*20
                if r+20>pos+length: die('IORT mapping overrun')
                ib,cnt,ob,oref,flags=struct.unpack_from('<IIIII',raw,r)
                if 0x01030000 <= ib <= 0x01030004:
                    mappings[ib]={'output_sid':ob,'id_count':cnt,'output_reference':oref,'flags':flags,'node_type':typ,'node_offset':pos}
        pos += length
    if pos != len(raw): die(f'IORT node end 0x{pos:x} != 0x{len(raw):x}')
    return mappings

def parse_s1ag(text):
    prefix=r'HKR,Parameters\0\S1AG,"MAP",%REG_BINARY%,'
    line=next((ln for ln in text.splitlines() if ln.lower().startswith(prefix.lower())),None)
    if not line: die('S1AG line missing')
    class M:
        def group(self,n): return line[len(prefix):]
    m=M()
    vals=[]
    for x in m.group(1).split(','):
        x=x.strip()
        if not x: continue
        vals.append(int(x,0))
    if len(vals)%5: die('S1AG record length')
    rec=[]
    for i in range(0,len(vals),5):
        b=vals[i:i+5]
        base=(b[0]<<24)|(b[1]<<16)|(b[2]<<8)|b[3]
        rec.append((base,b[4]))
    desc=None
    for line in text.splitlines():
        if re.search(r';\s*0x01030000\s+0x5\s+//VFE',line,re.I):
            desc=line.strip()
            break
    if not desc: die('VFE S1AG comment missing')
    return rec, desc

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--qciommuext-inf',type=Path,required=True)
    ap.add_argument('--iort',type=Path,required=True)
    ap.add_argument('--repo',type=Path,default=Path('.'))
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); root=a.repo.resolve()
    inf=a.qciommuext_inf.read_bytes(); iort=a.iort.read_bytes()
    if len(inf)!=QCIOMMU_BYTES or sha_bytes(inf)!=QCIOMMU_SHA: die('qciommuext identity drift')
    if len(iort)!=IORT_BYTES or sha_bytes(iort)!=IORT_SHA: die('IORT identity drift')
    if inf.startswith(b'\xff\xfe') or inf.startswith(b'\xfe\xff'):
        text=inf.decode('utf-16')
    else:
        text=inf.decode('utf-16le')
    rec, desc=parse_s1ag(text)
    if (0x01030000,5) not in rec: die('VFE S1AG base/count drift')
    if 'Camera CDM IFE, IFE/SFE RD/WR non-protected stream' not in desc: die('VFE S1AG semantic label drift')
    im=parse_iort(iort)
    expected={0x01030000:0x18a0,0x01030001:0x800,0x01030002:0x860,0x01030003:0x840,0x01030004:0x820}
    if {k:v['output_sid'] for k,v in im.items()} != expected: die('IORT VFE group mapping drift')
    qcs=json.loads((root/QCSMMU_REL).read_text())
    if not qcs.get('accepted') or qcs['source']['sha256']!='c1afd89419c12ca093a7d3b1f80ef980723d78d3549ceb158b9ee1a1ca051846': die('qcsmmu oracle drift')
    cb16={(x['sid'],x['mask']) for x in qcs['cb16_s1_ife_hlos']}
    if cb16 != {(0x800,0x60),(0x18a0,0)}: die('CB16 set drift')
    hw=json.loads((root/HWCDM_REL).read_text())
    if hw.get('status')!='PASS' or hw['windows_isp']['binary_sha256']!='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c': die('HWCDM oracle drift')
    if hw['live']['active_front_engine']!='RT_CDM_1' or not hw['native_acquire']['hardware_cdm_branch_hit']: die('active RT-CDM drift')
    out={
      'schema':'sp11-e003h-windows-rtcdm1-requester-sid-v1','accepted':True,
      'source':{
        'qciommuext8380.inf':{'bytes':len(inf),'sha256':sha_bytes(inf)},
        'live_iort':{'bytes':len(iort),'sha256':sha_bytes(iort)},
        'qcsmmu_oracle_git_sha256':git_sha(root,QCSMMU_REL),
        'hwcdm_oracle_git_sha256':git_sha(root,HWCDM_REL),
      },
      'windows_vfe_hlos_s1ag':{'input_base':'0x01030000','count':5,'semantic_comment':desc.lstrip(';').strip()},
      'windows_iort_group_map':{f'0x{k:08x}':f'0x{v["output_sid"]:04x}' for k,v in sorted(im.items())},
      'windows_qcsmmu_cb16':{'name':'S1_IFE_HLOS','sid_mask':['0x0800/0x0060','0x18a0/0x0000']},
      'windows_front_command_engine':'RT_CDM_1',
      'requester_sid':'0x18a0','requester_context_bank':16,'requester_context_name':'S1_IFE_HLOS',
      'derivation':[
        'Installed qciommuext groups VFE HLOS input IDs 0x01030000..0x01030004 and labels the group Camera CDM IFE plus IFE/SFE RD/WR non-protected streams.',
        'Same-machine live IORT maps group base 0x01030000 to SID 0x18a0; the other four group IDs map to 0x800/0x860/0x840/0x820.',
        'Installed qcsmmu independently places singleton SID 0x18a0 and masked 0x800-family streams in CB16 S1_IFE_HLOS.',
        'Exact qccamisp oracle proves accepted front IFE command execution is hardware RT_CDM1.',
      ],
      'public_vocabulary_crosscheck':{'role':'naming/corroboration only; not behavioral authority','reference':PUBLIC_V11,'statement':'X1E CAMSS IOMMU entry ordering independently names the fifth 0x18a0 entry S1 HLOS CDM IFE non-protected.'},
      'linux_consequence':'For the accepted front IFE command path, RT-CDM1 command fetches use SID 0x18a0 in CB16/S1_IFE_HLOS. A Linux CAMSS DMA domain that includes 0x18a0 can expose coherent command-buffer IOVAs to this requester; the Linux domain wiring is a separate implementation fact.',
      'runtime_authorized':False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: same-machine Windows VFE HLOS group + IORT + qcsmmu identify RT-CDM1 IFE command requester SID 0x18a0')
if __name__=='__main__': main()
