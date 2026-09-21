#!/usr/bin/python3
import json,re,sys
from pathlib import Path

def validate(camera,source_text,app):
 if camera not in ('front','rear'):raise ValueError('INVALID_CAMERA')
 size=10368000 if camera=='front' else 14321824
 entries=re.findall(r'cap dqbuf:\s*\d+ seq:\s*(\d+) bytesused:\s*'+str(size)+r'.*?ts:\s*([0-9]+\.[0-9]+)',source_text)
 if len(entries)!=2400:raise ValueError('INCOMPLETE_SOURCE_BUFFERS')
 seq=[int(x[0]) for x in entries];ts=[float(x[1]) for x in entries]
 if not all(a<b for a,b in zip(seq,seq[1:])) or not all(a<b for a,b in zip(ts,ts[1:])):raise ValueError('NONMONOTONIC_SOURCE')
 frame_bytes=3110400 if camera=='front' else 12441600
 device='/dev/video91' if camera=='front' else '/dev/video90'
 if not (app['status']=='PASS' and app['source']=='device' and app['camera']==camera and app['device']==device and app['complete_frames']==1800 and app['requested_frames']==1800 and app['complete_bytes']==1800*frame_bytes and app['all_payloads_distinct'] and app['normal_eos']):raise ValueError('INCOMPLETE_OR_WRONG_DIRECT_APP')
 return {'status':'PASS','camera':camera,'source_frames':len(seq),'source_first_last_sequence':[seq[0],seq[-1]],'source_sequence_gaps':sum(b-a-1 for a,b in zip(seq,seq[1:])),'source_span_s':round(ts[-1]-ts[0],6),'source_timestamp_fps':round((len(ts)-1)/(ts[-1]-ts[0]),4),'source_app_measurement_windows_differ':True,'direct_app':app,'permanent_service_or_windows_isp_parity_proven':False}

def main():
 camera=sys.argv[1];o=Path(sys.argv[2])
 source=o/('REAL-FRONT-RAW2400-CAPTURE.txt' if camera=='front' else 'REAL-REAR-CAPTURE2400.txt')
 app=json.loads((o/(camera.upper()+'-DIRECT-APP.jsonl')).read_text().splitlines()[-1])
 print(json.dumps(validate(camera,source.read_text(),app),indent=2))
if __name__=='__main__':main()
