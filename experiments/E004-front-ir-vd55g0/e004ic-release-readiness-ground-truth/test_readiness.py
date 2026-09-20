#!/usr/bin/env python3
"""E004ic fail-closed in-memory contradictory historical/readiness states."""
from pathlib import Path
import copy
import importlib.util
import json

HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location("e004ic_verifier",HERE/"verify_readiness.py")
assert S and S.loader
v=importlib.util.module_from_spec(S)
S.loader.exec_module(v)

def run():
    paths=(v.STRUCT,v.DOC,v.EN,v.EO,v.FU,v.GE,v.IA)
    original=[json.loads(p.read_text()) if p.suffix==".json"
              else p.read_text() for p in paths]
    assert v.assess(*original)
    neg=0
    alterations=[
      lambda a:a[0]["nonprotected_product"].__setitem__("status","READY_DEFAULT"),
      lambda a:a[0]["remaining_proofs"].__setitem__(
          "front_post_g3_changed_native_feedback","IMPLEMENTED_BUT_LIVE_PROOF_SCENE_GATED"),
      lambda a:a[0]["protected_path"].__setitem__("worker_production_admitted",True),
      lambda a:a[0]["safety_gates"].__setitem__(
          "native_linux_ir_emitter_activated_or_authorized",True),
      lambda a:a[0]["safety_gates"].__setitem__(
          "independent_current_irradiance_pulse_strobe_host_failure_emitter_cutoff_proven",True),
      lambda a:a[2].__setitem__("second_later_writes",1),
      lambda a:a[4].__setitem__("optical_signal_sufficient_for_face_auth",True),
      lambda a:a[5]["physical_evidence"].__setitem__("autonomous_host_and_strobe_fault_off",True),
      lambda a:a[6].__setitem__("real_user_enrolled_or_face_authenticated",True),
      lambda a:a.__setitem__(1,a[1]+"\nWait for a naturally changed/brighter scene"),
      lambda a:a.__setitem__(1,a[1].replace(
           "### Front post-G3 changed native feedback — CLOSED by E004en",
           "### Front post-G3 changed native feedback — UNVERIFIED")),
    ]
    for k,change in enumerate(alterations):
        mutant=copy.deepcopy(original)
        change(mutant)
        try:v.assess(*mutant)
        except AssertionError as err:
            assert str(err).startswith("E004IC_FAIL_CLOSED"),(k,str(err))
        else:raise AssertionError("E004IC_FALSE_READINESS_ACCEPTED "+str(k))
        neg+=1
    assert neg==11
    print("E004IC_CONTRADICTORY_IN_MEMORY_READINESS_NEGATIVES_PASS",neg)
    print("E004IC_NO_DEVICE_BOOT_OR_LOGIN_OPERATION")
    return neg

if __name__=="__main__":run()
