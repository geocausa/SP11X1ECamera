# SPDX-License-Identifier: GPL-2.0-only
"""Pure trace checks; no device access and no assumption about sequence origin."""
import re

def owner_groups(log):
    matches=re.findall(r"NATIVE_FRONT_OWNER_MATCH group=(\d+) sequence=(\d+)",log)
    groups={g:[int(s) for group,s in matches if int(group)==g] for g in range(5)}
    if "NATIVE_FRONT_OWNER_REJECT" in log or not groups[0]:
        raise ValueError("owner rejected or empty")
    first=groups[0][0]
    if not all(seq==groups[0] and seq==list(range(first,first+len(seq))) for seq in groups.values()):
        raise ValueError("owner groups differ or are discontinuous")
    return {"checks":len(matches),"first":first,"last":groups[0][-1],"rejections":0}

def critical_signatures(log):
    return re.findall(r"(?im)^.*(?:BUG:|Oops:|Kernel panic|Call trace:|\bIOMMU\b.*\bfault\b|\barm-smmu\b.*\bfault\b|NATIVE_FRONT_OWNER_REJECT).*$",log)
