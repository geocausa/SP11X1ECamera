#!/usr/bin/python3
import json,sys
from pathlib import Path
def validate(publisher,app):
 assert publisher['status']=='PASS' and publisher['frames']==publisher['requested']==2400
 assert publisher['source_sequence_first_last']==[0,2399] and publisher['source_sequence_gaps']==0
 assert publisher['source_span_s']>0
 assert app['status']=='PASS' and app['source']=='device' and app['camera']=='rear' and app['device']=='/dev/video90'
 assert app['app_format']=='I420_3840x2160'
 assert app['complete_frames']==app['requested_frames']==app['distinct_payloads']==1800
 assert app['complete_bytes']==1800*3840*2160*3//2
 assert app['all_payloads_distinct'] and app['normal_eos'] and not app['errors']
 return {'status':'PASS','publisher':publisher,'source_timestamp_fps':2399/publisher['source_span_s'],'direct_app':app,'source_app_windows_differ':True,'windows_isp_parity_proven':False}
if __name__=='__main__':
 assert sys.argv[1]=='rear'
 p=Path(sys.argv[2]);source=json.loads((p/'REAR-DIRECT-PUBLISHER.json').read_text().splitlines()[-1]);app=json.loads((p/'REAR-DIRECT-APP.jsonl').read_text().splitlines()[-1])
 print(json.dumps(validate(source,app),indent=2))
