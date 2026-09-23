#!/usr/bin/python3
"""Synthetic-only V4L2 text-event and UID1000 GStreamer caps negative checks."""
import unittest,json,tempfile
from pathlib import Path
from validate_bt601_live import parse_native_tag,validate

def log(camera):
 w,h=((1920,1080) if camera=="front" else (3840,2160))
 geometry=f"width={w} height={h} fourcc=842094158 bytesperline={w} sizeimage={w*h*3//2}"
 prefix=f"E004NC_COLOR_DIAG camera={camera}"
 requested=f"{prefix} stage=request {geometry} colorspace=1 ycbcr_enc=1 quantization=2 xfer_func=1"
 raw=f"{geometry} colorspace=1 ycbcr_enc=0 quantization=0 xfer_func=0"
 returned=f"{prefix} stage=S_FMT_return rc=0 errno=0 {raw}"
 getter=f"{prefix} stage=G_FMT_return rc=0 errno=0 {raw}"
 event=(f"E004NC_REAL_V4L2_OUTPUT_COLORIMETRY camera={camera} "
       f"width={w} height={h} colorspace=1 ycbcr_enc=0 "
       "quantization=0 xfer_func=0 effective_bt601=YES")
 return "\n".join((requested,returned,getter,event))+"\n"

def probe(camera):
 return dict(status="PASS",camera=camera,frames=90,effective_uid=1000,
       real_v4l2src_NV12_colorimetry="bt601",
       ordinary_UID1000_I420_consumer_colorimetry="bt601",
       consumer_colorimetry_from_actual_real_video_not_synthetic=True,
       pixel_files_saved=False,camera_route_or_controls_changed=False)

class BT601(unittest.TestCase):
 def test_native_tags_and_failclosed(self):
  self.assertTrue(parse_native_tag(log("front"),"front")["effective_V4L2_NV12_YCbCr601_limited_xfer709"])
  self.assertEqual(parse_native_tag(log("rear"),"rear")["actual_independent_G_FMT_return_raw_color_fields"]["ycbcr_enc"],0)
  for broken in (log("front").replace("colorspace=1","colorspace=3"),
                 log("front").replace("quantization=0","quantization=1"),
                 log("front").replace("ycbcr_enc=0","ycbcr_enc=2"),
                 log("front").replace("xfer_func=0","xfer_func=2"),
                 log("front").replace("effective_bt601=YES","effective_bt601=NO"),
                 log("front").replace("stage=G_FMT_return","stage=G_FMT_wrong"),
                 log("front").replace("stage=request","stage=S_FMT_return"),
                 log("front").replace("rc=0","rc=-1"),
                 log("front").replace("fourcc=842094158","fourcc=1"),
                 log("front").replace("height=1080","height=900"),
                 log("front")+log("front")):
   with self.assertRaises(ValueError):parse_native_tag(broken,"front")
 def test_real_app_exhaustive_two_cam_two_phase(self):
  with tempfile.TemporaryDirectory(prefix="synthetic-color-caps.") as root:
   p=Path(root)
   for camera in ("front","rear"):
    (p/(camera+"-SERVICE-STDERR.txt")).write_text(log(camera))
    for phase in ("DAYLIGHT","GAIN"):
     (p/(camera.upper()+"-"+phase+"-PROBE.json")).write_text(
         json.dumps(probe(camera)))
   self.assertTrue(validate(p)["both_actual_cameras_and_both_native_gain_phases_checked"])
   target=p/"FRONT-GAIN-PROBE.json"
   good=json.loads(target.read_text())
   for changes in (
       dict(real_v4l2src_NV12_colorimetry="bt709"),
       dict(ordinary_UID1000_I420_consumer_colorimetry=None),
       dict(effective_uid=0),dict(frames=89),
       dict(consumer_colorimetry_from_actual_real_video_not_synthetic=False)):
    target.write_text(json.dumps(dict(good,**changes)))
    with self.assertRaises(ValueError):validate(p)
   target.write_text(json.dumps(good))
   (p/"rear-SERVICE-STDERR.txt").unlink()
   with self.assertRaises(FileNotFoundError):validate(p)

if __name__=="__main__":unittest.main()
