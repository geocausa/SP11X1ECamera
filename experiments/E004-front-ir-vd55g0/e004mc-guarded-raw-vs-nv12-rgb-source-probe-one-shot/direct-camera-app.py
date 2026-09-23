#!/usr/bin/python3
"""Bounded independent direct GStreamer app, synthetic by default; no pixel files."""
import argparse, hashlib, json, os, statistics, time
import numpy as np
from pathlib import Path
import gi
gi.require_version('Gst','1.0')
from gi.repository import Gst
DEVICES={'front':('/dev/video91',1920,1080),'rear':('/dev/video90',3840,2160)}
MAX_FRAMES=2400

def quality(data,width,height):
 # Sample every 64th byte in each I420 plane. Numeric scene statistics only.
 ysize=width*height;csize=ysize//4
 arr=np.frombuffer(data,dtype=np.uint8)
 y=arr[:ysize:64];u=arr[ysize:ysize+csize:64];v=arr[ysize+csize:ysize+2*csize:64]
 return {'y_mean':float(y.mean()),'y_min':int(y.min()),'y_max':int(y.max()),
         'y_zero_fraction':float(np.mean(y==0)),'y_255_fraction':float(np.mean(y==255)),
         'u_mean':float(u.mean()),'v_mean':float(v.mean())}

def run(camera,frames,source='synthetic',require_distinct=False,deadline_seconds=180):
 if camera not in DEVICES or type(frames) is not int or not 1<=frames<=MAX_FRAMES:
  raise ValueError('INVALID_CAMERA_OR_FRAME_BOUND')
 if not 1<=deadline_seconds<=240:raise ValueError('INVALID_DEADLINE')
 device,width,height=DEVICES[camera];size=width*height*3//2
 if source=='device':
  cmd=Path('/proc/cmdline').read_text()
  if os.geteuid() not in (0,1000) or 'sp11_camera_e004mc_rgb_session=1' not in cmd.split():
   raise ValueError('LIVE_CAMERA_REQUIRES_NEW_E004MC_ISOLATED_BOOT')
  prefix=f'v4l2src device={device} io-mode=mmap num-buffers={frames}'
 elif source=='synthetic':prefix=f'videotestsrc pattern=ball num-buffers={frames} is-live=false'
 elif source=='constant':prefix=f'videotestsrc pattern=black num-buffers={frames} is-live=false'
 else:raise ValueError('INVALID_SOURCE')
 Gst.init(None)
 pipe=Gst.parse_launch(prefix+f' ! video/x-raw,format=NV12,width={width},height={height},framerate=30/1 ! videoconvert ! video/x-raw,format=I420,width={width},height={height} ! appsink name=app sync=false max-buffers=3 drop=false')
 sink=pipe.get_by_name('app');bus=pipe.get_bus();times=[];offsets=[];pts=[];hashes=set();total_bytes=0;errors=[]
 iq=[]
 started=time.monotonic();deadline=started+deadline_seconds
 try:
  if pipe.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:raise RuntimeError('PLAYING_FAILED')
  while len(times)<frames and time.monotonic()<deadline:
   sample=sink.emit('try-pull-sample',Gst.SECOND)
   if sample is None:
    message=bus.pop_filtered(Gst.MessageType.ERROR)
    if message is not None:
     error,_=message.parse_error();errors.append(str(error));break
    if sink.get_property('eos'):break
    continue
   arrival=time.monotonic_ns();buf=sample.get_buffer();caps=sample.get_caps().get_structure(0)
   if caps.get_string('format')!='I420' or caps.get_value('width')!=width or caps.get_value('height')!=height or buf.get_size()!=size:
    raise RuntimeError('INCOMPLETE_OR_WRONG_APPLICATION_FRAME')
   # Map the real Gst buffer once. Export neither pixels nor hashes.
   ok,mapping=buf.map(Gst.MapFlags.READ)
   if not ok:raise RuntimeError('BUFFER_MAP_FAILED')
   try:
    data=mapping.data
    hashes.add(hashlib.sha256(data).digest())
    if len(times)%30==0:iq.append(quality(data,width,height))
   finally:buf.unmap(mapping)
   times.append(arrival);offsets.append(int(buf.offset));pts.append(int(buf.pts));total_bytes+=size
   if len(times)%30==0:print(json.dumps({'progress_frames':len(times),'elapsed_s':round(time.monotonic()-started,3)}),flush=True)
  eof=False
  if len(times)==frames:
   # A num-buffers source must terminate, not silently exceed the request.
   extra=sink.emit('try-pull-sample',Gst.SECOND)
   if extra is not None:raise RuntimeError('EXTRA_APPLICATION_FRAME')
   msg=bus.timed_pop_filtered(2*Gst.SECOND,Gst.MessageType.EOS|Gst.MessageType.ERROR)
   eof=bool(msg is not None and msg.type==Gst.MessageType.EOS)
  intervals=[(b-a)/1e6 for a,b in zip(times,times[1:])]
  span=(times[-1]-times[0])/1e9 if len(times)>1 else 0
  known_offsets=[x for x in offsets if x!=Gst.BUFFER_OFFSET_NONE]
  ordered=all(a<b for a,b in zip(known_offsets,known_offsets[1:]))
  success=len(times)==frames and eof and not errors and (not require_distinct or len(hashes)==frames)
  report={'effective_uid':os.geteuid(),'status':'PASS' if success else 'FAIL','source':source,'camera':camera,'device':device if source=='device' else None,'app_format':f'I420_{width}x{height}','requested_frames':frames,'complete_frames':len(times),'complete_bytes':total_bytes,'all_payloads_distinct':len(hashes)==frames,'distinct_payloads':len(hashes),'observed_span_s':round(span,6),'observed_fps':round((len(times)-1)/span,4) if span else 0,'p95_gap_ms':round(sorted(intervals)[min(len(intervals)-1,int(len(intervals)*.95))],3) if intervals else 0,'max_gap_ms':round(max(intervals),3) if intervals else 0,'gst_offsets_available':len(known_offsets),'gst_offsets_monotonic':ordered,'gst_offset_first_last':[known_offsets[0],known_offsets[-1]] if known_offsets else [],'gst_offset_gaps':sum(max(0,b-a-1) for a,b in zip(known_offsets,known_offsets[1:])),'gst_offsets_are_sensor_sequences_proven':False,'actual_fps_uses_monotonic_arrivals':True,'synthetic_pts_used_as_fps':False,'normal_eos':eof,'errors':errors,'pixel_files_or_hashes_exported':False,'windows_isp_quality_parity_proven':False,'quality_stats':{'sample_every_frames':30,'plane_byte_stride':64,'samples':len(iq),'y_mean_range':[min(x['y_mean'] for x in iq),max(x['y_mean'] for x in iq)] if iq else [],'y_min':min((x['y_min'] for x in iq),default=None),'y_max':max((x['y_max'] for x in iq),default=None),'max_y_zero_fraction':max((x['y_zero_fraction'] for x in iq),default=None),'max_y_255_fraction':max((x['y_255_fraction'] for x in iq),default=None),'mean_u':statistics.mean(x['u_mean'] for x in iq) if iq else None,'mean_v':statistics.mean(x['v_mean'] for x in iq) if iq else None,'calibrated_quality_or_windows_scene_comparison':False}}
  print(json.dumps(report,sort_keys=True),flush=True)
  return report
 finally:pipe.set_state(Gst.State.NULL)

def main():
 p=argparse.ArgumentParser();p.add_argument('--camera',choices=DEVICES,required=True);p.add_argument('--frames',type=int,required=True);p.add_argument('--source',choices=('synthetic','constant','device'),default='synthetic');p.add_argument('--require-distinct',action='store_true');p.add_argument('--deadline-seconds',type=int,default=180)
 a=p.parse_args()
 try:r=run(a.camera,a.frames,a.source,a.require_distinct,a.deadline_seconds)
 except Exception as e:print(json.dumps({'status':'FAIL','error':str(e)}),flush=True);return 1
 return 0 if r['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
