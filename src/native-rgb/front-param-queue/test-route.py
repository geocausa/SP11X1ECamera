#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Synthetic complete data graph plus isolated control endpoint; no device access."""
import tempfile,shutil,runpy,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
def fixture():
 pads={f"msm_csiphy{i}":2 for i in [0,1,2,4]}
 pads.update({f"msm_csid{i}":5 for i in range(5)})
 edges=[]
 for phy in [0,1,2,4]:
  for csid in range(5):edges.append((f"msm_csiphy{phy}",1,f"msm_csid{csid}",0,False))
 for vfe in range(4):
  for port in range(4):
   capture=f"msm_vfe{vfe}_"+("pix" if vfe<2 and port==3 else f"rdi{port}")
   video=f"msm_vfe{vfe}_video{port}"
   pads[capture]=2;pads[video]=1
   edges.append((capture,1,video,0,True))
   for csid in range(5):edges.append((f"msm_csid{csid}",port+1,capture,0,False))
 for name,phy in [("sp11-vd55g0",0),("ov13858",1),("imx681",2)]:
  pads[name]=1;edges.append((name,0,f"msm_csiphy{phy}",0,True))
 pads["msm_vfe1_stats"]=1;edges.append(("msm_vfe1_pix",1,"msm_vfe1_stats",0,True))
 pads["msm_vfe1_params"]=1
 lines=[]
 for at,(name,count) in enumerate(pads.items()):
  related=[e for e in edges if name in [e[0],e[2]]]
  lines.append(f"- entity {at+1}: {name} ({count} {'pad' if count==1 else 'pads'}, {len(related)} links)")
  lines.append(f"    device node name /dev/video{at}")
  for pad in range(count):
   direction="SOURCE" if pad or name in ["sp11-vd55g0","ov13858","imx681","msm_vfe1_params"] else "SINK"
   lines.append(f"    pad{pad}: {direction}")
   for a,ap,b,bp,immutable in related:
    flags="ENABLED,IMMUTABLE" if immutable else ""
    if a==name and ap==pad:lines.append(f'        -> "{b}":{bp} [{flags}]')
    if b==name and bp==pad:lines.append(f'        <- "{a}":{ap} [{flags}]')
 return "\n".join(lines)+"\n"
class RouteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix="native-param-route-")
  p=Path(cls.temp.name)
  shutil.copy2(HERE/"route-contract.py",p/"route-contract.py")
  shutil.copy2(HERE.parent/"front-request-controls/route-contract.py",p/"base-route-contract.py")
  cls.classify=staticmethod(runpy.run_path(str(p/"route-contract.py"))["classify"])
  cls.graph=fixture()
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def reject(self,graph):
  with self.assertRaises(ValueError):self.classify(graph)
 def test_complete_neutral(self):self.assertEqual(self.classify(self.graph)[0],"neutral")
 def test_missing(self):self.reject(self.graph[:self.graph.index("- entity 46:")])
 def test_extra_links(self):self.reject(self.graph.replace("msm_vfe1_params (1 pad, 0 links)","msm_vfe1_params (1 pad, 1 links)"))
 def test_wrong_direction(self):self.reject(self.graph.replace("device node name /dev/video45\n    pad0: SOURCE","device node name /dev/video45\n    pad0: SINK"))
 def test_duplicate_device(self):self.reject(self.graph.replace("/dev/video45","/dev/video0"))
 def test_unexpected_entity(self):self.reject(self.graph.replace("msm_vfe1_params","unknown_params"))
 def test_duplicate_parameter(self):self.reject(self.graph+self.graph[self.graph.index("- entity 46:"):])
 def test_falsified_data_route(self):self.reject(self.graph.replace('-> "msm_csid0":0 []','-> "msm_csid0":0 [ENABLED]',1))
if __name__=="__main__":unittest.main()
