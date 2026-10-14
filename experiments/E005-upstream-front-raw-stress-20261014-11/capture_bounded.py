#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Bound and reap one standard capture process; only scalar stdout is retained."""
from pathlib import Path
import os,re,signal,subprocess,time
FRAME_RE = re.compile(r'cap dqbuf:\s*\d+ seq:\s*(\d+) bytesused:\s*(\d+)')
def proc_stopped(pid):
    state = Path(f'/proc/{pid}/status').read_text()
    return re.search(r'^State:\s+[Tt]\b', state, re.M) is not None
def capture_bounded(command, logfile, *, frames, hold_ms=0, trigger=60,
                    observe=None, timeout=50):
    logfile = Path(logfile)
    with logfile.open('x') as out:
        p = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT,
                             start_new_session=True)
        record = dict(pid=p.pid, process_group=p.pid, requested_frames=frames,
                      hold_ms=hold_ms, payload_discarded_by_caller=True)
        try:
            if hold_ms:
                deadline = time.monotonic() + min(timeout, 12)
                while time.monotonic() < deadline:
                    seen = FRAME_RE.findall(logfile.read_text())
                    if len(seen) >= trigger:
                        break
                    if p.poll() is not None:
                        raise RuntimeError('capture ended before planned freeze')
                    time.sleep(0.02)
                else:
                    raise TimeoutError('capture did not reach freeze admission')
                if len(seen) > frames - 12:
                    raise RuntimeError('insufficient capture remains for recovery')
                os.killpg(p.pid, signal.SIGSTOP)
                deadline = time.monotonic() + 1
                while time.monotonic() < deadline and not proc_stopped(p.pid):
                    time.sleep(0.01)
                if not proc_stopped(p.pid):
                    raise RuntimeError('capture process was not stopped')
                start = time.monotonic()
                record['last_logged_sequence_before_freeze'] = int(seen[-1][0])
                record['process_stopped_observed'] = True
                time.sleep(0.2)  # Permit the three queued buffers to drain.
                if not proc_stopped(p.pid):
                    raise RuntimeError('consumer resumed before the observer')
                if observe is None:
                    raise RuntimeError('starvation observer required')
                record['starvation_observation'] = observe(p.pid)
                remaining = hold_ms / 1000 - (time.monotonic() - start)
                if remaining > 0:
                    time.sleep(remaining)
                if not proc_stopped(p.pid):
                    raise RuntimeError('consumer resumed before planned release')
                record['actual_stopped_seconds'] = time.monotonic() - start
                os.killpg(p.pid, signal.SIGCONT)
                record['continue_requested'] = True
            record['returncode'] = p.wait(timeout=timeout)
            if record['returncode']:
                raise RuntimeError('capture process exit: ' + str(record['returncode']))
            return record
        finally:
            if p.poll() is None:
                # A stopped child must be woken before TERM can be delivered.
                for sig in [signal.SIGCONT, signal.SIGTERM]:
                    try: os.killpg(p.pid, sig)
                    except ProcessLookupError: pass
                try: p.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    try: os.killpg(p.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    p.wait(timeout=2)
            # Refuse surviving descendants of this dedicated process group.
            try: os.killpg(p.pid, 0)
            except ProcessLookupError: pass
            else:
                os.killpg(p.pid, signal.SIGKILL)
                raise RuntimeError('capture process group had surviving descendants')
