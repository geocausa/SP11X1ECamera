#!/usr/bin/env python3
"""Clean-room compact AEC bank decoder and automatic priority-map evaluator.

Only derived structures are returned; no vendor payload is written.
Explicit GetData/bank override IDs are outside automatic selection.
"""
from __future__ import annotations
from dataclasses import dataclass
import struct

@dataclass(frozen=True)
class Rule:
    contexts: tuple[int, ...]
    priority: int
    data_id: int

def select(rules, active_contexts):
    """Highest signed priority wins; equal priority retains the first match.

    Windows treats mask==1 (context 0 alone) as unconditional, otherwise
    all required bits must be present. AArch64 variable shifts use low 6 bits.
    """
    active = sum(1 << c for c in set(active_contexts) if 0 <= c < 64)
    selected, priority = None, -1
    for rule in rules:
        mask = 0
        for c in rule.contexts:
            mask |= 1 << (c & 63)
        rank = rule.priority
        if (mask == 1 or mask & ~active == 0) and rank > priority:
            selected, priority = rule.data_id, rank
    if selected is None:
        raise ValueError("no automatic rule selected; runtime fallback required")
    return selected

def decode(entries, root):
    ids = {e["id"]: e for e in entries}
    def raw(ref, name):
        e = ids[ref]
        if e["name"] != name:
            raise ValueError((ref, name, e["name"]))
        b = bytes.fromhex(e["raw_hex"])
        if len(b) != e["payload_size"]:
            raise ValueError("truncated entry")
        return b
    b = bytes.fromhex(root["raw_hex"])
    if len(b) != 40:
        raise ValueError("unexpected module size")
    words = struct.unpack("<10I", b)
    nrules, rule_ref, ndata, data_ref = words[6:]
    rules_raw = raw(rule_ref, "priorityMap")
    if len(rules_raw) != nrules * 16:
        raise ValueError("bad priority count")
    rules = []
    for off in range(0, len(rules_raw), 16):
        nctx, ctx_ref, rank, data_id = struct.unpack_from("<IIiI", rules_raw, off)
        ctx = raw(ctx_ref, "context")
        if len(ctx) != nctx * 4:
            raise ValueError("bad context count")
        rules.append(Rule(struct.unpack("<"+"I"*nctx, ctx), rank, data_id))
    kind = root["name"]
    stride = {"aecxdbconvbase": 56, "aecxdbconvstretch": 28}[kind]
    rows = raw(data_ref, "data")
    if len(rows) != ndata * stride:
        raise ValueError("bad data count")
    data = {}
    for off in range(0, len(rows), stride):
        w = struct.unpack_from("<"+"I"*(stride//4), rows, off)
        data_id, text_len, text_ref = w[:3]
        desc = raw(text_ref, "description")
        if len(desc) != text_len or not desc.endswith(b"\0") or data_id in data:
            raise ValueError("bad description or duplicate ID")
        data[data_id] = {"description": desc[:-1].decode("ascii"), "words": w}
    if any(r.data_id not in data for r in rules):
        raise ValueError("priority map references absent data")
    return {"root_id": root["id"], "mode_symbol": root["c"],
            "bank_type": words[5], "rules": rules, "data": data}

def leaves(entries, first_ref, first_count, core_words):
    """Walk each counted trigger node; stop at the exact leaf boundary."""
    ids = {e["id"]: e for e in entries}
    out = []
    def walk(ref, count, level):
        e = ids[ref]
        name = "trigger%dData" % level
        if e["name"] != name:
            raise ValueError((ref, name, e["name"]))
        b = bytes.fromhex(e["raw_hex"])
        stride = 16 if level < 3 else 8 + 4*core_words
        if len(b) != count * stride:
            raise ValueError((ref, "bad trigger count"))
        for off in range(0, len(b), stride):
            lo, hi = struct.unpack_from("<2f", b, off)
            if not lo <= hi:
                raise ValueError("bad trigger interval")
            if level < 3:
                n, child = struct.unpack_from("<2I", b, off+8)
                walk(child, n, level+1)
            else:
                out.append({"entry": ref, "interval": [lo, hi],
                            "core_bits": struct.unpack_from("<"+"I"*core_words, b, off+8)})
    walk(first_ref, first_count, 1)
    return out
