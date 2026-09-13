#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess

D=Path(__file__).resolve().parent
P=D.parent
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
K=ROOT/'02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss'
RGB=ROOT/'06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/route-oracle-summary.json'
IR=P/'e004a-windows-authority/E004_WINDOWS_ORACLE_SUMMARY_20260912.json'
W=P/'e004w-csiphy0-readback-runtime-r2/RESULT.json'

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

need(sha(K/'camss-csid.c')=='fc316d35114a23e29333b22a6fb10f9af2f5dfb15ae829a963ecd05c53d6b229','camss-csid source')
need(sha(K/'camss-csid-680.c')=='9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90','csid680 source')
need(sha(K/'camss-csid-gen2.h')=='aa06ec13ac34c76ee71f646dea5b3e7fc98d6d3fc6e19b137eacb1ee37ad6a49','gen2 header')
need(sha(RGB)=='b3d3bd03f17258178d062b879757007cbdf4d909a16e7b2352d9470b431e4317','RGB oracle')
need(sha(IR)=='69d7e9887d16acd78105e4c30eb16d176bbdd92f1bdebaadab8336e87dce40be','IR oracle')

w=json.load(open(W))
need(w['status']=='PASS_CSIPHY0_WINDOWS_96_OF_96_GOLDEN_RETURN_RETIRED','E004w')

rgb=json.load(open(RGB))
need(rgb['device']=='Surface Camera Front / Sony IMX681','RGB acquisition identity')
need(rgb['route_decode']['wrapper_io_path_cfg0']['active_output_ife']=='CSID1 (bit8 OUTPUT_IFE_EN set only at wrapper +0x004)','RGB route')
need(rgb['route_decode']['csid1_rx']['cfg0']=='0x11300000','RGB CSID1')

ir=json.load(open(IR))
need(ir['ir_source']['name']=='Surface IR Camera Front','IR identity')
need(ir['mipi']['lane_count']==1 and ir['mipi']['data_rate_bps']==840000000,'IR MIPI')
need(ir['mipi']['lane_mask']=='0x81','IR lane mask')
need(ir['csiphy0']['physical_base']=='0x0ace4000','IR CSIPHY0')
need('csid' not in {k.lower() for k in ir.keys()},'IR summary unexpectedly contains top-level CSID authority')

csid=(K/'camss-csid.c').read_text()
need('csid->phy.csiphy_id = csiphy->id;' in csid,'CSIPHY id link state')
need('csid->phy.lane_cnt = lane_cfg->num_data;' in csid,'lane count')
need('csid->phy.lane_assign = csid_get_lane_assign(lane_cfg);' in csid,'lane assign')
need('csid->phy.en_vc |= BIT(local->index - 1);' in csid,'VC bitmap')
need('MEDIA_BUS_FMT_Y10_1X10' in csid and 'MIPI_CSI2_DT_RAW10' in csid,'Y10 RAW10 map')
need('ret = csid->res->parent_dev_ops->get(camss, csid->id);' in csid,'parent VFE power dependency')

c680=(K/'camss-csid-680.c').read_text()
for token in ('#define CSID_CSI2_RX_CFG0','CSID_CSI2_RX_CFG1',
              'CSID_RDI_CFG0(rdi)','CSID_RDI_CFG1(rdi)',
              'DECODE_FORMAT_PAYLOAD_ONLY << RDI_CFG0_DECODE_FORMAT',
              'format->data_type << RDI_CFG0_DATA_TYPE',
              'vc << RDI_CFG0_VIRTUAL_CHANNEL',
              'RDI_CFG1_PACKING_MIPI'):
    need(token in c680,'csid680 token '+token)

RAW10=0x2b; PAYLOAD=0xf; vc=0; dt_id=0
cfg0=(1<<31)|(RAW10<<16)|(PAYLOAD<<12)|(vc<<22)|(dt_id<<27)
cfg1=(1<<0)|(1<<2)|(1<<4)|(1<<5)|(1<<6)|(1<<7)|(1<<8)|(1<<15)
rx0=(1<<20)
need(cfg0==0x802bf000,'RDI0 CFG0 calculation')
need(cfg1==0x000081f5,'RDI0 CFG1 calculation')
need(rx0==0x00100000,'RX CFG0 calculation')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='BLOCKED_PENDING_SAME_MACHINE_WINDOWS_IR_CSID_ROUTE_ORACLE','gate status')
need(r['windows_ir_csid_instance_proven'] is False,'unresolved boundary')
need(r['csid_runtime_authorized'] is False,'runtime must remain blocked')
need(r['sensor_stream_authorized'] is False and r['illumination_authorized'] is False,'safety')

need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')

print('E004X_VERIFY=PASS WINDOWS_IR_CSID_ROUTE=UNRESOLVED')
print('E004X_LINUX_CANDIDATE=CSIPHY0->CSID0_RDI0 VC0 RAW10_0x2b')
print('E004X_MODEL=RX0=0x00100000 RX1=0x1 RDI0_CFG0=0x802bf000 RDI0_CFG1=0x000081f5')
print('E004X_CSID_RUNTIME=BLOCKED SENSOR_STREAM=NO VFE_STREAM=NO CAPTURE=NO ILLUMINATION=NO')
