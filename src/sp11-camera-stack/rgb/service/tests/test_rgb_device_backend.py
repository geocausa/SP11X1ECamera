# SPDX-License-Identifier: MIT
"""Offline source-format, real-route adapter and service ownership injection tests."""
import re
import sys
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import media_backend
import rgb_device_backend
from session import RGBSession, SessionRejected

policy=media_backend.route_policy
TEXT=(HERE.parents[1]/"routing/tests/neutral-media.txt").read_text()
DISCOVERY={
    "media":"/dev/media0",
    "front_sensor_entity":"imx681 7-0010",
    "front_rdi_video_device":"/dev/video12",
    "rear_sensor_entity":"ov13858 8-0010",
    "rear_video_device":"/dev/video14",
}


def render(state):
    entity=None;pad=None;lines=[]
    for line in TEXT.splitlines():
        match=re.match(r"- entity \d+: (.*?) \(",line)
        if match: entity=policy.canonical(match[1])
        match=re.match(r"\s*pad(\d+):",line)
        if match:pad=int(match[1])
        match=re.fullmatch(r'\s*(->|<-) "([^"]+)":(\d+) \[\]',line)
        if match:
            direction,other,pad_other=match.groups()
            edge=((entity,pad,policy.canonical(other),int(pad_other))
                  if direction=="->" else
                  (policy.canonical(other),int(pad_other),entity,pad))
            if edge in state:line=line[:-2]+"[ENABLED]"
        lines.append(line)
    return "\n".join(lines)+"\n"


class OwnerFake:
    def __init__(self):
        self.phase=set()
        self.commands=[]
        self.authority=True
        self.lock=True
        self.ir=True
        self.reader_open=False
        self.active=None
        self.invocations={"front":0,"rear":0}
        self.stops_ok=True
        self.fail_link=False
        self.fail_format=False

    def authorized(self):return self.authority
    def lease_held(self):return self.lock
    def ir_off(self):return self.ir
    def no_camera_users(self):return not self.active and not self.reader_open
    def unit(self,camera):
        assert camera in ("front","rear")
        return f"sp11-camera-e004lz-session@{camera}.service"
    def service_state(self,camera):
        live=self.active==camera
        return {"active":live,"pid":1234 if live else 0,
                "invocation_id":f"{self.invocations[camera]:032x}"}
    def stop_proof(self,camera,invocation_id):
        return self.stops_ok and invocation_id==f"{self.invocations[camera]:032x}"
    def run(self,argv,*,timeout):
        self.commands.append((argv,timeout))
        if argv[:3]==("media-ctl","-d","/dev/media0"):
            if argv[3]=="-p":
                return render(self.phase)
            if argv[3]=="-V":
                assert len(argv)==5 and "fmt:" in argv[4]
                return ""
            if argv[3]=="-l":
                match=re.fullmatch(r'"([^"]+)":(\d+) -> "([^"]+)":(\d+) \[([01])\]',argv[4])
                assert match
                edge=(match[1],int(match[2]),match[3],int(match[4]))
                assert edge in (*policy.FRONT,*policy.REAR)
                if match[5]=="1":self.phase.add(edge)
                else:self.phase.remove(edge)
                if self.fail_link:raise OSError("INJECT_UNCERTAIN_GRAPH_WRITE")
                return ""
        if argv[0]=="v4l2-ctl":
            assert argv[1]=="-d" and argv[2] in ("/dev/video12","/dev/video14")
            camera="front" if argv[2]=="/dev/video12" else "rear"
            spec=rgb_device_backend.SPECS[camera]
            if argv[3].startswith("--set-fmt-video="):
                assert argv[3].endswith(spec["fmt"])
                return ""
            if argv[3]=="--get-fmt-video":
                return (f"Width/Height      : {spec['width_height']}\n"
                        f"Pixel Format      : '{'BAD!' if self.fail_format else spec['fourcc']}'\n"
                        f"Bytes per Line    : {spec['bytesperline']}\n"
                        f"Size Image        : {spec['sizeimage']}\n")
        if argv[:2]==("systemctl","start"):
            assert self.active is None
            camera=argv[2].split("@")[1].split(".")[0]
            self.invocations[camera]+=1;self.active=camera
            return ""
        if argv[:2]==("systemctl","stop"):
            camera=argv[2].split("@")[1].split(".")[0]
            assert self.active==camera
            self.active=None
            return ""
        raise AssertionError(f"Unexpected command {argv!r}")


class NativeDeviceTests(unittest.TestCase):
    def setUp(self):
        self.owner=OwnerFake()
        self.backend=rgb_device_backend.RGBDeviceBackend(DISCOVERY,self.owner)
        self.session=RGBSession(self.backend)

    def test_front_rear_reopen_complete_graph_and_service(self):
        for camera in ("front","rear","front","rear"):
            self.session.open(camera)
            self.assertEqual(self.session.active,camera)
            self.assertTrue(self.backend.publisher_running(camera))
            self.assertEqual(self.owner.active,camera)
            self.session.stop()
            self.assertIsNone(self.owner.active)
            self.assertEqual(self.owner.phase,set())
        self.assertEqual(self.session.completed_stops,4)
        self.assertEqual(self.owner.invocations,{"front":2,"rear":2})
        source_config=[a[0] for a in self.owner.commands if a[0][0]=="v4l2-ctl"]
        self.assertEqual(len(source_config),8)

    def test_switch_enforces_full_stop_and_neutral(self):
        self.session.open("front")
        self.session.switch("rear")
        self.assertEqual(self.session.completed_stops,1)
        self.assertEqual(self.owner.phase,set(policy.REAR))
        self.session.close()
        self.assertEqual(self.owner.phase,set())

    def test_invalid_discovery_denied_without_device_access(self):
        for field,value in (("media","/dev/media0; reboot"),
                            ("front_sensor_entity","imx681 7-0011"),
                            ("rear_video_device","/dev/video90"),
                            ("front_rdi_video_device","/dev/video14"),
                            ("rear_sensor_entity","vd55g0 7-0060")):
            with self.subTest(field=field):
                bad=dict(DISCOVERY);bad[field]=value
                with self.assertRaises(SessionRejected):
                    rgb_device_backend.RGBDeviceBackend(bad,self.owner)
                self.assertEqual(self.owner.commands,[])

    def test_wrong_exact_output_format_poison(self):
        self.owner.fail_format=True
        with self.assertRaisesRegex(SessionRejected,"SOURCE_FORMAT"):
            self.session.open("front")
        self.assertTrue(self.session.poisoned)
        self.assertIsNone(self.owner.active)
        self.assertEqual(self.owner.phase,set(policy.FRONT))

    def test_unverified_streamoff_no_route_write(self):
        self.session.open("rear")
        self.owner.stops_ok=False
        before=len([1 for a,_ in self.owner.commands if a[3:4]==("-l",)])
        with self.assertRaisesRegex(SessionRejected,"STREAMOFF"):
            self.session.stop()
        after=len([1 for a,_ in self.owner.commands if a[3:4]==("-l",)])
        self.assertEqual(before,after)
        self.assertEqual(self.owner.phase,set(policy.REAR))
        self.assertTrue(self.session.poisoned)

    def test_reader_left_open_no_route_write_after_stop(self):
        self.session.open("front")
        self.owner.reader_open=True
        with self.assertRaisesRegex(SessionRejected,"CAMERA_FDS"):
            self.session.stop()
        self.assertEqual(self.owner.phase,set(policy.FRONT))
        self.assertTrue(self.session.poisoned)

    def test_root_identity_or_lease_lost_mid_open(self):
        for attr in ("authority","lock","ir"):
            with self.subTest(attr=attr):
                owner=OwnerFake();owner.__dict__[attr]=False
                session=RGBSession(rgb_device_backend.RGBDeviceBackend(DISCOVERY,owner))
                with self.assertRaises(SessionRejected):
                    session.open("front")
                self.assertTrue(session.poisoned)
                self.assertEqual(owner.commands,[])

    def test_uncertain_link_fails_closed(self):
        self.owner.fail_link=True
        with self.assertRaises(OSError):
            self.session.open("front")
        self.assertTrue(self.session.poisoned)
        self.assertEqual(self.owner.phase,{policy.FRONT[0]})
        with self.assertRaisesRegex(SessionRejected,"POISONED"):
            self.session.switch("rear")


if __name__=="__main__":
    unittest.main()
