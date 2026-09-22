# SPDX-License-Identifier: MIT
"""Compile the actual C++ helper and compare all shortest routes with Python policy."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
test = root / "routing/tests/test_route_policy.py"
spec = importlib.util.spec_from_file_location("fixture", test)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
policy = fixture.policy
runner = r"""
#include "sp11-rgb-paths.h"
#include <iomanip>
#include <iostream>
int main()
{
    std::string sensor, a, b;
    unsigned int ap, bp;
    while (std::cin >> std::quoted(sensor) >> std::quoted(a) >> ap
                    >> std::quoted(b) >> bp)
        std::cout << sp11::edgeAllowed(sensor, a, ap, b, bp) << '\n';
    return std::cin.eof() ? 0 : 2;
}
"""
paths = []
expected = []
for sensor in ("imx681", "ov13858", "sp11-vd55g0"):
    candidates = [[edge] for edge in fixture.EDGES if edge[0] == sensor]
    for _ in range(3):
        candidates = [path + [edge] for path in candidates for edge in fixture.EDGES
                      if edge[0] == path[-1][2]]
    for path in candidates:
        paths.append((sensor, path))
        try:
            policy.admit_path(sensor, tuple(path))
            expected.append(True)
        except policy.Rejected:
            expected.append(False)
queries = []
for sensor, path in paths:
    for a, ap, b, bp in path:
        queries.append((sensor, a, ap, b, bp))
extra = [
    ("imx681 99-0010", "imx681 99-0010", 0, "msm_csiphy2", 0, True),
    ("imx681 99-0011", "imx681 99-0011", 0, "msm_csiphy2", 0, False),
    ("imx681 x-0010", "imx681 x-0010", 0, "msm_csiphy2", 0, False),
    ("imx681", "msm_csiphy2", 0, "msm_csid1", 0, False),
    ("imx681", "msm_csiphy2", 1, "msm_csid1", 1, False),
    ("imx681", "msm_csid1", 4, "msm_vfe1_pix", 0, False),
    ("imx681", "msm_csiphy2", 4294967295, "msm_csid1", 0, False),
    ("sp11-vd55g0 2-0060", "sp11-vd55g0 2-0060", 0, "msm_csiphy0", 0, False),
]
queries.extend(x[:5] for x in extra)
payload = "\n".join(f"{json.dumps(sensor)} {json.dumps(a)} {ap} {json.dumps(b)} {bp}"
                    for sensor, a, ap, b, bp in queries) + "\n"
with tempfile.TemporaryDirectory(prefix="sp11-path-filter-") as directory:
    c = Path(directory) / "runner.cpp"
    exe = Path(directory) / "runner"
    c.write_text(runner)
    subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                    "-fsanitize=undefined", "-fno-sanitize-recover=all",
                    "-I", str(root / "libcamera"), str(c), "-o", str(exe)], check=True)
    result = subprocess.run([str(exe)], input=payload, text=True,
                            capture_output=True, check=True)
answers = [line == "1" for line in result.stdout.splitlines()]
assert len(answers) == len(queries)
for index, want in enumerate(expected):
    assert all(answers[index * 4:index * 4 + 4]) == want, paths[index]
assert answers[960:] == [x[-1] for x in extra]
assert sum(expected) == 2
print("PASS: 240 complete paths, 960 edge decisions, 8 adversarial/name/pad cases; UBSan clean")
