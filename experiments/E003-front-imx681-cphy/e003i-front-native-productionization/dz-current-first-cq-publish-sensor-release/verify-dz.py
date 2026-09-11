#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DX=BASE/'dx-parent-cq-gain-feed'
DT=BASE/'dt-bounded-native-aec-cap-awb-hold-sensor-loop'

src=(HERE/'e003i-dz-six-frame-native-aec.c').read_text()
sched=(HERE/'native-db-schedule.c').read_text()+(HERE/'native-db-schedule.h').read_text()

# Static parent ordering contract.
thread=src[src.index('static void *pair_audit_thread'):]
i_aec=thread.index('e003i_raw_request_to_imx681_controls')
i_queue=thread.index('e003i_db_schedule_queue')
i_publish=thread.index('e003i_gain_feed_publish')
i_release=thread.index('release_control_at_video_boundary')
i_accept=thread.index('DZ_AEC_ACCEPT')
assert i_aec < i_queue < i_publish < i_release < i_accept
assert thread.count('release_control_at_video_boundary(ctx, target)')==1
assert 'target >= 2U && target <= 4U' in thread
assert 'source_generation = source' in (HERE/'native-db-schedule.c').read_text()
assert 'E003I_DB_WRITE_AFTER_OFFSET 1U' in sched
assert 'E003I_DB_WRITE_TO_EFFECT_DELAY 2U' in sched
assert 'E003I_DB_STATS_TO_REQUEST_DELAY 3U' in sched

# The producer/ABI implementation itself remains the already-passed DX one.
dx=json.loads((DX/'RESULT.json').read_text())
assert dx['status']=='PASS'
assert dx['c_writer_python_reader_abi']=='PASS'
assert dx['fd_poll_order_gate']=='PASS'

harness=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "native-db-schedule.h"
static struct e003i_imx681_controls good(unsigned n){
    struct e003i_imx681_controls c; memset(&c,0,sizeof(c));
    c.line_count_before_even=3554; c.frame_length_lines=3562; c.vertical_blanking=1402;
    c.exposure_lines=3554; c.analogue_gain_code=n; c.digital_gain_code=256; c.isp_gain=1.0f; return c;
}
static int evok(const struct e003i_db_apply_event *e,unsigned after){
    unsigned src=after-1;
    return e->apply && e->source_generation==src && e->write_after_generation==after &&
           e->logical_request_frame==src+3 && e->expected_effect_generation==after+2;
}
int main(void){
    struct e003i_db_schedule_state s; struct e003i_db_apply_event e; struct e003i_imx681_controls c;
    e003i_db_schedule_init(&s);
    c=good(1); if(e003i_db_schedule_queue(&s,1,&c)) return 11;
    for(unsigned g=2;g<=6;g++){
        c=good(g); if(e003i_db_schedule_queue(&s,g,&c)) return 20+(int)g;
        if(g<=4){ if(e003i_db_schedule_release(&s,g,&e) || !evok(&e,g)) return 30+(int)g; }
    }
    if(s.failed || s.queued_generation!=6 || s.released_writes!=3) return 50;
    puts("DZ_QUEUE_BEFORE_RELEASE=PASS");
    puts("DZ_RELEASE=G1@G2,G2@G3,G3@G4");
    puts("DZ_EFFECT=G4,G5,G6");
    return 0;
}
'''

with tempfile.TemporaryDirectory(prefix='e003i-dz-') as td:
    td=Path(td); hp=td/'h.c'; hp.write_text(harness); exe=td/'sched'; helper=td/'helper'
    cq=BASE/'cq-aec-output-imx681-control-adapter'
    ch=BASE/'ch-native-aec-t681-preview-arbitration'
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off',
                    '-I',str(HERE),'-I',str(cq),'-I',str(ch),str(HERE/'native-db-schedule.c'),str(hp),'-lm','-o',str(exe)],check=True)
    out=subprocess.check_output([str(exe)],text=True)
    assert 'DZ_QUEUE_BEFORE_RELEASE=PASS' in out
    subprocess.run([str(HERE/'build-helper.sh'),str(helper)],check=True)
    assert helper.is_file() and helper.stat().st_size>0

result={
  'schema':'sp11-e003i-dz-current-first-cq-publish-sensor-release-v1',
  'status':'PASS_OFFLINE',
  'runtime_performed':False,
  'ordering':['current_aec','current_schedule_queue','current_cq_gain_publish','previous_sensor_release'],
  'release_law':'G1@G2,G2@G3,G3@G4',
  'effect_law':'G4,G5,G6',
  'dx_gain_feed_abi_reused':True,
  'dy_attempt1_root_cause':'current CQ gain serialized behind previous sensor ioctl, delaying R5 by 23.502993 ms',
  'next_gate':'fresh one-shot live candidate with DZ parent and unchanged DX producer',
  'continuous_aec_claimed':False
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('DZ_PARENT_ORDER=AEC_QUEUE_PUBLISH_RELEASE PASS')
print('DZ_QUEUE_BEFORE_RELEASE_SCHEDULER=PASS')
print('DZ_RELEASE_EFFECT_LAW_UNCHANGED=PASS')
print('DZ_HELPER_WERROR=PASS')
print('DZ_RUNTIME=0')
print('DZ_VERIFY=PASS')
