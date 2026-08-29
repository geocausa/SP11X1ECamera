#!/usr/bin/env python3
import argparse, hashlib, json, re, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

INF_SHA='4db3acab414e344dc460478b54d964c9c7b5d3d648ee0c19db13523431262fcb'; INF_BYTES=16736
UMD_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'; UMD_BYTES=23998368
AVS_SHA='b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed'; AVS_BYTES=547192
DMFT_CLSID='{4C2331F0-66BE-4177-9841-2FCBA8CCF5CA}'

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(s,x,label):
    if x not in s: die(label+': '+x)

def pe(data):
    peo=struct.unpack_from('<I',data,0x3c)[0]; n=struct.unpack_from('<H',data,peo+6)[0]
    optsz=struct.unpack_from('<H',data,peo+20)[0]; opt=peo+24
    base=struct.unpack_from('<Q',data,opt+24)[0]; sh=opt+optsz; secs=[]
    for i in range(n):
        o=sh+i*40; name=data[o:o+8].rstrip(b'\0').decode(errors='ignore')
        vs,va,rs,raw=struct.unpack_from('<IIII',data,o+8); secs.append((name,va,vs,raw,rs))
    return base,secs

def rva_off(secs,rva):
    for _,va,vs,raw,rs in secs:
        if va <= rva < va+max(vs,rs): return raw+rva-va
    die(f'unmapped RVA 0x{rva:x}')

def disasm(data,base,secs):
    t=next(s for s in secs if s[0]=='.text'); _,va,vs,raw,rs=t
    md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.skipdata=True
    return {x.address-base:x for x in md.disasm(data[raw:raw+rs],base+va) if x.mnemonic!='.byte'}

def at(ins,rva,mnemonic,frag):
    x=ins.get(rva)
    if not x or x.mnemonic!=mnemonic or frag not in x.op_str:
        die(f'UMD anchor drift 0x{rva:x}: {None if not x else x.mnemonic+" "+x.op_str}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inf',type=Path,required=True); ap.add_argument('--umd',type=Path,required=True)
    ap.add_argument('--avstream',type=Path,required=True); ap.add_argument('--epoch0-oracle',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()
    for p,n,h in [(a.inf,INF_BYTES,INF_SHA),(a.umd,UMD_BYTES,UMD_SHA),(a.avstream,AVS_BYTES,AVS_SHA)]:
        if p.stat().st_size!=n or sha(p)!=h: die('identity drift '+str(p))
    inf=a.inf.read_text(encoding='utf-16'); umd=a.umd.read_bytes(); avs=a.avstream.read_bytes()
    for x in ['QcDeviceMFT8380.dll','DeviceMFT.Files','DMFTRegistration',DMFT_CLSID,'InprocServer32']:
        need(inf,x,'INF registration drift')
    need(inf,'%13%\\QcDeviceMFT8380.dll','INF InprocServer drift')
    for x in [b'{CCaptureFilter::PerformAddressPatching} CSLAddrPatch',
              b'{CCaptureFilter::FlushCSLPacket} CSLCmdMemDesc',
              b'{CCaptureFilter::SetSendPacket} Enqueued CSL packet',
              b'{CCaptureFilter::SendPacketInternal}  profile id and processing type and sending packet']:
        if x not in avs: die('AVStream UMD handoff string missing '+repr(x))
    for x in [b'CamX::IFENode::CreateCmdBuffers',b'CamX::IFENode::FetchCmdBuffers',
              b'CamX::IFENode::SubmitPacket',b'CamX::IFENode::CommitPacket',
              b'CamX::IFENode::CreateIFEIQModules',b'CamX::IFENode::ProgramIQConfig',
              b'OEMIFEIQSetting']:
        if x not in umd: die('CamX producer string missing '+repr(x))
    base,secs=pe(umd)
    if base!=0x180000000: die(f'UMD image base drift 0x{base:x}')
    ins=disasm(umd,base,secs)

    # Exact Titan680 command builder anchors: register-range base and/or DMI selector/size.
    anchors=[
      (0xb38e08,'mov','w1, #0x5f58'),(0xb38e28,'mov','w1, #0x5f08'),(0xb38e48,'mov','w1, #0x5f08'),(0xb38e68,'mov','w1, #0x5f08'),
      (0xb3bd60,'mov','w1, #0x3d58'),(0xb3bdb0,'mov','w1, #0x3d78'),(0xb3be0c,'mov','w1, #0x3d08'),
      (0xb3cdf8,'mov','w1, #0x4358'),(0xb3ce44,'mov','w1, #0x4308'),(0xb3ce64,'mov','w1, #0x4308'),(0xb3ce84,'mov','w1, #0x4308'),
      (0xb405dc,'mov','w1, #0x4958'),(0xb40600,'mov','w1, #0x4908'),
      (0xb4ab4c,'mov','w1, #0x4758'),(0xb4ab90,'mov','w1, #0x4708'),
      (0xb5296c,'mov','w1, #0xa058'),(0xb529bc,'mov','w1, #0xa258'),
      (0xb52a94,'mov','w1, #0xa008'),(0xb52ab4,'mov','w1, #0xa008'),(0xb52ad4,'mov','w1, #0xa208'),(0xb52af4,'mov','w1, #0xa208'),
      (0xb55a1c,'mov','w1, #0x4568'),
      (0xb5a9a8,'mov','w1, #0x5a58'),(0xb5a9cc,'mov','w1, #0x5a08'),
      (0xa09d54,'mov','x8, #0x3b60'),(0xa09d58,'movk','x8, #0x3b68')]
    for x in anchors: at(ins,*x)

    strings=[
      'CamX::IFEPDPC311Titan680::CreateCmdList','CamX::IFELSC411Titan680::WriteLUTtoDMI',
      'CamX::IFEGIC311Titan680::CreateCmdList','CamX::IFEBPCABF411Titan680::CreateCmdList',
      'CamX::IFEGTM131Titan680::CreateCmdList','CamX::IFEGamma151Titan680::CreateCmdList',
      'CamX::IFEDSX101Titan680::CreateCmdList','CamX::IFEWB201Titan680::CreateCmdList',
      'CamX::IFEDemuxBLS141Titan680::CreateCmdList',
      'CamX::IQInterface::Gamma151CalculateSetting','CamX::IQInterface::GIC311CalculateSetting',
      'CamX::IQInterface::GTM131CalculateSetting','CamX::IQInterface::BPCABF411CalculateSetting',
      'CamX::IQInterface::WB201CalculateSetting','CamX::IQInterface::DemuxBLS141CalculateSetting',
      'CamX::IFELSC411::CheckDependenceChange','CamX::IFEPDPC311::CheckDependenceChange',
      'LSC411Setting::CalculateTintlessSetting','TuningTMCTriggerData']
    for s in strings:
        if s.encode()+b'\0' not in umd: die('UMD semantic string missing '+s)
    for s in [b'Invalid Input: pNewAECUpdate %x  pNewAWBupdate %x HwContext %x',
              b'Invalid Input: pAECUpdateData %p  pHwContext %p pNewAWBUpdate %p',
              b'manual mode isp gain %f',b'App Gains [%f, %f, %f, %f]',
              b'DSX(Full) pre Crop',b'TMCEnabled = %d']:
        if s not in umd: die('UMD dependency evidence missing '+repr(s))

    epoch=json.loads(a.epoch0_oracle.read_text())
    if not epoch.get('accepted'): die('0024 oracle not accepted')
    reg_union=set(); dmi_union=set()
    for v in epoch['main_bl_variants']:
        reg_union.update(int(x['register_offset'],16) for x in v['dynamic_register_fields'])
        dmi_union.update(int(x['dmi_register_offset'],16) for x in v['dmi_shape'])
    expected_regs={0x3b70,0x3b74,0x3d58,0x3d5c,0x3d78,0x3d7c,0x3d80,0x3d84,
                   0x4358,0x435c,0x456c,0x4570,0x4758,0x475c,0x4958,0x495c,
                   0x5a58,0x5a5c,0x5f58,0x5f5c,0xa058,0xa05c,0xa258,0xa25c}
    expected_dmi={0x3d08,0x4308,0x4708,0x4908,0x5a08,0x5f08,0xa008,0xa208}
    if reg_union!=expected_regs: die('0024 dynamic register union drift '+repr(sorted(reg_union)))
    if dmi_union!=expected_dmi: die('0024 DMI union drift '+repr(sorted(dmi_union)))

    modules={
      'DemuxBLS141':{'dynamic_registers':['0x3b70','0x3b74'],'dmi':[],
                     'producer':'CamX::IFEDemuxBLS141 / IFEDemuxBLS141Titan680','dependencies':['pixel format','ISP/channel gain','BLS/tuning state']},
      'PDPC311':{'dynamic_registers':['0x3d58','0x3d5c','0x3d78','0x3d7c','0x3d80','0x3d84'],'dmi':['0x3d08:1:0x200'],
                 'producer':'CamX::IFEPDPC311 / IFEPDPC311Titan680','dependencies':['sensor mode/format','PDAF configuration','PDPC tuning/mapping state']},
      'LSC411':{'dynamic_registers':['0x4358','0x435c'],'dmi':['0x4308:1:0x374','0x4308:2:0x374','0x4308:3:0x374'],
                'producer':'CamX::IFELSC411 / IFELSC411Titan680','dependencies':['AEC update','AWB update','sensor calibration','geometry','tintless/ALSC stats and state']},
      'WB201':{'dynamic_registers':['0x456c','0x4570'],'dmi':[],
               'producer':'CamX::IFEWB201 / IFEWB201Titan680','dependencies':['application/AWB white-balance gains','WB tuning state']},
      'GIC311':{'dynamic_registers':['0x4758','0x475c'],'dmi':['0x4708:1:0x200'],
                'producer':'CamX::IFEGIC311 / IFEGIC311Titan680','dependencies':['CamX GIC311 IQ interpolation/calculation inputs']},
      'BPCABF411':{'dynamic_registers':['0x4958','0x495c'],'dmi':['0x4908:1:0x100'],
                   'producer':'CamX::IFEBPCABF411 / IFEBPCABF411Titan680','dependencies':['BPC/ABF tuning and per-request IQ inputs']},
      'GTM131':{'dynamic_registers':['0x5a58','0x5a5c'],'dmi':['0x5a08:1:0x800'],
                'producer':'CamX::IFEGTM131 / IFEGTM131Titan680','dependencies':['TMC state','AEC gain','DRC gain','GTM/LTM percentage and tone-mapping triggers']},
      'Gamma151':{'dynamic_registers':['0x5f58','0x5f5c'],'dmi':['0x5f08:1:0x400','0x5f08:2:0x400','0x5f08:3:0x400'],
                  'producer':'CamX::IFEGamma151 / IFEGamma151Titan680','dependencies':['AEC update','AWB update','gamma tuning state']},
      'DSX101':{'dynamic_registers':['0xa058','0xa05c','0xa258','0xa25c'],'dmi':['0xa008:1:0x300','0xa008:2:0x300','0xa208:1:0x180','0xa208:2:0x180'],
                'producer':'CamX::IFEDSX101 / IFEDSX101Titan680','dependencies':['crop type','MNDS output geometry','DS4 path geometry']}}
    out={'schema':'sp11-e003h-windows-vfe1-upstream-iq-producer-v1','accepted':True,
         'package':{'inf':{'bytes':INF_BYTES,'sha256':INF_SHA},'device_mft':{'file':'QcDeviceMFT8380.dll','bytes':UMD_BYTES,'sha256':UMD_SHA,'clsid':DMFT_CLSID},
                    'avstream':{'file':'surfacecamavs8380.sys','bytes':AVS_BYTES,'sha256':AVS_SHA}},
         'ownership':{'iq_value_and_dmi_payload_producer':'registered QcDeviceMFT8380.dll CamX DeviceMFT',
                      'kernel_consumer':'qccamisp8380 DAL_ife_process_iq_packet, already pinned separately',
                      'transport':'CamX builds/commits CSL command buffers; Surface AVStream miniport receives UMD CSL descriptors/address patches and queues/sends packets',
                      'five_shape_rule':'the 0x958/0x868/0x83c/0x6b8/0x5a4 steady main-BL shapes are incoming CamX IQ-module/dirty-group subsets, not a hidden qccamisp KMD selector'},
         'module_map':modules,
         'crosscheck':{'epoch0_dynamic_register_count':len(reg_union),'epoch0_dmi_register_count':len(dmi_union),
                       'all_dynamic_registers_named':True,'all_dmi_registers_named':True},
         'linux_consequence':{'consumer_boundary':'Linux steady-state materialization must consume module-level IQ outputs/dirty groups and rewrite DMI addresses to Linux-owned DMA; it must not freeze captured Windows frame values or payload IOVAs.',
                              'algorithm_boundary':'This oracle identifies the Windows producer and dependency families; it does not claim Linux has reproduced Qualcomm CamX AEC/AWB/TMC/tintless/IQ algorithms.',
                              'runtime_authorized':False}}
    txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(txt)
    else:print(txt,end='')
    print('PASS: registered QcDeviceMFT CamX owns every steady VFE1 IQ DMI/register group; KMD is downstream consumer')
if __name__=='__main__':main()
