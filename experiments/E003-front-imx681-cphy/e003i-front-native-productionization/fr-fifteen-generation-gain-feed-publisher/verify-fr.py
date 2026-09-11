#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
FK=BASE/'fk-twelve-generation-gain-feed-publisher'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)

need(sha(HERE/'gain-feed.h')==sha(FK/'gain-feed.h'),'ABI header drift')
src=(HERE/'gain-feed.c').read_text()
parent=(FK/'gain-feed.c').read_text()
need('generation > 15U' in src and 'generation > 12U' not in src,'G15 bound missing')
need(src.replace('generation > 15U','generation > 12U')==parent,'unexpected publisher delta')

test=r'''
#include "gain-feed.h"
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
static int rd(int fd,void *buf,size_t n){unsigned char*p=buf;while(n){ssize_t r=read(fd,p,n);if(r<=0)return -1;p+=(size_t)r;n-=(size_t)r;}return 0;}
int main(void){
 int fds[2]; if(pipe(fds)) return 10;
 for(uint32_t g=1;g<=15;g++){
   struct e003i_gain_feed_record r; float gain=1.0f+(float)g/1024.0f;
   int rc=e003i_gain_feed_publish(fds[1],g,g+3,gain); if(rc) return 20+(int)g;
   if(rd(fds[0],&r,sizeof(r))) return 50+(int)g;
   if(r.magic!=E003I_GAIN_FEED_MAGIC||r.version!=E003I_GAIN_FEED_VERSION||
      r.bytes!=E003I_GAIN_FEED_RECORD_BYTES||r.generation!=g||
      r.request!=g+3||r.reserved!=0) return 80+(int)g;
 }
 if(e003i_gain_feed_publish(fds[1],16,19,1.0f)!=-EINVAL) return 110;
 if(e003i_gain_feed_publish(fds[1],15,17,1.0f)!=-EINVAL) return 111;
 close(fds[0]); close(fds[1]);
 puts("FR_C_PUBLISHER_G1_G15=PASS G16_REJECT=PASS"); return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='e003i-fr-') as td:
    td=Path(td); c=td/'test.c'; b=td/'test'; c.write_text(test)
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-I',str(HERE),str(c),str(HERE/'gain-feed.c'),'-lm','-o',str(b)],check=True)
    need(subprocess.check_output([str(b)],text=True).strip()=='FR_C_PUBLISHER_G1_G15=PASS G16_REJECT=PASS','compiled publisher proof')

out={
 'schema':'sp11-e003i-fr-fifteen-generation-gain-feed-publisher-v1',
 'status':'PASS_OFFLINE_G1_G15_C_PUBLISHER',
 'parent':'FK',
 'delta':'generation validation upper bound 12 -> 15 only',
 'accepted_generations':list(range(1,16)),
 'rejected_generation':16,
 'request_identity':'request == generation + 3',
 'gain_feed_h_sha256':sha(HERE/'gain-feed.h'),
 'gain_feed_c_sha256':sha(HERE/'gain-feed.c'),
 'live_runtime_performed':False,
 'continuous_aec_claimed':False,
}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
