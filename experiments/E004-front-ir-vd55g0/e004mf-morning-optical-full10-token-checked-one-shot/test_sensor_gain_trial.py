#!/usr/bin/python3
"""Camera-free only: mock sensor/clock and test strict control lifetime."""
import importlib.util
from pathlib import Path
from unittest import TestCase,main,mock
p=Path(__file__).with_name("sensor_gain_trial.py")
spec=importlib.util.spec_from_file_location("sensor_gain_trial",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def app(y):
 return dict(status="PASS",frames=90,effective_uid=1000,
             pixel_files_saved=False,max_sampled_p99_y=y,
             max_sampled_tile_std_y=.5)
class TrialTests(TestCase):
 def test_exact_front_gain_and_restore(self):
  current=m.BASELINE["front"].copy();steps=[]
  def rd(node):return current.copy()
  def setv(node,value,camera):
   self.assertEqual(camera,"front")
   current.update(value);steps.append(value.copy())
  with mock.patch.object(m,"sensor_node",return_value="/dev/v4l-subdev0"),\
       mock.patch.object(m,"read",side_effect=rd),\
       mock.patch.object(m,"query_supported_bounds",return_value={n:{"min":0,"max":4096,"step":1} for n in m.CMDS}),\
       mock.patch.object(m,"set_supported",side_effect=setv),\
       mock.patch.object(m.time,"monotonic",side_effect=[100.,100.5,104.5,105.]),\
       mock.patch.object(m.time,"sleep",return_value=None):
   x=m.perform(Path("/no/sensor"),"front",app(19),lambda:app(21))
  self.assertEqual(steps,[m.TARGET["front"],m.BASELINE["front"]])
  self.assertEqual(x["effect_on_app_p99_y"],2)
  self.assertEqual(x["restored_controls"],m.BASELINE["front"])
  self.assertLess(x["settled_ms"],x["restore_started_ms"])
 def test_no_write_if_unexpected_baseline(self):
  with mock.patch.object(m,"sensor_node",return_value="/dev/v4l-subdev1"),\
       mock.patch.object(m,"read",return_value={"exposure":0}),\
       mock.patch.object(m,"query_supported_bounds",return_value={n:{"min":0,"max":4096,"step":1} for n in m.CMDS}),\
       mock.patch.object(m,"set_supported") as setv:
   with self.assertRaisesRegex(RuntimeError,"BASELINE_NOT_EXACT"):
    m.perform(Path("/no/sensor"),"rear",app(16),lambda:app(17))
   setv.assert_not_called()
 def test_range_parser_rejects_bad_target(self):
  listing=("exposure 0x009a0902 (int) : min=4 max=4000 step=2 default=100 value=3546\n"
           "analogue_gain 0x009e0903 (int) : min=0 max=960 step=1 default=0 value=0\n"
           "digital_gain 0x009e0904 (int) : min=256 max=4096 step=1 default=256 value=256\n")
  with mock.patch.object(m,"_run",return_value=listing):
   result=m.query_supported_bounds("/dev/v4l-subdev0","front")
   self.assertEqual(result["analogue_gain"]["max"],960)
  with mock.patch.object(m,"_run",return_value=listing.replace("max=960","max=255")):
   with self.assertRaisesRegex(RuntimeError,"OUTSIDE_ADVERTISED"):
    m.query_supported_bounds("/dev/v4l-subdev0","front")

 def test_reject_ir_and_unapproved_control_tuples(self):
  with self.assertRaisesRegex(RuntimeError,"CAMERA_NOT_RGB"):
   m.perform(Path("/no/sensor"),"ir",app(16),lambda:app(17))
  with self.assertRaisesRegex(RuntimeError,"UNAPPROVED"):
   m.set_supported("/dev/v4l-subdev0",{"exposure":4},"front")
 def test_fail_closed_if_change_readback_not_confirmed(self):
  with mock.patch.object(m,"sensor_node",return_value="/dev/v4l-subdev0"),\
       mock.patch.object(m,"read",return_value=m.BASELINE["front"]),\
       mock.patch.object(m,"query_supported_bounds",return_value={n:{"min":0,"max":4096,"step":1} for n in m.CMDS}),\
       mock.patch.object(m,"set_supported") as setv:
   with self.assertRaisesRegex(RuntimeError,"CHANGE_READBACK_NOT_CONFIRMED"):
    m.perform(Path("/no/sensor"),"front",app(16),lambda:app(17))
   self.assertEqual(setv.call_count,1)
if __name__=="__main__":main()
