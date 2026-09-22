#!/usr/bin/env python3
"""Static graph-order replay, not a live libcamera route observation."""
from collections import defaultdict, deque
from pathlib import Path
import hashlib
import importlib.util
import json
import re

root = Path(__file__).resolve().parents[3]
proof = root / "experiments/E004-front-ir-vd55g0/e004le-timing-clock-session-one-shot"
fixture = proof / "evidence/FINAL-NEUTRAL-MEDIA.txt"
text = fixture.read_text()
spec = importlib.util.spec_from_file_location("contract", proof / "camera-session-contract.py")
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
assert contract.classify(text)[0] == "neutral"

def canonical(name):
    return re.sub(r"^(imx681|ov13858|sp11-vd55g0) \d+-[0-9a-f]{4}$", r"\1", name)

edges = []
source = None
pad = None
for line in text.splitlines():
    match = re.match(r"- entity \d+: (.*?) \(", line)
    if match:
        source = canonical(match[1])
    match = re.match(r"\s*pad(\d+):", line)
    if match:
        pad = int(match[1])
    match = re.fullmatch(r'\s*-> "([^"]+)":(\d+) \[([^\]]*)\]', line)
    if match:
        edges.append((source, pad, canonical(match[1]), int(match[2]), match[3]))
assert len(edges) == 119
adj = defaultdict(list)
for edge in edges:
    adj[edge[0]].append(edge)

def replay(sensor):
    # Matches pinned SimpleCameraData BFS visitation/first-parent semantics.
    queue = deque([sensor])
    visited = set()
    parents = {}
    while queue:
        entity = queue.popleft()
        if re.fullmatch(r"msm_vfe\d+_video\d+", entity):
            path = []
            while entity in parents:
                edge = parents[entity]
                path.append(edge)
                entity = edge[0]
            return path[::-1]
        visited.add(entity)
        for edge in adj[entity]:
            target = edge[2]
            if target not in visited:
                queue.append(target)
                parents.setdefault(target, edge)
    raise AssertionError("No route")

def shortest_paths(sensor):
    queue = deque([(sensor, [])])
    answer = []
    length = None
    while queue:
        node, path = queue.popleft()
        if length is not None and len(path) > length:
            break
        if re.fullmatch(r"msm_vfe\d+_video\d+", node):
            answer.append(path)
            length = len(path)
            continue
        for edge in adj[node]:
            queue.append((edge[2], path + [edge]))
    return answer

def activate_text(path):
    enable = {edge[:4] for edge in path if "IMMUTABLE" not in edge[4]}
    output = []
    source = None
    pad = None
    for line in text.splitlines():
        match = re.match(r"- entity \d+: (.*?) \(", line)
        if match:
            source = canonical(match[1])
        match = re.match(r"\s*pad(\d+):", line)
        if match:
            pad = int(match[1])
        match = re.fullmatch(r'(\s*)(->|<-) "([^"]+)":(\d+) \[([^\]]*)\]', line)
        if match:
            _, direction, target, tp, flags = match.groups()
            key = (source, pad, canonical(target), int(tp)) if direction == "->" else (canonical(target), int(tp), source, pad)
            if key in enable:
                assert not flags
                line = line[:-2] + "[ENABLED]"
        output.append(line)
    return "\n".join(output) + "\n"

out = {}
for sensor in ("imx681", "ov13858", "sp11-vd55g0"):
    path = replay(sensor)
    alternatives = shortest_paths(sensor)
    accepted = []
    for candidate in alternatives:
        try:
            phase = contract.classify(activate_text(candidate))[0]
            accepted.append(phase)
        except ValueError:
            pass
    try:
        replay_admission = contract.classify(activate_text(path))[0]
    except ValueError as error:
        replay_admission = str(error)
    out[sensor] = {
        "shortest_path_count": len(alternatives),
        "accepted_shortest_paths": len(accepted),
        "accepted_phases": accepted,
        "fixture_order_replay": [path[0][0]] + [edge[2] for edge in path],
        "fixture_order_admission": replay_admission,
    }
assert out["imx681"]["shortest_path_count"] == 80
assert out["imx681"]["accepted_shortest_paths"] == 1
assert out["ov13858"]["accepted_shortest_paths"] == 1
assert out["sp11-vd55g0"]["accepted_shortest_paths"] == 0
assert out["imx681"]["fixture_order_admission"] == "UNAUTHORIZED_ENABLED_ROUTE_IN_COMPLETE_GRAPH"
assert out["ov13858"]["fixture_order_admission"] == "rear-only"
print(json.dumps({
    "status": "PASS_STATIC_ROUTE_ADMISSION_BLOCKER",
    "fixture_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
    "actual_live_libcamera_order_or_route_proven": False,
    "physical_test": False,
    "sensors": out,
}, indent=2))
