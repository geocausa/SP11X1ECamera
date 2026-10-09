#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile exact staged C log formats and feed their real stdout into the runtime parser."""
import argparse,json,re,runpy,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
CONTROL=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/native-rgb-rear-generation-20261007-48/camss/native-rear-queue.inc")
def fmt(source,tag):
 matches=re.findall(r'"'+re.escape(tag)+r' [^"\n]*"',source)
 assert len(matches)==1
 return matches[0]
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 assert not a.report.exists()
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v12.py"))
 qfmt=fmt((a.staged/"native-rear-queue.inc").read_text(),"NATIVE_REAR_QUEUE_SNAPSHOT")
 gfmt=fmt((a.staged/"native-rear-generation-hook.inc").read_text(),"NATIVE_REAR_SESSION_GATE")
 cfmt=fmt((a.staged/"native-rear-command-retire.inc").read_text(),"NATIVE_REAR_COMMAND_RETIRE")
 markerfmt=fmt((a.staged/"native-rear-generation-hook.inc").read_text(),"NATIVE_REAR_GENERATION_ATTEMPT")
 oldfmt=fmt(CONTROL.read_text(),"NATIVE_REAR_QUEUE_SNAPSHOT")
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-compiled-records-") as temp:
  temp=Path(temp)
  for cc in ["gcc","clang"]:
   c=temp/(cc+".c");exe=temp/cc
   c.write_text('#include <stdio.h>\nint main(void){\nprintf('+qfmt+',3U);\nfor(unsigned s=1;s<=3;s++)printf('+gfmt+',s,s,0U,0U,(unsigned long long)s,s,s,0U);\nreturn 0;}\n')
   subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",str(c),"-o",str(exe)],check=True,capture_output=True,text=True)
   out=subprocess.check_output([str(exe)],text=True)
   assert out.endswith("\n") and "\\n" not in out
   lines=out.splitlines();assert len(lines)==4
   snap=runtime["queue_snapshot"](lines[0])
   assert snap["retries"]==3
   for s in range(1,4):assert runtime["session_gate"](lines[s],s)["completed"]==s
   c.write_text('#include <stdio.h>\nint main(void){for(unsigned s=1;s<=3;s++){printf('+markerfmt+',s);printf('+gfmt+',s,s,0U,0U,(unsigned long long)s,s,s,0U);}return 0;}\n')
   subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",str(c),"-o",str(exe)],check=True,capture_output=True,text=True)
   marked=subprocess.check_output([str(exe)],text=True)
   for s in range(1,4):
    pairs=marked.splitlines()
    own="\n".join(pairs[2*(s-1):2*s])+"\n"
    scope=runtime["session_log"](own,s)
    assert runtime["session_gate"](scope,s)["completed"]==s
   c.write_text('#include <stdio.h>\nint main(void){for(unsigned s=1;s<=3;s++)printf('+cfmt+',0,4U,1U,0U,(unsigned long long)s,22U,0U);return 0;}\n')
   subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",str(c),"-o",str(exe)],check=True,capture_output=True,text=True)
   command_lines=subprocess.check_output([str(exe)],text=True).splitlines()
   assert len(command_lines)==3
   for s,line in enumerate(command_lines,1):
    facts,retired=runtime["command_retirement"](line,s)
    assert retired and facts["owner"]==s
   c.write_text('#include <stdio.h>\nint main(void){printf('+oldfmt+',0U);return 0;}\n')
   subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",str(c),"-o",str(exe)],check=True,capture_output=True,text=True)
   bad=subprocess.check_output([str(exe)],text=True)
   assert "\\n" in bad
   try:runtime["queue_snapshot"](bad)
   except RuntimeError:pass
   else:raise AssertionError("actual malformed rear37 formatter admitted")
   results.append(dict(compiler=cc,Werror=True,actual_staged_C_formatter_outputs_parsed=13,actual_retired37_literal_newline_control_rejected=True))
 report=dict(status="PASS_ACTUAL_COMPILED_KERNEL_SCALAR_LOG_TO_RUNTIME_PARSER",actual_staged_format_literals_compiled=True,synthetic_scalar_arguments=True,pixel_access=False,hardware_access=False,results=results)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
