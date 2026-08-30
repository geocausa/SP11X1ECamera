#!/usr/bin/env python3
import argparse, hashlib, json, struct
from pathlib import Path

EXPECTED_DRIVER_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
EXPECTED_MANAGER_SHA='08107ae0e9b59274aba29eb887e8f5601d26b2b53f7f08a0badbc25a52864f9e'
EXPECTED_COMMON_SHA='df872bd0e099ddd04752167a086364839680a43d6df1b734b8893cfd5cd93d7f'
EXPECTED_CALLBACKS_SHA='8741c4f651406fbd67a50eea3b4231252ed19174703be4548e37e87a711a2a0f'
EXPECTED_BYTES={
  0x1a330:'090440f928008052288100b9090440f928028052280d00b9080440f9011100b9c0035fd6',
  0x1a800:'7f2303d5fd7bbfa9fd030091281c00531f010071282080520905881a082c40b9880100341f050071e0000054c80000f001e138914801009000a13491a73c009406000014080840f9090500b903000014080840f9090100b9fd7bc1a8ff2303d5c0035fd6',
  0x1b830:'080440f9000140b9c0035fd600000000',
  0x1b7b0:'690640f928008052281500b9fd7bc1a8',
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text_auto(p):
    b=Path(p).read_bytes()
    if b.startswith(b'\xff\xfe') or (len(b)>2 and b[1:2]==b'\x00'):
        return b.decode('utf-16')
    return b.decode('utf-8',errors='replace')
def die(s): raise SystemExit('FAIL: '+s)
def one(text,needle,label):
    n=text.count(needle)
    if n != 1: die(f'{label}: expected one occurrence, got {n}')
    return text.index(needle)

def pe_rva_bytes(path,rva,n):
    b=path.read_bytes()
    if b[:2] != b'MZ': die('driver is not PE/MZ')
    peoff=struct.unpack_from('<I',b,0x3c)[0]
    if b[peoff:peoff+4] != b'PE\0\0': die('invalid PE signature')
    nsects=struct.unpack_from('<H',b,peoff+6)[0]
    optsz=struct.unpack_from('<H',b,peoff+20)[0]
    sec=peoff+24+optsz
    for i in range(nsects):
        o=sec+i*40
        vsize,vaddr,rawsize,rawptr=struct.unpack_from('<IIII',b,o+8)
        span=max(vsize,rawsize)
        if vaddr <= rva < vaddr+span:
            off=rawptr+(rva-vaddr)
            return b[off:off+n]
    die(f'RVA {rva:#x} not mapped')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--driver',type=Path,required=True)
    ap.add_argument('--manager-decomp',type=Path,required=True)
    ap.add_argument('--common-decomp',type=Path,required=True)
    ap.add_argument('--callbacks-decomp',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    for p,h,label in [(a.driver,EXPECTED_DRIVER_SHA,'driver'),(a.manager_decomp,EXPECTED_MANAGER_SHA,'manager decomp'),
                      (a.common_decomp,EXPECTED_COMMON_SHA,'common decomp'),(a.callbacks_decomp,EXPECTED_CALLBACKS_SHA,'callbacks decomp')]:
        if sha(p)!=h: die(f'{label} hash drift: {sha(p)}')
    for r,h in EXPECTED_BYTES.items():
        got=pe_rva_bytes(a.driver,r,len(bytes.fromhex(h))).hex()
        if got!=h: die(f'instruction bytes drift at RVA {r:#x}')

    m=text_auto(a.manager_decomp)
    c=text_auto(a.common_decomp)
    cb=text_auto(a.callbacks_decomp)

    # Full Gen2 callback table. local_1b0 is a uint*, so these indices map to
    # object byte offsets 0x1e8..0x228 / longlong slots 0x3d..0x45.
    table={
      'hw_version':'*(code **)(local_1b0 + 0x7a) = FUN_14001b830;',
      'reset':'*(code **)(local_1b0 + 0x7c) = FUN_14001a330;',
      'configure':'*(code **)(local_1b0 + 0x7e) = pcVar8;',
      'path_enable':'*(code **)(local_1b0 + 0x86) = pcVar8;',
      'route':'*(code **)(local_1b0 + 0x8a) = pcVar8;',
    }
    for k,n in table.items(): one(m,n,'callback table '+k)
    for n in ('pcVar8 = FUN_14001a870;','pcVar8 = FUN_14001b3d0;','pcVar8 = FUN_14001a800;'):
        if n not in m: die('missing Gen2 callback selection '+n)

    # Dispatcher proves normal reset uses SW reset only and stop uses HW reset only.
    normal_reset=one(c,'(plVar13[0x3e],plVar13,2);','normal reset callback')
    stop_reset=one(c,'(plVar13[0x3e],plVar13,1);','stop reset callback')
    if normal_reset >= stop_reset: die('reset/stop dispatcher order drift')

    # Manager DEVICE_CONFIG runtime control flow. Textual label is earlier because
    # the later reset block jumps back to it: route -> reset -> goto label -> config.
    label=one(m,'LAB_140018f9c:','post-reset config label')
    config=one(m,'(*puVar15,puVar15,6);','CSID config command')
    route=one(m,'(*puVar15,puVar15,7);','CSID wrapper route command')
    reset=one(m,'(*puVar15,puVar15,4,0,0);','CSID reset command')
    # There are several gotos to this label in the large function; require one after
    # the CSID/IFE/SFE reset-success block rather than asserting global uniqueness.
    goto=m.find('goto LAB_140018f9c;',reset)
    if goto < 0: die('no post-reset jump to config label')
    if not (label < config < route < reset < goto):
        die(f'manager control-flow layout drift label={label} config={config} route={route} reset={reset} goto={goto}')
    for pos,labelname in ((config,'config'),(route,'route'),(reset,'reset')):
        pre=m[max(0,pos-600):pos]
        if 'DAT_14004ae88 + 0x10' not in pre:
            die(labelname+' call no longer resolves through CSID table')

    # The exact reset callback bytes are three MMIO stores only:
    # TOP_IRQ_MASK=1, RESET_CFG=0x11, RESET_CMD=caller value. No IRQ_CMD +0x14 prewrite.
    # The separate ISR tail is where Windows writes IRQ_CMD=1 after status clear.
    if 'FUN_14001a330' not in cb or 'FUN_14001b5f0' not in cb:
        die('callback decomp missing reset/ISR')

    out={
      'schema':'sp11-e003h-windows-csid1-common-reset-v1','accepted':True,
      'date':'2026-08-30','machine':'SP11 Windows same physical X1E80100 device',
      'source':{
        'driver':'qccamisp8380.sys','driver_sha256':EXPECTED_DRIVER_SHA,
        'manager_decomp_sha256':EXPECTED_MANAGER_SHA,'common_decomp_sha256':EXPECTED_COMMON_SHA,
        'callbacks_decomp_sha256':EXPECTED_CALLBACKS_SHA,
      },
      'gen2_callback_table':{
        'object_0x1e8_hw_version':'RVA 0x1b830; read MMIO +0x0 only',
        'object_0x1f0_reset':'RVA 0x1a330',
        'object_0x1f8_full_configure':'RVA 0x1a870',
        'object_0x218_path_enable':'RVA 0x1b3d0',
        'object_0x228_wrapper_route':'RVA 0x1a800',
      },
      'wrapper_route':{
        'callback_rva':'0x1a800','csid1_wrapper_offset':'0x4','front_normal_value':'0x00000101',
        'alternate_value':'0x00000102',
      },
      'normal_reset':{
        'dispatcher_command':4,'callback_argument':2,'callback_rva':'0x1a330',
        'writes_in_order':[
          {'offset':'0x080','value':'0x00000001','role':'TOP_IRQ_MASK'},
          {'offset':'0x00c','value':'0x00000011','role':'RESET_CFG immediate + complete-location'},
          {'offset':'0x010','value':'0x00000002','role':'RESET_CMD software reset only'},
        ],
        'pre_reset_irq_cmd_0x14_write':False,
        'reset_wait_ms':50,
      },
      'irq_ack':{
        'isr_rva':'0x1b5f0','irq_cmd_write_rva':'0x1b7b8','offset':'0x014','value':'0x00000001',
        'classification':'post-status-clear ISR acknowledgement, not a pre-reset write',
      },
      'stop_reset':{
        'dispatcher_opcode':'0x805','callback_argument':1,'reset_cmd':'0x00000001','role':'hardware reset only',
      },
      'device_config_runtime_order':[
        'CSID setInfo/object state',
        'wrapper route command 7 -> CSID1 wrapper +0x4 = 0x101',
        'CSID reset command 4 -> TOP mask 1 -> RESET_CFG 0x11 -> RESET_CMD 2 -> wait',
        'IFE/SFE reset completion as applicable',
        'jump to post-reset config loop',
        'CSID config command 6 -> full Gen2 builder RVA 0x1a870',
      ],
      'linux_current_mismatch':{
        'route_relative_to_reset':'Linux route is programmed during stream prepare after reset; Windows programs route before reset.',
        'reset_cmd':'Linux CSID680 uses HW_RESET|SW_RESET = 3; Windows normal CSID reset uses software-only = 2.',
        'irq_cmd':'Linux prewrites IRQ_CMD_CLEAR before reset; Windows normal reset callback has no +0x14 write. Windows +0x14=1 is ISR acknowledgement.',
        'post_reset_generic_masks':'Linux csid_reset writes generic RDI/IPP/BUF/TOP masks after reset; Windows proceeds from reset completion into exact full configure without that generic all-mask staging.',
      },
      'linux_consequence':(
        'For the bounded SP11 front CSID1 path, represent the Windows common lifecycle before another runtime: '
        'program wrapper route 0x101 before reset; use RESET_CFG 0x11 and software-only RESET_CMD 2 with TOP mask 1; '
        'do not prewrite IRQ_CMD; after reset do not stage generic all-path masks before the exact front configure. '
        'Keep the existing ISR IRQ_CMD acknowledgement. Scope the delta to the same-machine X1E CSID1 front path unless broader parity is separately proven.'
      ),
      'runtime_authorized':False,
      'next_gate':'Implement/inspect the front-only reset+route lifecycle delta and fix prepared-state rollback warning; no runtime yet.'
    }
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
