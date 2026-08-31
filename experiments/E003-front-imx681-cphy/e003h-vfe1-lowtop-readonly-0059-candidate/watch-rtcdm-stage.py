#!/usr/bin/env python3
"""Persist E003h RT-CDM diagnostic stage transitions without touching MMIO."""
import argparse, os, select, time
from pathlib import Path

def read_state(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    return os.read(fd, 4096).decode('ascii', 'replace').strip()

def persist(fd, line):
    payload = f"{time.monotonic_ns()} {line}\n".encode()
    os.write(fd, payload)
    os.fdatasync(fd)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('attribute', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--ready', type=Path)
    a=ap.parse_args()
    afd=os.open(a.attribute, os.O_RDONLY | os.O_CLOEXEC)
    ofd=os.open(a.output, os.O_CREAT | os.O_TRUNC | os.O_WRONLY | os.O_CLOEXEC, 0o600)
    poll=select.poll(); poll.register(afd, select.POLLPRI | select.POLLERR)
    last=None
    state=read_state(afd); persist(ofd, state); last=state
    if a.ready:
        rfd=os.open(a.ready, os.O_CREAT | os.O_TRUNC | os.O_WRONLY | os.O_CLOEXEC, 0o600)
        os.write(rfd, b'READY\n'); os.fsync(rfd); os.close(rfd)
    try:
        while True:
            # sysfs_notify should wake POLLPRI; 1 ms timeout also catches a lost/coalesced notify.
            poll.poll(1)
            state=read_state(afd)
            if state != last:
                persist(ofd, state); last=state
    finally:
        os.close(ofd); os.close(afd)
if __name__ == '__main__': main()
