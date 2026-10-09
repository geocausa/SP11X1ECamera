#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Three guarded same-boot sessions; failures remain permanently consumed."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def replace(p,old,new):
 text=p.read_text()
 if text.count(old)!=1:raise RuntimeError("restart anchor drift:"+p.name+":"+old[:60])
 p.write_text(text.replace(old,new,1))
def apply(camss):
 for name in ["native-rear-session.h","native-rear-session-clean.inc"]:
  dest=camss/name
  assert not dest.exists()
  dest.write_bytes((HERE/name).read_bytes())
 inner=camss/"camss-vfe-e008n-rear-single-use.inc"
 replace(inner,"static atomic_t e008n_rear_consumed = ATOMIC_INIT(0);",
  '#include "native-rear-session.h"\n#include "native-rear-session-clean.inc"\nstatic struct native_rear_session_gate e008n_rear_sessions;')
 replace(inner,"\tif (atomic_cmpxchg(&e008n_rear_consumed, 0, 1))\n\t\treturn -EALREADY;",
  "\tret = native_rear_session_begin(&e008n_rear_sessions);\n\tif (ret)\n\t\treturn ret;")
 replace(inner,"\tif (!commands)\n\t\treturn -ENOMEM;",
  "\tif (!commands)\n\t\treturn native_rear_session_finish(&e008n_rear_sessions, -ENOMEM, false, 0);")
 replace(inner,"\tkfree(commands);\n\treturn 0;",
  "\tkfree(commands);\n\treturn native_rear_session_finish(&e008n_rear_sessions, 0,\n\t\tnative_rear_session_clean(result), result->transaction.owner_epoch);")
 replace(inner,"\t\t\treturn release_ret;",
  "\t\t\treturn native_rear_session_finish(&e008n_rear_sessions, release_ret, false, 0);")
 replace(inner,"\tkfree(commands);\n\treturn ret;",
  "\tkfree(commands);\n\treturn native_rear_session_finish(&e008n_rear_sessions, ret, false, 0);")
 replace(inner,"\treturn ret ? ret : -EIO;",
  "\treturn native_rear_session_finish(&e008n_rear_sessions, ret ? ret : -EIO, false, 0);")
 hook=camss/"native-rear-generation-hook.inc"
 replace(hook,"static atomic_t native_rear_generation_consumed = ATOMIC_INIT(0);",
  "static struct native_rear_session_gate native_rear_generation_sessions;")
 replace(hook," int ret;"," int ret;\n bool session_started = false;")
 replace(hook," if (atomic_cmpxchg(&native_rear_generation_consumed, 0, 1)) {\n  ret = -EALREADY;\n  goto out;\n }",
  " ret = native_rear_session_begin(&native_rear_generation_sessions);\n if (ret)\n  goto out;\n session_started = true;")
 replace(hook,"out:\n dev_info(camss->dev,",
  "out:\n if (session_started)\n  ret = native_rear_session_finish(&native_rear_generation_sessions, ret,\n   result.composed && native_rear_session_clean(&result.once),\n   result.once.transaction.owner_epoch);\n dev_info(camss->dev,\n"
  '  "NATIVE_REAR_SESSION_GATE attempted=%u completed=%u active=%u poisoned=%u owner=%llu inner_attempted=%u inner_completed=%u inner_poisoned=%u\\n",\n'
  "  native_rear_generation_sessions.attempted, native_rear_generation_sessions.completed,\n"
  "  native_rear_generation_sessions.active, native_rear_generation_sessions.poisoned,\n"
  "  (unsigned long long)native_rear_generation_sessions.last_owner,\n"
  "  e008n_rear_sessions.attempted, e008n_rear_sessions.completed, e008n_rear_sessions.poisoned);\n"
  " dev_info(camss->dev,")
 return {"maximum_same_boot_sessions":3,"serialized_outer_lock":True,
         "full_clean_stop_and_fresh_owner_required":True,"any_failure_permanently_poisoned":True,
         "outer_candidate_CONSUMED_still_single_use":True,"mandatory_Golden_return":True}
