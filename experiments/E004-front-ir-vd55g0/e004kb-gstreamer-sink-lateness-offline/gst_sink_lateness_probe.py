#!/usr/bin/python3
"""E004kb: camera-free synthetic timestamp/late-frame control experiments."""
import argparse
import json
import os
import threading
import time

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

Gst.init(None)
WIDTH, HEIGHT = 320, 180
NV12_BYTES=WIDTH*HEIGHT*3//2
SOURCE_FPS=22
CAPS_FPS=30
FRAME_NS=Gst.SECOND//CAPS_FPS
SAMPLE=bytes([127])*NV12_BYTES


def inspect_default_v4l2sink():
    sink=Gst.ElementFactory.make("v4l2sink")
    if sink is None:
        raise RuntimeError("installed GStreamer v4l2sink absent")
    result={
        "v4l2sink_sync_default":bool(sink.get_property("sync")),
        "v4l2sink_qos_default":bool(sink.get_property("qos")),
        "v4l2sink_max_lateness_default_ns":int(sink.get_property("max-lateness")),
        "v4l2sink_processing_deadline_default_ns":
            int(sink.get_property("processing-deadline")),
    }
    sink.set_state(Gst.State.NULL)
    return result


def probe_rawvideoparse_pts():
    """Verify caps framerate stamps the production fdsrc->rawvideoparse route."""
    rfd,wfd=os.pipe()
    pipeline=None
    observed=[]
    try:
        pipeline=Gst.parse_launch(
            f"fdsrc fd={rfd} blocksize={NV12_BYTES} ! "
            f"rawvideoparse format=nv12 width={WIDTH} height={HEIGHT} "
            "framerate=30/1 ! identity name=tap signal-handoffs=true "
            "! fakesink sync=false"
        )
        identity=pipeline.get_by_name("tap")
        identity.connect("handoff",lambda _self,buf:observed.append(int(buf.pts)))
        pipeline.set_state(Gst.State.PLAYING)
        payload=SAMPLE*3
        def writer():
            try:
                view=memoryview(payload)
                while view:
                    n=os.write(wfd,view[:65536])
                    view=view[n:]
            finally:
                os.close(wfd)
        thread=threading.Thread(target=writer,daemon=True)
        thread.start()
        msg=pipeline.get_bus().timed_pop_filtered(
            10*Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR)
        if msg is None:
            raise RuntimeError("rawvideoparse timestamp probe timed out")
        if msg.type == Gst.MessageType.ERROR:
            raise RuntimeError(msg.parse_error()[1])
        thread.join(timeout=2)
        if thread.is_alive():
            raise RuntimeError("probe writer did not finish")
        return observed
    finally:
        if pipeline is not None:
            pipeline.set_state(Gst.State.NULL)
        os.close(rfd)
        try:
            os.close(wfd)
        except OSError:
            pass


def simulate_paced_fdsrc(sink_mode, frames, fps):
    """Closely reproduce production fdsrc->rawvideoparse->clocked sink."""
    if sink_mode not in ("v4l2sink_default_clock_model","no_lateness_drop","unsynced"):
        raise ValueError("invalid sink clock model")
    if not 5 <= frames <= 120 or not 5 <= fps <= 60:
        raise ValueError("finite frame/fps bounds required")
    modes={
        "v4l2sink_default_clock_model":"sync=true qos=true max-lateness=5000000",
        "no_lateness_drop":"sync=true qos=true max-lateness=-1",
        "unsynced":"sync=false qos=false max-lateness=-1",
    }
    rfd,wfd=os.pipe()
    pipeline=None
    rendered=[]
    error=[]
    byte_count=[0]
    complete=[0]
    try:
        pipeline=Gst.parse_launch(
            f"fdsrc fd={rfd} blocksize={NV12_BYTES} ! "
            f"rawvideoparse format=nv12 width={WIDTH} height={HEIGHT} "
            "framerate=30/1 ! queue max-size-buffers=4 "
            "max-size-bytes=0 max-size-time=0 "
            f"! fakesink name=sink signal-handoffs=true {modes[sink_mode]}"
        )
        sink=pipeline.get_by_name("sink")
        sink.connect("handoff",lambda _sink,buf,_pad:
                     rendered.append(int(buf.pts//FRAME_NS)))
        pipeline.set_state(Gst.State.PLAYING)
        def writer():
            start=time.monotonic_ns()
            try:
                for index in range(frames):
                    remaining=(start+int(index*1e9/fps)-time.monotonic_ns())/1e9
                    if remaining>0:
                        time.sleep(remaining)
                    data=memoryview(SAMPLE)
                    while data:
                        count=os.write(wfd,data[:65536])
                        data=data[count:]
                        byte_count[0]+=count
                    complete[0]+=1
            except Exception as exc:
                error.append(repr(exc))
            finally:
                os.close(wfd)
        thread=threading.Thread(target=writer,daemon=True)
        thread.start()
        msg=pipeline.get_bus().timed_pop_filtered(
            24*Gst.SECOND,Gst.MessageType.ERROR | Gst.MessageType.EOS)
        if msg is None:
            raise RuntimeError("synthetic fdsrc simulation timeout")
        if msg.type==Gst.MessageType.ERROR:
            raise RuntimeError(str(msg.parse_error()))
        thread.join(timeout=2)
        if thread.is_alive() or error or complete[0]!=frames:
            raise RuntimeError(f"incomplete fdsrc source {complete} errors={error}")
        return {
            "sink_clock_mode":sink_mode,
            "synthetic_paced_fdsrc_frames_written":complete[0],
            "synthetic_fdsrc_bytes_written":byte_count[0],
            "synthetic_paced_fps":fps,
            "rawvideoparse_nominal_caps_pts_fps":CAPS_FPS,
            "fakesink_rendered_frames":len(rendered),
            "fakesink_late_dropped_frames":frames-len(rendered),
            "first_rendered_pts_frame":rendered[0] if rendered else None,
            "last_rendered_pts_frame":rendered[-1] if rendered else None,
            "real_camera_or_4k_device_activated":False,
        }
    finally:
        if pipeline is not None:
            pipeline.set_state(Gst.State.NULL)
        os.close(rfd)
        try:
            os.close(wfd)
        except OSError:
            pass


def simulate(sink_mode, frames, fps):
    if not 5 <= frames <= 120 or not 5 <= fps <= 60:
        raise ValueError("finite 5..120 frames and 5..60 source fps required")
    if sink_mode not in ("v4l2sink_default_clock_model","no_lateness_drop","unsynced"):
        raise ValueError("unsupported sink model")
    if sink_mode=="v4l2sink_default_clock_model":
        sink_args="sync=true qos=true max-lateness=5000000"
    elif sink_mode=="no_lateness_drop":
        sink_args="sync=true qos=true max-lateness=-1"
    else:
        sink_args="sync=false qos=false max-lateness=-1"
    pipeline=Gst.parse_launch(
        "appsrc name=source is-live=true format=time block=true "
        f"caps=video/x-raw,format=NV12,width={WIDTH},height={HEIGHT},framerate=30/1 "
        "! queue max-size-buffers=4 max-size-bytes=0 max-size-time=0 "
        f"! fakesink name=sink signal-handoffs=true {sink_args}"
    )
    source=pipeline.get_by_name("source")
    sink=pipeline.get_by_name("sink")
    rendered=[]
    sink.connect("handoff",
                 lambda _sink,buf,_pad: rendered.append(int(buf.pts//FRAME_NS)))
    problems=[]
    started_ns=0
    completed_push=0
    def producer():
        nonlocal started_ns,completed_push
        started_ns=time.monotonic_ns()
        try:
            for i in range(frames):
                deadline=started_ns+int(i*1e9/fps)
                remaining=(deadline-time.monotonic_ns())/1e9
                if remaining>0:
                    time.sleep(remaining)
                buf=Gst.Buffer.new_allocate(None,NV12_BYTES,None)
                if buf is None or buf.fill(0,SAMPLE)!=NV12_BYTES:
                    raise RuntimeError("synthetic frame allocation/fill failure")
                buf.pts=i*FRAME_NS
                buf.duration=FRAME_NS
                status=source.emit("push-buffer",buf)
                if status != Gst.FlowReturn.OK:
                    raise RuntimeError(f"source push returned {status}")
                completed_push+=1
            if source.emit("end-of-stream")!=Gst.FlowReturn.OK:
                raise RuntimeError("appsrc EOS not accepted")
        except Exception as exc:
            problems.append(repr(exc))
            source.emit("end-of-stream")
    try:
        pipeline.set_state(Gst.State.PLAYING)
        thread=threading.Thread(target=producer,daemon=True)
        thread.start()
        msg=pipeline.get_bus().timed_pop_filtered(
            24*Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR)
        if msg is None:
            raise RuntimeError("bounded appsrc test did not reach EOS")
        if msg.type==Gst.MessageType.ERROR:
            raise RuntimeError(f"pipeline error {msg.parse_error()}")
        thread.join(timeout=2)
        if thread.is_alive() or problems or completed_push!=frames:
            raise RuntimeError(f"incomplete producer {completed_push}/{frames}: {problems}")
        return {
            "sink_clock_mode":sink_mode,
            "synthetic_source_frames_pushed":completed_push,
            "synthetic_source_pace_fps":fps,
            "synthetic_caps_pts_fps":CAPS_FPS,
            "simulated_rendered_frames":len(rendered),
            "simulated_dropped_before_handoff":completed_push-len(rendered),
            "first_rendered_pts_frame":rendered[0] if rendered else None,
            "last_rendered_pts_frame":rendered[-1] if rendered else None,
            "camera_or_4k_hardware_test":False,
        }
    finally:
        pipeline.set_state(Gst.State.NULL)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--frames",type=int,default=90)
    parser.add_argument("--source-fps",type=int,default=22)
    a=parser.parse_args()
    result={"experiment":"E004kb",
            "source":"installed_Sp11_Golden_GStreamer_1.28.2",
            "actual_v4l2sink_default_properties":inspect_default_v4l2sink(),
            "rawvideoparse_first_three_pts":probe_rawvideoparse_pts(),
            "fdsrc_rawvideoparse_sink_simulations":[
                simulate_paced_fdsrc(mode,a.frames,a.source_fps)
                for mode in ("v4l2sink_default_clock_model",
                             "no_lateness_drop","unsynced")],
            "simulations":[simulate(mode,a.frames,a.source_fps)
                           for mode in ("v4l2sink_default_clock_model",
                                        "no_lateness_drop","unsynced")]}
    print("E004KB_SOURCE_ONLY_GSTREAMER_TEST="+json.dumps(result,sort_keys=True))
if __name__=="__main__":
    main()
