#!/usr/bin/python3
import json,os,sys
from pathlib import Path
p=Path(sys.argv[1]); r={'service_result':os.environ.get('SERVICE_RESULT'),'exit_code':os.environ.get('EXIT_CODE'),'exit_status':os.environ.get('EXIT_STATUS'),'invocation_id':os.environ.get('INVOCATION_ID'),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
with p.open('x') as f: json.dump(r,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
