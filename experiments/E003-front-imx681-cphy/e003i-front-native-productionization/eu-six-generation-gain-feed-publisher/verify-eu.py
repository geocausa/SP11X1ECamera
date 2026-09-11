#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess, tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
EN=BASE/'en-r5-r9-live-producer-integration'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
    if not x: raise AssertionError(m)
need(sha(HERE/'gain-feed.h')==sha(EN/'gain-feed.h'),'gain-feed.h drift')
src=(HERE/'gain-feed.c').read_text()
parent=(EN/'gain-feed.c').read_text()
need('generation > 6U' in src and 'generation > 3U' not in src,'six-generation bound missing')
need(src.replace('generation > 6U','generation > 3U')==parent,'unexpected publisher delta')
test=r'''
#include "gain-feed.h"
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
static int rd(int fd, void *buf, size_t n) {
    unsigned char *p=buf;
    while (n) {
        ssize_t r=read(fd,p,n);
        if (r<=0) return -1;
        p += (size_t)r; n -= (size_t)r;
    }
    return 0;
}
int main(void) {
    int fds[2];
    if (pipe(fds)) return 10;
    for (uint32_t g=1; g<=6; g++) {
        struct e003i_gain_feed_record rec;
        float gain = 1.0f + (float)g / 1024.0f;
        int rc=e003i_gain_feed_publish(fds[1],g,g+3,gain);
        if (rc) return 20+(int)g;
        if (rd(fds[0],&rec,sizeof(rec))) return 30+(int)g;
        if (rec.magic!=E003I_GAIN_FEED_MAGIC ||
            rec.version!=E003I_GAIN_FEED_VERSION ||
            rec.bytes!=E003I_GAIN_FEED_RECORD_BYTES ||
            rec.generation!=g || rec.request!=g+3 || rec.reserved!=0)
            return 40+(int)g;
    }
    if (e003i_gain_feed_publish(fds[1],7,10,1.0f) != -EINVAL) return 70;
    if (e003i_gain_feed_publish(fds[1],6,8,1.0f) != -EINVAL) return 71;
    close(fds[0]); close(fds[1]);
    puts("EU_C_PUBLISHER_G1_G6=PASS G7_REJECT=PASS");
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='e003i-eu-') as td:
    td=Path(td)
    c=td/'test.c'; b=td/'test'
    c.write_text(test)
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror',
                    '-I',str(HERE),str(c),str(HERE/'gain-feed.c'),'-lm','-o',str(b)],check=True)
    out=subprocess.check_output([str(b)],text=True).strip()
    need(out=='EU_C_PUBLISHER_G1_G6=PASS G7_REJECT=PASS','publisher runtime proof')
result={
  'schema':'sp11-e003i-eu-six-generation-gain-feed-publisher-v1',
  'status':'PASS_OFFLINE_G1_G6_C_PUBLISHER',
  'parent':'EN gain-feed publisher copied without modifying closed EN stage',
  'delta':'generation validation upper bound 3 -> 6 only',
  'accepted_generations':[1,2,3,4,5,6],
  'rejected_generation':7,
  'request_identity':'request == generation + 3',
  'gain_feed_h_sha256':sha(HERE/'gain-feed.h'),
  'gain_feed_c_sha256':sha(HERE/'gain-feed.c'),
  'live_runtime_performed':False,
  'continuous_aec_claimed':False
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
