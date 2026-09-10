#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,os,struct,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DW_RESULT=json.loads((BASE/'dw-iq-producer-live-cq-demux/RESULT.json').read_text())
DEFAULT_DT=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-dt/attempt1-six-frame-pass-20260910T2052/runtime-output/producer')
GAIN_BITS=[0x3f80397b,0x3f80216a,0x3f801646]

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b): return hashlib.sha256(bytes(b)).hexdigest()

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--dt-producer-dir',type=Path,default=DEFAULT_DT);ap.add_argument('--manifest',type=Path,default=HERE/'RESULT.json');a=ap.parse_args()
    DX=load(HERE/'live-iq-producer.py','dx_verify')
    assert DX.GAIN_RECORD.size==24 and DX.GAIN_MAGIC==0x31464749 and DX.GAIN_VERSION==1

    src=(HERE/'e003i-dx-six-frame-native-aec.c').read_text()
    assert src.count('e003i_gain_feed_publish(')==1
    assert 'if (target <= 3U)' in src
    assert src.index('e003i_db_schedule_queue(&ctx->schedule') < src.index('e003i_gain_feed_publish(ctx->gain_fd')
    assert '--aec-gain-fd' in src and 'signal(SIGPIPE, SIG_IGN)' in src

    with tempfile.TemporaryDirectory(prefix='e003i-dx-proof-') as td:
        td=Path(td)
        helper=td/'helper'
        subprocess.run([str(HERE/'build-helper.sh'),str(helper)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        # C publisher -> Python parser ABI proof.
        emit=td/'emit.c'; exe=td/'emit'
        emit.write_text(r'''#include <stdint.h>
#include <string.h>
#include "gain-feed.h"
int main(void){
    const uint32_t bits[3]={0x3f80397bU,0x3f80216aU,0x3f801646U};
    for(uint32_t i=0;i<3;i++){float f;memcpy(&f,&bits[i],4);if(e003i_gain_feed_publish(1,i+1,i+4,f))return 10+(int)i;}
    return 0;
}
''')
        subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-I',str(HERE),str(emit),str(HERE/'gain-feed.c'),'-lm','-o',str(exe)],check=True)
        cp=subprocess.run([str(exe)],check=True,stdout=subprocess.PIPE)
        blob=cp.stdout
        assert len(blob)==72
        records=[]
        for i,bitsv in enumerate(GAIN_BITS,1):
            gain,meta=DX.GainFeed.decode(blob[(i-1)*24:i*24],i)
            assert DX.bits(gain)==bitsv
            assert meta=={'generation':i,'request':i+3,'isp_gain_bits':f'0x{bitsv:08x}'}
            records.append(meta)

        # Real fd/poll/order behavior over the same C-produced byte stream.
        rfd,wfd=os.pipe()
        os.write(wfd,blob);os.close(wfd)
        feed=DX.GainFeed(rfd)
        got=[]
        for i,bitsv in enumerate(GAIN_BITS,1):
            gain,meta=feed.get(i,1000);assert DX.bits(gain)==bitsv;got.append(meta)
        os.close(rfd)
        assert got==records

        # Malformed generation is rejected rather than consumed as another frame.
        bad=bytearray(blob[:24]);struct.pack_into('<I',bad,8,2)
        try: DX.GainFeed.decode(bytes(bad),1)
        except RuntimeError: pass
        else: raise AssertionError('wrong generation accepted')

        # Replay the exact preserved DT G1..G3 pairs using the C-emitted feed.
        rfd,wfd=os.pipe();os.write(wfd,blob);os.close(wfd);feed=DX.GainFeed(rfd)
        p=DX.Producer(td/'producer');rows=[];caps={}
        for gen in (1,2,3):
            s=(a.dt_producer_dir/f'STATS3A-G{gen}.bin').read_bytes()
            t=(a.dt_producer_dir/f'TLBG-G{gen}.bin').read_bytes()
            gain,meta=feed.get(gen,1000)
            row,cap,_=p.process(s,t,gain);row['gain_feed']=meta;rows.append(row)
            assert row['cq_isp_gain_bits']==f'0x{GAIN_BITS[gen-1]:08x}'
            if cap is not None:caps[gen+3]=sha(cap)
        os.close(rfd)
        assert caps[5]==DW_RESULT['rows'][1]['new_capsule']
        assert caps[6]==DW_RESULT['rows'][2]['new_capsule']
        assert rows[1]['demux_bls']['reg_3b70']=='0x04280428' and rows[1]['demux_bls']['reg_3b74']=='0x04280427'
        assert rows[2]['demux_bls']['reg_3b70']=='0x04270427' and rows[2]['demux_bls']['reg_3b74']=='0x04280427'

    out={'schema':'sp11-e003i-dx-parent-cq-gain-feed-proof-v1','status':'PASS','runtime_performed':False,
         'record_bytes':24,'magic':'IGF1','generations':[1,2,3],'requests':[4,5,6],
         'isp_gain_bits':[f'0x{x:08x}' for x in GAIN_BITS],
         'c_writer_python_reader_abi':'PASS','fd_poll_order_gate':'PASS','malformed_generation_rejected':True,
         'full_helper_strict_build':'PASS','preserved_dt_replay_capsules':{'R5':caps[5],'R6':caps[6]},
         'preserved_dt_demux':{'R5':['0x04280428','0x04280427'],'R6':['0x04270427','0x04280427']},
         'next_gate':'fresh one-shot candidate using DX helper/producer with DT scheduler + proven kernel modules',
         'continuous_aec_claimed':False}
    a.manifest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('DX_C_WRITER_PYTHON_READER_ABI=PASS')
    print('DX_GAIN_ORDER_G1_G3=PASS')
    print('DX_MALFORMED_GENERATION_REJECTED=PASS')
    print('DX_HELPER_STRICT_BUILD=PASS')
    print('DX_DT_REPLAY_R5='+caps[5])
    print('DX_DT_REPLAY_R6='+caps[6])
    print('DX_RUNTIME=0')
    print('DX_VERIFY=PASS')
if __name__=='__main__': main()
