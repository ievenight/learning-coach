import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skill" / "learning-coach" / "scripts" / "learner_state.py"


class LearnerStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "state"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args, check=True):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def init_topic(self):
        self.run_cli(
            "init",
            "--root",
            str(self.root),
            "--topic",
            "linear-algebra",
            "--title",
            "Linear Algebra",
            "--goal",
            "Reason about transformations",
        )

    def test_init_and_validate(self):
        self.init_topic()
        result = self.run_cli("validate", "--root", str(self.root))
        self.assertIn("valid: 1 topic", result.stdout)
        self.assertTrue((self.root / "topics" / "linear-algebra" / "snapshot.json").exists())

    def test_evidence_is_append_only_and_snapshot_rebuilds(self):
        self.init_topic()
        base = [
            "record",
            "--root",
            str(self.root),
            "--topic",
            "linear-algebra",
            "--concept",
            "basis",
        ]
        self.run_cli(
            *base,
            "--challenge",
            "explain",
            "--outcome",
            "success",
            "--assistance",
            "hint",
            "--observation",
            "Succeeded after a directional hint",
        )
        self.run_cli(
            *base,
            "--challenge",
            "apply",
            "--outcome",
            "success",
            "--assistance",
            "none",
            "--delay",
            "delayed",
            "--observation",
            "Solved a changed example unaided",
        )
        evidence = (self.root / "topics" / "linear-algebra" / "evidence.jsonl").read_text().strip().splitlines()
        self.assertEqual(2, len(evidence))
        snapshot = json.loads((self.root / "topics" / "linear-algebra" / "snapshot.json").read_text())
        self.assertEqual("delayed", snapshot["concepts"]["basis"]["status"])
        self.assertFalse(snapshot["concepts"]["basis"]["needs_review"])

    def test_failure_preserves_history_and_flags_review(self):
        self.init_topic()
        common = [
            "--root",
            str(self.root),
            "--topic",
            "linear-algebra",
            "--concept",
            "basis",
        ]
        self.run_cli(
            "record",
            *common,
            "--challenge",
            "transfer",
            "--outcome",
            "success",
            "--assistance",
            "none",
            "--delay",
            "delayed",
            "--observation",
            "Transferred unaided",
        )
        self.run_cli(
            "record",
            *common,
            "--challenge",
            "transfer",
            "--outcome",
            "failure",
            "--assistance",
            "none",
            "--delay",
            "delayed",
            "--observation",
            "Missed a later boundary case",
        )
        snapshot = json.loads((self.root / "topics" / "linear-algebra" / "snapshot.json").read_text())
        concept = snapshot["concepts"]["basis"]
        self.assertEqual("transfer", concept["status"])
        self.assertTrue(concept["needs_review"])
        self.assertEqual(2, len(concept["evidence_ids"]))

    def test_due_queue(self):
        self.init_topic()
        self.run_cli(
            "review",
            "--root",
            str(self.root),
            "--topic",
            "linear-algebra",
            "--concept",
            "basis",
            "--due",
            "2026-07-15",
            "--evidence-type",
            "transfer",
            "--prompt",
            "Recognize basis change in a new domain",
        )
        result = self.run_cli("due", "--root", str(self.root), "--on", "2026-07-15")
        due = json.loads(result.stdout)
        self.assertEqual("basis", due[0]["concept_id"])

    def test_rejects_unsafe_topic_id(self):
        result = self.run_cli(
            "init",
            "--root",
            str(self.root),
            "--topic",
            "../escape",
            "--title",
            "Bad",
            "--goal",
            "Bad",
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("topic must use", result.stderr)


if __name__ == "__main__":
    unittest.main()

