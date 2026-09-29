#!/usr/bin/env python3
"""Validate this repository's simple Agent Skill package using only stdlib.

Frontmatter is deliberately limited to unquoted, single-line name and
description strings. This is a repository validator, not a general YAML parser.
"""

import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_REFERENCES = (
    "references/interaction-principles.md",
    "references/decision-framework.md",
    "references/scoring-rubric.md",
    "references/failure-modes.md",
    "references/examples.md",
    "references/safety.md",
    "references/platforms/moltbook.md",
)
PLACEHOLDER = re.compile(
    r"\b(?:TODO|TBD|FIXME)\b|\blorem ipsum\b|"
    r"\bYOUR_[A-Z_]+\b|\[INSERT[^\]\n]*HERE\]",
    re.IGNORECASE,
)
LINK = re.compile(r"\[[^\]\n]*\]\(([^\s)]+)\)")
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def read_text(path, errors):
    """Return UTF-8 text, recording a concise diagnostic on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"Cannot read {path.name}: {exc}")
        return None


def validate_frontmatter(text, root, errors):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.append("SKILL.md: missing opening frontmatter delimiter")
        return
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append("SKILL.md: missing closing frontmatter delimiter")
        return

    fields = {}
    for number, line in enumerate(lines[1:end], 2):
        match = re.fullmatch(r"([a-z][a-z-]*):(?: (.*))?", line)
        if not match:
            errors.append(f"SKILL.md:{number}: unsupported frontmatter syntax")
            continue
        key, value = match.group(1), (match.group(2) or "").strip()
        if key in fields:
            errors.append(f"SKILL.md:{number}: duplicate frontmatter key {key}")
        fields[key] = value
        if key not in {"name", "description"}:
            errors.append(f"SKILL.md:{number}: unsupported frontmatter key {key}")
        if not value:
            errors.append(f"SKILL.md: {key} must be nonempty")
        elif (
            value[0] in "[]{}&*!|>'\"%@`#?:,-"
            or ": " in value
            or " #" in value
            or value.lower() in {"true", "false", "null", "~", "yes", "no", "on", "off"}
            or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value)
        ):
            errors.append(f"SKILL.md: {key} must be a plain single-line string")

    for key in ("name", "description"):
        if key not in fields:
            errors.append(f"SKILL.md: missing required frontmatter field {key}")
    name = fields.get("name", "")
    if name and (len(name) > 64 or not NAME.fullmatch(name)):
        errors.append("SKILL.md: name must be lowercase hyphenated text, at most 64 characters")
    if name and name != root.name:
        errors.append("SKILL.md: name must match the containing directory name")
    description = fields.get("description", "")
    if len(description) > 1024:
        errors.append("SKILL.md: description exceeds 1024 characters")
    if not "\n".join(lines[end + 1:]).strip():
        errors.append("SKILL.md: instruction body is empty")


def validate(root):
    """Return validation errors; an empty list means success."""
    root = Path(root).resolve()
    errors = []
    skill = root / "SKILL.md"
    if not skill.is_file():
        return ["SKILL.md does not exist or is not a file"]
    text = read_text(skill, errors)
    if text is not None:
        validate_frontmatter(text, root, errors)
    for relative in REQUIRED_REFERENCES:
        if not (root / relative).is_file():
            errors.append(f"Missing required reference: {relative}")

    docs = sorted(root.rglob("*.md"))
    docs += [p for p in (root / "LICENSE", root / "evals/cases.jsonl") if p.is_file()]
    for path in docs:
        content = read_text(path, errors)
        if content is None:
            continue
        relative = path.relative_to(root)
        if not content.strip():
            errors.append(f"{relative}: file is empty")
        for number, line in enumerate(content.splitlines(), 1):
            if PLACEHOLDER.search(line):
                errors.append(f"{relative}:{number}: obvious unfinished placeholder")
        if path.suffix != ".md":
            continue
        for target in LINK.findall(content):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            linked = (path.parent / unquote(parsed.path)).resolve()
            try:
                linked.relative_to(root)
            except ValueError:
                errors.append(f"{relative}: local link escapes repository: {target}")
                continue
            if not linked.is_file():
                errors.append(f"{relative}: broken local link: {target}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: skill frontmatter, references, local links, and placeholder checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
