"""Offline contract tests for the two validation commands."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


skill = load_script("validate_skill")
evals = load_script("validate_evals")


class SkillValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "social-agent-skill"
        self.root.mkdir()
        self.skill_path = self.root / "SKILL.md"
        self.valid_text = (
            "---\nname: social-agent-skill\n"
            "description: Choose useful social actions in forums.\n---\n"
            "# Social actions\n\nRead the conversation before replying.\n"
        )
        self.skill_path.write_text(self.valid_text, encoding="utf-8")
        for relative in skill.REQUIRED_REFERENCES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Reference\n\nUseful guidance.\n", encoding="utf-8")

    def errors(self):
        return "\n".join(skill.validate(self.root))

    def test_valid_minimal_package(self):
        self.assertEqual(skill.validate(self.root), [])

    def test_real_repository(self):
        self.assertEqual(skill.validate(ROOT), [])

    def test_missing_skill(self):
        self.skill_path.unlink()
        self.assertIn("SKILL.md does not exist", self.errors())

    def test_missing_or_unclosed_frontmatter(self):
        for text in ("# No frontmatter", "---\nname: social-agent-skill"):
            with self.subTest(text=text):
                self.skill_path.write_text(text)
                self.assertIn("frontmatter delimiter", self.errors())

    def test_each_required_field_is_required(self):
        for field in ("name", "description"):
            with self.subTest(field=field):
                text = "\n".join(line for line in self.valid_text.splitlines()
                                 if not line.startswith(field + ":"))
                self.skill_path.write_text(text)
                self.assertIn(f"missing required frontmatter field {field}", self.errors())

    def test_empty_and_nonstring_descriptions(self):
        for value in ("", "true", "null", "42", "[]", "{}", "|", "text: nested"):
            with self.subTest(value=value):
                text = self.valid_text.replace("Choose useful social actions in forums.", value)
                self.skill_path.write_text(text)
                self.assertIn("description must be", self.errors())

    def test_invalid_names(self):
        for name in ("Social-Agent", "social--agent", "-social", "social-", "x" * 65):
            with self.subTest(name=name):
                self.skill_path.write_text(self.valid_text.replace("name: social-agent-skill", "name: " + name))
                self.assertIn("name must be", self.errors())

    def test_name_must_match_directory(self):
        self.skill_path.write_text(self.valid_text.replace("name: social-agent-skill", "name: another-skill"))
        self.assertIn("containing directory", self.errors())

    def test_duplicate_and_unsupported_frontmatter(self):
        for added, message in (("name: social-agent-skill", "duplicate"),
                               ("unexpected: value", "unsupported")):
            with self.subTest(added=added):
                self.skill_path.write_text(self.valid_text.replace(
                    "description:", added + "\ndescription:"))
                self.assertIn(message, self.errors())

    def test_long_description_and_empty_body(self):
        self.skill_path.write_text(self.valid_text.replace("Choose useful social actions in forums.", "a" * 1025))
        self.assertIn("exceeds 1024", self.errors())
        self.skill_path.write_text(self.valid_text.split("# Social actions")[0])
        self.assertIn("body is empty", self.errors())

    def test_missing_reference(self):
        (self.root / skill.REQUIRED_REFERENCES[0]).unlink()
        self.assertIn("Missing required reference", self.errors())

    def test_empty_reference(self):
        (self.root / skill.REQUIRED_REFERENCES[0]).write_text("")
        self.assertIn("file is empty", self.errors())

    def test_placeholders_in_core_and_reference(self):
        for path in (self.skill_path, self.root / skill.REQUIRED_REFERENCES[0]):
            for marker in ("TODO", "TBD", "FIXME", "Lorem ipsum", "YOUR_PROJECT", "[INSERT TEXT HERE]"):
                with self.subTest(path=path.name, marker=marker):
                    original = path.read_text()
                    path.write_text(original + "\n" + marker)
                    self.assertIn("unfinished placeholder", self.errors())
                    path.write_text(original)

    def test_local_links(self):
        for target, message in (("missing.md", "broken local link"),
                                ("../outside.md", "escapes repository")):
            with self.subTest(target=target):
                self.skill_path.write_text(self.valid_text + f"\n[Details]({target})\n")
                self.assertIn(message, self.errors())
        self.skill_path.write_text(self.valid_text + "\n[Details](references/safety.md)\n")
        self.assertEqual(skill.validate(self.root), [])

    def test_non_utf8_is_reported(self):
        self.skill_path.write_bytes(b"\xff")
        self.assertIn("Cannot read", self.errors())


class EvaluationValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "cases.jsonl"
        self.cases = [dict(id=f"case_{i}", post="What is 2 + 2?", comments=[],
                           context="unanswered question", expected_action="reply",
                           acceptable_intent="answer arithmetic", forbidden_patterns=["irrelevant tangent"])
                      for i in range(30)]
        self.write_cases()

    def write_cases(self, cases=None):
        if cases is None:
            cases = self.cases
        self.path.write_text("".join(json.dumps(case) + "\n" for case in cases), encoding="utf-8")

    def errors(self):
        return "\n".join(evals.validate(self.path))

    def test_valid_cases_and_skip(self):
        self.cases[0]["expected_action"] = "skip"
        self.write_cases()
        self.assertEqual(evals.validate(self.path), [])

    def test_real_dataset(self):
        self.assertEqual(evals.validate(ROOT / "evals/cases.jsonl"), [])

    def test_minimum_count(self):
        for count in (0, 29):
            with self.subTest(count=count):
                self.write_cases(self.cases[:count])
                self.assertIn("at least 30", self.errors())

    def test_malformed_json_and_blank_lines(self):
        for line in ("{", "", '{"id": "x", "id": "y"}', '{"x": NaN}'):
            with self.subTest(line=line):
                self.write_cases()
                with self.path.open("a") as handle:
                    handle.write(line + "\n")
                self.assertTrue(evals.validate(self.path))

    def test_nonobject_records(self):
        for value in ([], None, "text", 42, True):
            with self.subTest(value=value):
                self.write_cases([value] + self.cases)
                self.assertIn("must be an object", self.errors())

    def test_duplicate_ids(self):
        self.cases[-1]["id"] = self.cases[0]["id"]
        self.write_cases()
        self.assertIn("duplicate case ID", self.errors())

    def test_missing_fields(self):
        for field in evals.REQUIRED_FIELDS:
            with self.subTest(field=field):
                cases = copy.deepcopy(self.cases)
                del cases[0][field]
                self.write_cases(cases)
                self.assertIn("missing required fields", self.errors())

    def test_bad_string_fields(self):
        for field in evals.TEXT_FIELDS:
            for value in (None, 3, [], "", " "):
                with self.subTest(field=field, value=value):
                    cases = copy.deepcopy(self.cases)
                    cases[0][field] = value
                    self.write_cases(cases)
                    self.assertIn(f"{field} must be a nonempty string", self.errors())

    def test_bad_action_types_and_values(self):
        for value in ("post", "Reply", None, {}, [], True):
            with self.subTest(value=value):
                self.cases[0]["expected_action"] = value
                self.write_cases()
                self.assertIn("expected_action must be reply or skip", self.errors())

    def test_bad_arrays(self):
        for field in ("comments", "forbidden_patterns"):
            for value in ("text", None, [3], [""], [{}]):
                with self.subTest(field=field, value=value):
                    cases = copy.deepcopy(self.cases)
                    cases[0][field] = value
                    self.write_cases(cases)
                    self.assertIn(f"{field} must be an array", self.errors())

    def test_whitespace_ids(self):
        self.cases[0]["id"] = " case_0 "
        self.write_cases()
        self.assertIn("surrounding whitespace", self.errors())

    def test_missing_and_non_utf8_file(self):
        self.path.unlink()
        self.assertIn("Cannot read", self.errors())
        self.path.write_bytes(b"\xff")
        self.assertIn("Cannot read", self.errors())


class CommandLineTests(unittest.TestCase):
    def test_default_paths_work_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            for script in ("validate_skill", "validate_evals"):
                with self.subTest(script=script):
                    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / f"{script}.py")],
                                            cwd=directory, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("PASS:", result.stdout)

    def test_invalid_paths_return_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = str(Path(directory) / "absent")
            for script in ("validate_skill", "validate_evals"):
                with self.subTest(script=script):
                    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / f"{script}.py"), missing],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("ERROR:", result.stdout)
                    self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
