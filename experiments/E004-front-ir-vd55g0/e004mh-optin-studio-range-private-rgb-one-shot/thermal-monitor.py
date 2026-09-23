#!/usr/bin/python3
"""Read-only bounded thermal telemetry; never changes thermal or power policy."""
import json, signal, time
from pathlib import Path
stop=False
def finish(*_):
 global stop;stop=True
signal.signal(signal.SIGTERM,finish)
start=time.monotonic()
while not stop and time.monotonic()-start<500:
 values={}
 for p in Path('/sys/class/thermal').glob('thermal_zone*'):
  try:
   name=(p/'type').read_text().strip()
   if 'cpu' in name or 'camera' in name:values[name]=int((p/'temp').read_text())/1000
  except (OSError,ValueError):pass
 print(json.dumps({'elapsed_s':round(time.monotonic()-start,3),'temperature_c':values}),flush=True)
 time.sleep(2)
