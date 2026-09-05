#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED_SHA256 = "00e1ed5aa588f9fc1d3723ada477ccdda92c8558419a8ef2637ceffc0573a789"
PARSER_RE = re.compile(
    r"^E003IP2 PARSER n=(\d+) proc=([0-9a-f]+) thread=([0-9a-f]+) .*"
    r"x1raw=([0-9a-f]+).*x3parsed=([0-9a-f]+)"
)
TINTLESS_RE = re.compile(
    r"^E003IP2 TINTLESS n=(\d+) parser_count=(\d+) proc=([0-9a-f]+) "
    r"thread=([0-9a-f]+) .*x2stats=([0-9a-f]+)"
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fail-closed E003i-P live TL_BG/Tintless correlation extractor")
    ap.add_argument("log", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    raw = args.log.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"raw log SHA mismatch: {digest} != {EXPECTED_SHA256}")

    events = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        m = PARSER_RE.match(line)
        if m:
            events.append({
                "kind": "parser", "n": int(m.group(1)), "proc": m.group(2),
                "thread": m.group(3), "raw": m.group(4), "parsed": m.group(5),
            })
            continue
        m = TINTLESS_RE.match(line)
        if m:
            events.append({
                "kind": "tintless", "n": int(m.group(1)), "parser_count": int(m.group(2)),
                "proc": m.group(3), "thread": m.group(4), "stats": m.group(5),
            })

    parsers = [e for e in events if e["kind"] == "parser"]
    tintless = [e for e in events if e["kind"] == "tintless"]
    if len(parsers) != 153 or len(tintless) != 150:
        raise SystemExit(f"unexpected trace counts: parser={len(parsers)} tintless={len(tintless)}")

    consumed = set()
    pairs = []
    previous = None
    for event in events:
        if event["kind"] == "parser":
            previous = event
            continue
        if previous is None:
            raise SystemExit("Tintless event without preceding parser")
        if event["parser_count"] != previous["n"]:
            raise SystemExit(
                f"Tintless {event['n']} parser_count={event['parser_count']} "
                f"does not name immediate parser {previous['n']}"
            )
        pair = {
            "tintless": event["n"], "parser": previous["n"],
            "pointer_equal": event["stats"] == previous["parsed"],
            "same_process": event["proc"] == previous["proc"],
            "same_thread": event["thread"] == previous["thread"],
        }
        if not all((pair["pointer_equal"], pair["same_process"], pair["same_thread"])):
            raise SystemExit(f"producer/consumer mismatch at Tintless {event['n']}: {pair}")
        consumed.add(previous["n"])
        pairs.append(pair)

    superseded = [e["n"] for e in parsers if e["n"] not in consumed]
    if superseded != [82, 84, 104]:
        raise SystemExit(f"unexpected superseded parser generations: {superseded}")

    result = {
        "schema": 1,
        "raw_sha256": digest,
        "raw_bytes": len(raw),
        "parser_hits": len(parsers),
        "tintless_hits": len(tintless),
        "immediate_pointer_matches": sum(p["pointer_equal"] for p in pairs),
        "same_process_pairs": sum(p["same_process"] for p in pairs),
        "same_thread_pairs": sum(p["same_thread"] for p in pairs),
        "first_tintless_parser_count": tintless[0]["parser_count"],
        "last_tintless_parser_count": tintless[-1]["parser_count"],
        "superseded_parser_generations": superseded,
        "request_delay_authority": False,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
