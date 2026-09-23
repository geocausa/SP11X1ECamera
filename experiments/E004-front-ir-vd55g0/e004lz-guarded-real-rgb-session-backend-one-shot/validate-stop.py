#!/usr/bin/python3
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text())
assert (r['service_result'],r['exit_code'],r['exit_status'])==('success','exited','143')
assert r['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert r['invocation_id'] and r['invocation_id']==Path(sys.argv[2]).read_text().strip()
print(r['exit_status'])
