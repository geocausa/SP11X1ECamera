#!/usr/bin/env python3
"""Fail-closed proof of the private LSC tuning-tree parser/mutation boundary.

This proof closes the normal static mechanisms that could turn a correct front
SensorTuningData payload into the rear/default LSC41 tree without changing the
private DataManager source bytes.  It also revalidates an Aug-4 active-dump
historical transport sample where front/rear KMD caches are clean and distinct.

It intentionally does NOT claim the exact Sep-2 verified-front DataManager
+0x38/+0x30 bytes were front IMX681: that remains the narrow live provenance
oracle unless recoverable from stale/offline memory.

No camera runtime is performed.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump')
DEFAULT_DUMP = Path('/mnt/windows/Windows/LiveKernelReports/NetAdapterCx-20260804-1913.dmp')

PATHS = {
    'device_mft': ARCHIVE/'surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll',
    'avs': ARCHIVE/'surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys',
    'front_kmd': ARCHIVE/'surfacecamfrontsensor8380.inf_arm64_747e2ddb5eb5a22b/surfacecamfrontsensor8380.sys',
    'front_module': ARCHIVE/'surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin',
    'front_tuning': ARCHIVE/'surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin',
    'rear_module': ARCHIVE/'surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.sensormodule.rfc_ov13858.bin',
    'rear_tuning': ARCHIVE/'surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin',
}
SHA = {
    'device_mft': 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35',
    'avs': 'b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed',
    'front_kmd': '80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03',
    'front_module': 'f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c',
    'front_tuning': '2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d',
    'rear_module': 'f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14',
    'rear_tuning': '4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635',
    'dump': '2ca55e2a058df20936068bd5dfe4c111769ee2d0758c96072adbd3c71a27db40',
    'cache_page': '8308296a82e4d4c3da184029a6ecb4f2948bcbe12a97655305df7f89a542bf24',
    'record_page': '120e164ac5e6986daec13dc0ae5f43f68e6730faa948ba45fa2ed388375072eb',
}

DUMP_FILE_OFF = {
    'record_page': 0x6359000,
    'front_module_head': 0x6B9C8000,
    'rear_module_head': 0x6B97E000,
    'front_tuning_head': 0x649AE000,
    'rear_tuning_head': 0x6BC8C000,
    'cache_page': 0x6B94B000,
}


def u16(b: bytes, o=0): return struct.unpack_from('<H', b, o)[0]
def u32(b: bytes, o=0): return struct.unpack_from('<I', b, o)[0]
def u64(b: bytes, o=0): return struct.unpack_from('<Q', b, o)[0]
def sha_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda: f.read(8 << 20), b''): h.update(x)
    return h.hexdigest()

def need(cond: bool, msg: str):
    if not cond: raise RuntimeError(msg)

def eq(got, want, msg: str):
    if got != want: raise RuntimeError(f'{msg}: got {got!r}, want {want!r}')


class PE:
    def __init__(self, b: bytes):
        self.b = b
        pe = u32(b, 0x3c)
        need(b[pe:pe+4] == b'PE\0\0', 'bad PE')
        self.nsec = u16(b, pe+6)
        opt = u16(b, pe+20)
        self.sh = pe + 24 + opt
        self.image_base = u64(b, pe+24+24)
        self.sections = []
        for i in range(self.nsec):
            o = self.sh + 40*i
            name = b[o:o+8].rstrip(b'\0').decode('ascii','replace')
            vsz, va, rsz, raw = struct.unpack_from('<IIII', b, o+8)
            chars = u32(b, o+36)
            self.sections.append((name,vsz,va,rsz,raw,chars))
    def off(self, rva: int) -> int:
        for _,vsz,va,rsz,raw,_ in self.sections:
            if va <= rva < va + max(vsz,rsz): return raw + rva - va
        raise RuntimeError(f'RVA {rva:#x} unmapped')
    def at(self, rva: int, n: int) -> bytes:
        o = self.off(rva); x = self.b[o:o+n]
        need(len(x) == n, f'short PE read {rva:#x}+{n:#x}')
        return x
    def bl_calls_to(self, target_rva: int) -> list[int]:
        out=[]
        for _,vsz,va,rsz,raw,chars in self.sections:
            if not (chars & 0x20000000): continue
            n=min(max(vsz,rsz), rsz)
            for d in range(0,n-3,4):
                insn=u32(self.b,raw+d)
                if insn & 0xFC000000 != 0x94000000: continue
                imm=insn & 0x03FFFFFF
                if imm & (1<<25): imm -= 1<<26
                rva=va+d
                if rva + (imm<<2) == target_rva: out.append(rva)
        return out


class ActiveDump:
    ADDR_MASK=0x0000FFFFFFFFF000
    def __init__(self,p:Path):
        self.path=p
        with p.open('rb') as f:
            self.hdr=f.read(0x2000); f.seek(0x2000); sh=f.read(0x38)
        need(self.hdr[:8]==b'PAGEDU64' and u32(self.hdr,3992)==6 and sh[:8]==b'SDMPDUMP','not expected ARM64 active dump')
        self.filebase=u64(sh,0x20); self.pages=u64(sh,0x28); self.bits=u64(sh,0x30)
        with p.open('rb') as f: f.seek(0x2038); self.bitmap=f.read(self.bits//8)
        eq(sum(x.bit_count() for x in self.bitmap),self.pages,'SDMP page count')
        self.prefix=[0]*(len(self.bitmap)+1)
        for i,v in enumerate(self.bitmap): self.prefix[i+1]=self.prefix[i]+v.bit_count()
        self.dtb=u64(self.hdr,0x10)&~0xfff
    def pa_to_file(self,pa:int):
        page,off=pa>>12,pa&0xfff; bi,bit=page>>3,page&7
        if bi>=len(self.bitmap) or not(self.bitmap[bi]&(1<<bit)): return None
        rank=self.prefix[bi]+(self.bitmap[bi]&((1<<bit)-1)).bit_count()
        return self.filebase+rank*0x1000+off
    def read_pa(self,pa:int,n:int):
        out=bytearray()
        with self.path.open('rb') as f:
            while n:
                take=min(n,0x1000-(pa&0xfff)); fo=self.pa_to_file(pa)
                if fo is None:return None
                f.seek(fo);x=f.read(take)
                if len(x)!=take:return None
                out+=x;pa+=take;n-=take
        return bytes(out)
    def va_to_pa(self,va:int):
        x,tp=va&((1<<48)-1),self.dtb
        for level,shift in enumerate((39,30,21,12)):
            pg=self.read_pa(tp,0x1000)
            if pg is None:return None
            d=u64(pg,((x>>shift)&0x1ff)*8);typ=d&3
            if typ==0:return None
            if level<3 and typ==1:
                size=1<<shift;return ((d&self.ADDR_MASK)&~(size-1))+(x&(size-1))
            if typ!=3:return None
            if level==3:return (d&self.ADDR_MASK)|(x&0xfff)
            tp=d&self.ADDR_MASK
        return None
    def read_va(self,va:int,n:int):
        out=bytearray()
        while n:
            pa=self.va_to_pa(va)
            if pa is None:return None
            take=min(n,0x1000-(va&0xfff));x=self.read_pa(pa,take)
            if x is None:return None
            out+=x;va+=take;n-=take
        return bytes(out)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--dump',type=Path,default=DEFAULT_DUMP)
    ap.add_argument('--out',type=Path,default=HERE/'lsc-private-tuning-tree-provenance-oracle.json')
    a=ap.parse_args()

    blobs={}
    for k,p in PATHS.items():
        blobs[k]=p.read_bytes(); eq(sha_bytes(blobs[k]),SHA[k],f'{k} SHA')
    dm=PE(blobs['device_mft']); avs=PE(blobs['avs'])

    # Upstream accepted boundaries are prerequisites, not duplicated claims.
    conv=json.loads((HERE/'lsc-front-calibration-tuning-convergence-oracle.json').read_text())
    own=json.loads((HERE/'lsc-tuning-manager-ownership-oracle.json').read_text())
    need(conv.get('status')=='PASS','calibration/tuning convergence prerequisite not PASS')
    need(own.get('accepted') is True,'tuning-manager ownership prerequisite not accepted')

    # Durable Aug-4 audit carves.
    cdir=HERE/'oracle-aug4-front-tuning-transport'
    cache=(cdir/'KMD_FRONT_REAR_TUNING_CACHE_PAGE_1000.bin').read_bytes()
    rec=(cdir/'FRONT_SENSOR_TUNING_RECORD_PAGE_1000.bin').read_bytes()
    eq(len(cache),0x1000,'cache carve size'); eq(sha_bytes(cache),SHA['cache_page'],'cache carve SHA')
    eq(len(rec),0x1000,'record carve size'); eq(sha_bytes(rec),SHA['record_page'],'record carve SHA')

    rear={'module_ptr':u64(cache,0x80),'module_size':u64(cache,0x88),'tuning_ptr':u64(cache,0x90),'tuning_size':u64(cache,0x98)}
    front={'module_ptr':u64(cache,0x5d0),'module_size':u64(cache,0x5d8),'tuning_ptr':u64(cache,0x5e0),'tuning_size':u64(cache,0x5e8)}
    eq(rear, {'module_ptr':0xffff94825fd02000,'module_size':0x24326,'tuning_ptr':0xffff948260010000,'tuning_size':0x279abe},'rear KMD cache tuple')
    eq(front,{'module_ptr':0xffff94825fd4c000,'module_size':0x33d30,'tuning_ptr':0xffff948260290000,'tuning_size':0x62a5ef},'front KMD cache tuple')
    for o in (0x4c,0x64,0x7c): eq(u32(cache,o)>>16,0xd855,'rear packed sensor id')
    for o in (0x59c,0x5b4,0x5cc): eq(u32(cache,o)>>16,0x0aff,'front packed sensor id')
    eq(front['module_size'],len(blobs['front_module']),'front module size authority')
    eq(front['tuning_size'],len(blobs['front_tuning']),'front tuning size authority')
    eq(rear['module_size'],len(blobs['rear_module']),'rear module size authority')
    eq(rear['tuning_size'],len(blobs['rear_tuning']),'rear tuning size authority')

    key=b'SensorTuningData\0'; eq(rec.find(key),0x1fc,'serialized SensorTuningData record offset')
    total=u32(rec,0x21c); header=u32(rec,0x220)
    eq(total,0x62a61b,'serialized tuning record total bytes'); eq(header,0x2c,'serialized tuning record header bytes')
    eq(total-header,len(blobs['front_tuning']),'serialized payload length')
    eq(rec[0x224:0x224+0x200],blobs['front_tuning'][:0x200],'serialized front tuning payload prefix')
    need(b'com.surface.tuned.ffc_imx681' in rec[0x224:0x400],'serialized front tuning identity missing')
    need(b'rfc_ov13858' not in rec,'rear tuning name unexpectedly present in front record page')

    # Full source active dump revalidation and exact KMD cache target hashes.
    eq(sha_file(a.dump),SHA['dump'],'Aug-4 source dump SHA')
    d=ActiveDump(a.dump); eq(d.filebase,0x483000,'SDMP filebase');eq(d.pages,787224,'SDMP pages');eq(d.bits,12582912,'SDMP bits')
    live={}
    for side,tup in [('front',front),('rear',rear)]:
        for kind in ('module','tuning'):
            ptr=tup[f'{kind}_ptr']; size=tup[f'{kind}_size']; x=d.read_va(ptr,size)
            need(x is not None,f'{side} {kind} live mapping missing')
            h=sha_bytes(x); eq(h,SHA[f'{side}_{kind}'],f'{side} {kind} live hash')
            live[f'{side}_{kind}']={'va':hex(ptr),'bytes':size,'sha256':h,'head_file_offset':hex(d.pa_to_file(d.va_to_pa(ptr)))}
    eq(int(live['front_module']['head_file_offset'],16),DUMP_FILE_OFF['front_module_head'],'front module dump head')
    eq(int(live['rear_module']['head_file_offset'],16),DUMP_FILE_OFF['rear_module_head'],'rear module dump head')
    eq(int(live['front_tuning']['head_file_offset'],16),DUMP_FILE_OFF['front_tuning_head'],'front tuning dump head')
    eq(int(live['rear_tuning']['head_file_offset'],16),DUMP_FILE_OFF['rear_tuning_head'],'rear tuning dump head')

    # Exact DeviceMFT mechanics: private source -> fresh manager/parser -> instance-local root.
    sigs={
      0x7133ac:'1387ff97601600f9804201b46a3240b9691e40f9a94001b4080040f9090500f9080040f90a0900f9601640f9bc87ff97',
      0x6f52f4:'00c882d212e51694f30300aa930000b402c882d201008052bda42194b30f00f9930000b4e00313aa2576e79702000014000080d2a80240f9000100f9a80240f9000140f9000400b4010540f9c10300b4020940f9820300b4dff3ff971f040071',
      0x6f3188:'881a02f9963a04b916150034',
      0x6f3384:'881642f9880000b56825aa9b881602f9',
      0x6f34c4:'881a42f9881602f9',
      0x716cc4:'a27e40d3e10317aac0a20391ec192194',
      0x716110:'6e70ff9760020034400f40f9081840b9770200b4a8000034e21642f9620000b4011442f99375ff97e80240f9',
      0x29bbe0:'480940f9081540b90806e836aa0243f9490180d24809c99a08a9099b1f0100f1440940fa29050054a80643f91f010aebc0040054a02640f9aa0603f9080040f9081140f9ef0308aa116700f031de43f920023fd6e0013fd6f403002aa02640f9080040f954020035081540f9',
      0x29257c:'6892513969965139516305912b220029',
      0x292874:'65ad0c9441230491000840f9a2f5ff97',
      0x2905a8:'8b1540b95f050071c10200546a0103328a1500b94900803788020035810b8052c0021a91b35d2994665640b9c4021a911f0000f1288700d002a117918404809a8000805205431f9123430791e1ff9f52ac29f697a91240f9e85a48b9030000146a7902128a1500b9',
    }
    for r,h in sigs.items(): eq(dm.at(r,len(bytes.fromhex(h))),bytes.fromhex(h),f'DeviceMFT signature {r:#x}')
    avs_sigs={
      0x880fc:'a8621b911f010039c80000900361349104008052020080d2000080d2880000d001e124912e50fe97fd7bc8a8f50b40f9f353c2a8ff2303d5c0035fd6830a40b97f100071c80000548232009181008052e04300911053fe97020000149302001828fdff90088141f9e00314aa00013fd6e01340f928fdff90082941f900013fd6a8621b9113fcff37e41340b904010039',
      0x64ac:'82238052e1621891e00301914e580094',
    }
    for r,h in avs_sigs.items(): eq(avs.at(r,len(bytes.fromhex(h))),bytes.fromhex(h),f'AVS signature {r:#x}')

    # Call graph invariants.  The graft helper has exactly one external caller:
    # DataManager::LoadTuningBin; the other call is recursion inside the helper.
    eq(dm.bl_calls_to(0x6f3780),[0x6f39c0,0x716134],'tuned-tree graft callsites')
    eq(dm.bl_calls_to(0x6f52c8),[0x71308c,0x7133d8],'CreateTunedModeTree callsites')
    eq(dm.bl_calls_to(0x6f22c8),[0x6f534c,0x716110,0x721a8c,0xe0df3c],'generic parser callsites')

    # Strings pin the explicit hot-reload path and AVS registry source/default.
    for s in [b'C:\\Data\\test\\Livetuning\\\0',b'DataManager::CheckForTuningBinUpdate\0',b'DataManager::LoadTuningBin\0']:
        need(s in blobs['device_mft'],f'DeviceMFT marker missing: {s!r}')
    for s in ['enableLiveTuning'.encode('utf-16le'), '\\Registry\\Machine\\System\\CurrentControlSet\\Control\\Qualcomm\\Camera\\'.encode('utf-16le')]:
        need(s in blobs['avs'],f'AVS live-tuning marker missing: {s[:32]!r}')
    # DeviceConfigInfo payload starts at CCaptureFilter+0x618, and its +0xc0 byte
    # is therefore the same object byte at +0x6d8 used by CheckEnableLiveTuning.
    eq(0x618+0xc0,0x6d8,'AVS DeviceConfigInfo live-tuning field arithmetic')

    current_live_dir=Path('/mnt/windows/Data/test/Livetuning')
    current_camx_override=Path('/mnt/windows/Data/test/camxoverridesettings.txt')
    current_obs={'live_tuning_directory_exists':current_live_dir.exists(),'camx_override_file_exists':current_camx_override.exists()}

    result={
      'schema':'sp11-e003h-lsc-private-tuning-tree-provenance-v1',
      'accepted':True,
      'status':'PASS',
      'classification':(
        'CLOSED NORMAL-PATH PARSER/MUTATION BOUNDARY: Aug-4 live kernel memory contains distinct front IMX681 and rear OV13858 '
        'KMD module+tuning caches whose complete mapped bytes hash exactly to their installed authorities, and a serialized '
        'SensorTuningData record carries the exact front tuning length/identity. DeviceMFT normal construction copies the private '
        'DataManager source into a fresh TuningDataManager, allocates a fresh parser/tree object, and stores tree/root state in '
        'instance-local +0x430/+0x428. The only external caller of the tree-graft helper is DataManager::LoadTuningBin. That reload '
        'is reached only through the explicit EnableLiveTuning/request-mod-10 path; AVS defaults enableLiveTuning to zero when its '
        'registry value is absent. Therefore ordinary parser cache reuse/global rear-tree injection is excluded. The exact Sep-2 '
        'verified-front DataManager+0x38/+0x30 source bytes (and capture-time override bit, if any) remain the narrow unresolved provenance oracle.'
      ),
      'source_authority':{k:{'path':str(PATHS[k]),'sha256':SHA[k]} for k in PATHS},
      'aug4_dump':{
        'path':str(a.dump),'sha256':SHA['dump'],'bytes':a.dump.stat().st_size,
        'cache_page':{'file_offset':hex(DUMP_FILE_OFF['cache_page']),'sha256':SHA['cache_page']},
        'front_sensor_tuning_record_page':{'file_offset':hex(DUMP_FILE_OFF['record_page']),'sha256':SHA['record_page'],'record_offset_in_page':'0x1fc','payload_offset_in_page':'0x224','record_total_bytes':'0x62a61b','record_header_bytes':'0x2c'},
        'kmd_cache':{'front_sensor_id':'0x0aff','rear_sensor_id':'0xd855','front':front,'rear':rear},
        'complete_live_cache_hashes':live,
      },
      'private_tree_mechanics':{
        'normal_datamanager_construct':'RVA 0x7133ac: fresh manager; DataManager+0x38/+0x30 copied into manager source +0x8/+0x10; CreateTunedModeTree called',
        'fresh_parser':'RVA 0x6f52f4 allocates/zeros 0x1640 parser before generic parser call',
        'instance_tree_storage':['parser+0x430 node-array/storage','parser+0x428 root'],
        'graft_helper_rva':'0x6f3780','graft_callsites':['0x6f39c0 recursive','0x716134 DataManager::LoadTuningBin'],
        'create_tuned_mode_tree_callsites':['0x71308c','0x7133d8'],
        'generic_parser_callsites':['0x6f534c tuned-mode tree','0x716110 live-tuning temp tree','0x721a8c sensor-module manager','0xe0df3c FD tuning'],
      },
      'live_tuning_gate':{
        'avs_registry_path':'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Qualcomm\\Camera',
        'avs_registry_value':'enableLiveTuning',
        'avs_missing_value_default':0,
        'avs_field':'CCaptureFilter+0x6d8 = DeviceConfigInfo+0xc0 (payload base +0x618)',
        'devicemft_transport':'DeviceConfigInfo -> DataManager+0xe8 -> CaptureDevice block -> CaptureDevice+0x464 -> SetStaticSettings[0x15] -> bit29',
        'request_gate':'CaptureDevice::IsTuningBinChanged checks bit29, only nonzero request numbers divisible by 10, then vtable +0x20 CheckForTuningBinUpdate and +0x28 LoadTuningBin',
        'reload_path':'C:\\Data\\test\\Livetuning\\...',
        'current_recovered_windows_observation':current_obs,
        'capture_time_sep2_value_observed':False,
      },
      'closed_exclusions':[
        'normal TuningDataManager parser/tree is a global singleton shared across cameras',
        'normal CreateTunedModeTree silently reuses another camera parser/root rather than building from its own source',
        'an untracked second external tree-graft call mutates the private manager after construction',
        'Aug-4 front KMD cache contains rear module/tuning bytes',
        'Aug-4 serialized SensorTuningData record is rear tuning by length/identity',
      ],
      'remaining_provenance_gate':(
        'Recover or capture the exact Sep-2 verified-front private DataManager+0x38/+0x30 source buffer and, if needed, its '
        'capture-time EnableLiveTuning state. If the source is rear OV13858, investigate the live InitParams source inconsistency. '
        'If the source is front IMX681 while live tuning was disabled, ordinary parser/reuse/graft explanations are exhausted and '
        'the remaining hypothesis class is abnormal memory corruption or an as-yet-unseen write that must be proven directly.'
      ),
      'safety':{'linux_camera_runtime':False,'linux_request6_executed':False,'linux_request6_authorized':False},
    }
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS private tuning-tree parser/mutation provenance boundary')
    print('  Aug-4 front live tuning:', live['front_tuning']['sha256'])
    print('  Aug-4 rear live tuning :', live['rear_tuning']['sha256'])
    print('  graft callsites         :', [hex(x) for x in dm.bl_calls_to(0x6f3780)])
    print('  current live dir exists :', current_obs['live_tuning_directory_exists'])
    print('  remaining               : Sep-2 private DataManager+0x38/+0x30 identity')
    print('  oracle',a.out)
    return 0

if __name__=='__main__': raise SystemExit(main())
