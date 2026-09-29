#!/usr/bin/env python3
"""Check evaluation JSONL structure; this does not judge agent behavior."""

import argparse
import json
from pathlib import Path


DEFAULT_PATH = Path(__file__).resolve().parents[1] / "evals/cases.jsonl"
REQUIRED_FIELDS = {
    "id", "post", "comments", "context", "expected_action",
    "acceptable_intent", "forbidden_patterns",
}
TEXT_FIELDS = ("id", "post", "context", "acceptable_intent")
MIN_CASES = 30


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-standard JSON constant: {value}")


def validate(path):
    """Return all discovered schema errors without contacting any service."""
    path = Path(path)
    errors = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [f"Cannot read evaluation file: {exc}"]
    ids = set()
    count = 0
    for number, line in enumerate(lines, 1):
        prefix = f"line {number}"
        if not line.strip():
            errors.append(f"{prefix}: blank lines are not JSONL records")
            continue
        try:
            case = json.loads(line, object_pairs_hook=unique_object, parse_constant=reject_constant)
        except (ValueError, RecursionError) as exc:
            errors.append(f"{prefix}: invalid JSON: {exc}")
            continue
        if not isinstance(case, dict):
            errors.append(f"{prefix}: record must be an object")
            continue
        count += 1
        missing = REQUIRED_FIELDS - case.keys()
        if missing:
            errors.append(f"{prefix}: missing required fields: {', '.join(sorted(missing))}")
        for field in TEXT_FIELDS:
            if field in case and (not isinstance(case[field], str) or not case[field].strip()):
                errors.append(f"{prefix}: {field} must be a nonempty string")
        ident = case.get("id")
        if isinstance(ident, str) and ident.strip():
            if ident != ident.strip():
                errors.append(f"{prefix}: id must not have surrounding whitespace")
            if ident.strip() in ids:
                errors.append(f"{prefix}: duplicate case ID: {ident.strip()}")
            ids.add(ident.strip())
        if "expected_action" in case and case["expected_action"] not in ("reply", "skip"):
            errors.append(f"{prefix}: expected_action must be reply or skip")
        for field in ("comments", "forbidden_patterns"):
            if field not in case:
                continue
            value = case[field]
            if not isinstance(value, list) or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                errors.append(f"{prefix}: {field} must be an array of nonempty strings")
    if count < MIN_CASES:
        errors.append(f"Expected at least {MIN_CASES} evaluation cases; found {count}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args(argv)
    errors = validate(args.path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: evaluation JSONL, unique IDs, schema, actions, and minimum case count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
