#!/usr/bin/python3
import json,re,sys
from pathlib import Path
def validate(camera,text,app):
 n,w,h,node=(1800,1920,1080,'/dev/video91') if camera=='front' else (1800,3840,2160,'/dev/video90')
 lines=text.splitlines();pub=json.loads(lines[-1])
 life=re.fullmatch(r'E004KQ_LIFECYCLE captured=(\d+) published=(\d+) termination_requested=1 streamoff_completed=1',lines[-2]);assert life
 captured,published=map(int,life.groups())
 assert pub['status']=='STOPPED' and pub['requested']==2400
 assert n<=pub['frames']==published<=captured<2400 and captured-published<=1
 assert pub['source_sequence_first_last']==[0,captured-1] and pub['source_sequence_gaps']==0
 assert pub['source_span_s']>0
 assert app['effective_uid']==1000
 assert app['status']=='PASS' and app['source']=='device' and app['camera']==camera and app['device']==node
 assert app['app_format']==f'I420_{w}x{h}'
 assert app['complete_frames']==app['requested_frames']==app['distinct_payloads']==n
 assert app['complete_bytes']==n*w*h*3//2
 assert app['all_payloads_distinct'] and app['normal_eos'] and not app['errors']
 return {'status':'PASS','camera':camera,'publisher':pub,'captured_frames':captured,'controlled_stop_streamoff_completed':True,'source_timestamp_fps':(captured-1)/pub['source_span_s'],'direct_app':app,'source_app_windows_differ':True,'windows_isp_parity_proven':False}
if __name__=='__main__':
 camera=sys.argv[1];assert camera in ('front','rear');p=Path(sys.argv[2]);key=camera.upper()
 text=(p/f'{key}-DIRECT-PUBLISHER.json').read_text();app=json.loads((p/f'{key}-DIRECT-APP.jsonl').read_text().splitlines()[-1])
 print(json.dumps(validate(camera,text,app),indent=2))
