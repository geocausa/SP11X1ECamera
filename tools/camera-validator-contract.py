#!/usr/bin/env python3
"""Camera-free pre-arm check: shell success literal must equal validator JSON status.

Catches stale copy-forward grep guards before a new physical one-shot is armed.
This validates only a narrow contract and does NOT approve a camera test, boot,
IR activation, Golden changes, or reuse of a consumed experiment identity.
"""
from __future__ import annotations
import argparse
import ast
import pathlib
import re
import sys

OUTPUT = "PAIRED-RAW-NV12-RESULT.json"


def declared_status(validator: pathlib.Path) -> str:
    tree = ast.parse(validator.read_text(), filename=str(validator))
    funcs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "validate"]
    if len(funcs) != 1:
        raise ValueError("EXPECTED_SINGLE_VALIDATE_FUNCTION")
    statuses = set()
    for node in ast.walk(funcs[0]):
        if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            if isinstance(key, ast.Constant) and key.value == "status":
                if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                    raise ValueError("DYNAMIC_RESULT_STATUS_REQUIRES_MANUAL_REVIEW")
                statuses.add(value.value)
    if len(statuses) != 1:
        raise ValueError("AMBIGUOUS_OR_MISSING_VALIDATOR_STATUS")
    return next(iter(statuses))


def required_status(runner: pathlib.Path) -> str:
    expected = []
    for line in runner.read_text().splitlines():
        if OUTPUT not in line or not re.search(r"\bgrep\s+-Fq\s+", line):
            continue
        found = re.search(r"\bgrep\s+-Fq\s+'([^']+)'", line)
        if not found:
            raise ValueError("UNSUPPORTED_RESULT_GUARD_SYNTAX")
        expected.append(found.group(1))
    if len(expected) != 1:
        raise ValueError("MISSING_OR_DUPLICATE_PAIRED_RESULT_GUARD")
    return expected[0]


def verify(runner: pathlib.Path, validator: pathlib.Path) -> str:
    observed = declared_status(validator)
    required = required_status(runner)
    if observed != required:
        raise ValueError(f"STALE_RUNNER_RESULT_CONTRACT expected={required} emitted={observed}")
    return observed


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runner", required=True, type=pathlib.Path)
    p.add_argument("--validator", required=True, type=pathlib.Path)
    args = p.parse_args()
    try:
        accepted = verify(args.runner, args.validator)
    except (ValueError, OSError, SyntaxError) as err:
        print(f"CAMERA_VALIDATOR_CONTRACT=FAIL {err}", file=sys.stderr)
        return 1
    print(f"CAMERA_VALIDATOR_CONTRACT=PASS exact_status={accepted} camera_access=NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
