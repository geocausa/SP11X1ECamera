#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

EXPECTED = [
    (0x0800, 0x0060),
    (0x0820, 0x0060),
    (0x0840, 0x0060),
    (0x0860, 0x0060),
    (0x18a0, 0x0000),
]

def die(msg):
    raise SystemExit('FAIL: ' + msg)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--hamoa',type=Path,required=True)
    ap.add_argument('--dma-mapping',type=Path,required=True)
    ap.add_argument('--arm-smmu',type=Path,required=True)
    ap.add_argument('--structural-diff',type=Path,required=True)
    ap.add_argument('--summary',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    h=a.hamoa.read_text(); dm=a.dma_mapping.read_text(); sm=a.arm_smmu.read_text()
    props=re.findall(r'iommus\s*=\s*(.*?);',h,re.S)
    candidates=[]
    for prop in props:
        vals=[(int(x,16),int(y,16)) for x,y in re.findall(r'<&apps_smmu\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)>',prop)]
        if (0x0800,0x0060) in vals and (0x18a0,0x0000) in vals:
            candidates.append(vals)
    if len(candidates)!=1: die('CAMSS IOMMU property candidate count !=1: '+repr(candidates))
    got=candidates[0]
    if got != EXPECTED: die('CAMSS IOMMU set drift: '+repr(got))
    need_dma=[
      'if (dma_alloc_direct(dev, ops) || arch_dma_alloc_direct(dev))',
      'else if (use_dma_iommu(dev))',
      'cpu_addr = iommu_dma_alloc(dev, size, dma_handle, flag, attrs);',
    ]
    for x in need_dma:
        if x not in dm: die('DMA API semantic missing: '+x)
    need_smmu=[
      'fwid |= FIELD_PREP(ARM_SMMU_SMR_ID, args->args[0]);',
      'fwid |= FIELD_PREP(ARM_SMMU_SMR_MASK, args->args[1]);',
      'return iommu_fwspec_add_ids(dev, &fwid, 1);',
      'arm_smmu_master_install_s2crs(cfg, S2CR_TYPE_TRANS,',
      'smmu_domain->cfg.cbndx, fwspec);',
    ]
    for x in need_smmu:
        if x not in sm: die('SMMU semantic missing: '+x)
    diff=a.structural_diff.read_text()
    meaningful=[ln for ln in diff.splitlines() if ln.startswith('+') or ln.startswith('-')]
    meaningful=[ln for ln in meaningful if not ln.startswith('+++') and not ln.startswith('---')]
    if len(meaningful)!=2 or not all('iommus =' in ln for ln in meaningful):
        die('DT structural delta is not exactly one iommus replacement')
    out={
      'schema':'sp11-e003h-linux-camss-iommu-five-entry-v1',
      'accepted':True,
      'classification':'LINUX_IMPLEMENTATION',
      'parity_claim':False,
      'runtime_authorized':False,
      'iommu_specifiers':[{'sid':f'0x{x:04x}','mask':f'0x{y:04x}'} for x,y in got],
      'dma_semantics':{
        'coherent_allocation_api':'dma_alloc_coherent -> dma_alloc_attrs',
        'iommu_branch':'use_dma_iommu(dev) -> iommu_dma_alloc(dev, ...)',
        'address_result':'DMA API returns an IOVA from the device DMA/IOMMU domain when IOMMU-backed',
      },
      'smmu_semantics':{
        'of_xlate':'each DT SID/mask is encoded into the device iommu_fwspec',
        'attach':'all fwspec entries are installed as S2CR_TYPE_TRANS to smmu_domain->cfg.cbndx',
        'domain_scope':'one Linux IOMMU domain/context bank for the CAMSS platform device fwspec set',
      },
      'equivalence_basis':'Public X1E CAMSS v13 uses this exact five-entry Linux implementation set; same-machine Windows qcsmmu independently proves 0x18a0/mask0 is a VFE/IFE HLOS route. Exact RT-CDM1 requester->SID remains separately unverified.',
      'source_sha256':{
        'hamoa_dtsi':sha(a.hamoa),
        'dma_mapping_c':sha(a.dma_mapping),
        'arm_smmu_c':sha(a.arm_smmu),
        'structural_diff':sha(a.structural_diff),
        'summary':sha(a.summary),
      },
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: X1E CAMSS five-entry Linux IOMMU implementation and DMA API semantics are mechanically pinned; parity remains unclaimed')
if __name__=='__main__': main()
