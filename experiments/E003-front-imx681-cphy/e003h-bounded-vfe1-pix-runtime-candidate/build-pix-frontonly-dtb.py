#!/usr/bin/env python3
import argparse, hashlib, subprocess
from pathlib import Path

NODE = '/soc@0/isp@acb7000'
EXPECTED_BASE_SHA256 = '333e3c81c8a490f1b8b444e9a8d8005539799c438f2d03ebc6acfc366074b14e'
EXPECTED_IOMMUS = ['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']

def get(dt, prop, typ='x'):
    return subprocess.check_output(['fdtget','-t',typ,str(dt),NODE,prop], text=True).strip().split()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    if sha(a.base) != EXPECTED_BASE_SHA256:
        raise SystemExit('0041 full DTB identity drift: ' + sha(a.base))
    a.out.write_bytes(a.base.read_bytes())

    reg = get(a.out, 'reg')
    names = get(a.out, 'reg-names', 's')
    irq = get(a.out, 'interrupts')
    inames = get(a.out, 'interrupt-names', 's')
    iommus = get(a.out, 'iommus')
    if len(reg) != 18 * 4 or names[-5:] != ['vfe0','vfe1','vfe_lite0','vfe_lite1','rt_cdm1']:
        raise SystemExit('CAMSS resource layout drift')
    if reg[13*4+3] != 'f000' or reg[14*4+3] != 'f000':
        raise SystemExit('VFE aperture drift')
    if reg[-4:] != ['0','ac26000','0','1000']:
        raise SystemExit('RT-CDM1 resource drift')
    if len(irq) != 14 * 3 or inames[-1] != 'rt_cdm1' or irq[-3:] != ['0','11f','1']:
        raise SystemExit('RT-CDM1 IRQ drift')
    if iommus != EXPECTED_IOMMUS:
        raise SystemExit('0041 IOMMU set drift: ' + repr(iommus))

    # Disposable first-PIX candidate remains front-only. Remove the rear graph so
    # notifier completion cannot depend on OV13858, matching the accepted RDI isolation.
    subprocess.run(['fdtput','-r',str(a.out),NODE+'/ports/port@1'], check=True)
    rear = '/soc@0/cci@ac15000/i2c-bus@1/camera@10'
    subprocess.run(['fdtput','-t','s',str(a.out),rear,'status','disabled'], check=True)
    subprocess.run(['fdtput','-r',str(a.out),rear+'/port'], check=True)

    ports = subprocess.check_output(['fdtget','-l',str(a.out),NODE+'/ports'], text=True).split()
    if ports != ['port@2']:
        raise SystemExit('front-only ports drift: ' + repr(ports))
    if subprocess.check_output(['fdtget','-t','x',str(a.out),NODE+'/ports/port@2/endpoint','bus-type'], text=True).strip() != '1':
        raise SystemExit('front bus type drift')
    if subprocess.check_output(['fdtget','-t','x',str(a.out),NODE+'/ports/port@2/endpoint','data-lanes'], text=True).strip() != '0':
        raise SystemExit('front lane drift')

    # Round-trip validation; only graph diagnostics are fatal here.
    check = Path(str(a.out) + '.check')
    log = Path(str(a.out) + '.dtc.log')
    with log.open('w') as err:
        subprocess.run(['dtc','-I','dtb','-O','dtb',str(a.out),'-o',str(check)], stderr=err, check=True)
    text = log.read_text(errors='replace')
    check.unlink(missing_ok=True)
    if 'graph_endpoint' in text or 'graph_child_address' in text:
        raise SystemExit(text)

    print('base_sha256=' + sha(a.base))
    print('candidate_sha256=' + sha(a.out))
    print('iommus=0x800/0x60,0x820/0x60,0x840/0x60,0x860/0x60,0x18a0/0')
    print('vfe_span=0xf000')
    print('rt_cdm1=0x0ac26000/0x1000 irq=GIC_SPI_287')
    print('ports=port@2 only')

if __name__ == '__main__':
    main()
