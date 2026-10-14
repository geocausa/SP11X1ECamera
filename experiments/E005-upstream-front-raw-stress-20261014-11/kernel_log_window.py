#!/usr/bin/env python3
"""Select a same-boot kernel-log window without relying on ring-buffer length."""
import re

STAMP = re.compile(r"^\[\s*(\d+)\.(\d{1,9})\]")


def entries(log):
    """Keep untimestamped continuation lines with their preceding record."""
    timestamp = None
    lines = []
    for line in log.splitlines():
        match = STAMP.match(line)
        if match:
            if timestamp is not None:
                yield timestamp, "\n".join(lines)
            timestamp = int(match[1]) * 1_000_000_000 + int(match[2].ljust(9, "0"))
            lines = [line]
        elif timestamp is not None:
            lines.append(line)
        elif line.strip():
            raise ValueError("kernel log does not begin with a raw timestamp")
    if timestamp is not None:
        yield timestamp, "\n".join(lines)


def make_boundary(log, boot_id):
    stamps = [stamp for stamp, _ in entries(log)]
    if not stamps or not boot_id:
        raise ValueError("kernel log boundary is unavailable")
    return {"boot_id": boot_id, "last_timestamp_ns": max(stamps)}


def window(log, boundary, boot_id):
    if boundary["boot_id"] != boot_id:
        raise ValueError("boot changed during evidence collection")
    records = [record for stamp, record in entries(log)
               if stamp > boundary["last_timestamp_ns"]]
    return "\n".join(records) + ("\n" if records else "")


def self_test():
    # A full old ring can contain more lines than the new ring after rollover.
    before = "".join(f"[ {i}.000000] old\n" for i in range(1, 101))
    after = "[ 99.000000] old\n[100.000000] old\n[101.000000] started\n"
    after += "[102.000000] WARNING: test\n continuation\n[103.000000] stopped\n"
    boundary = make_boundary(before, "boot-a")
    result = window(after, boundary, "boot-a")
    assert result == ("[101.000000] started\n[102.000000] WARNING: test\n"
                      " continuation\n[103.000000] stopped\n")
    assert window(before, boundary, "boot-a") == ""
    assert window("[100.000001] new\n", boundary, "boot-a").endswith("new\n")
    for action in (lambda: window(after, boundary, "boot-b"),
                   lambda: make_boundary("", "boot-a"),
                   lambda: make_boundary("unexpected log format\n", "boot-a")):
        try:
            action()
        except ValueError:
            continue
        raise AssertionError("invalid evidence boundary accepted")
    print("kernel-log rollover, continuation, precision and boot-identity checks: PASS")


if __name__ == "__main__":
    self_test()
